// Course site worker. The whole course is private: only enrolled Google accounts (ALLOWED_EMAILS) get in.
//   /login                      sign-in page (Google button)            public
//   GET  /api/config            { clientId }                           public
//   POST /api/session           body { credential: <Google ID token> } -> sets the session cookie if the email is enrolled
//   POST /api/logout            clears the session cookie
//   GET  /api/me                { name, email, picture }               signed in
//   GET/PUT /api/progress       the learner's saved progress           signed in
//   everything else             the course page and its files          signed in (others are sent to /login)
const JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs";
const ISSUERS = ["https://accounts.google.com", "accounts.google.com"];
const COOKIE = "dfz_s", DAYS = 30, MAX_BYTES = 256 * 1024;
const KEY_PREFIX = "dfz:"; // keeps this course's keys apart if the KV namespace is shared with another course
let jwksCache = { at: 0, keys: [] }, hmacKey = null;

const enc = new TextEncoder(), dec = new TextDecoder();
const b64u = (bytes) => btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64u = (s) => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(s.length / 4) * 4, "=")), (c) => c.charCodeAt(0));
const json = (data, status = 200, headers = {}) => new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store", ...headers } });
const enrolled = (env, email) => (env.ALLOWED_EMAILS || "").toLowerCase().split(/[\s,]+/).filter(Boolean).includes((email || "").toLowerCase());

async function googleKeys() {
  if (Date.now() - jwksCache.at < 3600_000 && jwksCache.keys.length) return jwksCache.keys;
  const { keys } = await (await fetch(JWKS_URL)).json();
  jwksCache = { at: Date.now(), keys };
  return keys;
}
async function verifyGoogle(token, clientId) {
  const p = (token || "").split(".");
  if (p.length !== 3) throw new Error("bad token");
  const head = JSON.parse(dec.decode(unb64u(p[0]))), body = JSON.parse(dec.decode(unb64u(p[1])));
  if (head.alg !== "RS256") throw new Error("bad alg");
  const jwk = (await googleKeys()).find((k) => k.kid === head.kid);
  if (!jwk) throw new Error("unknown key");
  const key = await crypto.subtle.importKey("jwk", jwk, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  if (!(await crypto.subtle.verify("RSASSA-PKCS1-v1_5", key, unb64u(p[2]), enc.encode(p[0] + "." + p[1])))) throw new Error("bad signature");
  if (body.aud !== clientId || !ISSUERS.includes(body.iss) || !(body.exp > Date.now() / 1000 - 60) || !body.sub || body.email_verified === false) throw new Error("bad claims");
  return body;
}
async function key(env) {          // signing key for session cookies, made once and kept in KV
  if (hmacKey) return hmacKey;
  let raw = await env.PROGRESS.get(KEY_PREFIX + "cfg:session-key");
  if (!raw) { raw = b64u(crypto.getRandomValues(new Uint8Array(32))); await env.PROGRESS.put(KEY_PREFIX + "cfg:session-key", raw); }
  hmacKey = await crypto.subtle.importKey("raw", unb64u(raw), { name: "HMAC", hash: "SHA-256" }, false, ["sign", "verify"]);
  return hmacKey;
}
async function makeCookie(env, who) {
  const payload = b64u(enc.encode(JSON.stringify({ ...who, exp: Math.floor(Date.now() / 1000) + DAYS * 86400 })));
  const sig = b64u(await crypto.subtle.sign("HMAC", await key(env), enc.encode(payload)));
  return `${COOKIE}=${payload}.${sig}; Path=/; Max-Age=${DAYS * 86400}; HttpOnly; Secure; SameSite=Lax`;
}
async function session(request, env) {
  const m = (request.headers.get("cookie") || "").match(new RegExp(`(?:^|; )${COOKIE}=([^;]+)`));
  if (!m) return null;
  const [payload, sig] = m[1].split(".");
  if (!payload || !sig) return null;
  try {
    if (!(await crypto.subtle.verify("HMAC", await key(env), unb64u(sig), enc.encode(payload)))) return null;
    const s = JSON.parse(dec.decode(unb64u(payload)));
    if (!(s.exp > Date.now() / 1000) || !enrolled(env, s.email)) return null;   // removed from the list -> signed out
    return s;
  } catch { return null; }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url), path = url.pathname;
    const clientId = env.GOOGLE_CLIENT_ID || "";

    // public: the sign-in page and the sign-in API
    if (path === "/login" || path === "/login.html") {
      const res = await env.ASSETS.fetch(new Request(url.origin + "/login.html"));
      const out = new Response(res.body, res);
      out.headers.set("cache-control", "no-store");
      return out;
    }
    if (path === "/api/config") return json({ clientId });
    if (path === "/api/session" && request.method === "POST") {
      let who;
      try { const { credential } = await request.json(); who = await verifyGoogle(credential, clientId); }
      catch { return json({ error: "sign in again" }, 401); }
      if (!enrolled(env, who.email)) return json({ error: "not enrolled" }, 403);
      const cookie = await makeCookie(env, { sub: who.sub, email: who.email, name: who.given_name || who.name || "", picture: who.picture || "" });
      return json({ ok: true }, 200, { "set-cookie": cookie });
    }
    if (path === "/api/logout") return json({ ok: true }, 200, { "set-cookie": `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax` });

    // everything else needs an enrolled, signed-in learner
    const s = await session(request, env);
    if (!s) {
      if (path.startsWith("/api/")) return json({ error: "sign in" }, 401);
      const next = path + url.search;
      return Response.redirect(`${url.origin}/login?next=${encodeURIComponent(next)}`, 302);
    }
    if (path === "/api/me") return json({ name: s.name, email: s.email, picture: s.picture });
    if (path === "/api/progress") {
      const k = KEY_PREFIX + "u:" + s.sub;
      if (request.method === "GET") return json((await env.PROGRESS.get(k, "json")) || {});
      if (request.method === "PUT") {
        const text = await request.text();
        if (text.length > MAX_BYTES) return json({ error: "too large" }, 413);
        let data; try { data = JSON.parse(text); } catch { return json({ error: "bad json" }, 400); }
        if (typeof data !== "object" || data === null || Array.isArray(data)) return json({ error: "bad shape" }, 400);
        await env.PROGRESS.put(k, JSON.stringify({ ...data, email: s.email, savedAt: new Date().toISOString() }));
        return json({ ok: true });
      }
      return json({ error: "method not allowed" }, 405);
    }
    if (path.startsWith("/api/")) return json({ error: "not found" }, 404);
    const res = await env.ASSETS.fetch(request);
    const out = new Response(res.body, res);
    out.headers.set("cache-control", "private, no-cache");
    return out;
  },
};

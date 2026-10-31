// Course site worker.
//   Signed out: the free edition (Start here, Linux, Networking) at /, and the sign-in page at /login.
//   Signed in:  the full course at /, and progress saved per learner in KV.
// Sign-in is Google only, for Gmail addresses on the enrolled list (ALLOWED_EMAILS).
//
//   GET  /api/config            { clientId }                            public
//   POST /api/session           { credential: <Google ID token> }       public, Google sign-in
//   POST /api/logout            clears the session cookie
//   GET  /api/me                { name, email, picture, via }           signed in
//   GET/PUT /api/progress       the learner's saved progress            signed in
const JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs";
const ISSUERS = ["https://accounts.google.com", "accounts.google.com"];
const COOKIE = "dfz_s", DAYS = 30, MAX_BYTES = 256 * 1024;
const KEY_PREFIX = "dfz:"; // keeps this course's keys apart if the KV namespace is shared with another course
let jwksCache = { at: 0, keys: [] }, hmacKey = null;

const enc = new TextEncoder(), dec = new TextDecoder();
const b64u = (bytes) => btoa(String.fromCharCode(...new Uint8Array(bytes))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const unb64u = (s) => Uint8Array.from(atob(s.replace(/-/g, "+").replace(/_/g, "/").padEnd(Math.ceil(s.length / 4) * 4, "=")), (c) => c.charCodeAt(0));
const json = (data, status = 200, headers = {}) => new Response(JSON.stringify(data), { status, headers: { "content-type": "application/json", "cache-control": "no-store", ...headers } });
const norm = (s) => String(s || "").trim().toLowerCase();
const enrolled = (env, email) => (env.ALLOWED_EMAILS || "").toLowerCase().split(/[\s,]+/).filter(Boolean).includes(norm(email));

/* ---------- Google ---------- */
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
  if (body.aud !== clientId) throw new Error("wrong client id");
  if (!ISSUERS.includes(body.iss) || !(body.exp > Date.now() / 1000 - 60) || !body.sub || body.email_verified === false) throw new Error("bad claims");
  return body;
}

/* ---------- sessions ---------- */
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
    if (!(s.exp > Date.now() / 1000)) return null;
    // checked again on every request, so removing someone from ALLOWED_EMAILS signs them out
    if (s.via !== "google" || !enrolled(env, s.email)) return null;
    return s;
  } catch { return null; }
}
const signedIn = async (env, who) => json({ ok: true }, 200, { "set-cookie": await makeCookie(env, who) });

/* ---------- pages ---------- */
async function page(env, url, file) {
  const res = await env.ASSETS.fetch(new Request(url.origin + file));
  const out = new Response(res.body, res);
  out.headers.set("cache-control", "private, no-cache");
  return out;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url), path = url.pathname, method = request.method;
    const clientId = env.GOOGLE_CLIENT_ID || "";

    // ----- public -----
    if (path === "/login" || path === "/login.html") return page(env, url, "/login.html");
    if (path === "/api/config") return json({ clientId });
    if (path === "/api/logout") return json({ ok: true }, 200, { "set-cookie": `${COOKIE}=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax` });

    if (path === "/api/session" && method === "POST") {           // Google
      let who;
      try { const { credential } = await request.json(); who = await verifyGoogle(credential, clientId); }
      catch (e) { return json({ error: "google", detail: String(e && e.message || e) }, 401); }
      if (!enrolled(env, who.email)) return json({ error: "not enrolled", email: who.email }, 403);
      return signedIn(env, { via: "google", sub: who.sub, email: norm(who.email), name: who.given_name || who.name || "", picture: who.picture || "" });
    }

    // ----- the course page: full when signed in, free edition otherwise -----
    const s = await session(request, env);
    if (path === "/" || path === "/index.html") return page(env, url, s ? "/course.html" : "/index.html");
    if (!s) {
      if (path.startsWith("/api/")) return json({ error: "sign in" }, 401);
      return Response.redirect(`${url.origin}/login?next=${encodeURIComponent(path + url.search)}`, 302);
    }

    // ----- signed in -----
    if (path === "/api/me") return json({ name: s.name, email: s.email, picture: s.picture, via: s.via });
    if (path === "/api/progress") {
      const k = KEY_PREFIX + "p:" + norm(s.email);
      if (method === "GET") return json((await env.PROGRESS.get(k, "json")) || {});
      if (method === "PUT") {
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

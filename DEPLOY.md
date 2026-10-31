# Deploy to Cloudflare

A small Cloudflare Worker (`worker/index.js`) sits in front of the course:

- Signed out, anyone can read the free chapters: Start here, the Linux command line and Networking (Days 1 to 10).
  Every other lesson shows its title with a "Sign in to open" button. The free parts are set by `FREE_PARTS`
  in `site/build.py`.
- Signed in, learners get all 55 lessons, and their progress (lessons passed, quiz scores, review cards) is
  saved in Cloudflare KV, so it follows them between laptop and phone.

There are three ways to sign in, all on the `/login` page:

1. **Google**, for Gmail addresses on the enrolled list (`ALLOWED_EMAILS`).
2. **Email and password**, for accounts made with **Sign up**. Sign-up needs the invite code, so only people
   you give the code to can join. Passwords are stored as salted PBKDF2 hashes in KV.
3. **Test IDs** (`test1`, `test2`, `test3`), listed in `TEST_ACCOUNTS` as salted hashes. Their passwords are not in the repo.

Progress is saved by email address, so the same person keeps the same progress whether they use Google or a password.

Cloudflare's and Google's dashboards change now and then, so button names may differ a little from these steps.

## 1. Check the settings in `wrangler.jsonc`

```jsonc
"kv_namespaces": [{ "binding": "PROGRESS", "id": "db7a4fe1777f4276b3bf62828c86b331" }],
"vars": {
  "GOOGLE_CLIENT_ID": "213282967449-...apps.googleusercontent.com",
  "ALLOWED_EMAILS": "ai.arunav@gmail.com",
  "INVITE_CODE_SHA256": "<SHA-256 of the invite code>",
  "TEST_ACCOUNTS": "test1:<salt>:<hash>;test2:<salt>:<hash>;test3:<salt>:<hash>"
}
```

- `ALLOWED_EMAILS`: the enrolled learners. Add more as a comma-separated list, for example
  `"ai.arunav@gmail.com, friend@gmail.com"`. Removing an address signs that person out on their next request.
- `GOOGLE_CLIENT_ID`: the same Google sign-in client as ai-engineer-from-zero, so you don't need a new one.
- `INVITE_CODE_SHA256`: turns on sign-up. People type the invite code; the worker compares its SHA-256 with this value.
  Delete the line to close sign-up.
- `TEST_ACCOUNTS`: ready-made logins for testing. Delete an entry to disable that login.
- The KV namespace is also the one ai-engineer-from-zero uses. This course stores its keys under `dfz:`,
  so the two courses never touch each other's data. Deploy both from the same Cloudflare account.
  If you'd rather keep them apart, run `npx wrangler kv namespace create PROGRESS` and paste the new id here.

## 2. Allow the new site address in Google

Google only shows the sign-in button on addresses it knows.

1. Open https://console.cloud.google.com and pick the project that holds the ai-engineer-from-zero sign-in client.
2. Go to **APIs & Services** → **Credentials**, and open the OAuth 2.0 Client ID that ends in `...6fej68qpv`.
3. Under **Authorized JavaScript origins**, click **Add URI** and add
   `https://devops-from-zero.ai-arunav.workers.dev` (and your custom domain, if you add one later).
4. Save. Google can take a few minutes, sometimes a few hours, to accept a new origin.
5. If the consent screen is in **Testing** mode, open **OAuth consent screen** → **Test users** (in newer
   consoles: **Google Auth Platform** → **Audience**) and make sure every enrolled Gmail address is listed.

## 3. Deploy

### Option A: connect the GitHub repo (recommended)

Do this once. After that, every push to `main` redeploys the site by itself.

1. Sign in at https://dash.cloudflare.com with the same account as ai-engineer-from-zero.
2. In the left menu, open **Workers & Pages**, then click **Create** (or **Create application**).
3. Choose **Import a repository** and pick **GitHub**.
4. The first time, GitHub asks you to install the Cloudflare app. Choose **Only select repositories**,
   add `devops-from-zero`, and save. If the app is already installed, add the repo under
   GitHub → Settings → Applications → Cloudflare Workers and Pages → Configure.
5. Select `arunav-bhattacharya/devops-from-zero`.
6. Fill in the settings:
   - Project (Worker) name: `devops-from-zero`. It must match `"name"` in `wrangler.jsonc`.
   - Production branch: `main`
   - Build command: leave empty
   - Deploy command: `npx wrangler deploy`
   - Root directory: leave as `/`
7. Click **Save and Deploy** (or **Deploy**) and wait about a minute.

### Option B: deploy from your Mac

```bash
brew install node
```

```bash
git clone https://github.com/arunav-bhattacharya/devops-from-zero ~/code/devops-from-zero
```

```bash
cd ~/code/devops-from-zero
```

```bash
npx wrangler login
```

```bash
npx wrangler deploy
```

`wrangler login` opens a browser to approve access once. `wrangler deploy` prints the site's URL at the end.

## 4. Check it works

1. Open `https://devops-from-zero.ai-arunav.workers.dev` in a private window. You should see the free chapters, with
   a "Sign in" button at the top, and a locked lesson such as Day 30 should say "Sign in to open".
2. Sign in with a test ID (Email or test ID tab), or with an enrolled Gmail address. You should see all 55 lessons,
   with your name and "Sign out" at the top.
3. Mark Day 1 as passed, then open the site on your phone and sign in: Day 1 shows as passed there too.
4. Try a Gmail address that is not enrolled: you should see "This Google account is not enrolled".

## Change the invite code

Pick a new code, then put its hash in `INVITE_CODE_SHA256` and redeploy:

```bash
printf %s 'DFZ-NEW-CODE-HERE' | shasum -a 256
```

Accounts made with the old code keep working.

## Add or change a test login

This prints an entry for `TEST_ACCOUNTS` (here for `test4`). Keep the password somewhere safe; it is not stored anywhere else.

```bash
python3 -c "import base64,hashlib,os,sys;pw=sys.argv[1];s=os.urandom(16);b=lambda x:base64.urlsafe_b64encode(x).decode().rstrip('=');print('test4:'+b(s)+':'+b(hashlib.pbkdf2_hmac('sha256',pw.encode(),s,100000,32)))" 'choose-a-long-password'
```

Add it to `TEST_ACCOUNTS` with a `;` between entries, then redeploy.

## Remove a password account

Accounts live in KV under `dfz:acct:<email>`. Deleting the key signs that person out for good:

```bash
npx wrangler kv key delete --remote --binding PROGRESS "dfz:acct:someone@example.com"
```

## Enrolling or removing a Google learner

1. Edit `ALLOWED_EMAILS` in `wrangler.jsonc`.
2. If the Google consent screen is in Testing mode, add or remove the same address under its test users.
3. Commit and push (Option A redeploys), or run `npx wrangler deploy` (Option B).

## Changing the course later

1. Edit the lessons in `content/pN.json` (or the site in `site/`).
2. Rebuild the pages:

   ```bash
   pip install pygments
   python3 site/build.py
   ```

3. Commit and push. With Option A, Cloudflare redeploys on its own. With Option B, run `npx wrangler deploy` again.

## Test the worker on your laptop

```bash
npx wrangler dev
```

Then open http://localhost:8787. You'll see the free chapters; test IDs and sign-up work locally too. Google sign-in itself only works on an
address listed in step 2, so add `http://localhost:8787` there too if you want to sign in locally.

## If something goes wrong

- Google sign-in fails or the button does not load: the site address is missing from the client's authorized JavaScript origins (step 2), or Google hasn't picked it up yet. The Email or test ID tab works without Google.
- "This Google account is not enrolled": add the address to `ALLOWED_EMAILS` and redeploy.
- "Sign-in failed": the `GOOGLE_CLIENT_ID` in `wrangler.jsonc` does not match the client whose origins you edited.
- Deploy error about the KV namespace: the id in `wrangler.jsonc` must exist in the Cloudflare account you deploy to.
- "Worker name does not match": make the dashboard name and `"name"` in `wrangler.jsonc` the same.
- The page shows old content: run `python3 site/build.py` and commit `public/index.html`.

# Deploy to Cloudflare

The site is one static page: `public/index.html`. `wrangler.jsonc` in the repo root tells Cloudflare to serve
the `public/` folder. There is no server code and no sign-in: anyone with the link can read every lesson, and each
visitor's progress is saved in their own browser.

Cloudflare's dashboard changes now and then, so button names may differ a little from these steps.

## Option A: GitHub Actions deploys on every push (set up once)

The repo has `.github/workflows/deploy.yml`. On every push to `main` it runs `wrangler deploy` on GitHub's servers.
It needs two secrets from your Cloudflare account:

1. Create an API token. In the Cloudflare dashboard, open **My Profile** (top right) → **API Tokens** → **Create Token**.
   Next to **Edit Cloudflare Workers**, click **Use template**. Under **Account Resources**, pick your account.
   Click **Continue to summary**, then **Create Token**, and copy the token (Cloudflare shows it only once).
2. Find your Account ID. Open **Workers & Pages**: the **Account ID** is in the right-hand panel. It is also the long
   code in the dashboard address, `https://dash.cloudflare.com/<account-id>/...`.
3. Add both as GitHub secrets. In the repo on GitHub, open **Settings** → **Secrets and variables** → **Actions** →
   **New repository secret**, and add:
   - `CLOUDFLARE_API_TOKEN` with the token from step 1
   - `CLOUDFLARE_ACCOUNT_ID` with the ID from step 2
4. Run the first deploy. Open the **Actions** tab → **deploy** → **Run workflow** → **Run workflow**.
   It takes about a minute. The log ends with the site's URL.

From then on, every push to `main` redeploys. If a run fails with "Add CLOUDFLARE_API_TOKEN...", a secret is missing.

## Option C: let Cloudflare watch the repo instead

Use this instead of Option A, not as well.

1. In the Cloudflare dashboard, open **Workers & Pages** → `devops-from-zero` → **Settings** → **Build**, and connect the
   GitHub repository (or, for a new Worker: **Create** → **Import a repository** → GitHub).
2. Settings: production branch `main`, no build command, deploy command `npx wrangler deploy`, root directory `/`.
3. Deploy. Cloudflare then posts a check on each commit in GitHub, so you can see every build.

## Option B: deploy from your Mac

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

## Changing the course later

1. Edit the lessons in `content/pN.json` (or the site in `site/`).
2. Rebuild the page:

   ```bash
   pip install pygments
   python3 site/build.py
   ```

3. Commit and push. With Option A or C, the site redeploys on its own. With Option B, run `npx wrangler deploy` again.

## Optional extras

- Your own domain: open the Worker, then **Settings** → **Domains & Routes** → **Add** → **Custom domain**.

## If something goes wrong

- The live site still shows an old version (for example a sign-in page): it was deployed by hand and never updated.
  Use Option A (or run Option B again), then open the site in a private window.
- "Worker name does not match": make the dashboard name and `"name"` in `wrangler.jsonc` the same.
- The page shows old content: run `python3 site/build.py` and commit `public/index.html`.
- Blank page or 404: check that `public/index.html` exists in the repo and `wrangler.jsonc` says `"directory": "./public"`.

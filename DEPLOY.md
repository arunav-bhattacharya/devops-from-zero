# Deploy to Cloudflare

The site is one static page: `public/index.html`. `wrangler.jsonc` in the repo root tells Cloudflare
to serve the `public/` folder. There is no server code and nothing to build on Cloudflare's side.

Cloudflare's dashboard changes now and then, so button names may differ a little from these steps.

## Option A: connect the GitHub repo (recommended)

Do this once. After that, every push to `main` redeploys the site by itself.

1. Sign in at https://dash.cloudflare.com with the account you used for ai-engineer-from-zero.
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
8. Open `https://devops-from-zero.<your-subdomain>.workers.dev`. Your subdomain is the same one the
   AI course uses, so it should be `https://devops-from-zero.ai-arunav.workers.dev`.

To see past deploys or a failed one, open the Worker in the dashboard and look at its builds or deployments tab.

## Option B: deploy from your Mac

Good for a one-off deploy, or if you don't want Cloudflare to watch the repo.

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

3. Commit and push. With Option A, Cloudflare redeploys on its own. With Option B, run `npx wrangler deploy` again.

## Optional extras

- Your own domain: open the Worker, then **Settings** → **Domains & Routes** → **Add** → **Custom domain**.
- Keep it private: put the site behind Cloudflare Access (Zero Trust) so only your Google account can open it,
  or reuse the sign-in worker from ai-engineer-from-zero.

## If something goes wrong

- "Worker name does not match": make the dashboard name and `"name"` in `wrangler.jsonc` the same.
- The page shows old content: check that you ran `python3 site/build.py` and committed `public/index.html`.
- Blank page or 404: check that `public/index.html` exists in the repo and `wrangler.jsonc` says `"directory": "./public"`.

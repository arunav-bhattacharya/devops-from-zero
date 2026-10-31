# Deploy to Cloudflare

The site is one static page: `public/index.html`. `wrangler.jsonc` in the repo root tells Cloudflare to serve
the `public/` folder. There is no server code and no sign-in: anyone with the link can read every lesson, and each
visitor's progress is saved in their own browser.

Cloudflare's dashboard changes now and then, so button names may differ a little from these steps.

## Option A: connect the GitHub repo (recommended)

Do this once. After that, every push to `main` redeploys the site by itself.

1. Sign in at https://dash.cloudflare.com.
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
8. Open `https://devops-from-zero.<your-subdomain>.workers.dev` (for you, likely `https://devops-from-zero.ai-arunav.workers.dev`).

If you already connected the repo for the earlier version with sign-in, this push replaces it; nothing else to change.

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

3. Commit and push. With Option A, Cloudflare redeploys on its own. With Option B, run `npx wrangler deploy` again.

## Optional extras

- Your own domain: open the Worker, then **Settings** → **Domains & Routes** → **Add** → **Custom domain**.

## If something goes wrong

- "Worker name does not match": make the dashboard name and `"name"` in `wrangler.jsonc` the same.
- The page shows old content: run `python3 site/build.py` and commit `public/index.html`.
- Blank page or 404: check that `public/index.html` exists in the repo and `wrangler.jsonc` says `"directory": "./public"`.

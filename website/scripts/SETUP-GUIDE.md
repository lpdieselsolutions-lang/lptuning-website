# Auto-Blog Setup Guide — LP Tuning

One-time setup to get the automation running. Takes about 15 minutes.

---

## What it does

Every 3 days, GitHub automatically:
1. Picks the next topic from a rotation list (26 topics covering diesel tuning + locations + machines)
2. Uses Claude AI to write a full HTML blog post in the LP Tuning style
3. Adds it to blog.html and sitemap.xml
4. Commits and pushes — Cloudflare Pages auto-publishes it live

---

## Step 1 — Create a GitHub account (if you don't have one)

Go to https://github.com and sign up. Free plan is fine.

---

## Step 2 — Create a new repository

1. Click the **+** icon (top right) → **New repository**
2. Repository name: `lptuning-website`
3. Set it to **Private**
4. Click **Create repository**

---

## Step 3 — Upload the website files

In the new empty repo:

1. Click **uploading an existing file** (the link in the middle of the page)
2. Drag the entire contents of the `website` folder into the upload area
   - Include all `.html` files, images, `.github/` folder, `scripts/` folder
3. Scroll down, write a commit message like "Initial upload"
4. Click **Commit changes**

---

## Step 4 — Add your Anthropic API key as a secret

The script uses Claude AI to write the posts. You need an API key.

**Get the key:**
1. Go to https://console.anthropic.com
2. Click **API Keys** → **Create Key**
3. Copy the key (starts with `sk-ant-...`)

**Add it to GitHub:**
1. In your GitHub repo, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ANTHROPIC_API_KEY`
4. Value: paste your key
5. Click **Add secret**

---

## Step 5 — Connect Cloudflare Pages to GitHub

This replaces your current manual deploy with automatic deploy on every push.

1. Log in to the Cloudflare dashboard → **Pages**
2. Find your lptuning.com.au project → **Settings** → **Builds & deployments**
3. Under **Build configuration**, click **Connect to Git**
4. Authorise GitHub and select your `lptuning-website` repo
5. Branch: `main`
6. Build command: (leave blank — it's a static site)
7. Build output directory: `/` (root)
8. Click **Save**

From now on: every commit to GitHub auto-deploys to lptuning.com.au within 1-2 minutes.

---

## Step 6 — Test it manually

1. In your GitHub repo, click **Actions** (top menu)
2. Click **Auto-publish Blog Post** (left sidebar)
3. Click **Run workflow** → **Run workflow**
4. Watch it run (takes about 60 seconds)
5. Check your repo — a new `blog-diesel-tuning-brisbane.html` file should appear
6. Check lptuning.com.au/blog.html — the new post card should be at the top

---

## How the topic rotation works

Topics are in `scripts/generate_blog.py` in the `TOPICS` list.
Used topics are tracked in `scripts/used_topics.json`.
After all 26 topics are used, it resets and starts again.

To add new topics: open `generate_blog.py` and add a new dict to the `TOPICS` list at the bottom.

---

## Schedule

The action runs at 8pm AEST every 3 days. You can also trigger it manually at any time from the Actions tab.

---

## Cost

Each post costs approximately $0.05 AUD in Claude API credits (uses claude-haiku-5-5, cheapest model).
Running every 3 days = ~10 posts/month = ~$0.50/month.

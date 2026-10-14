# Cloudflare CDN Setup for lptuning.com.au

This puts Cloudflare's free CDN in front of your Netlify site. It takes about 15 minutes.

---

## What this does

- Your visitors hit Cloudflare's servers (fast, globally distributed) instead of Netlify directly
- Images and static files are cached at the edge — served instantly from a server close to the visitor
- Free DDoS protection and SSL certificate
- Google page speed typically improves by 1-2 seconds for Australian visitors

---

## Step 1 — Create a Cloudflare account

1. Go to [cloudflare.com](https://cloudflare.com) and sign up for a free account
2. After signing in, click **Add a site**
3. Enter `lptuning.com.au` and click **Add site**
4. Select the **Free** plan and continue

---

## Step 2 — Cloudflare scans your DNS

Cloudflare will automatically scan and import your existing DNS records. Wait for it to finish (30–60 seconds).

**Verify these records exist after the scan:**

| Type | Name | Content |
|------|------|---------|
| CNAME | `www` | your Netlify URL (e.g. `your-site.netlify.app`) |
| A or CNAME | `@` (root) | pointing to Netlify |

If any records are missing, add them manually. Your existing Netlify DNS values can be found in Netlify: **Site settings → Domain management → DNS panel**.

Make sure the **orange cloud icon** (Proxied) is turned ON for both the `@` and `www` records. This is what routes traffic through Cloudflare.

Click **Continue**.

---

## Step 3 — Update your nameservers at your domain registrar

Cloudflare will give you two nameservers, e.g.:
```
ada.ns.cloudflare.com
bob.ns.cloudflare.com
```

You need to update these at wherever you registered `lptuning.com.au` (likely Squarespace Domains, Namecheap, GoDaddy, or auDA registrar).

1. Log into your domain registrar
2. Find the DNS / Nameserver settings for `lptuning.com.au`
3. Replace the existing nameservers with the two Cloudflare nameservers
4. Save

DNS propagation takes 5–60 minutes (sometimes up to 24 hours). Cloudflare will email you when it's active.

---

## Step 4 — Recommended Cloudflare settings (once active)

Go to your Cloudflare dashboard for `lptuning.com.au` and apply these:

### Speed settings
- **Speed → Optimization → Auto Minify**: tick CSS, JavaScript, HTML
- **Speed → Optimization → Brotli**: ON
- **Speed → Optimization → Early Hints**: ON (pre-loads resources)

### Caching
- **Caching → Configuration → Browser Cache TTL**: set to **1 year**
- **Caching → Configuration → Caching Level**: Standard

### SSL/TLS
- **SSL/TLS → Overview**: set to **Full (strict)**
  - This encrypts traffic between Cloudflare and Netlify as well

### Redirects (important)
- **Rules → Redirect Rules**: add a rule to redirect `http://lptuning.com.au` → `https://lptuning.com.au` (Cloudflare may do this automatically)

---

## Step 5 — Test it

Once Cloudflare confirms your site is active:

1. Visit [pagespeed.web.dev](https://pagespeed.web.dev) and run a fresh test on `https://www.lptuning.com.au`
2. You should see a significant improvement — typically from 69 to 85–95
3. Also test on [gtmetrix.com](https://gtmetrix.com) — check "Fully Loaded Time"

---

## Troubleshooting

**Site shows SSL error after switching:** Set SSL mode to **Full** (not Flexible) in Cloudflare. Flexible causes redirect loops with Netlify.

**DNS not propagating:** Check [whatsmydns.net](https://whatsmydns.net) and enter your domain — once most locations show Cloudflare IPs you're good.

**Want to clear Cloudflare's cache after a site update:** Cloudflare dashboard → Caching → Purge Cache → Purge Everything. Do this after each Netlify deploy until you set up automatic cache purging.

---

*Prepared for LP Tuning — June 2026*

#!/usr/bin/env python3
"""
LP Tuning — Automated Blog Post Generator
Runs via GitHub Actions every 3 days.
Generates a new SEO-targeted blog post and updates blog.html + sitemap.xml.
"""

import os
import re
import json
import datetime
import anthropic

# ---------------------------------------------------------------------------
# Topic rotation — ordered list. Script picks the next unused topic.
# Add new topics to the bottom to keep the queue going.
# ---------------------------------------------------------------------------
TOPICS = [
    {
        "slug": "diesel-tuning-brisbane",
        "title": "Diesel Tuning Brisbane — What to Expect and How to Choose a Tuner",
        "category": "Diesel Tuning",
        "description": "What diesel tuning actually involves in Brisbane, how to choose a reputable mobile tuner, and what results are realistic for trucks, 4WDs, and heavy machinery.",
        "keywords": "diesel tuning Brisbane, ECU tuning Brisbane, diesel remap Brisbane",
    },
    {
        "slug": "diesel-tuning-toowoomba",
        "title": "Diesel Tuning Toowoomba — Mobile ECU Remapping for Darling Downs Operators",
        "category": "Diesel Tuning",
        "description": "LP Tuning's mobile diesel tuning service covering Toowoomba, the Darling Downs, and surrounding regions. Tractors, trucks, excavators, and 4WDs.",
        "keywords": "diesel tuning Toowoomba, ECU tuning Darling Downs, diesel remap Toowoomba",
    },
    {
        "slug": "diesel-tuning-gold-coast",
        "title": "Diesel Tuning Gold Coast — ECU Remapping for Trades, Towing, and Fleets",
        "category": "Diesel Tuning",
        "description": "Mobile diesel ECU tuning across the Gold Coast. More torque, better fuel economy, and 30-day free trial for utes, trucks, and heavy machinery.",
        "keywords": "diesel tuning Gold Coast, ECU remap Gold Coast, diesel tuning SEQ",
    },
    {
        "slug": "diesel-tuning-sunshine-coast",
        "title": "Diesel Tuning Sunshine Coast — Mobile Remap Service for Vehicles and Machinery",
        "category": "Diesel Tuning",
        "description": "LP Tuning covers the Sunshine Coast with mobile diesel tuning for utes, trucks, tractors, and earthmoving equipment. 30-day trial on every tune.",
        "keywords": "diesel tuning Sunshine Coast, ECU remap Sunshine Coast, mobile diesel tuning SEQ",
    },
    {
        "slug": "diesel-tuning-ipswich",
        "title": "Diesel Tuning Ipswich — ECU Remapping for Trades, Farmers, and Fleets",
        "category": "Diesel Tuning",
        "description": "Mobile diesel tuning in Ipswich and the Lockyer Valley. Utes, trucks, tractors and heavy machinery tuned on-site. Free quote, 30-day trial.",
        "keywords": "diesel tuning Ipswich, ECU remap Lockyer Valley, diesel tuning South East Queensland",
    },
    {
        "slug": "diesel-tuning-how-it-works",
        "title": "How Diesel Tuning Works — A Plain-English Explanation",
        "category": "Diesel Tuning",
        "description": "What actually happens during a diesel ECU remap, why factory maps are conservative, and what realistic gains look like for trucks and machinery in Queensland.",
        "keywords": "how diesel tuning works, diesel ECU remap explained, what is diesel tuning",
    },
    {
        "slug": "diesel-tuning-fuel-savings",
        "title": "Diesel Tuning Fuel Savings — Real Numbers for Queensland Operators",
        "category": "Diesel Tuning",
        "description": "How much fuel can diesel tuning actually save? Real-world figures for trucks, tractors, excavators, and 4WDs operating in Queensland conditions.",
        "keywords": "diesel tuning fuel savings, ECU remap fuel economy, diesel tuning ROI Queensland",
    },
    {
        "slug": "diesel-tuning-fleet",
        "title": "Diesel Tuning for Fleets — How Queensland Operators Cut Fuel Bills Across Multiple Vehicles",
        "category": "Fleet Tuning",
        "description": "How fleet managers use ECU remapping to reduce fuel spend across truck, ute, and machinery fleets. Per-vehicle ROI, visit scheduling, and what to expect.",
        "keywords": "fleet diesel tuning Queensland, diesel tuning for fleets, ECU remap fleet Brisbane",
    },
    {
        "slug": "isuzu-npr-diesel-tuning-queensland",
        "title": "Isuzu NPR Diesel Tuning Queensland — ECU Remap for the 4HK1 and 4JJ1 Engine",
        "category": "Truck Tuning",
        "description": "How ECU remapping improves the Isuzu NPR for Queensland delivery, trades, and tipper operations. More torque, less fuel, mobile service.",
        "keywords": "Isuzu NPR diesel tuning Queensland, Isuzu ECU remap, 4HK1 tuning Brisbane",
    },
    {
        "slug": "isuzu-fvz-diesel-tuning-queensland",
        "title": "Isuzu FVZ Diesel Tuning Queensland — Remap Results for Heavy Haulage",
        "category": "Truck Tuning",
        "description": "What an ECU remap delivers for the Isuzu FVZ — more pulling power, better fuel economy, and improved performance under load. Mobile service across QLD.",
        "keywords": "Isuzu FVZ diesel tuning Queensland, Isuzu FVZ remap, heavy truck ECU tuning Queensland",
    },
    {
        "slug": "kenworth-diesel-tuning-queensland",
        "title": "Kenworth Diesel Tuning Queensland — What a Remap Delivers for Your Kenworth",
        "category": "Truck Tuning",
        "description": "ECU remapping for Kenworth prime movers and highway trucks in Queensland. Fuel savings, power gains, and mobile on-site service across QLD.",
        "keywords": "Kenworth diesel tuning Queensland, Kenworth ECU remap, prime mover tuning QLD",
    },
    {
        "slug": "ford-ranger-diesel-tuning-brisbane",
        "title": "Ford Ranger Diesel Tuning Brisbane — ECU Remap for the 2.0 Bi-Turbo and 3.2 TDCi",
        "category": "4WD & Ute Tuning",
        "description": "What diesel tuning does for the Ford Ranger in Brisbane. More torque for towing, better fuel on long runs, and a 30-day free trial to prove it.",
        "keywords": "Ford Ranger diesel tuning Brisbane, Ranger ECU remap, PUMA 2.0 tuning SEQ",
    },
    {
        "slug": "mazda-bt50-diesel-tuning-queensland",
        "title": "Mazda BT-50 Diesel Tuning Queensland — ECU Remap for the 3.0 and 3.2 TDCi",
        "category": "4WD & Ute Tuning",
        "description": "How a diesel remap transforms the Mazda BT-50 for Queensland towing, work duties, and highway runs. Mobile service, 30-day trial.",
        "keywords": "Mazda BT-50 diesel tuning Queensland, BT-50 ECU remap, BT-50 tuning Brisbane",
    },
    {
        "slug": "mitsubishi-triton-diesel-tuning-brisbane",
        "title": "Mitsubishi Triton Diesel Tuning Brisbane — ECU Remap Results for the MR and MQ",
        "category": "4WD & Ute Tuning",
        "description": "What a diesel remap delivers on the Mitsubishi Triton MR and MQ. More torque, better towing economy, mobile service across Brisbane and SEQ.",
        "keywords": "Mitsubishi Triton diesel tuning Brisbane, Triton ECU remap, MR Triton tuning SEQ",
    },
    {
        "slug": "cat-excavator-diesel-tuning-queensland",
        "title": "Caterpillar Excavator Diesel Tuning Queensland — ECU Remap for CAT 320, 325, 330",
        "category": "Mining & Construction",
        "description": "How ECU remapping improves productivity and fuel economy on Caterpillar excavators operating in Queensland. CAT 320, 325, 330 and larger.",
        "keywords": "CAT excavator diesel tuning Queensland, Caterpillar ECU remap, CAT 320 tuning",
    },
    {
        "slug": "komatsu-excavator-diesel-tuning-queensland",
        "title": "Komatsu Excavator Diesel Tuning Queensland — What a Remap Delivers for PC200 to PC490",
        "category": "Mining & Construction",
        "description": "ECU remapping for Komatsu excavators in Queensland mining and construction. Better power under load, fuel savings, mobile on-site service.",
        "keywords": "Komatsu excavator diesel tuning Queensland, Komatsu ECU remap, PC200 tuning QLD",
    },
    {
        "slug": "diesel-tuning-vs-chip-tuning-difference",
        "title": "Diesel Tuning vs Chip Tuning — What's the Actual Difference?",
        "category": "Diesel Tuning",
        "description": "ECU remapping vs chip tuning: what they are, how they differ, and why custom diesel tuning produces better results for Queensland operators.",
        "keywords": "diesel tuning vs chip tuning, ECU remap vs chip, what is chip tuning Queensland",
    },
    {
        "slug": "diesel-tuning-warranty-queensland",
        "title": "Does Diesel Tuning Void Your Warranty? What Queensland Operators Need to Know",
        "category": "Diesel Tuning",
        "description": "The honest answer on diesel tuning and manufacturer warranties in Australia. What the law says, what manufacturers actually check, and how LP Tuning's trial protects you.",
        "keywords": "diesel tuning warranty Queensland, does ECU remap void warranty, diesel tuning warranty Australia",
    },
    {
        "slug": "case-ih-tractor-diesel-tuning-queensland",
        "title": "Case IH Tractor Diesel Tuning Queensland — ECU Remap for the Puma, Maxxum, and Optum",
        "category": "Agricultural Tuning",
        "description": "What diesel tuning delivers for Case IH tractors in Queensland. Fuel savings across broadacre and mixed farming operations, mobile service.",
        "keywords": "Case IH diesel tuning Queensland, Case IH ECU remap, Puma tractor tuning QLD",
    },
    {
        "slug": "new-holland-tractor-diesel-tuning-queensland",
        "title": "New Holland Tractor Diesel Tuning Queensland — ECU Remap for T6, T7, T8, and T9 Series",
        "category": "Agricultural Tuning",
        "description": "How ECU remapping improves fuel economy and pulling power on New Holland tractors across Queensland farms. Mobile service, 30-day trial.",
        "keywords": "New Holland diesel tuning Queensland, New Holland ECU remap, T7 tractor tuning QLD",
    },
    {
        "slug": "diesel-tuning-before-after",
        "title": "Diesel Tuning Before and After — What Changes and What to Expect",
        "category": "Diesel Tuning",
        "description": "A realistic look at what diesel ECU tuning changes: power, torque, fuel consumption, throttle response, and driveability. Before and after explained.",
        "keywords": "diesel tuning before and after, ECU remap results, diesel tuning what to expect",
    },
    {
        "slug": "diesel-tuning-mining-queensland",
        "title": "Diesel Tuning for Mining Equipment Queensland — Reducing Fuel Costs at the Pit",
        "category": "Mining & Construction",
        "description": "How Queensland mining operations use diesel ECU tuning to cut fuel spend and eliminate emission system downtime on excavators, dozers, and haul trucks.",
        "keywords": "diesel tuning mining Queensland, mining equipment ECU remap, excavator diesel tuning QLD",
    },
    {
        "slug": "volvo-truck-diesel-tuning-queensland",
        "title": "Volvo Truck Diesel Tuning Queensland — ECU Remap for FH, FM, and FMX Series",
        "category": "Truck Tuning",
        "description": "What a diesel remap delivers for Volvo FH, FM, and FMX trucks operating in Queensland. Fuel savings, improved torque, mobile on-site service.",
        "keywords": "Volvo truck diesel tuning Queensland, Volvo ECU remap, FH diesel tuning QLD",
    },
    {
        "slug": "man-truck-diesel-tuning-queensland",
        "title": "MAN Truck Diesel Tuning Queensland — ECU Remapping for TGX and TGS",
        "category": "Truck Tuning",
        "description": "ECU remapping for MAN TGX and TGS trucks in Queensland. Better fuel economy, more pulling power, mobile workshop service.",
        "keywords": "MAN truck diesel tuning Queensland, MAN ECU remap, TGX tuning QLD",
    },
    {
        "slug": "diesel-tuning-lockyer-valley",
        "title": "Diesel Tuning Lockyer Valley — Mobile ECU Remapping for Farms and Fleets",
        "category": "Diesel Tuning",
        "description": "LP Tuning's mobile diesel tuning service covers the Lockyer Valley — tractors, trucks, 4WDs, and earthmoving equipment tuned on-site.",
        "keywords": "diesel tuning Lockyer Valley, ECU remap Lockyer Valley, mobile diesel tuning QLD",
    },
    {
        "slug": "diesel-tuning-rockhampton",
        "title": "Diesel Tuning Rockhampton — ECU Remapping for Central Queensland Operators",
        "category": "Diesel Tuning",
        "description": "Mobile diesel tuning for Rockhampton and Central Queensland. Cattle station equipment, mining machinery, trucks, and 4WDs tuned on-site.",
        "keywords": "diesel tuning Rockhampton, ECU remap Central Queensland, mobile diesel tuning CQ",
    },
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLOG_INDEX = os.path.join(BASE_DIR, "blog.html")
SITEMAP = os.path.join(BASE_DIR, "sitemap.xml")
USED_FILE = os.path.join(BASE_DIR, "scripts", "used_topics.json")


def load_used() -> list:
    if os.path.exists(USED_FILE):
        with open(USED_FILE) as f:
            return json.load(f)
    return []


def save_used(used: list):
    with open(USED_FILE, "w") as f:
        json.dump(used, f, indent=2)


def pick_topic(used: list) -> dict:
    for t in TOPICS:
        if t["slug"] not in used:
            return t
    # All used — reset and start again
    save_used([])
    return TOPICS[0]


def today_str() -> str:
    return datetime.date.today().strftime("%Y-%m-%d")


def month_year() -> str:
    return datetime.date.today().strftime("%B %Y")


# ---------------------------------------------------------------------------
# Blog post HTML generator (calls Claude API)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a content writer for LP Tuning, a mobile diesel ECU tuning business
in Queensland, Australia (ABN 28 704 248 020). You write factual, no-nonsense blog articles
for farmers, miners, tradies, and fleet operators.

CRITICAL RULES — never break these:
- Never mention EGR, DPF, or AdBlue DELETES for on-road/registered vehicles or cars — these
  are only discussed for off-road machinery (mining, agriculture, earthmoving).
- Never say "retune" — always "remap" or "tune".
- Never name "AgroEcoPower" or "TruckEcoPower" — these are supplier names, not customer-facing.
- Never include specific pricing unless it is exactly: light vehicles $1,450+GST, heavy machinery
  contact for quote. If in doubt, omit pricing entirely.
- Never mention a dyno or rolling road for heavy machinery — we are a mobile service only.
- Do not write in lists for most content — use natural prose paragraphs. Lists are fine for
  bullet-point specs or compatible models.
- Do not use em dashes (—) anywhere in the article body text.
- Australian English throughout (e.g. "colour", "tyre", "organisation", "licence").
- The 30-day free trial is available now for SEQ (South East Queensland) customers.
- LP Tuning's phone number: 0491 097 706.
- LP Tuning's website: lptuning.com.au.
- LP Tuning is a mobile service. We come to the customer — no workshop drop-off required.
- LP Tuning has completed over 350,000 tunes globally via its parent network.
- Always end with a CTA to get-your-quote.html or call 0491 097 706.

TONE: Confident, practical, honest. Like a knowledgeable tradie talking to another tradie.
No fluff, no hype. State the facts and let them speak.

TARGET KEYWORD: Each post must naturally include "diesel tuning" and the location/context from
the topic brief, multiple times throughout the article, in a way that reads naturally.
"""


def generate_post_html(topic: dict, client: anthropic.Anthropic) -> str:
    slug = topic["slug"]
    title = topic["title"]
    category = topic["category"]
    description = topic["description"]
    keywords = topic["keywords"]
    date = today_str()
    month = month_year()

    user_prompt = f"""Write a complete, self-contained HTML blog post page for LP Tuning.

TOPIC: {title}
CATEGORY: {category}
META DESCRIPTION (use this exactly): {description}
TARGET KEYWORDS: {keywords}
DATE: {date}
MONTH/YEAR label for article: {month}

The HTML must follow this EXACT structure and style. Do not deviate from the CSS or layout.
Produce the full HTML document from <!DOCTYPE html> to </html>.

---TEMPLATE TO FOLLOW---

<!DOCTYPE html>
<html lang="en-AU">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[PAGE TITLE] | LP Tuning</title>
    <meta name="description" content="[META DESCRIPTION]">
    <link rel="canonical" href="https://lptuning.com.au/blog-{slug}.html">
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://lptuning.com.au/blog-{slug}.html">
    <meta property="og:title" content="[OG TITLE]">
    <meta property="og:description" content="[OG DESC]">
    <meta property="og:image" content="https://lptuning.com.au/hero.webp">
    <meta property="og:locale" content="en_AU">
    <meta property="og:site_name" content="LP Tuning">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:image" content="https://lptuning.com.au/hero.webp">
    <link rel="icon" href="favicon.ico" sizes="any">
    <link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
    <link rel="manifest" href="site.webmanifest">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preload" href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Oswald:wght@400;500;600;700&display=swap" as="style" onload="this.onload=null;this.rel='stylesheet'">
    <noscript><link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Oswald:wght@400;500;600;700&display=swap" rel="stylesheet"></noscript>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": "[H1 TEXT]",
        "description": "[META DESCRIPTION]",
        "author": {{"@type": "Organization", "name": "LP Tuning"}},
        "publisher": {{"@type": "Organization", "name": "LP Tuning", "url": "https://www.lptuning.com.au"}},
        "datePublished": "{date}",
        "dateModified": "{date}",
        "url": "https://lptuning.com.au/blog-{slug}.html",
        "image": "https://lptuning.com.au/hero.webp",
        "keywords": "{keywords}"
    }}
    </script>
    <style>
        :root {{
            --black: #0a0a0a; --gray-900: #1a1a1a; --gray-800: #222222;
            --gray-500: #808080; --gray-400: #909090; --gray-300: #999999; --gray-200: #bbbbbb;
            --white: #f5f5f5; --green-primary: #4CAF50; --green-light: #66BB6A;
            --font-heading: 'Oswald', sans-serif; --font-body: 'Inter', sans-serif;
            --transition-fast: 0.2s ease;
        }}
        *,*::before,*::after{{margin:0;padding:0;box-sizing:border-box}}
        html{{scroll-behavior:smooth;font-size:16px;-webkit-font-smoothing:antialiased}}
        body{{font-family:var(--font-body);background-color:var(--black);color:var(--gray-200);line-height:1.7;overflow-x:hidden}}
        a{{text-decoration:none;color:inherit;transition:color var(--transition-fast)}}
        h1,h2,h3,h4{{font-family:var(--font-heading);font-weight:700;line-height:1.2;color:var(--white);text-transform:uppercase;letter-spacing:0.02em}}
        p{{margin-bottom:1.4rem;color:var(--gray-300);line-height:1.9}}
        .container{{width:100%;max-width:760px;margin:0 auto;padding:0 2rem}}
        .nav{{position:fixed;top:0;left:0;right:0;z-index:1000;background:rgba(10,10,10,0.95);backdrop-filter:blur(20px);border-bottom:1px solid rgba(255,255,255,0.05);height:80px;display:flex;align-items:center}}
        .nav-inner{{display:flex;align-items:center;justify-content:space-between;width:100%;max-width:1100px;margin:0 auto;padding:0 2rem}}
        .nav-logo{{display:flex;align-items:center;gap:0.75rem}}
        .nav-logo img{{height:52px;width:auto;max-width:280px;object-fit:contain;border-radius:0}}
        .nav-links{{display:flex;align-items:center;gap:1.5rem}}
        .nav-link{{font-size:0.82rem;font-weight:500;letter-spacing:0.06em;color:var(--gray-300);transition:color var(--transition-fast)}}
        .nav-link:hover{{color:var(--green-primary)}}
        .nav-cta{{font-family:var(--font-heading);font-size:0.8rem;font-weight:600;letter-spacing:0.12em;text-transform:uppercase;padding:0.6rem 1.4rem;background:var(--green-primary);color:#0a0a0a;border-radius:4px}}
        .nav-cta:hover{{background:var(--green-light)}}
        .article-hero{{padding:140px 0 60px;border-bottom:1px solid rgba(255,255,255,0.06)}}
        .article-label{{font-family:var(--font-heading);font-size:0.75rem;letter-spacing:0.25em;text-transform:uppercase;color:var(--green-primary);margin-bottom:1rem}}
        .article-hero h1{{font-size:clamp(1.8rem,4vw,2.8rem);margin-bottom:1.25rem;line-height:1.15}}
        .article-meta{{font-size:0.82rem;color:var(--gray-500);margin-bottom:0}}
        .article-body{{padding:4rem 0 6rem}}
        .article-body h2{{font-size:clamp(1.3rem,2.5vw,1.75rem);margin:2.5rem 0 1rem}}
        .article-body ul{{margin:0 0 1.4rem 1.5rem;list-style:disc}}
        .article-body ul li{{color:var(--gray-300);margin-bottom:0.5rem;line-height:1.75}}
        .callout{{background:rgba(76,175,80,0.08);border-left:3px solid var(--green-primary);border-radius:0 8px 8px 0;padding:1.25rem 1.5rem;margin:2rem 0}}
        .callout p{{margin:0;color:var(--gray-200);font-weight:500}}
        .stats-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:2rem 0}}
        .stat-box{{background:var(--gray-900);border:1px solid rgba(76,175,80,0.15);border-radius:10px;padding:1.5rem;text-align:center}}
        .stat-number{{font-family:var(--font-heading);font-size:2rem;font-weight:700;color:var(--green-primary);display:block;margin-bottom:0.25rem}}
        .stat-label{{font-size:0.8rem;color:var(--gray-500)}}
        .article-cta{{background:var(--gray-900);border:1px solid rgba(255,255,255,0.06);border-radius:16px;padding:2.5rem;text-align:center;margin:3rem 0}}
        .article-cta h3{{margin-bottom:0.75rem;font-size:1.4rem}}
        .article-cta p{{margin-bottom:1.5rem;font-size:0.95rem}}
        .btn{{display:inline-block;padding:0.85rem 2rem;border-radius:4px;font-family:var(--font-heading);font-size:0.85rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;transition:background 0.2s,transform 0.15s}}
        .btn-primary{{background:var(--green-primary);color:#0a0a0a}}
        .btn-primary:hover{{background:var(--green-light);transform:translateY(-1px)}}
        .footer{{background:var(--gray-900);border-top:1px solid rgba(255,255,255,0.06);padding:2rem 0;text-align:center}}
        .footer p{{font-size:0.82rem;color:var(--gray-500);margin:0}}
        .footer a{{color:var(--gray-400)}}
        .footer a:hover{{color:var(--green-primary)}}
        .lp-mobile-bar{{display:none}}
        @media(max-width:767px){{
            .nav-links{{display:none}}
            .stats-grid{{grid-template-columns:1fr}}
            .lp-mobile-bar{{display:flex;position:fixed;bottom:0;left:0;right:0;z-index:999;background:#111;border-top:1px solid rgba(255,255,255,0.08);padding:0.5rem 0.75rem;gap:0.5rem}}
            .lp-mobile-bar a{{flex:1;display:flex;align-items:center;justify-content:center;gap:0.4rem;font-size:0.8rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:0.75rem 0.5rem;border-radius:5px;text-decoration:none;white-space:nowrap}}
            .mb-call{{background:rgba(76,175,80,0.15);border:1px solid rgba(76,175,80,0.3);color:var(--green-primary)}}
            .mb-quote{{background:var(--green-primary);color:#0a0a0a}}
        }}
    </style>
</head>
<body>
    <nav class="nav">
        <div class="nav-inner">
            <a href="index.html" class="nav-logo">
                <img src="logo-nav-transparent.webp" alt="LP Tuning Logo">
            </a>
            <div class="nav-links">
                <a href="index.html#services" class="nav-link">Services</a>
                <a href="blog.html" class="nav-link">Blog</a>
                <a href="get-your-quote.html" class="nav-cta">Get a Quote</a>
            </div>
        </div>
    </nav>

    <header class="article-hero">
        <div class="container">
            <p class="article-label">[CATEGORY] &bull; {month}</p>
            <h1>[H1 TITLE — write a compelling, keyword-rich H1]</h1>
            <p class="article-meta">By LP Tuning &nbsp;&bull;&nbsp; {date} &nbsp;&bull;&nbsp; Queensland, Australia</p>
        </div>
    </header>

    <article class="article-body">
        <div class="container">

            [ARTICLE BODY — write 700 to 900 words of practical, factual content.
             Use h2 subheadings to break it up (4 to 6 sections).
             Include one stats-grid with 3 stat-boxes showing realistic results.
             Include one callout about the 30-day free trial.
             Include one article-cta block near the end.
             End with a paragraph about coverage area and mobile service.
             Use natural prose paragraphs, not bullet lists (lists OK for compatible models/specs only).]

        </div>
    </article>

    <footer class="footer">
        <div class="container">
            <p>&copy; 2026 LP Tuning &mdash; ABN 28 704 248 020. Mobile diesel tuning Brisbane &amp; Queensland. <a href="index.html">Home</a> &nbsp;|&nbsp; <a href="blog.html">Blog</a> &nbsp;|&nbsp; <a href="privacy-policy.html">Privacy Policy</a></p>
        </div>
    </footer>

    <a href="https://wa.me/61491097706?text=Hi%20LP%20Tuning%2C%20I%27d%20like%20to%20enquire%20about%20a%20diesel%20remap." target="_blank" rel="noopener" aria-label="Chat on WhatsApp" style="position:fixed;bottom:2rem;left:2rem;width:52px;height:52px;background:#25D366;border-radius:50%;display:flex;align-items:center;justify-content:center;box-shadow:0 4px 20px rgba(37,211,102,0.4);z-index:900;transition:transform 0.2s,box-shadow 0.2s" onmouseover="this.style.transform='scale(1.12)'" onmouseout="this.style.transform=''">
        <svg xmlns="http://www.w3.org/2000/svg" width="26" height="26" viewBox="0 0 24 24" fill="white"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>
    </a>

    <div class="lp-mobile-bar" aria-label="Quick contact bar">
        <a href="tel:0491097706" class="mb-call">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 13.5 19.79 19.79 0 01.5 4.93 2 2 0 012.5 2.75h3a2 2 0 012 1.72c.13.96.36 1.9.7 2.81a2 2 0 01-.45 2.11L6.91 10.23a16 16 0 005.85 5.85l1.55-1.55a2 2 0 012.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0122 16.92z"/></svg>
            Call Now
        </a>
        <a href="get-your-quote.html" class="mb-quote">
            Get a Quote
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
        </a>
    </div>
</body>
</html>
---END TEMPLATE---

Now write the full HTML for topic: {title}
Fill in all [BRACKETED] placeholders and write the complete article body.
Return ONLY the raw HTML. No markdown fences, no explanation, no preamble.
"""

    message = client.messages.create(
        model="claude-haiku-5-5",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    for block in message.content:
        if hasattr(block, "text"):
            return block.text.strip()
    raise ValueError("No text block found in API response")


# ---------------------------------------------------------------------------
# Update blog index (prepend new card to the grid)
# ---------------------------------------------------------------------------
def make_blog_card(topic: dict) -> str:
    slug = topic["slug"]
    title = topic["title"]
    category = topic["category"]
    description = topic["description"]
    month = month_year()

    return (
        f'\n                <a href="blog-{slug}.html" style="display:block;background:var(--gray-800);'
        f'border:1px solid rgba(255,255,255,0.06);border-radius:16px;overflow:hidden;'
        f'transition:all 0.2s ease;text-decoration:none" '
        f'onmouseover="this.style.borderColor=\'rgba(76,175,80,0.4)\';this.style.transform=\'translateY(-4px)\'" '
        f'onmouseout="this.style.borderColor=\'rgba(255,255,255,0.06)\';this.style.transform=\'\'">\n'
        f'                    <div style="padding:2rem">\n'
        f'                        <div style="font-family:var(--font-heading);font-size:0.7rem;letter-spacing:0.2em;'
        f'text-transform:uppercase;color:var(--green-primary);margin-bottom:0.75rem">'
        f'{category} &nbsp;&bull;&nbsp; {month}</div>\n'
        f'                        <h3 style="font-size:1.2rem;margin-bottom:0.75rem;color:var(--white);line-height:1.3">'
        f'{title}</h3>\n'
        f'                        <p style="font-size:0.88rem;color:var(--gray-400);margin-bottom:1.25rem;line-height:1.7">'
        f'{description}</p>\n'
        f'                        <div style="display:flex;align-items:center;gap:0.5rem;font-family:var(--font-heading);'
        f'font-size:0.75rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:var(--green-primary)">\n'
        f'                            Read Article\n'
        f'                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        f'stroke-width="2.5"><path d="M5 12h14M12 5l7 7-7 7"/></svg>\n'
        f'                        </div>\n'
        f'                    </div>\n'
        f'                </a>\n'
    )


def update_blog_index(topic: dict):
    with open(BLOG_INDEX, "r", encoding="utf-8") as f:
        content = f.read()

    card = make_blog_card(topic)
    # Insert the new card as the FIRST item in the grid
    marker = '<!-- Featured Posts -->\n            <div style="display:grid'
    insert_after = content.find(marker)
    if insert_after == -1:
        # Fallback: find the opening grid div
        marker = 'display:grid;grid-template-columns:repeat(auto-fill'
        insert_after = content.find(marker)
        if insert_after == -1:
            print("WARNING: Could not find insertion point in blog.html")
            return

    # Find the end of the opening <div> tag after the grid marker
    open_tag_end = content.find(">", insert_after) + 1
    content = content[:open_tag_end] + card + content[open_tag_end:]

    with open(BLOG_INDEX, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated blog.html with card for: {topic['slug']}")


# ---------------------------------------------------------------------------
# Update sitemap.xml
# ---------------------------------------------------------------------------
def update_sitemap(topic: dict):
    with open(SITEMAP, "r", encoding="utf-8") as f:
        content = f.read()

    new_entry = (
        f"\n  <url>\n"
        f"    <loc>https://lptuning.com.au/blog-{topic['slug']}.html</loc>\n"
        f"    <lastmod>{today_str()}</lastmod>\n"
        f"    <changefreq>monthly</changefreq>\n"
        f"    <priority>0.7</priority>\n"
        f"  </url>"
    )

    # Insert before closing </urlset>
    content = content.replace("</urlset>", new_entry + "\n</urlset>")

    with open(SITEMAP, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Updated sitemap.xml with: blog-{topic['slug']}.html")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set")

    client = anthropic.Anthropic(api_key=api_key)

    used = load_used()
    topic = pick_topic(used)
    print(f"Generating post: {topic['slug']}")

    html = generate_post_html(topic, client)

    # Save the new blog post HTML
    out_path = os.path.join(BASE_DIR, f"blog-{topic['slug']}.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {out_path}")

    # Update blog index and sitemap
    update_blog_index(topic)
    update_sitemap(topic)

    # Mark as used
    used.append(topic["slug"])
    save_used(used)

    # Write title to temp file for the git commit message
    with open("/tmp/lp_blog_title.txt", "w") as f:
        f.write(topic["title"][:72])

    print(f"Done: {topic['title']}")


if __name__ == "__main__":
    main()

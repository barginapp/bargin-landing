"""Builds the SEO pages for bargin.app. Run from the repo root: python3 _tools/build_seo.py
Safe to re-run: generated pages are rewritten, edits to other pages are idempotent."""
import json, re, os, sys, datetime
sys.path.insert(0, os.path.dirname(__file__))
from guides_content import GUIDES

SITE = "https://www.bargin.app"
TODAY = datetime.date.today().isoformat()
calc = open("vinted-profit-calculator.html", encoding="utf-8").read()
style = re.search(r"<style>.*?</style>", calc, re.S).group(0)
icon = re.search(r'<link rel="icon"[^>]*>', calc).group(0)
header = re.search(r'<header class="site">.*?</header>', calc, re.S).group(0)
footer = re.search(r"<footer>.*?</footer>", calc, re.S).group(0)
fonts = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@500;600;700&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">')
extra_css = """<style>
  .prose h2{margin-top:36px;}
  .prose ul{padding-left:20px;} .prose li{margin:6px 0;}
  .prose b{color:var(--ink);}
  .calc-box,.note-box{background:var(--card);border:1px solid var(--hairline);border-radius:14px;padding:16px 20px;margin:18px 0;}
  .calc-box p{margin:6px 0;} .note-box{border-color:rgba(246,196,83,.4);color:var(--ink-soft);font-size:.92rem;}
  .crumbs{font-size:.85rem;color:var(--ink-faint);margin:28px 0 0;} .crumbs a{color:var(--ink-soft);text-decoration:none;}
  .cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;margin:24px 0;}
  .gcard{display:block;background:var(--card);border:1px solid var(--hairline);border-radius:16px;padding:22px;text-decoration:none;color:var(--ink);}
  .gcard:hover{border-color:rgba(52,211,153,.5);} .gcard span{display:block;color:var(--ink-soft);font-size:.92rem;margin-top:6px;}
  .gcard small{font-family:'IBM Plex Mono',monospace;color:var(--accent);font-size:.72rem;letter-spacing:.08em;text-transform:uppercase;}
</style>"""

def esc(s): return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")
def social(title, desc, url):
    return (f'<link rel="canonical" href="{url}">\n'
            f'<meta property="og:type" content="website">\n<meta property="og:site_name" content="Bargin">\n'
            f'<meta property="og:title" content="{esc(title)}">\n<meta property="og:description" content="{esc(desc)}">\n'
            f'<meta property="og:url" content="{url}">\n<meta property="og:image" content="{SITE}/og-image.png">\n'
            f'<meta property="og:image:width" content="1200">\n<meta property="og:image:height" content="630">\n'
            f'<meta property="og:locale" content="en_GB">\n<meta name="twitter:card" content="summary_large_image">\n'
            f'<meta name="twitter:title" content="{esc(title)}">\n<meta name="twitter:description" content="{esc(desc)}">\n'
            f'<meta name="twitter:image" content="{SITE}/og-image.png">\n<meta name="theme-color" content="#0B1F3A">')
def ld(obj): return '<script type="application/ld+json">\n' + json.dumps(obj, ensure_ascii=False, indent=1) + "\n</script>"
def faq_ld(pairs): return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
    {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
def crumbs_ld(items): return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
    {"@type": "ListItem", "position": i + 1, "name": n, "item": u} for i, (n, u) in enumerate(items)]}

def page(title, desc, url, head_extra, main):
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
{social(title, desc, url)}
{icon}
{fonts}
{head_extra}
{style}
{extra_css}
</head>
<body>
{header}
<main class="wrap">
{main}
</main>
{footer}
</body>
</html>
"""

cta = """<div class="cta-band">
    <h2>Check any listing in seconds</h2>
    <p>Paste a Vinted or Depop link and Bargin checks what the same item has actually sold for recently, then shows your real profit.</p>
    <a class="btn btn-primary" href="/#waitlist">Get Bargin</a>
  </div>"""

related_all = [("vinted-profit-calculator", "Tool", "Vinted profit calculator", "Work out your real profit, fees and postage included."),
               ("depop-fee-calculator", "Tool", "Depop fee calculator", "See what you keep after Depop's payment fee."),
               ("vinted-fees-explained", "Guide", "Vinted fees explained", "Buyer Protection, postage and what sellers pay."),
               ("vinted-tax-hmrc", "Guide", "Vinted and HMRC tax rules", "The 30-item rule and when resellers owe tax."),
               ("how-to-flip-on-vinted", "Guide", "How to flip on Vinted", "A beginner's guide to reselling for profit.")]
def related(exclude):
    cards = "".join(f'<a class="gcard" href="/{s}.html"><small>{k}</small>{t}<span>{d}</span></a>' for s, k, t, d in related_all if s != exclude)
    return f'<section class="info"><div class="prose"><h2>More free tools and guides</h2></div><div class="cards">{cards}</div></section>'

written = []
for g in GUIDES:
    url = f"{SITE}/{g['slug']}.html"
    faqs = "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in g["faq"])
    head_extra = "\n".join([
        ld({"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
            "mainEntityOfPage": url, "image": f"{SITE}/og-image.png", "inLanguage": "en-GB",
            "datePublished": "2026-09-29", "dateModified": TODAY,
            "author": {"@type": "Organization", "name": "Bargin", "url": SITE},
            "publisher": {"@type": "Organization", "name": "Bargin", "url": SITE}}),
        ld(faq_ld(g["faq"])),
        ld(crumbs_ld([("Home", SITE + "/"), ("Guides", SITE + "/guides.html"), (g["h1"], url)]))])
    main = f"""<nav class="crumbs" aria-label="Breadcrumb"><a href="/">Home</a> › <a href="/guides.html">Guides</a> › {g['h1']}</nav>
  <article class="intro prose">
    <span class="eyebrow">{g['eyebrow']}</span>
    <h1>{g['h1']}</h1>
    {g['body']}
    <h2>Questions</h2>
    {faqs}
  </article>
  {related(g['slug'])}
  {cta}"""
    open(f"{g['slug']}.html", "w", encoding="utf-8").write(page(g["title"], g["desc"], url, head_extra, main))
    written.append(g["slug"])

# Guides hub
hub_url = f"{SITE}/guides.html"
hub_cards = "".join(f'<a class="gcard" href="/{s}.html"><small>{k}</small>{t}<span>{d}</span></a>' for s, k, t, d in related_all)
open("guides.html", "w", encoding="utf-8").write(page(
    "Free Reselling Tools & Guides for Vinted and Depop (UK) — Bargin",
    "Free calculators and plain-English guides for UK Vinted and Depop resellers: fees, profit, tax and how to flip for profit.",
    hub_url, ld(crumbs_ld([("Home", SITE + "/"), ("Guides", hub_url)])),
    f"""<div class="intro"><span class="eyebrow">Free · UK resellers</span><h1>Reselling tools and guides</h1>
  <p class="lede">Everything you need to flip on Vinted and Depop without losing money: calculators, fee breakdowns and the tax rules in plain English.</p></div>
  <div class="cards">{hub_cards}</div>
  {cta}"""))
written.append("guides")

# Depop fee calculator: same tool, Depop-first
dep = calc
dep = dep.replace("<title>Vinted Profit Calculator (UK, 2026) — Bargin</title>", "<title>Depop Fee Calculator (UK, 2026): What You Keep After Fees — Bargin</title>")
dep = re.sub(r'<meta name="description" content="[^"]*">', '<meta name="description" content="Free Depop fee calculator for UK sellers. Depop has no selling fee, but charges 2.9% + £0.30 payment processing. See what you keep and your real profit on a flip.">', dep, 1)
dep = dep.replace("vinted-profit-calculator.html", "depop-fee-calculator.html")
dep = dep.replace('<h1>Vinted profit calculator</h1>', '<h1>Depop fee calculator</h1>')
dep = dep.replace("Work out what you'll really make on a flip before you buy. Includes Vinted Buyer Protection, Depop payment fees and postage.",
                  "See what you keep after Depop's payment processing fee, and your real profit on a flip. Works for Vinted too.")
dep = dep.replace("var buy = 'vinted', sell = 'vinted';", "var buy = 'vinted', sell = 'depop';")
dep = dep.replace('<button type="button" data-sell="vinted" aria-pressed="true">', '<button type="button" data-sell="vinted" aria-pressed="false">')
dep = dep.replace('<button type="button" data-sell="depop" aria-pressed="false">', '<button type="button" data-sell="depop" aria-pressed="true">')
dep = re.sub(r'<meta property="og:title" content="[^"]*">', '<meta property="og:title" content="Depop Fee Calculator (UK, 2026)">', dep)
dep = re.sub(r'<meta property="og:description" content="[^"]*">', '<meta property="og:description" content="What you keep after Depop fees, and your real profit.">', dep)
open("depop-fee-calculator.html", "w", encoding="utf-8").write(dep)
written.append("depop-fee-calculator")

# Add social image + related links to both calculators (idempotent)
for f in ["vinted-profit-calculator.html", "depop-fee-calculator.html"]:
    s = open(f, encoding="utf-8").read()
    if "og:image" not in s:
        s = s.replace('<meta property="og:type" content="website">',
                      '<meta property="og:type" content="website">\n<meta property="og:site_name" content="Bargin">\n'
                      f'<meta property="og:image" content="{SITE}/og-image.png">\n<meta property="og:locale" content="en_GB">\n'
                      '<meta name="twitter:card" content="summary_large_image">\n'
                      f'<meta name="twitter:image" content="{SITE}/og-image.png">\n<meta name="theme-color" content="#0B1F3A">')
    s = s.replace('<html lang="en">', '<html lang="en-GB">')
    if "gcard" not in s:
        s = s.replace("</style>", extra_css.replace("<style>", "").replace("</style>", "") + "</style>", 1)
        slug = f[:-5]
        s = s.replace('  <div class="cta-band">', related(slug) + '\n  <div class="cta-band">', 1)
    open(f, "w", encoding="utf-8").write(s)

# 404
open("404.html", "w", encoding="utf-8").write(page("Page not found — Bargin", "This page doesn't exist.", SITE + "/404.html",
    '<meta name="robots" content="noindex">',
    f"""<div class="intro"><h1>That page doesn't exist</h1><p class="lede">It may have moved. Try one of these instead.</p></div>
  <div class="cards">{hub_cards}</div>"""))

# robots + sitemap
pages = [("", "1.0"), ("vinted-profit-calculator.html", "0.9"), ("depop-fee-calculator.html", "0.8"), ("guides.html", "0.7")] + \
        [(g["slug"] + ".html", "0.7") for g in GUIDES] + [("privacy.html", "0.2"), ("terms.html", "0.2"), ("delete-account.html", "0.1")]
open("sitemap.xml", "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' +
    "".join(f"  <url><loc>{SITE}/{p}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>\n" for p, pr in pages) + "</urlset>\n")
open("robots.txt", "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\nDisallow: /_tools/\n\nSitemap: {SITE}/sitemap.xml\n")
print("written:", written)

"""Archive journal author-guideline / fee pages (body text) via the session Chrome (CDP), with a ledger."""
import asyncio
import datetime
import hashlib
import json
import os
import sys

from playwright.async_api import async_playwright

URLS = {
    "agu_publication_fees": "https://www.agu.org/publish-with-agu/publish/author-resources/publication-fees",
    "jgr_space_author_guidelines": "https://agupubs.onlinelibrary.wiley.com/hub/journal/21699402/about/author-guidelines",
    "acta_astronautica_guide": "https://www.sciencedirect.com/journal/acta-astronautica/publish/guide-for-authors",
    "jastp_guide": "https://www.sciencedirect.com/journal/journal-of-atmospheric-and-solar-terrestrial-physics/publish/guide-for-authors",
    "jsse_guide": "https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/publish/guide-for-authors",
    "scimago_acta_astronautica": "https://www.scimagojr.com/journalsearch.php?q=12360&tip=sid",
    "scimago_jastp": "https://www.scimagojr.com/journalsearch.php?q=27525&tip=sid",
    "scimago_jsse": "https://www.scimagojr.com/journalsearch.php?q=21100869517&tip=sid",
    "scimago_asr": "https://www.scimagojr.com/journalsearch.php?q=12347&tip=sid",
    # corrected Scimago source ids (2026-11-10): the four ids above resolve to unrelated journals (see
    # LEDGER.jsonl correction records); ids below were taken from the Scimago search results page.
    "scimago_acta_astronautica_sid12372": "https://www.scimagojr.com/journalsearch.php?q=12372&tip=sid",
    "scimago_jastp_sid28436": "https://www.scimagojr.com/journalsearch.php?q=28436&tip=sid",
    "scimago_asr_sid12375": "https://www.scimagojr.com/journalsearch.php?q=12375&tip=sid",
    "scimago_jsse_sid21100871641": "https://www.scimagojr.com/journalsearch.php?q=21100871641&tip=sid",
    "acta_astronautica_about": "https://www.sciencedirect.com/journal/acta-astronautica/about/aims-and-scope",
    "acta_astronautica_insights": "https://www.sciencedirect.com/journal/acta-astronautica/about/insights",
}


async def main(keys):
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp("http://localhost:29229")
        ctx = b.contexts[0]
        for k in keys:
            u = URLS[k]
            pg = await ctx.new_page()
            try:
                r = await pg.goto(u, timeout=60000, wait_until="domcontentloaded")
                await pg.wait_for_timeout(8000)
                txt, st = await pg.inner_text("body"), (r.status if r else None)
            except Exception as e:  # noqa: BLE001
                txt, st = f"ERROR {e}", None
            await pg.close()
            day = datetime.datetime.utcnow().strftime("%Y%m%d")
            fn = f"{k}_{day}.txt"
            if os.path.exists(fn):
                fn = f"{k}_{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%S')}.txt"
            open(fn, "w").write(txt)
            rec = dict(file=fn, url=u, status=st, retrieved_utc=datetime.datetime.utcnow().isoformat(),
                       bytes=os.path.getsize(fn), sha256=hashlib.sha256(open(fn, "rb").read()).hexdigest(),
                       method="session Chrome via CDP, body innerText", terms="publisher web page; archived for citation of requirements")
            open("LEDGER.jsonl", "a").write(json.dumps(rec) + "\n")
            print(k, st, len(txt))

asyncio.run(main(sys.argv[1:] or list(URLS)))

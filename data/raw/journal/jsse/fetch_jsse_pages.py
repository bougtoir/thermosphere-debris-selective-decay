import asyncio, hashlib, datetime, sys
from playwright.async_api import async_playwright
OUT='/home/ubuntu/repos/thermosphere-debris-selective-decay/data/raw/journal/jsse/'
urls={'journal_home':'https://www.sciencedirect.com/journal/journal-of-space-safety-engineering',
 'guide_for_authors':'https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/publish/guide-for-authors',
 'aims_scope':'https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/about/aims-and-scope',
 'open_access':'https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/publish/open-access-options',
 'insights':'https://www.sciencedirect.com/journal/journal-of-space-safety-engineering/about/insights',
 'elsevier_page':'https://www.elsevier.com/journals/journal-of-space-safety-engineering/2468-8967',
}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:29229')
        ctx=b.contexts[0]
        for k,u in urls.items():
            pg=await ctx.new_page()
            try:
                r=await pg.goto(u,wait_until='domcontentloaded',timeout=60000); await pg.wait_for_timeout(6000)
                t=await pg.inner_text('body'); h=await pg.content()
                open(OUT+k+'.txt','w').write(t); open(OUT+k+'.html','w').write(h)
                print(k, r.status if r else None, pg.url, len(t), datetime.datetime.utcnow().isoformat()+'Z', hashlib.sha256(h.encode()).hexdigest())
            except Exception as e: print(k,'ERR',e)
            await pg.close()
asyncio.run(main())

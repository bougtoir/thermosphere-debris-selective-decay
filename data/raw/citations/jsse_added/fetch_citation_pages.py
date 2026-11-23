import asyncio, os, hashlib, json, datetime
from playwright.async_api import async_playwright
OUT='/home/ubuntu/repos/thermosphere-debris-selective-decay/data/raw/citations/jsse_added'
DOIS=["10.1016/S2468-8967(16)30022-2","10.1016/j.jsse.2020.06.006","10.1016/j.jsse.2022.12.001","10.1016/j.jsse.2024.04.002","10.1016/j.jsse.2020.07.020","10.1016/S2468-8967(17)30003-4","10.1016/j.actaastro.2013.10.005","10.1016/j.actaastro.2012.11.009","10.1016/j.paerosci.2015.11.001","10.1029/JA083iA06p02637","10.1126/science.1121337"]
async def main():
    async with async_playwright() as p:
        b=await p.chromium.connect_over_cdp('http://localhost:29229'); ctx=b.contexts[0]
        led=[]
        for d in DOIS:
            pg=await ctx.new_page()
            try:
                r=await pg.goto('https://doi.org/'+d,wait_until='domcontentloaded',timeout=60000)
                await pg.wait_for_timeout(6000)
                txt=await pg.inner_text('body'); st=r.status if r else None; url=pg.url
            except Exception as e:
                txt=f'ERROR {e}'; st=None; url=''
            fn=os.path.join(OUT,d.replace('/','_')+'.txt'); open(fn,'w').write(txt)
            led.append(dict(doi=d,final_url=url,status=st,retrieved_utc=datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),file=os.path.basename(fn),bytes=len(txt.encode()),sha256=hashlib.sha256(txt.encode()).hexdigest()))
            print(d,st,len(txt),flush=True); await pg.close()
        with open(os.path.join(OUT,'LEDGER.jsonl'),'w') as f:
            for x in led: f.write(json.dumps(x)+'\n')
asyncio.run(main())

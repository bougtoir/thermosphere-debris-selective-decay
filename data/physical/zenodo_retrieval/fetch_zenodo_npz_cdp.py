import asyncio, json, os, hashlib
from playwright.async_api import async_playwright
OUT='/home/ubuntu/repos/thermosphere-debris-selective-decay/data/physical/processed'
d=json.load(open('/home/ubuntu/zen_record.json'))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.connect_over_cdp('http://localhost:29229')
        ctx = b.contexts[0]
        for f in d['files']:
            if not f['key'].endswith('.npz'): continue
            dest=os.path.join(OUT,f['key'])
            if os.path.exists(dest) and os.path.getsize(dest)==f['size']: continue
            pg = await ctx.new_page()
            url=f"https://zenodo.org/records/24101202/files/{f['key']}?download=1"
            async with pg.expect_download(timeout=900000) as di:
                try: await pg.goto(url, timeout=60000)
                except Exception as e: pass
            dl = await di.value
            await dl.save_as(dest)
            print(f['key'], os.path.getsize(dest), flush=True)
            await pg.close()
asyncio.run(main())

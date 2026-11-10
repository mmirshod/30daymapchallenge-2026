"""Verify the real bilingual gallery, all report pages and PDF downloads."""
import argparse,functools,http.server,json,threading
from pathlib import Path
from playwright.sync_api import sync_playwright
parser=argparse.ArgumentParser();parser.add_argument('--url');args=parser.parse_args()
project=Path(__file__).resolve().parents[1];docs=project.parents[1]/'docs'
out=project/('report/gallery_live' if args.url else 'report/gallery_qa');out.mkdir(exist_ok=True)
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=None;thread=None
if args.url:base=args.url
else:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(docs)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}/'
errors=[];bad=[];checks=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True,args=['--disable-background-networking','--disable-extensions'])
        context=browser.new_context(viewport={'width':1440,'height':1000})
        page=context.new_page();page.on('pageerror',lambda e:errors.append(str(e)))
        page.on('response',lambda r:bad.append({'url':r.url,'status':r.status}) if r.status>=400 else None)
        page.goto(base+'?lang=ru',wait_until='networkidle')
        assert page.locator('.work-card').count()==6
        assert 'Тридцать дней' in page.locator('h1').inner_text()
        for kind,count in [('interactive',2),('analysis',3),('process',1),('all',6)]:
            page.locator('[data-filter="'+kind+'"]').click();assert page.locator('.work-card:visible').count()==count
        checks.append('six published days and interactive/analysis/process filters')
        page.locator('#gallery-language').select_option('en');assert 'Thirty days' in page.locator('h1').inner_text()
        page.locator('#gallery-language').select_option('ru')
        page.screenshot(path=str(out/'gallery_desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844});assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(out/'gallery_mobile.png'),full_page=True)
        checks.append('gallery RU/EN switching and 390px mobile layout')
        for day in ['day01','day02','day03','day04','day05','day10']:
            page.goto(base+'reports/'+day+'/?lang=ru',wait_until='networkidle')
            assert page.locator('.method-section li').count()==3
            assert page.locator('.report-posters figure').count()>0
            assert page.locator('.limits-note p').inner_text().strip()
            assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
            for img in page.locator('.report-posters img').all():
                img.scroll_into_view_if_needed();img.evaluate("el=>el.loading='eager'")
                page.wait_for_function('(src)=>{const e=[...document.images].find(x=>x.src===src);return e&&e.complete&&e.naturalWidth>0;}',arg=img.get_attribute('src') if img.get_attribute('src').startswith('http') else img.evaluate('e=>e.src'))
            link=page.locator('.report-actions a[href$=".pdf"]').get_attribute('href')
            from urllib.parse import urljoin
            response=context.request.get(urljoin(page.url,link));assert response.status==200 and response.body().startswith(b'%PDF-')
            checks.append(day+': original poster images, method, limitations and working PDF')
            if day=='day03':page.screenshot(path=str(out/'report_mobile.png'),full_page=True)
            page.locator('#gallery-language').select_option('en');assert 'How the study works' in page.locator('.method-section').inner_text()
        for path in ['day01/','day05/']:
            response=context.request.get(base+path);assert response.status==200
        checks.append('existing Day 01 map and Day 05 explorer remain reachable')
        assert not errors,errors
        assert not bad,bad
        browser.close()
    result={'status':'passed','url':base if args.url else 'local docs preview','checks':checks,'page_errors':errors,'http_errors':bad}
    (out/'validation.json').write_text(json.dumps(result,indent=2),encoding='utf8');print(json.dumps(result,indent=2))
finally:
    if server:server.shutdown();server.server_close();thread.join(timeout=3)

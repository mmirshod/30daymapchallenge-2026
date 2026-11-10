"""Real Edge acceptance checks using the existing browser, served locally."""
import argparse,contextlib,csv,functools,http.server,json,threading,time
from pathlib import Path
from playwright.sync_api import sync_playwright

project=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--url',help='Verify a deployed explorer instead of starting a local server')
args=parser.parse_args()
root=project/'web';output=project/('report/g6/qa_live' if args.url else 'report/g6/qa');output.mkdir(parents=True,exist_ok=True)
class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):pass
server=None;thread=None
if args.url:url=args.url
else:
    server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(QuietHandler,directory=str(root)))
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    url=f'http://127.0.0.1:{server.server_port}/'
errors=[];failed=[];checks=[]
try:
    with sync_playwright() as p:
        browser=p.chromium.launch(channel='msedge',headless=True,args=['--disable-background-networking','--disable-extensions'])
        context=browser.new_context(viewport={'width':1440,'height':1100},device_scale_factor=1)
        page=context.new_page();page.on('pageerror',lambda error:errors.append(str(error)))
        page.on('response',lambda response:failed.append({'url':response.url,'status':response.status}) if response.status>=400 else None)
        page.goto(url,wait_until='networkidle');page.wait_for_function('window.BTSReady===true')
        assert page.locator('#ranking-body tr').count()==1302;checks.append('all 1302 summits loaded')
        fixture=page.evaluate('''() => {
          const d=state.data.summits;
          const errN=Math.max(...d.map(s=>Math.abs(BTSScore.score(s,[30,25,30,15],'nps',.2)-s.nps)));
          const errM=Math.max(...d.map(s=>Math.abs(BTSScore.score(s,[30,25,30,15],'mps',.2)-s.mps)));
          const zero=JSON.stringify(BTSScore.normalize([0,0,0,0]))===JSON.stringify(BTSScore.normalize([30,25,30,15]));
          let invalid=false;try{BTSScore.normalize([-1,1,1,1]);}catch{invalid=true;}
          return {errN,errM,zero,invalid,winner:state.ranking[0].id};
        }''')
        assert fixture['errN']<1e-10 and fixture['errM']<1e-10 and fixture['zero'] and fixture['invalid']
        assert fixture['winner']=='node:1544318728';checks.append('browser scores reproduce every published NPS and MPS')
        assert page.locator('#leader-button').get_attribute('data-summit')==fixture['winner']
        assert page.locator('.rank-pin').count()==1 and page.locator('.selection-halo').count()==1
        page.locator('#show-top10').check()
        assert page.locator('.rank-pin').count()==10
        page.locator('#search').fill('no-such-summit-test')
        assert page.locator('#ranking-body tr').count()==0
        assert page.locator('.rank-pin').count()==10 and page.locator('.selection-halo').count()==1
        assert page.locator('#leader-button').get_attribute('data-summit')==fixture['winner']
        page.locator('#search').fill('')
        checks.append('persistent mode leader, optional Top 10 and selected halo remain visible through filters')
        page.locator('#map').scroll_into_view_if_needed()
        box=page.locator('#map').bounding_box();zoom=page.evaluate('map.getZoom()')
        page.mouse.move(box['x']+box['width']*.6,box['y']+min(box['height']*.55,500))
        page.mouse.wheel(0,-400)
        page.wait_for_function('(z)=>map.getZoom()>z',arg=zoom)
        page.wait_for_function('!map._animatingZoom')
        zoomed=page.evaluate('map.getZoom()');page.mouse.wheel(0,400)
        page.wait_for_function('(z)=>map.getZoom()<z',arg=zoomed)
        page.wait_for_function('!map._animatingZoom')
        assert page.evaluate('map.touchZoom.enabled()')
        page.evaluate('()=>{map.fitBounds(state.data.bounds,{animate:false});}')
        checks.append('wheel/touchpad zoom in and out; touch pinch handler enabled')
        page.locator('#mountaineering').click();assert page.locator('#ranking-body tr').first.locator('button').get_attribute('data-summit')=='node:2556670543'
        assert page.locator('#leader-button').get_attribute('data-summit')=='node:2556670543'
        assert page.locator('.rank-pin').count()==10
        checks.append('published MPS winner reproduced')
        page.locator('#ranking-body tr').first.locator('button').click();page.wait_for_selector('#profile svg')
        page.locator('#show-connections').check();page.locator('#horizon-only').check()
        assert '12 visible connections' in page.locator('#connection-count').inner_text();checks.append('Zamok detail, skyline and 12 non-self Horizon connections')
        page.evaluate("document.getElementById('w-terrain').value=100;document.getElementById('w-terrain').dispatchEvent(new Event('input',{bubbles:true}))")
        assert 'Your weights' in page.locator('#ranking-label').inner_text();checks.append('slider reranks and marks custom scores')
        assert page.evaluate("document.getElementById('leader-button').dataset.summit===state.ranking[0].id")
        page.locator('#show-top10').uncheck();assert page.locator('.rank-pin').count()==1
        checks.append('leader follows mode/custom weights and Top 10 can be hidden independently')
        with page.expect_download() as event:page.locator('#download').click()
        event.value.save_as(output/'custom_ranking.csv')
        rows=list(csv.DictReader((output/'custom_ranking.csv').open(encoding='utf-8-sig')))
        assert len(rows)==1302 and rows[0]['mode']=='mps';checks.append('custom CSV download includes 1302 rows and weights')
        page.locator('#band').select_option('3000–3500 m') if '3000–3500 m' in page.locator('#band').inner_text() else page.locator('#band').select_option(index=2)
        assert 0<page.locator('#ranking-body tr').count()<1302;checks.append('elevation band filtering')
        page.locator('#band').select_option('all');page.locator('#search').fill('node:2556670543')
        assert page.locator('#ranking-body tr').count()==1;checks.append('OSM identity search')
        page.locator('#search').fill('');page.locator('#landmarks').select_option('node:3328009998')
        count=page.locator('#ranking-body tr').count();assert 0<count<1302;checks.append('individual Horizon visibility filter')
        page.locator('#landmarks').select_option('all');page.locator('#reset').click()
        for key in ['terrain','peaks','skyline','distance']:
            page.evaluate("id=>{const e=document.getElementById(id);e.value=0;e.dispatchEvent(new Event('input',{bubbles:true}));}",'w-'+key)
        assert 'All weights are zero' in page.locator('#weights-warning').inner_text();checks.append('all-zero weights safely restore default scoring')
        page.locator('#reset').click();page.locator('#natural').click()
        share=page.url;page.reload(wait_until='networkidle');page.wait_for_function('window.BTSReady===true');assert page.url==share
        assert page.locator('#ranking-body tr').count()==1302;checks.append('shared URL state restored')
        page.wait_for_selector('#profile svg');page.screenshot(path=str(output/'desktop.png'),full_page=True)
        page.set_viewport_size({'width':390,'height':844});page.screenshot(path=str(output/'mobile.png'),full_page=True)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1');checks.append('390px layout has no horizontal overflow')
        page.locator('#map').screenshot(path=str(output/'map.png'))
        original_first=page.locator('#ranking-body tr').first.locator('button').get_attribute('data-summit')
        page.locator('#language').select_option('ru')
        page.wait_for_function("document.documentElement.lang==='ru'")
        assert page.locator('#natural').inner_text()=='Природный'
        assert page.locator('label[for="search"]').inner_text()=='Найти вершину'
        assert page.locator('#ranking-label').inner_text()=='Исходные веса'
        assert page.locator('#ranking-body tr').first.locator('button').get_attribute('data-summit')==original_first
        assert 'Компонент горизонта' in page.locator('#detail').inner_text()
        assert 'lang=ru' in page.url
        checks.append('Russian static and dynamic labels, unchanged ranking, language in shared URL')
        page.locator('#band').select_option(index=2)
        assert 0<page.locator('#ranking-body tr').count()<1302
        page.locator('#band').select_option('all');page.locator('#mountaineering').click()
        assert page.locator('#ranking-body tr').first.locator('button').get_attribute('data-summit')=='node:2556670543'
        assert 'lang=ru' in page.url
        page.reload(wait_until='networkidle');page.wait_for_function('window.BTSReady===true')
        assert page.locator('#mountaineering').inner_text()=='Альпинистский'
        assert 'Исходные веса' in page.locator('#ranking-label').inner_text()
        assert page.locator('#ranking-body tr').count()==1302
        checks.append('Russian band filtering, MPS switch and language retained after reload')
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.screenshot(path=str(output/'mobile_ru.png'),full_page=True)
        page.set_viewport_size({'width':1440,'height':1100});page.screenshot(path=str(output/'desktop_ru.png'),full_page=True)
        page.locator('#language').select_option('en')
        page.wait_for_function("document.documentElement.lang==='en'")
        assert page.locator('#mountaineering').inner_text()=='Mountaineering'
        assert page.locator('#ranking-label').inner_text()=='Published weights'
        checks.append('English restored without losing scoring state; Russian mobile has no overflow')
        assert not errors,errors
        assert not failed,failed
        browser.close()
    result={'status':'passed','url':url if args.url else 'local preview','checks':checks,'score_max_error':fixture,'page_errors':errors,'failed_http_responses':failed,'browser':'Installed Microsoft Edge via Playwright; no browser download'}
    (output/'browser_validation.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result,indent=2))
finally:
    if server:server.shutdown();server.server_close();thread.join(timeout=3)

"""Build a bilingual collection and report pages around preserved source art."""
from pathlib import Path
import shutil
from PIL import Image
from jinja2 import Environment,FileSystemLoader,select_autoescape
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import yaml
from .runtime import PROJECT,REPOSITORY,config,require_resources,fingerprint,atomic_json

def build_gallery():
    require_resources(config())
    docs=REPOSITORY/'docs';gallery=docs/'gallery';assets=gallery/'assets';assets.mkdir(parents=True,exist_ok=True)
    content=PROJECT/'config/gallery.yaml'
    days=yaml.safe_load(content.read_text(encoding='utf-8'))['days']
    env=Environment(loader=FileSystemLoader(PROJECT/'templates'),autoescape=select_autoescape(['html']))
    source_hashes={}
    for day in days:
        require_resources(config())
        folder=docs/'reports'/day['id'];folder.mkdir(parents=True,exist_ok=True)
        if any(folder.iterdir()) and not (folder/'index.html').exists():
            raise ValueError('Unexpected unowned report folder: '+str(folder))
        day.setdefault('interactive',None);day['report_url']='reports/'+day['id']+'/'
        images=[]
        for i,name in enumerate(day['images']):
            source=REPOSITORY/name;source_hashes[name]=fingerprint(source)
            if source.is_relative_to(docs):target=source
            else:
                target=folder/'images'/f'page_{i+1:02d}.png';target.parent.mkdir(exist_ok=True);shutil.copy2(source,target)
            with Image.open(source) as image:width,height=image.size
            images.append({'path':target.relative_to(docs).as_posix(),'width':width,'height':height})
        day['image_urls']=images
        with Image.open(REPOSITORY/day['images'][0]) as image:
            image=image.convert('RGB');image.thumbnail((900,900));image.save(assets/(day['id']+'.webp'),'WEBP',quality=86)
        if day.get('pdf'):day['pdf_url']=day['pdf']
        else:
            pdf=folder/'report.pdf';report=canvas.Canvas(str(pdf));report.setTitle('Day '+day['number']+' — '+day['title']['en'])
            report.setAuthor('Original cartography: mmirshod · image-only PDF export')
            for name in day['images']:
                with Image.open(REPOSITORY/name) as image:
                    w,h=image.size;scale=900/max(w,h);width,height=w*scale,h*scale
                    report.setPageSize((width,height));report.drawImage(ImageReader(image),0,0,width,height);report.showPage()
            report.save();day['pdf_url']=pdf.relative_to(docs).as_posix()
    for index,day in enumerate(days):
        html=env.get_template('gallery_report.html').render(day=day,next_day=days[(index+1)%len(days)])
        (docs/'reports'/day['id']/'index.html').write_text(html,encoding='utf-8',newline='\n')
    with Image.open(PROJECT/'report/g6/assets/ranking_map.png') as image:
        image=image.convert('RGB');image.thumbnail((1100,1100));image.save(assets/'panorama.webp','WEBP',quality=88)
    for name in ['gallery.css','gallery.js']:shutil.copy2(PROJECT/'templates'/name,gallery/name)
    (docs/'index.html').write_text(env.get_template('gallery.html').render(days=days),encoding='utf-8',newline='\n')
    files=[docs/'index.html',*[p for p in gallery.rglob('*') if p.is_file() and p.name!='export.json'],*[p for p in (docs/'reports').rglob('*') if p.is_file()]]
    manifest={'kind':'30DayMapChallenge gallery','days':[d['id'] for d in days],'sources':source_hashes,
        'content_sha256':fingerprint(content),'files':{p.relative_to(docs).as_posix():fingerprint(p) for p in files}}
    atomic_json(gallery/'export.json',manifest)
    return {'days':len(days),'files':len(manifest['files']),'bytes':sum(p.stat().st_size for p in files),'original_reports_modified':False}

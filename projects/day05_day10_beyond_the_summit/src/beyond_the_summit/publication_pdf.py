"""Six editorial landscape pages rendered from measured project evidence."""
from pathlib import Path
from html import escape
import json
import numpy as np
import matplotlib.font_manager as fm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3,landscape
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.graphics.barcode.qr import QrCodeWidget
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF
from .runtime import PROJECT,config,require_resources

PAPER='#f5f3eb';INK='#233f38';MUTED='#63756d';GREEN='#416e5c';GOLD='#bd9657';PANEL='#e5ebe2'
W,H=landscape(A3)

class Pages:
    def __init__(self,path,title,day):
        self.path=path;self.title=title;self.day=day;self.number=0
        self.c=canvas.Canvas(str(path),pagesize=(W,H));self.c.setTitle(title);self.c.setAuthor('Beyond the Summit · Python + Codex')
        for name,weight in [('Body','normal'),('Bold','bold')]:
            font=fm.findfont(fm.FontProperties(family='DejaVu Sans',weight=weight));pdfmetrics.registerFont(TTFont(name,font))
    def text(self,text,x,y,size=14,bold=False,color=INK):
        self.c.setFillColor(HexColor(color));self.c.setFont('Bold' if bold else 'Body',size);self.c.drawString(x,y,text)
    def para(self,text,x,y,width,size=14,color=INK):
        style=ParagraphStyle('body',fontName='Body',fontSize=size,leading=size*1.5,textColor=HexColor(color))
        p=Paragraph(text,style);_,height=p.wrap(width,H)
        if y-height<48:raise ValueError('PDF text overflows page: '+text[:80])
        p.drawOn(self.c,x,y-height);return y-height-14
    def rect(self,x,y,w,h,color=PANEL):
        self.c.setFillColor(HexColor(color));self.c.rect(x,y,w,h,fill=1,stroke=0)
    def image(self,path,x,y,w,h):self.c.drawImage(str(path),x,y,w,h,preserveAspectRatio=True,anchor='c',mask='auto')
    def page(self,title,subtitle):
        if self.number:self.c.showPage()
        self.number+=1;self.rect(0,0,W,H,PAPER)
        self.text('30DAYMAPCHALLENGE 2026  /  '+self.day,40,H-38,11,True,GREEN)
        title_size=min(32,(W-80)/pdfmetrics.stringWidth(title,'Bold',1))
        self.text(title,40,H-88,title_size,True)
        self.text(subtitle,40,H-116,12,False,MUTED)
        self.c.setStrokeColor(HexColor('#cbd1c6'));self.c.line(40,46,W-40,46)
        self.text('OSM contributors · Copernicus DEM · Gorets · Python · Codex',40,25,9,False,MUTED)
        self.c.setFillColor(HexColor(GREEN));self.c.setFont('Bold',10)
        self.c.drawRightString(W-40,25,f'{self.day} / {self.number:02d}')
    def close(self):self.c.save()

def metric(pdf,x,y,value,label,width=250):
    pdf.text(value,x,y,40,True,GREEN);pdf.para(label,x,y-16,width,12,MUTED)

def qr(pdf,url,x,y,size=84):
    widget=QrCodeWidget(url);b=widget.getBounds();w=b[2]-b[0];h=b[3]-b[1]
    d=Drawing(size,size,transform=[size/w,0,0,size/h,0,0]);d.add(widget);renderPDF.draw(d,pdf.c,x,y)

def reports(scores,plots,logs,publication):
    root=PROJECT/'report/g6';root.mkdir(parents=True,exist_ok=True)
    nps=scores.loc[scores.position.idxmin()];mps=scores.loc[scores.mps_position.idxmin()]
    p=Pages(root/'day05_beyond_the_summit.pdf','Beyond the Summit — Where Are the Best Mountain Views?','DAY 05 · SIGHT')
    p.page('Beyond the Summit','Where are the best mountain views? An exploratory ranking of the same 1,302 summits used in Days 01–04.')
    p.image(plots['ranking_map'],40,110,740,570)
    p.text('THE BIG PICTURE',815,675,12,True,GREEN)
    y=p.para('Higher is not automatically better. Terrain, visible peaks, skyline shape and distance tell different parts of the story.',815,650,330,18)
    p.rect(805,y-103,345,100)
    p.text('NATURAL #1',820,y-25,11,True,GREEN)
    p.text(nps.observer_id,820,y-51,19,True)
    p.text(f'NPS {nps.nps:.2f} / 100 · {nps.elevation_m:,.0f} m',820,y-78,14)
    y-=132;p.rect(805,y-103,345,100,'#eee4d4')
    p.text('MOUNTAINEERING #1',820,y-25,11,True,GREEN)
    p.text('Замок / Zamok',820,y-51,22,True)
    p.text(f'MPS {mps.mps:.2f} · {int(mps.visible_horizon_count)} / 15 Horizon targets',820,y-78,14)
    p.para('• 100 km projected radius; 30 m terrain.<br/>• Elevation–NPS Spearman correlation: 0.329.<br/>• The highest summit ranks 729th in NPS.<br/>• The top two NPS scores differ by only 0.029.',815,y-125,330,13)
    p.text('Map: published NPS. Stars mark the NPS and MPS winners. Shaded relief is a preview backdrop.',55,80,11,False,MUTED)
    p.page('The anatomy of a panorama','Example: Zamok, the published MPS winner. Ground visibility is a modelled proxy, not a field observation.')
    for x,key,title,caption in [
        (40,'viewshed','01  Visible terrain','Green: visible ground cells. Display raster is reduced; analysis remains 30 m.'),
        (425,'skyline','02  The skyline','Signed elevation angle across true bearing. Source profile: 0.1° angular intervals.'),
        (810,'network','03  Visibility connections','All visible peak-ground proxies. Gold lines identify visible Horizon landmarks.')]:
        p.text(title,x,675,18,True);p.image(plots[key],x,380,340,265);p.para(caption,x,365,340,12,MUTED)
    p.rect(40,175,535,125);p.text('NPS = .30 T + .25 P + .30 S + .15 D',60,268,20,True)
    p.para('T: visible terrain area and open directions. P: peak count and bearing coverage. S: multiscale angular skyline contrast and complexity. D: terrain depth and peak angular relief. Components use fixed G5 cohort normalization.',60,247,490,12)
    p.rect(605,175,545,125,'#eee4d4');p.text('MPS = .80 NPS + .20 L',625,268,20,True)
    p.para('Horizon-only L: 70% visible coverage, 15% distance and 15% positive angular relief. All observers share the denominator of 15; self-observation is excluded. Program breadth is omitted because only one program is eligible.',625,247,500,12)
    p.para('Model: GDAL GVM_Edge; observer +1.7 m; target at DEM ground; Earth curvature with k=0.14286. Copernicus is a surface model. A feature on the skyline need not be a named summit; angular contrast is not topographic prominence.',40,140,1090,12,MUTED)
    p.page('The results, with room for doubt','Published weights are one interpretation. The explorer lets visitors build and download their own ranking.')
    p.image(plots['elevation'],40,350,530,325);p.image(plots['top10'],610,350,540,325)
    p.text('A modest association, not a rule',40,310,19,True)
    p.para('Spearman ρ = 0.329; Pearson r = 0.338. Descriptive for a mapped, spatially dependent ≥1,800 m cohort. No causal claim or independent-sample significance test is made.',40,287,510,13)
    special=json.loads((PROJECT/'data/processed/g5/special_winners.json').read_text(encoding='utf-8'))
    p.para(f"Special viewpoints: largest visible area {special['largest_visible_area']['value']:,.1f} km² ({special['largest_visible_area']['observer_id']}); most visible peak proxies: Каракуш / Karakush, {int(special['most_visible_peaks']['value'])}.",40,200,510,13)
    p.text('Weights change the answer',610,310,19,True)
    p.para('Zamok wins MPS with 20% or 30% landmark weight and with count-only L. At 10%, the NPS winner returns to first place. The NPS leaders are nearly tied; the ordering is not a universal aesthetic judgement.',610,287,530,13)
    p.para('Limits: 30 m surface terrain, incomplete OSM names, ground-cell targets, engine disagreement and subjective scoring. Radius is projected: some reported geodesic distances slightly exceed 100 km. Lakes and other excluded programs contribute nothing.',610,195,410,12,MUTED)
    qr(p,publication['site_url'],1050,85,85)
    p.text('Explore the interactive map:',40,105,11,True,GREEN)
    p.text(publication['site_url'],40,84,11)
    p.close()

    status=json.loads((PROJECT/'data/processed/g4_status.json').read_text(encoding='utf-8'))
    d=Pages(root/'day10_beyond_the_prompt.pdf','Beyond the Prompt — Building a Geospatial Research Project with Codex','DAY 10 · PROMPTING ONLY')
    d.page('Beyond the Prompt','Building a geospatial research project with Codex — from a broad question to a reproducible, bounded experiment.')
    d.text('THE QUESTION',40,670,12,True,GREEN)
    y=d.para('Which summits offer the most interesting mountain panoramas — and does height predict the answer?',40,645,500,25)
    d.para('A human supplied the objective, local knowledge, source files and scope decisions. Codex inspected the environment, wrote and ran Python, tested the methods and generated the deliverables. Development used code; no manual QGIS or Figma export was required.',40,y-15,500,15)
    metric(d,40,310,'1,302','Existing observation summits; Days 01–04 preserved.')
    metric(d,315,310,'2 + 1','Two reports and one static interactive explorer.',230)
    d.para('Human responsibilities: set the scope, supply program identities, accept exploratory accuracy and authorize resource use. Agent responsibilities: implement, measure, preserve evidence and disclose uncertainty. Publication is a separate authorization.',40,195,500,14)
    d.rect(610,155,540,520)
    d.text('PROMPT → EVIDENCE → PUBLICATION',635,640,16,True)
    steps=[('01  Discover','Audit Windows, source data, memory and GIS runtimes.'),('02  Test','Compare engines; measure a pilot before full execution.'),('03  Compute','Checkpoint every summit; control concurrency live.'),('04  Interpret','Freeze component formulas, then rank and test sensitivity.'),('05  Export','Python builds PDF, PNG, JSON, CSV and static web assets.')]
    for i,(title,body) in enumerate(steps):
        y=592-i*87;d.text(title,635,y,18,True,GREEN);d.para(body,635,y-12,480,13)
    d.page('How the code became a pipeline','The important revisions changed both the scientific scope and the cost of execution.')
    phases=[('G1 · Engine','GDAL synthetic acceptance; correct CRS, heights, curvature and NoData.'),('G2 · Inputs','Complete 100 km DEM support; international peak targets; source hashes.'),('G3 · Benchmark','Twelve sequential cases; measure time and memory rather than guess.'),('G4 · Production','1,302 checkpoints; three workers; pause or reduce concurrency at any time.'),('G5 · Rankings','Frozen NPS; scoped Horizon-only MPS; weight and skyline sensitivity.'),('G6 · Exports','Reproducible reports; browser-only ranking weights; local staging.')]
    for i,(title,body) in enumerate(phases):
        x=40+(i%3)*385;y=660-(i//3)*190;d.rect(x,y-150,350,150)
        d.text(title,x+18,y-32,18,True,GREEN);d.para(body,x+18,y-50,310,13)
    d.text('Actual prompt revisions',40,245,20,True)
    d.para('“considering dramatic speedup and that this is not real research project but more for fun right now, let\'s re plan the pipeline using GDAL”',40,220,520,13)
    d.para('“retain only 1 GiB reserved, test first with 3 workers, then after successfull test start G4 full analysis. While processing G4, make sure to have checkpoints in order to reduce number of workers anytime”',620,220,520,13)
    d.para('The supplied prompt archive records these revisions. Source hashes, per-summit artifacts and machine-readable CLI logs connect a decision to the result it produced. Counts below refer only to captured records.',40,115,1100,12,MUTED)
    d.page('What worked. What failed. What remains.','Measured evidence is reported separately from missing development telemetry.')
    metric(d,40,625,str(logs['captured_execution_starts']),'Recorded process starts, including workers',245)
    metric(d,330,625,str(logs['captured_prompt_files']),'Supplied prompt files captured',245)
    metric(d,620,625,f"{status['wall_seconds']/3600:.2f} h",'G4 elapsed wall time, including an interruption gap',245)
    metric(d,910,625,f"{status['sampled_peak_process_tree_rss_bytes']/2**30:.2f} GiB",'Sampled peak G4 process-tree RSS',240)
    d.text('Reliable patterns',40,475,19,True)
    d.para('Small pilots prevented expensive wrong turns. Hashed checkpoints let work resume safely. The six-case three-worker benchmark measured a 1.55× speedup; concurrency could drain from three workers to one and return without losing completed results.',40,450,340,14)
    d.text('Useful failures',425,475,19,True)
    d.para('90 m terrain changed visible area by roughly 20–32% in the pilot, so 30 m was retained. Windows installation needed a short-prefix prebuilt environment and a GRASS DLL workaround. GDAL was accepted with disclosed disagreement. RAM gates paused later attempts; no unrelated processes were killed.',425,450,340,14)
    d.text('Honest boundaries',810,475,19,True)
    d.para('Complete agent-iteration counts and active development hours were not captured. CLI starts are not agent turns. Log durations overlap and must not be summed as elapsed development. GIS tests are not field validation. Rankings depend on scope and subjective weights.',810,450,340,14)
    d.rect(40,75,1110,170)
    d.text('Reproducibility is a deliverable',60,211,20,True,GREEN)
    d.para(f"At export: {logs['successful_finishes']} successful and {logs['failed_finishes']} failed captured CLI finishes. Earlier baseline verification: 51 tests passed; MPS: 3 focused tests passed. G6 browser/export validation is saved separately with the build. Source locks, manifests, actual prompts, decisions and failure records are retained.",60,189,1055,13)
    d.para('Lesson: a prompt-only workflow still needs explicit human choices, scientific restraint and reproducible checks. The useful output is an inspectable chain from source data to a result, with its limits attached.',60,124,1055,13)
    d.close()
    # Render each actual PDF page, rather than maintaining a separate PNG layout.
    import pymupdf
    paths=[p.path,d.path]
    for path in paths:
        require_resources(config())
        with pymupdf.open(path) as doc:
            if len(doc)!=3:raise ValueError('Expected exactly three publication pages')
            for i,page in enumerate(doc):
                image=page.get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False)
                image.save(root/(path.stem+f'_page_{i+1:02d}.png'))
    return paths

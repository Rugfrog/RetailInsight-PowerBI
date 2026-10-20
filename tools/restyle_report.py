"""Apply the owner's reference layout to native PBIR visuals.

Background PNGs contain decorative panels/icons only. All metrics, charts,
tables, slicers, search and navigation remain native Power BI objects.
Requires Pillow. Run from any directory; preserves semantic-model bindings.
"""
from pathlib import Path
import copy
import hashlib
import json
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / 'RetailInsight.Report'
PAGES = REPORT / 'definition/pages'
MAIN = '9c3fd9548500350a4d65'
PERF = 'e817a0215fba4ad0a503'
W, H = 1600, 1104
SCHEMA = 'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.7.0/schema.json'
C = dict(canvas='#ECF1F4', rail='#263643', ink='#243446', muted='#6B8097', line='#D8E2EB', green='#33996D', amber='#D9A329', red='#D65760', blue='#365F7C', white='#FFFFFF')
RES = REPORT / 'StaticResources/RegisteredResources'
RES.mkdir(exist_ok=True)

def uid(label): return hashlib.sha256(label.encode()).hexdigest()[:20]
def lit(v):
    if isinstance(v, bool): s = str(v).lower()
    elif isinstance(v, (int,float)): s = str(v)+'D'
    else: s = "'"+v.replace("'","''")+"'"
    return {'expr':{'Literal':{'Value':s}}}
def fill(c): return {'solid':{'color':lit(c)}}
def obj(props, selector=None):
    d={'properties':props}
    if selector: d['selector']=selector
    return [d]
def column(t,p): return {'Column':{'Expression':{'SourceRef':{'Entity':t}},'Property':p}}
def measure(p): return {'Measure':{'Expression':{'SourceRef':{'Entity':'Feedback'}},'Property':p}}
def projection(field, label=None):
    d=next(iter(field.values())); t=d['Expression']['SourceRef']['Entity']; p=d['Property']
    r={'field':field,'queryRef':t+'.'+p,'nativeQueryRef':p}
    if label: r['displayName']=label
    return r
def chrome(alt):
    return {'title':obj({'show':lit(False)}), 'background':obj({'show':lit(False)}),
            'border':obj({'show':lit(False)}), 'dropShadow':obj({'show':lit(False)}),
            'padding':obj({k:lit(0) for k in ('top','bottom','left','right')}),
            'general':obj({'altText':lit(alt)})}

def background(performance=False):
    # Static chrome only: no metric values, charts, maps, tables or filter values.
    im=Image.new('RGB',(W*2,H*2),C['canvas']); d=ImageDraw.Draw(im)
    def rect(x,y,w,h,color,r=0,outline=None):
        box=(x*2,y*2,(x+w)*2,(y+h)*2)
        if r: d.rounded_rectangle(box,r*2,fill=color,outline=outline,width=2)
        else: d.rectangle(box,fill=color,outline=outline,width=2)
    def face(x,y,color,kind):
        d.ellipse(((x-12)*2,(y-12)*2,(x+12)*2,(y+12)*2),fill={'positive':'#E3F3EA','neutral':'#FFF3D8','negative':'#FBE7E8'}[kind])
        d.ellipse(((x-7)*2,(y-7)*2,(x+7)*2,(y+7)*2),outline=color,width=2)
        for ex in (x-3,x+3): d.ellipse((ex*2-1,(y-3)*2-1,ex*2+1,(y-3)*2+1),fill=color)
        if kind=='neutral': d.line(((x-3)*2,(y+3)*2,(x+3)*2,(y+3)*2),fill=color,width=2)
        else:
            box=((x-4)*2,(y-2 if kind=='positive' else y+2)*2,(x+4)*2,(y+5 if kind=='positive' else y+8)*2)
            d.arc(box,0 if kind=='positive' else 180,180 if kind=='positive' else 360,fill=color,width=2)
    rect(0,0,230,H,C['rail'])
    for y in (80,710,850,1036): rect(17,y,195,1,'#465764')
    for x,h in ((18,10),(27,18),(36,14)): rect(x,56-h,5,h,'#69BED0',1)
    for i,color in enumerate(('#BBD2E3','#74BFA1','#E4BF61','#E2A0A5','#BBD2E3')):
        x=260+i*265
        rect(x,124,251,125,C['white'],4,C['line']); rect(x+2,124,247,3,color,1)
    face(553,154,C['green'],'positive');face(818,154,C['amber'],'neutral');face(1083,154,C['red'],'negative')
    rect(1242,38,328,54,C['white'],4,C['line'])
    if performance:
        rect(260,264,824,794,C['white'],4,C['line']);rect(1098,264,472,794,C['white'],4,C['line'])
    else:
        for x,y,w,h in ((260,264,802,382),(1078,264,492,382),(260,662,777,396),(1052,662,518,396)):
            rect(x,y,w,h,C['white'],4,C['line'])
    for y,kind,key in ((910,'positive','green'),(950,'neutral','amber'),(990,'negative','red')): face(32,y,C[key],kind)
    name='retailinsight-'+('stores' if performance else 'overview')+'-20261020.png'
    im.save(RES/name,optimize=True)
    return name

class Page:
    def __init__(self,name,display,performance=False):
        self.name=name;self.folder=PAGES/name;self.visuals={};self.n=0
        self.folder.mkdir(exist_ok=True)
        bg=background(performance)
        self.definition={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json',
            'name':name,'displayName':display,'displayOption':'FitToPage','height':H,'width':W,
            'objects':{'background':obj({'color':fill(C['canvas']),'transparency':lit(0),
                'image':{'image':{'name':lit(bg),'url':{'expr':{'ResourcePackageItem':{'PackageName':'RegisteredResources','PackageType':1,'ItemName':bg}}},'scaling':lit('Fit')}}})}}
    def add(self,label,typ,x,y,w,h,roles=None,objects=None,identity=None):
        self.n+=1; name=identity or uid(self.name+label)
        v={'$schema':SCHEMA,'name':name,'position':{'x':x,'y':y,'width':w,'height':h,'z':self.n*10,'tabOrder':self.n},
           'visual':{'visualType':typ,'drillFilterOtherVisuals':True,'visualContainerObjects':chrome(label)}}
        if roles: v['visual']['query']={'queryState':{k:{'projections':[projection(*p) if isinstance(p,tuple) else projection(p) for p in fields]} for k,fields in roles.items()}}
        if objects: v['visual']['objects']=objects
        self.visuals[name]=v
        return v
    def text(self,label,text,x,y,w,h,size=10,color=None,bold=False):
        return self.add(label,'textbox',x,y,w,h,objects={'general':obj({'paragraphs':[{'textRuns':[{'value':text,'textStyle':{'fontFamily':'Segoe UI','fontSize':str(size)+'pt','color':color or C['ink'],'fontWeight':'bold' if bold else 'normal'}}]}]})})
    def card(self,label,metric,x,y,w,h,size=28,color=None,identity=None):
        v=self.add(label,'cardVisual',x,y,w,h,{'Data':[measure(metric)]},identity=identity)
        sel={'id':'default'}
        v['visual']['objects']={
            'value':obj({'fontSize':lit(size),'fontColor':fill(color or C['ink']),'bold':lit(True),'horizontalAlignment':lit('left'),'labelDisplayUnits':lit(1)},sel),
            'label':obj({'show':lit(False)},sel),'outline':obj({'show':lit(False)},sel),
            'padding':obj({'paddingUniform':lit(8)},sel),'layout':obj({'paddingUniform':lit(0)},sel),
            'fillCustom':obj({'show':lit(False)},sel),'shadowCustom':obj({'show':lit(False)},sel),
            'glowCustom':obj({'show':lit(False)},sel),'accentBar':obj({'show':lit(False)},sel),'divider':obj({'show':lit(False)},sel)}
        return v
    def slicer(self,label,t,p,x,y,w=194,h=64):
        v=self.add(label+' filter','slicer',x,y,w,h,{'Values':[column(t,p)]},{
            'data':obj({'mode':lit('Dropdown')}),
            'header':obj({'show':lit(True),'text':lit(label),'fontColor':fill('#E6EDF3'),'textSize':lit(10),'fontFamily':lit('Segoe UI Semibold')}),
            'items':obj({'fontColor':fill('#F3F6F9'),'background':fill('#354754'),'textSize':lit(10),'padding':lit(2),'outlineColor':fill('#627581'),'outlineWeight':lit(1)}),
            'selection':obj({'singleSelect':lit(False),'selectAllCheckboxEnabled':lit(True)})})
        v['visual']['syncGroup']={'groupName':'RetailInsight '+t+'.'+p,'fieldChanges':True,'filterChanges':True}
        return v
    def button(self,label,text,x,y,w,h,action,target=None,active=False):
        v=self.add(label,'actionButton',x,y,w,h)
        v['visual']['objects']={
            'text':[{'properties':{'show':lit(True)}},{'properties':{'text':lit(text),'fontSize':lit(11),'fontColor':fill('#ECF3F8'),'horizontalAlignment':lit('left'),'verticalAlignment':lit('middle'),'leftMargin':lit(10)},'selector':{'id':'default'}}],
            'fill':[{'properties':{'show':lit(active)}},{'properties':{'fillColor':fill('#38586E')},'selector':{'id':'default'}}],
            'outline':obj({'show':lit(False)}),'shape':obj({'tileShape':lit('rectangleRounded'),'roundEdge':lit(3)})}
        props={'show':lit(True),'type':lit(action)}
        if target: props['navigationSection']=lit(target)
        v['visual']['visualContainerObjects']['visualLink']=obj(props)
        return v
    def table(self,label,fields,x,y,w,h,widths):
        v=self.add(label,'tableEx',x,y,w,h,{'Values':fields})
        v['visual']['visualContainerObjects']['stylePreset']=obj({'name':lit('None')})
        v['visual']['visualContainerObjects']['visualHeader']=obj({'show':lit(True),'showOptionsMenu':lit(True)})
        v['visual']['objects']={
            'columnHeaders':obj({'fontFamily':lit('Segoe UI Semibold'),'fontSize':lit(10),'fontColor':fill('#3E5870'),'backColor':fill('#EAF1F6'),'autoSizeColumnWidth':lit(False),'columnAdjustment':lit('fixedWidth'),'wordWrap':lit(False),'outline':lit('None')}),
            'values':obj({'fontSize':lit(9),'fontFamily':lit('Segoe UI'),'fontColorPrimary':fill('#40566E'),'fontColorSecondary':fill('#40566E'),'backColorPrimary':fill('#FFFFFF'),'backColorSecondary':fill('#F6F8FA'),'wordWrap':lit(False)}),
            'grid':obj({'gridVertical':lit(False),'gridHorizontal':lit(True),'gridHorizontalColor':fill('#E9EFF4'),'rowPadding':lit(8),'outlineColor':fill('#E9EFF4')}),
            'total':obj({'totals':lit(False)}),
            'columnWidth':[{'properties':{'value':lit(width)},'selector':{'metadata':projection(f[0] if isinstance(f,tuple) else f)['queryRef']}} for f,width in zip(fields,widths)]}
        return v
    def save(self):
        for path in (self.folder/'visuals').glob('*/visual.json'):
            if path.parent.name not in self.visuals: path.unlink() # saved in baseline Git bundle
        for name,v in self.visuals.items():
            out=self.folder/'visuals'/name/'visual.json';out.parent.mkdir(parents=True,exist_ok=True)
            out.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
        (self.folder/'page.json').write_text(json.dumps(self.definition,indent=2)+'\n',encoding='utf-8')

def scaffold(page,performance=False):
    page.text('brand','Retail Insight',51,25,162,29,15,'#E6EDF3',True)
    page.text('brand subtitle','PERFORMANCE REPORTING',51,53,170,18,6,'#9BAFBC')
    page.text('filter heading','REPORT FILTERS',17,100,194,20,8,'#93ADBD',True)
    for label,t,p,y in [('Year','Calendar','Year',126),('Week','Calendar','Week',200),('Feedback','Feedback','Sentiment',274),('Region','Store','Region',348),('County / council area','Store','County',422),('City','Store','City',496),('Channel','Feedback','Channel',570)]:
        page.slicer(label,t,p,17,y)
    page.button('Clear slicers','↺  Clear slicers',17,648,195,44,'ClearAllSlicers')
    page.text('pages heading','REPORT PAGES',17,724,194,20,8,'#93ADBD',True)
    page.button('Customer feedback navigation','▤  Customer feedback',17,754,195,42,'PageNavigation',MAIN,not performance)
    page.button('Store performance navigation','▦  Store performance',17,800,195,42,'PageNavigation',PERF,performance)
    page.text('sentiment mix heading','SENTIMENT MIX',17,865,194,20,8,'#93ADBD',True)
    for name,metric,y in [('Positive','Positive %',896),('Neutral','Neutral %',936),('Negative','Negative %',976)]:
        page.text('sidebar '+name,name,56,y+5,90,28,10,'#E6EDF3')
        page.card('sidebar '+name+' percentage',metric,151,y,64,32,10,'#E6EDF3')
    page.text('demo note','Portfolio demonstration\nFictional sample data only',20,1050,190,42,8,'#A3B4C1')
    page.text('eyebrow','CUSTOMER EXPERIENCE / REPORT OVERVIEW',260,23,800,22,9,'#367CA5',True)
    page.text('page title','Store Performance' if performance else 'Customer Feedback Insights',260,46,950,44,24,C['ink'],True)
    page.text('subtitle','Compare response volume and service sentiment across UK locations' if performance else 'In-store feedback, sentiment and trends across UK locations',260,88,930,25,11,C['muted'])
    page.text('period','01 Jan – 29 Sep 2024',1260,47,290,24,11,C['ink'],True)
    page.text('period caption','Sample dataset period',1260,72,290,18,8,C['muted'])
    labels=['Total responses','Positive sentiment','Neutral sentiment','Negative sentiment','Average store rating']
    metrics=['Total Responses','Positive %','Neutral %','Negative %','Average Rating']
    ids=['e056985f92a562d260c1','52d606abfec785cba0a3','d21534db87add39d0b27','03228eed153bcb2f17f7','a4bc57f55072bd8f0765']
    for i,(label,metric) in enumerate(zip(labels,metrics)):
        x=260+i*265
        page.text('KPI label '+label,label,x+(47 if i in (1,2,3) else 16),143,198 if i in (1,2,3) else 220,28,10,C['ink'],True)
        page.card(label,metric,x+8,164,235,60,26,identity=ids[i] if not performance else None)
        page.text('KPI caption '+label,('Feedback submissions' if i==0 else 'Rating out of 5' if i==4 else 'Share of selected responses'),x+16,224,225,20,9,C['muted'])
    page.text('footer','Retail Insight · Fictional retail customer experience portfolio',260,1071,900,24,8,'#8096AA')
    page.text('export hint','Export records using the feedback table’s ⋯ menu',1135,1071,435,24,8,'#8096AA')

main=Page(MAIN,'Customer feedback');scaffold(main)
main.text('trend heading','Feedback trend by sentiment',276,282,730,26,12,C['ink'],True)
main.text('trend subtitle','Daily response counts · select a series or date to explore',276,308,730,22,9,C['muted'])
trend=main.add('Sentiment trend','lineChart',282,340,754,286,
    {'Category':[column('Calendar','Date')],'Y':[measure(m) for m in ('Positive Responses','Neutral Responses','Negative Responses')]},identity='e7ad5a1d80fe5d84c41f')
trend['visual']['objects']={
    'legend':obj({'show':lit(True),'position':lit('Bottom'),'showTitle':lit(False),'fontSize':lit(9),'labelColor':fill('#4F6680')}),
    'categoryAxis':obj({'show':lit(True),'showAxisTitle':lit(False),'fontSize':lit(9),'labelColor':fill(C['muted']),'axisType':lit('Continuous')}),
    'valueAxis':obj({'show':lit(True),'showAxisTitle':lit(False),'fontSize':lit(9),'labelColor':fill(C['muted']),'gridlineShow':lit(True),'gridlineColor':fill('#E7EDF2'),'start':lit(0)}),
    'lineStyles':obj({'strokeWidth':lit(2)}),
    'dataPoint':[{'properties':{'fill':fill(color)},'selector':{'metadata':'Feedback.'+metric}} for metric,color in zip(('Positive Responses','Neutral Responses','Negative Responses'),(C['green'],C['amber'],C['red']))]}
main.text('map heading','Store locations & sentiment',1094,282,455,26,12,C['ink'],True)
main.text('map subtitle','Select a location · hover for response and sentiment measures',1094,308,455,25,9,C['muted'])
mp=main.add('UK store locations','map',1090,340,467,292,{'Location':[column('Store','City')],'Latitude':[column('Store','Latitude')],'Longitude':[column('Store','Longitude')],'Size':[measure('Total Responses')],'Tooltips':[measure('Positive %'),measure('Neutral %'),measure('Negative %')]},identity='e587dfe1f09b91aa03bd')
mp['visual']['objects']={'dataPoint':obj({'defaultColor':fill(C['green'])}),'mapStyles':obj({'mapTheme':lit('grayscale')})}
mp['visual']['visualContainerObjects']['visualTooltip']=obj({'show':lit(True)})
main.text('feedback heading','Recent customer feedback',276,681,480,26,12,C['ink'],True)
main.text('feedback subtitle','Individual responses from the selected locations',276,706,480,22,9,C['muted'])
search=main.add('Search customer comments','textSlicer',796,678,225,50,{'Values':[column('Feedback','Feedback')]})
fields=[(column('Feedback','ResponseDate'),'Date'),column('Feedback','Store'),column('Feedback','Feedback'),column('Feedback','Sentiment'),(column('Feedback','ResponseID'),'ID')]
detail=main.table('Customer response records',fields,273,738,751,303,[98,145,345,105,54])
detail['visual']['query']['sortDefinition']={'sort':[{'field':column('Feedback','ResponseDate'),'direction':'Descending'},{'field':column('Feedback','ResponseID'),'direction':'Descending'}]}
main.text('performance heading','Store performance',1068,681,480,26,12,C['ink'],True)
main.text('performance subtitle','Response volume and positive sentiment',1068,706,480,22,9,C['muted'])
perf_fields=[(column('Store','City'),'Store'),(measure('Total Responses'),'Responses'),measure('Positive %')]
ranking=main.table('Store performance summary',perf_fields,1065,738,491,303,[214,105,167])
def format_ranking(v):
    v['visual']['query']['sortDefinition']={'sort':[{'field':measure('Total Responses'),'direction':'Descending'},{'field':column('Store','City'),'direction':'Ascending'}]}
    v['visual']['objects']['columnFormatting']=[{'properties':{'dataBars':{'positiveColor':fill('#7CAF94'),'negativeColor':fill(C['red']),'axisColor':fill('#DDE6ED'),'reverseDirection':lit(False),'hideText':lit(False),'minValue':lit(0),'maxValue':lit(1)}},'selector':{'metadata':'Feedback.Positive %'}}]
format_ranking(ranking)

stores=Page(PERF,'Store performance',True);scaffold(stores,True)
stores.text('full ranking heading','Store comparison',276,282,770,26,12,C['ink'],True)
stores.text('full ranking subtitle','Compare volume and sentiment together; low sample sizes can distort percentages',276,308,770,25,9,C['muted'])
full_fields=[column('Store','Store'),column('Store','Region'),(measure('Total Responses'),'Responses'),measure('Positive %'),measure('Neutral %'),measure('Negative %'),measure('Average Rating')]
full=stores.table('Store comparison table',full_fields,276,348,790,690,[177,135,100,90,90,90,102]);format_ranking(full)
full['visual']['query']['sortDefinition']['sort'][1]={'field':column('Store','Store'),'direction':'Ascending'}
stores.text('store chart heading','Positive sentiment by store',1114,282,434,26,12,C['ink'],True)
stores.text('store chart subtitle','Select a bar to filter the comparison',1114,308,434,25,9,C['muted'])
bar=stores.add('Store sentiment ranking','clusteredBarChart',1114,348,434,690,{'Category':[column('Store','City')],'Y':[measure('Positive %')],'Tooltips':[measure('Total Responses'),measure('Average Rating')]})
bar['visual']['query']['sortDefinition']={'sort':[{'field':measure('Positive %'),'direction':'Descending'}]}
bar['visual']['objects']={'dataPoint':obj({'defaultColor':fill('#7CAF94')}),'categoryAxis':obj({'showAxisTitle':lit(False),'labelColor':fill(C['muted']),'fontSize':lit(9)}),'valueAxis':obj({'showAxisTitle':lit(False),'start':lit(0),'end':lit(1),'labelColor':fill(C['muted']),'fontSize':lit(9)}),'legend':obj({'show':lit(False)})}
bar['visual']['visualContainerObjects']['visualTooltip']=obj({'show':lit(True)})

main.save();stores.save()
metadata=PAGES/'pages.json';meta=json.loads(metadata.read_text());meta.update(pageOrder=[MAIN,PERF],activePageName=MAIN);metadata.write_text(json.dumps(meta,indent=2)+'\n')
report_path=REPORT/'definition/report.json';report=json.loads(report_path.read_text())
report['resourcePackages']=[p for p in report['resourcePackages'] if p['name']!='RegisteredResources']+[{'name':'RegisteredResources','type':'RegisteredResources','items':[{'name':p.name,'path':p.name,'type':'Image'} for p in sorted(RES.glob('retailinsight-*-20261020.png'))]}]
report_path.write_text(json.dumps(report,indent=2)+'\n')
theme=REPORT/'StaticResources/SharedResources/BaseThemes/CY26SU02.json';t=json.loads(theme.read_text());t.update(dataColors=[C['green'],C['amber'],C['red'],C['blue'],'#72AFC7','#91A3B3'],foreground=C['ink'],background=C['white'],tableAccent=C['blue'],good=C['green'],neutral=C['amber'],bad=C['red']);t['textClasses']['callout'].update(fontSize=26,color=C['ink']);theme.write_text(json.dumps(t,indent=2)+'\n')
custom=copy.deepcopy(t);custom['name']='RetailInsight Reference';custom['visualStyles']={'*':{'*':{'dropShadow':[{'show':False}],'title':[{'fontFamily':'Segoe UI Semibold','fontSize':12}]}},'slicer':{'*':{'header':[{'fontFamily':'Segoe UI Semibold','textSize':10}],'items':[{'fontFamily':'Segoe UI','textSize':10}]}}}
(RES/'RetailInsightTheme.json').write_text(json.dumps(custom,indent=2)+'\n')
report['resourcePackages'][-1]['items'].append({'name':'RetailInsightTheme','path':'RetailInsightTheme.json','type':'CustomTheme'})
report['themeCollection']['customTheme']={'name':'RetailInsightTheme','type':'RegisteredResources','reportVersionAtImport':{'visual':'2.7.0','report':'3.2.0','page':'2.1.0'}}
report_path.write_text(json.dumps(report,indent=2)+'\n')
print('Restyled existing report:',len(main.visuals),'overview objects,',len(stores.visuals),'store-page objects. HTML demo unchanged.')


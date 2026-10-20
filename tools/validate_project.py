"""Static checks only: this does not execute TMDL, M, DAX, or Power BI visuals.

Run with Python 3.12+, jsonschema 4.x, and network access to Microsoft schemas.
"""
from pathlib import Path
from collections import Counter
from datetime import date, timedelta
import hashlib
import json
import re
import urllib.request
import sys

from jsonschema.validators import validator_for
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[1]
CACHE = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / '.schema-cache'
CACHE.mkdir(exist_ok=True, parents=True)

def retrieve(uri):
    if not uri.startswith('https://developer.microsoft.com/json-schemas/'):
        raise ValueError(f'Unexpected schema host: {uri}')
    path = CACHE / (hashlib.sha256(uri.encode()).hexdigest() + '.json')
    if not path.exists():
        with urllib.request.urlopen(uri, timeout=30) as response:
            path.write_bytes(response.read())
    return Resource.from_contents(json.loads(path.read_text(encoding='utf-8-sig')))

registry = Registry(retrieve=retrieve)
files = [ROOT/'RetailInsight.pbip', ROOT/'RetailInsight.Report/definition.pbir', ROOT/'RetailInsight.SemanticModel/definition.pbism']
files += list((ROOT/'RetailInsight.Report/definition').rglob('*.json'))
for path in files:
    data = json.loads(path.read_text(encoding='utf-8'))
    schema = retrieve(data['$schema']).contents
    validator_for(schema)(schema, registry=registry).validate(data)
print(f'PASS: {len(files)} project/report JSON documents satisfy their Microsoft schemas.')

tables = {}
for path in (ROOT/'RetailInsight.SemanticModel/definition/tables').glob('*.tmdl'):
    text = path.read_text(encoding='utf-8')
    tables[path.stem] = {m.group(2).strip("'") for m in re.finditer(r'^\t(column|measure) (.+?)(?: =.*)?$', text, re.M)}
for path in (ROOT/'RetailInsight.Report/definition').rglob('visual.json'):
    visual = json.loads(path.read_text(encoding='utf-8'))
    for role in visual['visual'].get('query',{}).get('queryState',{}).values():
        for projection in role.get('projections',[]):
            field = projection['field']
            field = field.get('Column',field.get('Measure'))
            entity = field['Expression']['SourceRef']['Entity']
            assert field['Property'] in tables[entity], (path, entity, field['Property'])
    pos=visual['position']
    assert pos['x'] >= 0 and pos['y'] >= 0 and pos['x']+pos['width']<=1440 and pos['y']+pos['height']<=810, path
print('PASS: all visual field references resolve; all objects fit the report canvas.')

# Independently reproduce the deterministic fixture for later Power BI reconciliation.
fact = (ROOT/'RetailInsight.SemanticModel/definition/tables/Feedback.tmdl').read_text(encoding='utf-8')
stores = re.findall(r'\[City="([^"]+)", County="([^"]+)", Region="([^"]+)", Latitude=([\d.-]+), Longitude=([\d.-]+)\]',fact)
assert len(stores)==20
rows=[]
for i in range(1,7251):
    store=(i*17+i//31)%20
    score=(i*37+i//11)%100
    sentiment='Positive' if score<71 else 'Neutral' if score<87 else 'Negative'
    day=date(2024,1,1)+timedelta(days=(i*19+i//7)%273)
    rows.append((i,day,store,sentiment))
counts=Counter(row[3] for row in rows)
assert counts=={'Positive':5167,'Neutral':1161,'Negative':922}
assert min(r[1] for r in rows)==date(2024,1,1)
assert max(r[1] for r in rows)==date(2024,9,29)
assert len(set(r[1] for r in rows))==273
assert len(set(r[2] for r in rows))==20
# A selected sentiment must intersect each numerator, not replace its filter.
for selected in ({'Positive'}, {'Neutral','Negative'}, {'Positive','Neutral','Negative'}):
    subset=[r for r in rows if r[3] in selected]
    percentages=[sum(r[3]==s for r in subset)/len(subset) for s in counts]
    assert abs(sum(percentages)-1)<1e-12
assert fact.count('KEEPFILTERS(Feedback[Sentiment]')==3
print('PASS: synthetic fixture has 7,250 responses, 20 stores, 273 dates; sentiment counts:',dict(counts))
print('UNVERIFIED: TMDL/M/DAX engine execution, rendering, map availability, interaction behavior and deployment.')

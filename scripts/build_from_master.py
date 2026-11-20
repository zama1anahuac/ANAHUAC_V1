#!/usr/bin/env python3
"""Export deterministic, whitelist-only local preview from master workbook.
Usage: python3 scripts/build_from_master.py /path/to/02_ATLAS_MAESTRO_MAYAB_V1.xlsx
Does NOT grant publication permission. Never put master XLSX inside public repository.
"""
import csv,json,re,sys,zipfile,hashlib,collections,xml.etree.ElementTree as E
from pathlib import Path
N='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
NAMES={1:'investigaciones',2:'temas',3:'problemas',4:'preguntas',6:'sectores',12:'relaciones',13:'fuentes',9:'conceptos',20:'co_relaciones',21:'lineas'}
def read_sheets(path):
 with zipfile.ZipFile(path) as z:
  shared=[]
  if 'xl/sharedStrings.xml' in z.namelist():shared=[''.join(t.text or '' for t in x.iter(N+'t')) for x in E.fromstring(z.read('xl/sharedStrings.xml')).findall(N+'si')]
  out={}
  for idx,name in NAMES.items():
   root=E.fromstring(z.read(f'xl/worksheets/sheet{idx+1}.xml')); rows=[]
   for row in root.findall(f'.//{N}sheetData/{N}row'):
    d={}
    for cell in row.findall(N+'c'):
     col=0
     for char in re.match('[A-Z]+',cell.get('r')).group():col=col*26+ord(char)-64
     v=cell.find(N+'v');inline=cell.find(N+'is');txt=v.text if v is not None else ''.join(y.text or '' for y in inline.iter(N+'t')) if inline is not None else ''
     if cell.get('t')=='s' and txt:txt=shared[int(txt)]
     d[col-1]=txt or ''
    rows.append([d.get(i,'') for i in range(max(d,default=-1)+1)])
   header=rows[0];out[name]=[dict(zip(header,row+['']*(len(header)-len(row)))) for row in rows[1:]]
  return out
def export(master):
 folder=Path(__file__).resolve().parent.parent/'data';folder.mkdir(exist_ok=True)
 tables=read_sheets(master)
 ids={key:{x['id'] for x in arr} for key,arr in tables.items() if arr and 'id' in arr[0]}
 issues=[]
 for k in ('investigaciones','preguntas','relaciones','temas','problemas','sectores','conceptos','co_relaciones'):
  if len(ids.get(k,set()))!=len(tables[k]):issues.append('Duplicated ID in '+k)
 for i in tables['investigaciones']:
  if i['tema_id'] not in ids['temas'] or i['problema_id'] not in ids['problemas'] or i['sector_id'] not in ids['sectores']:issues.append('Research FK '+i['id'])
 for q in tables['preguntas']:
  if q['investigacion_id'] not in ids['investigaciones']:issues.append('Question FK '+q['id'])
 for r in tables['relaciones']:
  if r['investigacion_id'] not in ids['investigaciones'] or r['pregunta_id'] not in ids['preguntas'] or r['sector_id'] not in ids['sectores']:issues.append('Route FK '+r['id'])
 for e in tables['co_relaciones']:
  if e['investigacion_id'] not in ids['investigaciones'] or e['concepto_id'] not in ids['conceptos']:issues.append('CO relation FK '+e['id'])
 counts={'investigaciones':len(tables['investigaciones']),'preguntas':len(tables['preguntas']),'descriptivas':sum(x['alcance']=='DES' for x in tables['preguntas']),'causales_candidatas':sum(x['alcance']=='CAU' for x in tables['preguntas']),'rutas_sectoriales':len(tables['relaciones']),'conceptos_co':len(tables['conceptos']),'vinculos_co_provisionales':len(tables['co_relaciones'])}
 for key,expected in [('investigaciones',249),('preguntas',365),('descriptivas',249),('causales_candidatas',116),('rutas_sectoriales',1157),('conceptos_co',30),('vinculos_co_provisionales',6)]:
  if counts[key]!=expected:issues.append(f'Count {key}: {counts[key]} rather than {expected}')
 if issues:raise SystemExit('EXPORT BLOQUEADA: '+ '; '.join(issues[:25]))
 allowed={
 'investigaciones':['id','origen_id','titulo','tema_id','linea_id','problema_id','sector_id','sector_texto','territorio','unidad','metodo','datos','fuentes','estado','co_estado','publicacion'],
 'preguntas':['id','investigacion_id','origen_propuesta','alcance','texto','exposicion','resultado','confusores','temporalidad','diseno','estado','fuentes'],
 'relaciones':['id','investigacion_id','pregunta_id','alcance','sector_id','territorio','origen_folio','estado'],
 'temas':['id','nombre','linea_id','estado'],'problemas':['id','linea_id','descripcion','afirmacion'],'sectores':['id','nombre','territorio','tipo'],
 'fuentes':['id','autor','titulo','fecha','url','limite'],
 'conceptos':['id','nombre','etapa','nivel','sintesis','capitulo','pagina','diapositiva','estado'],
 'co_relaciones':['id','investigacion_id','concepto_id','grado','justificacion','fuente','estado']}
 for key,fields in allowed.items():
  data=[{col:row.get(col,'') for col in fields} for row in tables[key]]
  name='modelo' if key=='conceptos' else key
  if key in ('conceptos','co_relaciones'):continue
  (folder/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':'),sort_keys=True),encoding='utf8')
 model={'conceptos':[{k:r.get(k,'') for k in allowed['conceptos']} for r in tables['conceptos']],'vinculos':[{k:r.get(k,'') for k in allowed['co_relaciones']} for r in tables['co_relaciones']],'niveles':['IND','GRU','ORG'],'etapas':['INS','PRO','RES'],'retroalimentacion':'conceptual_no_causal'}
 (folder/'modelo.json').write_text(json.dumps(model,ensure_ascii=False,separators=(',',':'),sort_keys=True),encoding='utf8')
 (folder/'lineas.json').write_text(json.dumps([{'id':x['id_linea'],'nombre':x['nombre']} for x in tables['lineas']],ensure_ascii=False,separators=(',',':')),encoding='utf8')
 manifest={'version':'V1','fecha':'2026-11-20','entorno':'PROTOTIPO_LOCAL_NO_PUBLICAR','autorizacion_publicacion':False,'conteos':{**counts,'historico_conservado_interno':5270,'descartes_internos':2730},'descargas_pdf':{},'master_sha256':hashlib.sha256(Path(master).read_bytes()).hexdigest(),'avisos':['Prototipo local, pendiente revisión docente y autorización de difusión']}
 (folder/'manifiesto.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
 with (folder/'investigaciones.csv').open('w',newline='',encoding='utf-8-sig') as f:
  cols=['id','origen_id','titulo','tema_id','problema_id','sector_id','territorio','estado','co_estado'];writer=csv.DictWriter(f,fieldnames=cols);writer.writeheader();writer.writerows({k:r.get(k,'') for k in cols} for r in tables['investigaciones'])
 print('OK, regenerado desde Excel maestro, SIN autorización para publicación',counts)
if __name__=='__main__':
 if len(sys.argv)!=2:raise SystemExit('Uso: python scripts/build_from_master.py /ruta/02_ATLAS_MAESTRO_MAYAB_V1.xlsx')
 export(sys.argv[1])

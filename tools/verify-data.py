"""Independent round-trip check of GLB triangle corners against Studio OBJ."""
import json,struct,hashlib
import numpy as np
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).parent
raw=(ROOT/'assets/bacon.glb').read_bytes()
assert struct.unpack_from('<III',raw)==(0x46546c67,2,len(raw))
length,kind=struct.unpack_from('<II',raw,12);assert kind==0x4e4f534a
g=json.loads(raw[20:20+length]);offset=20+length
blength,bkind=struct.unpack_from('<II',raw,offset);assert bkind==0x004e4942
binary=raw[offset+8:offset+8+blength]
def attribute(index):
    a=g['accessors'][index];v=g['bufferViews'][a['bufferView']]
    dt={5126:'<f4',5125:'<u4'}[a['componentType']]
    ar=np.frombuffer(binary,dtype=dt,count=a['count']*{'SCALAR':1,'VEC2':2,'VEC3':3}[a['type']],offset=v.get('byteOffset',0)+a.get('byteOffset',0))
    return ar if a['type']=='SCALAR' else ar.reshape(a['count'],-1)
vertices=[];normals=[];uvs=[];faces=defaultdict(list);current=None
for line in (ROOT/'source/bacon-studio.obj').read_text().splitlines():
    p=line.split()
    if not p:continue
    if p[0]=='v':vertices.append([float(x) for x in p[1:4]])
    elif p[0]=='vn':normals.append([float(x) for x in p[1:4]])
    elif p[0]=='vt':uvs.append([float(x) for x in p[1:3]])
    elif p[0]=='g':current=' '.join(p[1:])
    elif p[0]=='f':
        corners=[tuple(int(x)-1 for x in c.split('/')) for c in p[1:]]
        for i in range(1,len(corners)-1):faces[current].extend([corners[0],corners[i],corners[i+1]])
vertices=np.array(vertices);normals=np.array(normals);uvs=np.array(uvs)
world={}
def visit(i,parent):
    n=g['nodes'][i];local=np.array(n.get('matrix',np.eye(4).T.reshape(-1))).reshape(4,4).T
    world[i]=parent@local
    for c in n.get('children',[]):visit(c,world[i])
for i in g['scenes'][0]['nodes']:visit(i,np.eye(4))
origin=np.array(g['nodes'][0]['extras']['originShiftStuds'])
results=[]
for i,node in enumerate(g['nodes']):
    if 'mesh' not in node:continue
    mesh=g['meshes'][node['mesh']];source=faces[mesh['extras']['nativeObjGroup']]
    p=mesh['primitives'][0];idx=attribute(p['indices'])
    position=attribute(p['attributes']['POSITION'])[idx].astype(float)
    normal=attribute(p['attributes']['NORMAL'])[idx].astype(float)
    uv=attribute(p['attributes']['TEXCOORD_0'])[idx].astype(float);uv[:,1]=1-uv[:,1]
    position=(world[i][:3,:3]@position.T).T+world[i][:3,3]+origin
    normal=(world[i][:3,:3]@normal.T).T
    expected_p=vertices[[c[0] for c in source]];expected_n=normals[[c[2] for c in source]];expected_uv=uvs[[c[1] for c in source]]
    assert len(idx)==len(source)
    errors=[float(np.max(np.abs(position-expected_p))),float(np.max(np.abs(normal-expected_n))),float(np.max(np.abs(uv-expected_uv)))]
    assert max(errors)<1e-6,(mesh['name'],errors)
    results.append({'part':mesh['name'],'triangleCornersCompared':len(idx),'maxPositionErrorStuds':errors[0],'maxNormalError':errors[1],'maxUVError':errors[2]})
image_view=g['bufferViews'][g['images'][0]['bufferView']]
png=binary[image_view['byteOffset']:image_view['byteOffset']+image_view['byteLength']]
assert png==(ROOT/'source/Handle1_diff.png').read_bytes()
report={'everyTriangleCornerCompared':True,'triangleCornersCompared':sum(x['triangleCornersCompared'] for x in results),'embeddedPNGByteIdentical':True,'textureSHA256':hashlib.sha256(png).hexdigest(),'results':results}
(ROOT/'round-trip-verification.json').write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='results'}))

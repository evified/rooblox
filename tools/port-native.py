"""Encode the untouched Studio OBJ/PNG as glTF; no geometry or UV reconstruction."""
import json,struct,hashlib
from pathlib import Path
from collections import OrderedDict,deque
import numpy as np

ROOT=Path(__file__).resolve().parent
if not (ROOT/'source'/'bacon-studio.obj').is_file():
    ROOT=ROOT.parent
SOURCE=ROOT/'source'
OUT=ROOT/'assets'; OUT.mkdir(exist_ok=True)
meta=json.loads((SOURCE/'studio-metadata.json').read_text())
positions=[];normals=[];uvs=[];groups=OrderedDict();active=None;material=None
for line in (SOURCE/'bacon-studio.obj').read_text().splitlines():
    s=line.split()
    if not s:continue
    if s[0]=='v': positions.append([float(v) for v in s[1:4]])
    elif s[0]=='vn': normals.append([float(v) for v in s[1:4]])
    elif s[0]=='vt': uvs.append([float(v) for v in s[1:3]])
    elif s[0]=='g': active=' '.join(s[1:]);groups[active]={'faces':[]}
    elif s[0]=='usemtl':material=s[1];groups[active]['material']=material
    elif s[0]=='f':
        corners=[tuple(int(v)-1 for v in corner.split('/')) for corner in s[1:]]
        for i in range(1,len(corners)-1):groups[active]['faces'].append([corners[0],corners[i],corners[i+1]])
positions=np.array(positions);normals=np.array(normals);uvs=np.array(uvs)
origin=np.array([meta['worldPivot'][0],positions[:,1].min(),meta['worldPivot'][2]])
partmap={p['name']:p for p in meta['parts']}
def cf(values):
    m=np.eye(4);m[:3,3]=values[:3];m[:3,:3]=np.array(values[3:]).reshape((3,3));return m
def normalized(m):
    m=m.copy();m[:3,3]-=origin;return m
def flattened(m):return m.T.reshape(-1).tolist()

native_mapping={}
for group,record in groups.items():
    v=positions[list({c[0] for f in record['faces'] for c in f})]
    center=(v.min(0)+v.max(0))/2
    target='Handle' if group.startswith('Handle') else min((p for p in meta['parts'] if p['name'] not in ['Handle','HumanoidRootPart']),key=lambda p:np.linalg.norm(center-np.array(p['worldCFrame'][:3])))['name']
    assert target not in native_mapping.values()
    native_mapping[group]=target

blob=bytearray()
gltf={'asset':{'version':'2.0','generator':'Direct packaging of Roblox Studio Export Selection OBJ'},'scene':0,'scenes':[{'nodes':[0]}],'nodes':[{'name':'BaconHair','children':[],'extras':{'source':'Workspace.BaconHair','nativeSource':'source/bacon-studio.obj','originShiftStuds':origin.tolist()}}],'meshes':[],'materials':[],'textures':[{'source':0,'sampler':0}],'samplers':[{'magFilter':9729,'minFilter':9987,'wrapS':33071,'wrapT':33071}],'images':[],'buffers':[],'bufferViews':[],'accessors':[]}
def buffer_view(raw,target=None):
    while len(blob)%4:blob.append(0)
    view={'buffer':0,'byteOffset':len(blob),'byteLength':len(raw)}
    if target:view['target']=target
    gltf['bufferViews'].append(view);blob.extend(raw);return len(gltf['bufferViews'])-1
def accessor(array,type,component=5126,target=34962):
    a=np.asarray(array,dtype='<f4' if component==5126 else '<u4')
    record={'bufferView':buffer_view(a.tobytes(),target),'componentType':component,'count':len(a),'type':type}
    if type=='VEC3':record.update(min=a.min(0).tolist(),max=a.max(0).tolist())
    gltf['accessors'].append(record);return len(gltf['accessors'])-1
png=(SOURCE/'Handle1_diff.png').read_bytes()
gltf['images'].append({'name':'Studio baked appearance atlas','mimeType':'image/png','bufferView':buffer_view(png)})
# Studio has already baked each part's body color into the atlas. Multiplying
# by the MTL Kd color a second time would incorrectly tint skin and clothing.
gltf['materials'].append({'name':'Studio appearance atlas','pbrMetallicRoughness':{'baseColorTexture':{'index':0},'baseColorFactor':[1,1,1,1],'metallicFactor':0,'roughnessFactor':1},'alphaMode':'OPAQUE','doubleSided':False,'extras':{'colorBakedByStudio':True}})
# Legacy hair contains open strand surfaces. Preserve every source triangle,
# while keeping the reverse-facing strand surfaces visible in browser rendering.
gltf['materials'].append({**gltf['materials'][0],'name':'Studio hair strand surfaces','doubleSided':True})

nodes=gltf['nodes'];part_nodes={};world_nodes={0:np.eye(4)}
def node(name,matrix,parent):
    index=len(nodes);nodes.append({'name':name,'matrix':flattened(matrix)})
    nodes[parent].setdefault('children',[]).append(index)
    world_nodes[index]=world_nodes[parent]@matrix
    return index
rootpart=node('HumanoidRootPart',normalized(cf(partmap['HumanoidRootPart']['worldCFrame'])),0)
part_nodes['HumanoidRootPart']=rootpart
remaining=list(meta['joints'])
while remaining:
    progress=False
    for joint in list(remaining):
        a,b=joint['part0'],joint['part1']
        if (a in part_nodes)==(b in part_nodes):continue
        forward=a in part_nodes
        parent,child=(a,b) if forward else (b,a)
        attach_parent=cf(joint['c0' if forward else 'c1'])
        attach_child=cf(joint['c1' if forward else 'c0'])
        j=node(joint['name'].replace(' ','_'),attach_parent,part_nodes[parent])
        nodes[j]['extras']={'robloxJointClass':joint['class'],'part0':a,'part1':b,'C0':joint['c0'],'C1':joint['c1']}
        # Use the actual source rest frame to retain its floating point transform.
        target_world=normalized(cf(partmap[child]['worldCFrame']))
        child_local=np.linalg.inv(world_nodes[j])@target_world
        part_nodes[child]=node(child.replace(' ','_'),child_local,j)
        remaining.remove(joint);progress=True
    if not progress:raise RuntimeError('Unresolved source joint hierarchy: '+str(remaining))

audit=[]
for group,record in groups.items():
    part=native_mapping[group];matrix=cf(partmap[part]['worldCFrame']);inverse=np.linalg.inv(matrix)
    indexed=OrderedDict();triangles=[]
    for face in record['faces']:
        triangle=[]
        for c in face:
            if c not in indexed:indexed[c]=len(indexed)
            triangle.append(indexed[c])
        triangles.extend(triangle)
    keys=list(indexed)
    source_p=positions[[k[0] for k in keys]]
    local_p=(inverse[:3,:3]@source_p.T).T+inverse[:3,3]
    source_n=normals[[k[2] for k in keys]]
    local_n=(inverse[:3,:3]@source_n.T).T
    source_uv=uvs[[k[1] for k in keys]]
    # OBJ UV origin is bottom-left; glTF UV origin is top-left.
    gltf_uv=source_uv.copy();gltf_uv[:,1]=1-source_uv[:,1]
    primitive={'attributes':{'POSITION':accessor(local_p,'VEC3'),'NORMAL':accessor(local_n,'VEC3'),'TEXCOORD_0':accessor(gltf_uv,'VEC2')},'indices':accessor(np.array(triangles),'SCALAR',5125,34963),'material':1 if part=='Handle' else 0,'mode':4}
    mesh_index=len(gltf['meshes']);gltf['meshes'].append({'name':part.replace(' ','_'),'primitives':[primitive],'extras':{'nativeObjGroup':group}})
    nodes[part_nodes[part]]['mesh']=mesh_index
    meshworld=world_nodes[part_nodes[part]]
    packed_p=local_p.astype('<f4').astype(float)
    reconstructed=(meshworld[:3,:3]@packed_p.T).T+meshworld[:3,3]+origin
    packed_n=local_n.astype('<f4').astype(float)
    reconstructed_n=(meshworld[:3,:3]@packed_n.T).T
    packed_uv=gltf_uv.astype('<f4').astype(float);packed_uv[:,1]=1-packed_uv[:,1]
    audit.append({'sourceGroup':group,'part':part,'triangles':len(record['faces']),'indexedVertices':len(keys),'sourceBounds':{'min':source_p.min(0).tolist(),'max':source_p.max(0).tolist()},'maxPositionErrorStuds':float(np.max(np.abs(reconstructed-source_p))),'maxNormalError':float(np.max(np.abs(reconstructed_n-source_n))),'maxUVError':float(np.max(np.abs(packed_uv-source_uv)))})

gltf['buffers']=[{'byteLength':len(blob)}]
json_bytes=json.dumps(gltf,separators=(',',':')).encode()
json_bytes+=b' '*((-len(json_bytes))%4)
blob+=b'\0'*((-len(blob))%4)
total=12+8+len(json_bytes)+8+len(blob)
glb=struct.pack('<III',0x46546c67,2,total)+struct.pack('<II',len(json_bytes),0x4e4f534a)+json_bytes+struct.pack('<II',len(blob),0x004e4942)+blob
(OUT/'bacon.glb').write_bytes(glb)
report={'source':'Native Roblox Studio Export Selection OBJ + its unchanged PNG','sourceFiles':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [SOURCE/'bacon-studio.obj',SOURCE/'bacon-studio.mtl',SOURCE/'Handle1_diff.png']},'embeddedTextureSHA256':hashlib.sha256(png).hexdigest(),'originShiftStuds':origin.tolist(),'meshCount':len(audit),'triangleCount':sum(a['triangles'] for a in audit),'parts':audit,'engineVersion':meta['engineVersion'],'generator':gltf['asset']['generator']}
assert max(a['maxPositionErrorStuds'] for a in audit)<1e-6
assert max(a['maxNormalError'] for a in audit)<1e-6
assert max(a['maxUVError'] for a in audit)<1e-6
assert len(audit)==7
(ROOT/'native-port-audit.json').write_text(json.dumps(report,indent=2))
print(json.dumps({'bytes':len(glb),'meshes':len(audit),'triangles':report['triangleCount'],'maxPositionError':max(a['maxPositionErrorStuds'] for a in audit),'textureSHA256':report['embeddedTextureSHA256']},indent=2))

import json,collections,numpy as np
from pathlib import Path
from PIL import Image
root=Path(__file__).resolve().parent.parent
p=[];n=[];uv=[];faces=[];group=''
for line in (root/'source/bacon-studio.obj').read_text().splitlines():
 s=line.split()
 if not s:continue
 if s[0]=='v':p.append(list(map(float,s[1:])))
 elif s[0]=='vn':n.append(list(map(float,s[1:])))
 elif s[0]=='vt':uv.append(list(map(float,s[1:])))
 elif s[0]=='g':group=s[1]
 elif s[0]=='f' and group=='Handle1':faces.append([tuple(int(i)-1 for i in c.split('/')) for c in s[1:]])
p=np.array(p);n=np.array(n);uv=np.array(uv);dots=[];edges=collections.Counter()
for f in faces:
 a,b,c=p[[v[0]for v in f]];dots.append(float(np.dot(np.cross(b-a,c-a),np.mean(n[[v[2]for v in f]],0))))
 for i in range(3):edges[tuple(sorted((f[i][0],f[(i+1)%3][0])))]+=1
used=uv[list({v[1]for f in faces for v in f})];im=Image.open(root/'source/Handle1_diff.png')
print(json.dumps({'hairTriangles':len(faces),'reverseNormals':sum(d< -1e-8 for d in dots),'openEdges':sum(v==1 for v in edges.values()),'uvMin':used.min(0).tolist(),'uvMax':used.max(0).tolist(),'atlasAlphaExtrema':im.getchannel('A').getextrema()}))

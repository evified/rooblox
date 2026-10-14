"""Package the verified source/assets for offline opening; no gameplay rewrite."""
from pathlib import Path
import base64,json,re
ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT.parent/'Rooblox-Accuracy.html'
def uri(content,mime):return 'data:'+mime+';base64,'+base64.b64encode(content).decode()
imports={}
core=(ROOT/'vendor/three.core.js').read_bytes();imports['three/core']=uri(core,'text/javascript')
three=(ROOT/'vendor/three.module.js').read_text(encoding='utf-8').replace("'./three.core.js'","'three/core'")
imports['three']=uri(three.encode(),'text/javascript')
utils=(ROOT/'vendor/addons/utils/BufferGeometryUtils.js').read_text(encoding='utf-8');imports['three/addons/utils/BufferGeometryUtils.js']=uri(utils.encode(),'text/javascript')
loader=(ROOT/'vendor/addons/loaders/GLTFLoader.js').read_text(encoding='utf-8').replace("'../utils/BufferGeometryUtils.js'","'three/addons/utils/BufferGeometryUtils.js'")
imports['three/addons/loaders/GLTFLoader.js']=uri(loader.encode(),'text/javascript')
files=['game','load-bacon','animation-player','motion-controller','camera-controller','local-ui']
for name in files:
 source=(ROOT/(name+'.js')).read_text(encoding='utf-8')
 for n in files:source=source.replace("'./"+n+".js'","'rooblox/"+n+"'")
 imports['rooblox/'+name]=uri(source.encode(),'text/javascript')
assets={}
for name in ['bacon.glb','game-config.json','animations.json','studio-reference.json','fidelity-config.json','extracted-defaults.json']:
 assets[name]=uri((ROOT/'assets'/name).read_bytes(),'model/gltf-binary'if name.endswith('.glb')else'application/json')
styles=(ROOT/'ui.css').read_text(encoding='utf-8')
for font in (ROOT/'assets/fonts').glob('*.otf'):styles=styles.replace('./assets/fonts/'+font.name,uri(font.read_bytes(),'font/otf'))
html=(ROOT/'index.html').read_text(encoding='utf-8').replace('<link rel="stylesheet" href="./ui.css">','<style>'+styles+'</style>')
html=re.sub(r'<script type="importmap">.*?</script>','<script type="importmap">'+json.dumps({'imports':imports})+'</script>',html,flags=re.S)
boot='''<script>const offlineAssets=ASSETS;const originalFetch=window.fetch.bind(window);window.fetch=(input,options)=>{const url=typeof input==='string'?input:input.url;const match=Object.entries(offlineAssets).find(([name])=>url.endsWith('/assets/'+name));return originalFetch(match?match[1]:input,options);};</script><script type="module">import 'rooblox/game';</script>'''.replace('ASSETS',json.dumps(assets))
html=html.replace('<script type="module" src="./game.js"></script>',boot)
OUT.write_text(html,encoding='utf-8');print(json.dumps({'standalone':str(OUT),'bytes':OUT.stat().st_size,'assetCount':len(assets),'allOriginalSourceEmbedded':True}))


from pathlib import Path
from urllib.request import urlopen
import shutil,argparse
root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,default=root.parent/'rooblox-baseplate'/'dist');args=parser.parse_args();out=args.output;out.mkdir(parents=True,exist_ok=True)
files=['build/three.module.js','build/three.core.js','examples/jsm/loaders/GLTFLoader.js','examples/jsm/utils/BufferGeometryUtils.js','examples/jsm/controls/OrbitControls.js']
for name in files:
 target=root/'vendor'/name.replace('build/','').replace('examples/jsm/','addons/')
 target.parent.mkdir(parents=True,exist_ok=True)
 if not target.exists():
  with urlopen('https://cdn.jsdelivr.net/npm/three@0.180.0/'+name,timeout=40)as f:target.write_bytes(f.read())
license=root/'vendor/LICENSE.txt'
if not license.exists():
 with urlopen('https://cdn.jsdelivr.net/npm/three@0.180.0/LICENSE',timeout=40)as f:license.write_bytes(f.read())
for name in ['index.html','game.js','animation-player.js','load-bacon.js','motion-controller.js','camera-controller.js','local-ui.js','ui.css']:
 shutil.copy2(root/name,out/name)
for name in ['bacon.glb','animations.json','game-config.json','studio-reference.json','extracted-defaults.json','fidelity-config.json']:
 (out/'assets').mkdir(exist_ok=True);shutil.copy2(root/'assets'/name,out/'assets'/name)
shutil.copytree(root/'vendor',out/'vendor',dirs_exist_ok=True)
shutil.copytree(root/'assets/fonts',out/'assets/fonts',dirs_exist_ok=True)
print('Prepared self-contained baseplate game:',out)

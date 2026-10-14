import * as THREE from 'three';
import {loadBacon} from './load-bacon.js';
import {NativeAnimator} from './animation-player.js';

try{
const [config,clips,reference]=await Promise.all(['./assets/game-config.json','./assets/animations.json','./assets/studio-reference.json'].map(u=>fetch(u).then(r=>{if(!r.ok)throw Error(`Could not load ${u}`);return r.json();})));
const settings=config.settings,sp=settings.starterPlayer,gravity=settings.workspace.Gravity;
if(matchMedia('(max-width:650px)').matches)document.querySelector('aside details').open=false;
const scene=new THREE.Scene();scene.background=new THREE.Color(0x8bbbd5);scene.fog=new THREE.Fog(0x8bbbd5,350,1300);
const camera=new THREE.PerspectiveCamera(settings.camera.FieldOfView,innerWidth/innerHeight,.05,3000);
const renderer=new THREE.WebGLRenderer({antialias:true,powerPreference:'high-performance'});renderer.setPixelRatio(Math.min(devicePixelRatio,3));renderer.setSize(innerWidth,innerHeight);renderer.shadowMap.enabled=true;renderer.shadowMap.type=THREE.PCFSoftShadowMap;document.body.prepend(renderer.domElement);
scene.add(new THREE.HemisphereLight(0xb6dfff,0x8f9baa,2.6));scene.add(new THREE.AmbientLight(0xffffff,.65));
const sun=new THREE.DirectionalLight(0xffffff,2);scene.add(sun,sun.target);sun.castShadow=true;sun.shadow.mapSize.set(4096,4096);Object.assign(sun.shadow.camera,{left:-14,right:14,top:14,bottom:-14,near:.1,far:100});sun.shadow.normalBias=.04;sun.shadow.bias=-.00002;
const plate=settings.baseplate,ground=plate.Position[1]+plate.Size[1]/2;
const baseplate=new THREE.Mesh(new THREE.BoxGeometry(...plate.Size),new THREE.MeshStandardMaterial({color:new THREE.Color().setRGB(...plate.Color,THREE.SRGBColorSpace),roughness:1}));baseplate.position.fromArray(plate.Position);baseplate.receiveShadow=true;scene.add(baseplate);
const grid=new THREE.GridHelper(plate.Size[0],plate.Size[0]/2,0x737373,0x686868);grid.position.y=ground+.004;grid.material.transparent=true;grid.material.opacity=.28;scene.add(grid);
const bacon=await loadBacon(scene);const avatar=bacon.avatar;const animator=new NativeAnimator(avatar,clips,config.animationSets);
avatar.traverse(o=>{if(o.isMesh){o.material.map.anisotropy=renderer.capabilities.getMaxAnisotropy();o.material.map.needsUpdate=true;}});
const player={position:new THREE.Vector3(0,ground,0),velocityY:0,grounded:true,health:settings.humanoid.MaxHealth,jumpTime:0,respawnLeft:0};
const keys=new Set();let yaw=0,pitch=.24,distance=12,shiftLock=false,preview=null,lastTime=performance.now(),accumulator=0,drag=null;
const labels={idle:'Idle',walk:'Walk',run:'Run',jump:'Jump',fall:'Fall',climb:'Climb',sit:'Sit',toolnone:'Tool hold',toolslash:'Tool slash',toollunge:'Tool lunge',wave:'Wave',point:'Point',dance1:'Dance 1',dance2:'Dance 2',dance3:'Dance 3',laugh:'Laugh',cheer:'Cheer'};
const menu=document.querySelector('#animation');for(const [name,entries]of Object.entries(config.animationSets))entries.forEach((entry,index)=>{const option=document.createElement('option');option.value=`${name}:${entry.id}`;option.textContent=`${labels[name]}${entries.length>1?` · ${index+1}`:''}`;menu.append(option);});
function stopPreview(){preview=null;menu.value='auto';animator.play('idle',{fade:.1});}
function playSelected(){if(menu.value==='auto'){stopPreview();return;}const [name,id]=menu.value.split(':');preview={name,id};const speed=['walk','run'].includes(name)?sp.CharacterWalkSpeed/14.5:name==='climb'?(sp.CharacterWalkSpeed*.7)/12:1;animator.play(name,{id,fade:name==='sit'?.5:.1,speed,once:['wave','point','laugh','cheer'].includes(name),restart:true});}
document.querySelector('#play').onclick=playSelected;menu.onchange=playSelected;
function reset(){player.position.set(0,ground,0);player.velocityY=0;player.grounded=true;player.health=settings.humanoid.MaxHealth;player.jumpTime=0;player.respawnLeft=0;avatar.rotation.set(0,0,0);avatar.visible=true;stopPreview();}
document.querySelector('#reset').onclick=reset;
function toggleLock(){shiftLock=!shiftLock;document.querySelector('#lock').setAttribute('aria-pressed',String(shiftLock));}
document.querySelector('#lock').onclick=toggleLock;
document.querySelector('#copy').onclick=async()=>{const button=document.querySelector('#copy');try{const defaults=await fetch('./assets/extracted-defaults.json').then(r=>r.json());await navigator.clipboard.writeText(JSON.stringify({studio:config,extractedDefaults:defaults,current:{position:player.position.toArray(),animation:animator.current,velocityY:player.velocityY},asset:{source:'Roblox Studio native OBJ',scaleStuds:1}},null,2));button.textContent='Copied';setTimeout(()=>button.textContent='Copy settings',1500);}catch{button.textContent='Clipboard unavailable';}};
document.querySelector('#walk-speed').textContent=sp.CharacterWalkSpeed+' studs/s';document.querySelector('#jump-height').textContent=sp.CharacterJumpHeight.toFixed(1)+' studs';document.querySelector('#gravity').textContent=gravity.toFixed(1)+' studs/s²';
function jump(){if(player.grounded&&player.health>0){stopPreview();player.velocityY=sp.CharacterUseJumpPower?sp.CharacterJumpPower:Math.sqrt(2*gravity*sp.CharacterJumpHeight);player.grounded=false;player.jumpTime=0;animator.play('jump',{fade:.1});}}
addEventListener('keydown',e=>{if(e.target.closest('select,button,input,textarea'))return;if(['Space','ArrowUp','ArrowDown','ArrowLeft','ArrowRight'].includes(e.code))e.preventDefault();keys.add(e.code);if(e.code==='Space'&&!e.repeat)jump();if(e.code==='ShiftLeft'&&!e.repeat&&sp.EnableMouseLockOption)toggleLock();});
addEventListener('keyup',e=>keys.delete(e.code));addEventListener('blur',()=>{keys.clear();drag=null;});
const canvas=renderer.domElement;canvas.addEventListener('contextmenu',e=>e.preventDefault());canvas.addEventListener('pointerdown',e=>{document.activeElement?.blur();drag={id:e.pointerId,x:e.clientX,y:e.clientY};canvas.setPointerCapture(e.pointerId);});canvas.addEventListener('pointermove',e=>{if(!drag||e.pointerId!==drag.id)return;yaw-=(e.clientX-drag.x)*.006;pitch=Math.max(-1.35,Math.min(1.35,pitch+(e.clientY-drag.y)*.006));drag.x=e.clientX;drag.y=e.clientY;});canvas.addEventListener('pointerup',()=>drag=null);canvas.addEventListener('pointercancel',()=>drag=null);canvas.addEventListener('wheel',e=>{e.preventDefault();distance=Math.min(sp.CameraMaxZoomDistance,Math.max(sp.CameraMinZoomDistance,distance*Math.exp(e.deltaY*.001)));},{passive:false});
document.querySelectorAll('[data-key]').forEach(b=>{b.onpointerdown=e=>{e.preventDefault();keys.add(b.dataset.key);b.setPointerCapture(e.pointerId);};b.onpointerup=b.onpointercancel=()=>keys.delete(b.dataset.key);});document.querySelector('#jump').onpointerdown=e=>{e.preventDefault();jump();};
const direction=new THREE.Vector3();
function simulate(dt){
 if(player.health<=0){player.respawnLeft-=dt;if(player.respawnLeft<=0)reset();return;}
 direction.set(Number(keys.has('KeyD')||keys.has('ArrowRight'))-Number(keys.has('KeyA')||keys.has('ArrowLeft')),0,Number(keys.has('KeyS')||keys.has('ArrowDown'))-Number(keys.has('KeyW')||keys.has('ArrowUp')));const moving=direction.lengthSq()>0;if(moving){if(preview)stopPreview();direction.normalize().applyAxisAngle(new THREE.Vector3(0,1,0),yaw);player.position.addScaledVector(direction,sp.CharacterWalkSpeed*dt);}
 const overPlate=Math.abs(player.position.x-plate.Position[0])<=plate.Size[0]/2&&Math.abs(player.position.z-plate.Position[2])<=plate.Size[2]/2;
 if(!player.grounded||!overPlate){player.grounded=false;const previousY=player.position.y;player.position.y+=player.velocityY*dt-.5*gravity*dt*dt;player.velocityY-=gravity*dt;player.jumpTime+=dt;if(overPlate&&previousY>=ground&&player.position.y<=ground&&player.velocityY<=0){player.position.y=ground;player.velocityY=0;player.grounded=true;}}
 if(player.position.y<settings.workspace.FallenPartsDestroyHeight){player.health=0;player.respawnLeft=settings.players.RespawnTime;avatar.visible=false;}
 if(moving&&settings.humanoid.AutoRotate)avatar.rotation.y=Math.atan2(-direction.x,-direction.z);else if(shiftLock&&!preview)avatar.rotation.y=yaw;
 if(!preview){if(!player.grounded){animator.play(player.jumpTime<.3?'jump':'fall',{fade:player.jumpTime<.3?.1:.3});}else animator.play(moving?'walk':'idle',{fade:.1,speed:moving?sp.CharacterWalkSpeed/settings.rigScale/14.5:1});}
 animator.update(dt);if(preview&&animator.current.name!==preview.name){preview=null;menu.value='auto';}avatar.position.copy(player.position);
}
function render(){const target=player.position.clone().add(new THREE.Vector3(0,3,0));if(shiftLock)target.add(new THREE.Vector3(1.75,0,0).applyAxisAngle(new THREE.Vector3(0,1,0),yaw));const offset=new THREE.Vector3(Math.sin(yaw)*Math.cos(pitch),Math.sin(pitch),Math.cos(yaw)*Math.cos(pitch)).multiplyScalar(distance);camera.position.copy(target).add(offset);camera.position.y=Math.max(ground+.3,camera.position.y);camera.lookAt(target);avatar.visible=player.health>0&&distance>=1;sun.target.position.copy(player.position);sun.position.copy(player.position).add(new THREE.Vector3().fromArray(reference.lighting.sunDirection).multiplyScalar(40));sun.target.updateMatrixWorld();document.querySelector('#state').textContent=player.health<=0?'Respawning…':labels[animator.current?.name]??'Idle';document.querySelector('#health').textContent=`${player.health} / ${settings.humanoid.MaxHealth}`;renderer.render(scene,camera);}
animator.play('idle');document.querySelector('#loading').remove();
window.baseplateGame={THREE,scene,camera,renderer,avatar,animator,player,config,keys,jump,reset,simulate,render,get preview(){return preview;},stopPreview};window.avatarReady=true;
renderer.setAnimationLoop(now=>{accumulator+=Math.min((now-lastTime)/1000,.1);lastTime=now;while(accumulator>=1/120){simulate(1/120);accumulator-=1/120;}render();});
addEventListener('resize',()=>{camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();renderer.setSize(innerWidth,innerHeight);});
}catch(error){document.querySelector('#loading').textContent='Could not load the game: '+error.message;console.error(error);}

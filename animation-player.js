import * as THREE from 'three';

const jointNames={'Torso':'RootJoint','Head':'Neck','Left Arm':'Left_Shoulder','Right Arm':'Right_Shoulder','Left Leg':'Left_Hip','Right Leg':'Right_Hip'};
export function cframeMatrix(c){return new THREE.Matrix4().set(c[3],c[4],c[5],c[0],c[6],c[7],c[8],c[1],c[9],c[10],c[11],c[2],0,0,0,1);}
const identity=()=>({position:new THREE.Vector3(),quaternion:new THREE.Quaternion()});
function blend(a,b,t){if(t===0||t===1){const v=t===0?a:b;return {position:v.position.clone(),quaternion:v.quaternion.clone(),matrix:v.matrix?.clone()};}return {position:a.position.clone().lerp(b.position,t),quaternion:a.quaternion.clone().normalize().slerp(b.quaternion.clone().normalize(),t)};}

// These exported Roblox clips use Linear easing, In direction, and weight 1.
// Keep per-joint sparse channels; an omitted pose is not an identity keyframe.
export class NativeAnimator{
 constructor(avatar,clips,sets){
  this.sets=sets;this.clips={};this.joints={};this.transforms={};this.current=null;this.time=0;this.speed=1;
  for(const [part,name]of Object.entries(jointNames)){const node=avatar.getObjectByName(name);if(!node)throw Error(`Missing source joint ${name}`);this.joints[part]={node,rest:node.matrix.clone()};this.transforms[part]=identity();}
  for(const [id,clip]of Object.entries(clips)){
   if(!clip.keyframes?.length)throw Error(`Empty Studio animation ${id}`);
   const channels={};
   function visit(p,time){if(jointNames[p.name]){if(p.easingStyle!=='Linear'||p.weight!==1)throw Error('Unsupported native pose interpolation');const m=cframeMatrix(p.cframe),position=new THREE.Vector3(),quaternion=new THREE.Quaternion();m.decompose(position,quaternion,new THREE.Vector3());(channels[p.name]??=[]).push({time,position,quaternion,matrix:m,source:p.cframe});}for(const child of p.children)visit(child,time);}
   for(const k of clip.keyframes)for(const p of k.poses)visit(p,k.time);
   this.clips[id]={...clip,channels,duration:clip.keyframes.at(-1).time};
  }
 }
 sample(id,time){const out={},clip=this.clips[id];for(const [part,keys]of Object.entries(clip.channels)){let next=keys.findIndex(k=>k.time>time);if(next===0)out[part]=keys[0];else if(next<0)out[part]=keys.at(-1);else {const a=keys[next-1],b=keys[next];out[part]=blend(a,b,(time-a.time)/(b.time-a.time));}}return out;}
 choose(name){const entries=this.sets[name];if(!entries?.length)throw Error(`Unknown animation ${name}`);let r=Math.random()*entries.reduce((s,x)=>s+x.weight,0);return entries.find(x=>(r-=x.weight)<0)?.id??entries.at(-1).id;}
 play(name,{id=null,fade=.1,speed=1,once=false,restart=false,repeat=false}={}){
  if(!restart&&this.current?.name===name&&(!id||this.current.id===id)){this.speed=speed;return;}
  const chosen=id??this.choose(name);if(!this.clips[chosen])throw Error(`Missing Studio clip ${chosen}`);
  this.from=Object.fromEntries(Object.entries(this.transforms).map(([p,t])=>[p,blend(t,t,0)]));this.fade=fade;this.fadeTime=0;this.time=0;this.speed=speed;this.current={name,id:chosen,once,pinned:!!id,repeat};
 }
 apply(pose){for(const [part,{node,rest}]of Object.entries(this.joints)){const t=pose[part]??identity();this.transforms[part]=blend(t,t,0);node.matrixAutoUpdate=false;node.matrix.copy(rest).multiply(t.matrix??new THREE.Matrix4().compose(t.position,t.quaternion,new THREE.Vector3(1,1,1)));node.matrixWorldNeedsUpdate=true;}}
 update(dt){if(!this.current)return;const clip=this.clips[this.current.id];this.time+=dt*this.speed;this.fadeTime+=dt;
  if(this.time>clip.duration&&clip.duration>0){if(this.current.once){this.play('idle',{fade:.1});}else if(clip.loop||this.current.repeat){this.time%=clip.duration;const chosen=this.current.pinned?this.current.id:this.choose(this.current.name);if(chosen!==this.current.id){this.current.id=chosen;}}else this.time=clip.duration;}
  const target=this.sample(this.current.id,this.time),pose={};const f=this.fade?Math.min(1,this.fadeTime/this.fade):1;
  for(const part of Object.keys(this.joints))pose[part]=blend(this.from?.[part]??identity(),target[part]??identity(),f);this.apply(pose);
 }
}

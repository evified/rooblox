import * as THREE from 'three';
export class SourceCamera{
 constructor(camera,settings,fidelity){this.camera=camera;this.settings=settings;this.source=fidelity.camera;this.sensitivity=this.source.mouseSensitivity;this.shiftLock=false;this.reset();}
 reset(){this.yaw=0;this.pitch=this.source.initialPitch;this.distance=this.source.defaultDistance;this.goal=this.distance;this.zoomVelocity=0;this.opacity=1;}
 get firstPerson(){return this.goal<this.source.firstPersonThreshold;}
 rotate(dx,dy,touch=false){const scale=touch?this.source.touchScale:this.source.mouseScale;let pitchScale=1;if(touch&&dy*this.pitch>0)pitchScale=(1-(2*Math.abs(this.pitch)/Math.PI)**.75)*.75+.25;this.yaw-=dx*scale[0]*this.sensitivity;this.pitch=THREE.MathUtils.clamp(this.pitch+dy*scale[1]*this.sensitivity*pitchScale,-this.source.maxPitch,this.source.maxPitch);}
 zoom(delta){const sp=this.settings.starterPlayer,step=delta/this.source.wheelAdapterPixelsPerStep,curve=this.source.zoomCurveFactor;let next=step>0?this.goal+step*(1+this.goal*curve):(this.goal+step)/(1-step*curve);if(next<1)next=sp.CameraMinZoomDistance;this.goal=THREE.MathUtils.clamp(next,sp.CameraMinZoomDistance,sp.CameraMaxZoomDistance);}
 step(dt,player,baseplate){
  const f=this.source.zoomSpringHz*2*Math.PI,offset=this.goal-this.distance,q=f*dt,decay=Math.exp(-q);this.distance=this.goal+(this.zoomVelocity*dt-offset*(q+1))*decay;this.zoomVelocity=((offset*f-this.zoomVelocity)*q+this.zoomVelocity)*decay;
  this.distance=THREE.MathUtils.clamp(this.distance,this.settings.starterPlayer.CameraMinZoomDistance,this.settings.starterPlayer.CameraMaxZoomDistance);
  const target=player.position.clone().add(new THREE.Vector3(0,3+this.source.subjectHeightAboveRoot,0));
  if(this.shiftLock&&!this.firstPerson)target.add(new THREE.Vector3(this.source.mouseLockOffset,0,0).applyAxisAngle(new THREE.Vector3(0,1,0),this.yaw));
  const offset3=new THREE.Vector3(Math.sin(this.yaw)*Math.cos(this.pitch),Math.sin(this.pitch),Math.cos(this.yaw)*Math.cos(this.pitch));let radius=this.firstPerson?.5:this.distance;
  if(baseplate){baseplate.updateMatrixWorld();const ray=new THREE.Raycaster(target,offset3,.05,radius);const hit=ray.intersectObject(baseplate,false)[0];if(hit)radius=Math.max(.5,hit.distance-.05);}
  this.camera.position.copy(target).addScaledVector(offset3,radius);this.camera.lookAt(target);
  const desiredOpacity=radius<2?(radius-.5)/1.5:1,delta=THREE.MathUtils.clamp(desiredOpacity-this.opacity,-this.source.transparencyRate*dt,this.source.transparencyRate*dt);this.opacity=THREE.MathUtils.clamp(this.opacity+delta,0,1);if(this.firstPerson)this.opacity=0;
  this.actualRadius=radius;this.target=target;return this.opacity;
 }
}

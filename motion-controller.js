// Responses below come from the Studio capture in fidelity-config.json.
export const wrapAngle=a=>Math.atan2(Math.sin(a),Math.cos(a));
export class MotionController{
 constructor(settings,fidelity){this.settings=settings;this.fidelity=fidelity;this.reset();}
 reset(){this.x=0;this.y=0;this.z=0;this.vx=0;this.vy=0;this.vz=0;this.yaw=0;this.grounded=true;this.jumpAge=Infinity;this.airAge=0;this.targetYaw=0;this.accumulator=0;this.lastState={moving:false,speed:0};}
 jump(){if(!this.grounded)return false;const sp=this.settings.starterPlayer;this.vy=sp.CharacterUseJumpPower?sp.CharacterJumpPower:this.fidelity.movement.heightModeLaunchVelocity;this.grounded=false;this.jumpAge=0;this.airAge=0;return true;}
 step(dt,input={}){this.accumulator+=dt;const step=this.fidelity.movement.groundSolverFit.stepSeconds;while(this.accumulator+1e-10>=step){this.lastState=this.physicsStep(step,input);this.accumulator-=step;}return this.lastState;}
 physicsStep(dt,{x=0,z=0,cameraYaw=0,cameraRelative=false,jumpHeld=false,enabled=true}={}){
  const sp=this.settings.starterPlayer,plate=this.settings.baseplate,g=this.settings.workspace.Gravity,f=this.fidelity.movement;
  if(!enabled){x=0;z=0;jumpHeld=false;}
  let magnitude=Math.hypot(x,z);if(magnitude>1){x/=magnitude;z/=magnitude;magnitude=1;}
  const sin=Math.sin(cameraYaw),cos=Math.cos(cameraYaw),wx=x*cos+z*sin,wz=z*cos-x*sin;
  const goalX=wx*sp.CharacterWalkSpeed,goalZ=wz*sp.CharacterWalkSpeed;
  if(jumpHeld)this.jump();
  if(this.grounded){
   const dx=goalX-this.vx,dz=goalZ-this.vz,length=Math.hypot(dx,dz),solver=f.groundSolverFit,amount=Math.min(length,length*solver.velocityGainPerSecond*dt,solver.maxAcceleration*dt);if(length>0){this.vx+=dx/length*amount;this.vz+=dz/length*amount;}this.x+=this.vx*dt;this.z+=this.vz*dt;
  }else{const dx=goalX-this.vx,dz=goalZ-this.vz,length=Math.hypot(dx,dz),amount=Math.min(length,f.airAcceleration*dt),reach=Math.min(dt,length/f.airAcceleration);this.x+=this.vx*dt;this.z+=this.vz*dt;if(length>0){const cx=dx/length*amount,cz=dz/length*amount;this.x+=cx*(dt-.5*reach);this.z+=cz*(dt-.5*reach);this.vx+=cx;this.vz+=cz;}}
  const overPlate=Math.abs(this.x-plate.Position[0])<=plate.Size[0]/2&&Math.abs(this.z-plate.Position[2])<=plate.Size[2]/2;
  if(!this.grounded||!overPlate){if(this.grounded)this.airAge=0;this.grounded=false;const oldY=this.y;this.y+=this.vy*dt-.5*g*dt*dt;this.vy-=g*dt;this.airAge+=dt;this.jumpAge+=dt;if(overPlate&&oldY>=0&&this.y<=0&&this.vy<=0){this.y=0;this.vy=0;this.grounded=true;}}
  if(this.settings.humanoid.AutoRotate&&(cameraRelative||magnitude>0)){
   const target=cameraRelative?cameraYaw:Math.atan2(-wx,-wz);this.targetYaw=target;this.yaw=wrapAngle(this.yaw+wrapAngle(target-this.yaw)*(-Math.expm1(-f.rotationRate*dt)));
  }
  return {moving:magnitude>0,speed:Math.hypot(this.vx,this.vz)};
 }
}

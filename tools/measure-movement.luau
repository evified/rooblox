local HS=game:GetService("HttpService")local RS=game:GetService("RunService")
local original=workspace.BaconHair
local m=original:Clone()m.Name="RoobloxTemporaryMeasurement"m.Parent=workspace
for _,p in ipairs(m:GetDescendants())do if p:IsA("BasePart")then p.Anchored=false p.CanTouch=false end end
local root=m.HumanoidRootPart local h=m.Humanoid
h.WalkSpeed=game.StarterPlayer.CharacterWalkSpeed h.UseJumpPower=game.StarterPlayer.CharacterUseJumpPower h.JumpHeight=game.StarterPlayer.CharacterJumpHeight h.AutoRotate=true
local a=m:FindFirstChild("Animate")if a then a.Disabled=true end
root:SetNetworkOwner(nil)
local result={engine=version(),rig="R6",gravity=workspace.Gravity,walkSpeed=h.WalkSpeed,useJumpPower=h.UseJumpPower,jumpHeight=h.JumpHeight,trials={}}
local function reset(yaw)
 h:Move(Vector3.zero,false)m:PivotTo(CFrame.new(70,3.05,70)*CFrame.Angles(0,yaw,0))root.AssemblyLinearVelocity=Vector3.zero root.AssemblyAngularVelocity=Vector3.zero task.wait(.5)
end
local function run(label,duration,direction)
 local t=0 local rows={}local p=root.Position local startYaw=math.atan2(-root.CFrame.LookVector.X,-root.CFrame.LookVector.Z)
 table.insert(rows,{t=0,yaw=startYaw,x=p.X,y=p.Y,z=p.Z,vx=root.AssemblyLinearVelocity.X,vy=root.AssemblyLinearVelocity.Y,vz=root.AssemblyLinearVelocity.Z})
 while t<duration do h:Move(direction,false)local dt=RS.Heartbeat:Wait()t+=dt local v=root.AssemblyLinearVelocity local pos=root.Position table.insert(rows,{t=t,yaw=math.atan2(-root.CFrame.LookVector.X,-root.CFrame.LookVector.Z),x=pos.X,y=pos.Y,z=pos.Z,vx=v.X,vy=v.Y,vz=v.Z,state=h:GetState().Name})end
 table.insert(result.trials,{label=label,direction={direction.X,direction.Y,direction.Z},samples=rows})
end
for _,degrees in ipairs({45,90,180,-90})do reset(0)run("turn_"..degrees,0.65,Vector3.new(-math.sin(math.rad(degrees)),0,-math.cos(math.rad(degrees))))end
reset(0)run("accelerate_forward",.65,Vector3.new(0,0,-1))run("release_forward",.5,Vector3.zero)
reset(0)run("accelerate_diagonal",.65,Vector3.new(-1,0,-1).Unit)
reset(0)h.Jump=true run("jump_stationary",.9,Vector3.zero)
reset(0)run("before_air_reverse",.4,Vector3.new(0,0,-1))h.Jump=true run("air_reverse",.85,Vector3.new(0,0,1))
m:Destroy()
return HS:JSONEncode(result)

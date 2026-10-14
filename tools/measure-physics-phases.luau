local RS=game.RunService local m=workspace.BaconHair:Clone()m.Name="RoobloxTemporaryMeasurement"m.Parent=workspace
for _,p in ipairs(m:GetDescendants())do if p:IsA("BasePart")then p.Anchored=false p.CanTouch=false end end
local root=m.HumanoidRootPart local h=m.Humanoid h.WalkSpeed=16 h.UseJumpPower=false h.JumpHeight=game.StarterPlayer.CharacterJumpHeight
local a=m:FindFirstChild("Animate")if a then a.Disabled=true end root:SetNetworkOwner(nil)
local out={engine=version(),method="PreSimulation Move, PostSimulation root samples, deltaTimeSim accumulated",trials={}}
local function reset()h:Move(Vector3.zero)m:PivotTo(CFrame.new(70,3.05,70))root.AssemblyLinearVelocity=Vector3.zero root.AssemblyAngularVelocity=Vector3.zero task.wait(.5)end
local function sample(t)local pos=root.Position local v=root.AssemblyLinearVelocity return {t=t,x=pos.X,y=pos.Y,z=pos.Z,vx=v.X,vy=v.Y,vz=v.Z,yaw=math.atan2(-root.CFrame.LookVector.X,-root.CFrame.LookVector.Z),state=h:GetState().Name}end
local function run(name,frames,dir)local samples={sample(0)}local t=0 for i=1,frames do local dt=RS.PreSimulation:Wait()h:Move(dir,false)RS.PostSimulation:Wait()t+=dt table.insert(samples,sample(t))end table.insert(out.trials,{label=name,direction={dir.X,dir.Y,dir.Z},samples=samples})end
reset()run("start_forward",35,Vector3.new(0,0,-1))run("stop_forward",30,Vector3.zero)
reset()run("turn_90",40,Vector3.new(-1,0,0))run("stop_left",30,Vector3.zero)
reset()run("turn_diagonal",40,Vector3.new(-1,0,-1).Unit)run("stop_diagonal",30,Vector3.zero)
m:Destroy()return game.HttpService:JSONEncode(out)

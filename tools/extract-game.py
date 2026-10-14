import json,re
from pathlib import Path
from urllib.request import Request,urlopen
ROOT=Path(__file__).resolve().parent.parent
token=Path(r'C:\Users\larp\.robloxstudio-mcp\auth-token').read_text().strip()
def call(code):
    req=Request('http://127.0.0.1:58741/mcp/execute_luau',data=json.dumps({'code':code,'instance_id':'instance:qia-6lf'}).encode(),headers={'X-MCP-Auth':token,'Content-Type':'application/json'})
    with urlopen(req,timeout=150) as f:r=json.load(f)
    if not r.get('success'):raise Exception(r)
    return json.loads(r['returnValue'])
data=call('''local m=workspace.BaconHair
local function props(o,keys)local t={} for _,k in ipairs(keys)do local ok,v=pcall(function()return o[k]end) if ok then if typeof(v)=="Vector3" then v={v.X,v.Y,v.Z} elseif typeof(v)=="Color3" then v={v.R,v.G,v.B} elseif typeof(v)=="EnumItem" then v=tostring(v)end t[k]=v end end return t end
local parts={} for _,p in ipairs(m:GetDescendants())do if p:IsA("BasePart") then parts[p.Name]=props(p,{"Size","CanCollide","CanTouch","CanQuery","Massless","Transparency","Anchored"}) end end
local b=workspace:FindFirstChild("Baseplate")
local configured={} for _,c in ipairs(m.Animate:GetChildren())do local list={}for _,a in ipairs(c:GetChildren())do if a:IsA("Animation")then table.insert(list,{id=a.AnimationId,weight=a:FindFirstChild("Weight") and a.Weight.Value or 1})end end if #list>0 then configured[c.Name]=list end end
return game:GetService("HttpService"):JSONEncode({animate=m.Animate.Source,configured=configured,rigScale=m:GetScale(),players=props(game:GetService("Players"),{"RespawnTime","CharacterAutoLoads"}),humanoid=props(m.Humanoid,{"WalkSpeed","JumpHeight","JumpPower","UseJumpPower","HipHeight","MaxSlopeAngle","AutoRotate","Health","MaxHealth","RigType"}),starterPlayer=props(game:GetService("StarterPlayer"),{"CharacterWalkSpeed","CharacterJumpHeight","CharacterJumpPower","CharacterUseJumpPower","CameraMinZoomDistance","CameraMaxZoomDistance","AutoJumpEnabled","EnableMouseLockOption"}),workspace=props(workspace,{"Gravity","FallenPartsDestroyHeight"}),camera=props(workspace.CurrentCamera,{"FieldOfView"}),baseplate=b and props(b,{"Size","Position","Color","Material"}) or {},parts=parts})''')
(ROOT/'source'/'game-settings.json').write_text(json.dumps(data,indent=2))
(ROOT/'source'/'Animate.luau').write_text(data['animate'])
sets={}
block=data['animate'].split('local animNames = {',1)[1].split('local dances',1)[0]
for match in re.finditer(r'(\w+)\s*=\s*\{(.*?)(?=\n\t\w+\s*=|\Z)',block,re.S):
    sets[match[1]]=[{'id':i,'weight':int(w)} for i,w in re.findall(r'id\s*=\s*"http://www.roblox.com/asset/\?id=(\d+)"\s*,\s*weight\s*=\s*(\d+)',match[2])]
for name,entries in data['configured'].items():
    sets[name]=[{'id':re.search(r'\d+',a['id'])[0],'weight':a['weight']} for a in entries]
data.pop('animate')
(ROOT/'assets'/'game-config.json').write_text(json.dumps({'settings':data,'animationSets':sets},indent=2))
data['animate']=(ROOT/'source'/'Animate.luau').read_text()
ids=sorted(set(re.findall(r'rbxassetid://(\d+)|[?&]id=(\d+)',data['animate'])))
ids=sorted(set(a or b for a,b in ids))
print(json.dumps({'settings':{k:v for k,v in data.items()if k!='animate'},'animationIds':ids}))
code='''local ids=IDS local result={} local kp=game:GetService("KeyframeSequenceProvider")
local function pose(p)local t={name=p.Name,weight=p.Weight,easingStyle=p.EasingStyle.Name,easingDirection=p.EasingDirection.Name,cframe={p.CFrame:GetComponents()},children={}} for _,c in ipairs(p:GetSubPoses())do table.insert(t.children,pose(c))end return t end
for _,id in ipairs(ids)do local ok,s=pcall(function()return kp:GetKeyframeSequenceAsync("rbxassetid://"..id)end) if ok then local t={id=id,loop=s.Loop,priority=s.Priority.Name,keyframes={}} for _,k in ipairs(s:GetKeyframes())do local q={time=k.Time,name=k.Name,poses={}} for _,p in ipairs(k:GetPoses())do table.insert(q.poses,pose(p))end table.insert(t.keyframes,q)end table.sort(t.keyframes,function(a,b)return a.time<b.time end) result[id]=t else result[id]={error=tostring(s)}end end return game:GetService("HttpService"):JSONEncode(result)'''.replace('IDS','{'+','.join('"'+i+'"'for i in ids)+'}')
existing=ROOT/'assets'/'animations.json'
if existing.exists() and all(v.get('keyframes') for v in json.loads(existing.read_text()).values()):
    print('Using existing, complete Studio keyframe capture.')
    raise SystemExit(0)
animations=call(code)
assert all(v.get('keyframes') for v in animations.values()),'Incomplete capture: original file preserved.'
(ROOT/'assets'/'animations.json').write_text(json.dumps(animations,separators=(',',':')))
print(json.dumps({i:len(v.get('keyframes',[])) if 'error'not in v else v['error'] for i,v in animations.items()}))

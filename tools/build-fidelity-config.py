import json,hashlib,re,shutil
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
motion=json.loads((ROOT/'source/movement-measurements.json').read_text());repeat=json.loads((ROOT/'source/movement-repeat.json').read_text());fit=json.loads((ROOT/'audit/movement-calibration.json').read_text());inputs=json.loads((ROOT/'source/input-evidence.json').read_text());ui=json.loads((ROOT/'source/runtime-evidence.json').read_text())
def trial(d,name):return next(t['samples']for t in d['trials']if t['label']==name)
def velocity(s):return np.hypot(s['vx'],s['vz'])
ground=trial(motion,'turn_90');first=next(i for i,s in enumerate(ground)if velocity(s)>0.01)
profile=[[0,0]]+[[j/60,float(velocity(s)/16)]for j,s in enumerate(ground[first:first+8],1)]
release=trial(motion,'release_forward');releaseProfile=[[0,0]]+[[j/60,float(1-velocity(s)/16)]for j,s in enumerate(release[1:9],1)]
jump=trial(motion,'jump_stationary');firstJump=next(i for i,s in enumerate(jump)if s.get('state')=='Jumping');rows=[]
for j,s in enumerate(jump[firstJump:],1):
 if s.get('state')not in ['Jumping','Freefall']:break
 rows.append((j/60,s['y']-jump[0]['y'],s['vy']))
x=np.array([r[0]for r in rows]);y=np.array([r[1]for r in rows]);g=motion['gravity'];b,c=np.linalg.lstsq(np.stack([x,np.ones(len(x))],1),y+.5*g*x*x,rcond=None)[0]
pred=b*x-.5*g*x*x;res=pred-y
air=trial(motion,'air_reverse');changes=[abs(s2['vz']-s1['vz'])*60 for s1,s2 in zip(air,air[1:])if .05<s1['t']<.2]
config={'engineVersion':motion['engine'],'capturedDate':'2026-10-13','sourceScope':'Native R6 clone, same Place1 flat baseplate; current Studio controller modules and attached user UI screenshot','movement':{'groundStartResponse':profile,'groundStopResponse':releaseProfile,'rotationRate':fit['rotation']['responseRatePerSecond'],'observedCommandPipelineDelay':fit['rotation']['observedPipelineDelaySeconds'],'rotationFit':fit['rotation'],'airAcceleration':float(np.median(changes)),'heightModeLaunchVelocity':float(b),'nativeJumpMeasuredPeak':max(y),'jumpBallisticRMSEStuds':float(np.sqrt(np.mean(res**2))),'jumpBallisticMaxErrorStuds':float(np.max(abs(res))),'modelNote':'Ground profiles use captured per-physics-frame velocity at 60Hz. Render/command scheduling latency is excluded from movement input adapter. Turning rate is a measured fit; jump ballistic fit retains nominal property separately.'},'camera':{'defaultDistance':12.5,'initialPitch':np.pi/12,'maxPitch':np.deg2rad(80),'subjectHeightAboveRoot':1.5,'firstPersonThreshold':1,'mouseLockOffset':1.75,'zoomSpringHz':4.5,'zoomCurveFactor':.5,'mouseScale':[.008727000094950199,.006719999946653843],'touchScale':[.01744999922811985,.01152000017464161],'mouseSensitivity':inputs['settings']['MouseSensitivity'],'transparencyRate':2.8,'wheelAdapterPixelsPerStep':100,'note':'Constants directly captured from current BaseCamera/ClassicCamera/ZoomController/CameraInput/MouseLockController/TransparencyController. Wheel pixel conversion is a browser adapter choice.'},'chat':{'username':'Player1','runtimeConfiguration':ui['services'],'referenceLayout':{'topbar':[14,18,120,55],'chat':[10,81,594,368],'tabsHeight':49,'footerHeight':94},'historyLimit':200,'maxMessageCharacters':200,'note':'Here/Global/Friends and SVG icon shapes follow user screenshot. Only Here is local functional chat; microphone/global/friends/summary services are absent. History/message bounds are local implementation policy.'},'sourceHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in (ROOT/'source/runtime-scripts').glob('*.luau')}}
(ROOT/'assets/fidelity-config.json').write_text(json.dumps(config,indent=2))
phase=json.loads((ROOT/'source/physics-phases.json').read_text())
release=next(t['samples']for t in phase['trials']if t['label']=='stop_forward')
firstSpeed=abs(release[2]['vz']);secondSpeed=abs(release[3]['vz']);substep=1/120
retention=float(np.sqrt(secondSpeed/firstSpeed));gain=(1-retention)/substep;cap=(16-firstSpeed)/(2*substep)
config['movement']['groundSolverFit']={'stepSeconds':substep,'velocityGainPerSecond':gain,'maxAcceleration':cap,'source':'PreSimulation/PostSimulation captured stop_forward plus start/diagonal validation','derivation':'Two 1/120s updates explain first active-frame displacement=(v1+v2)/120; later 1/60s residual velocity ratio is retention². Parameters inferred from saved samples, not public engine properties.'}
config['movement']['modelNote']='Ground velocity gain/cap fitted to phase-aligned native samples at 1/120s, including exact displacement validation. Plugin command scheduling delay is excluded from browser input adapter. Turning remains a measured exponential fit; jump is ballistic fit with nominal property separate.'
(ROOT/'assets/fidelity-config.json').write_text(json.dumps(config,indent=2))
(ROOT/'audit/jump-calibration.json').write_text(json.dumps({'fitLaunchVelocity':float(b),'nativeQuadraticIntercept':float(c),'nominalHeight':motion['jumpHeight'],'sourceRows':rows,'rmseStuds':config['movement']['jumpBallisticRMSEStuds'],'maxErrorStuds':config['movement']['jumpBallisticMaxErrorStuds'],'repeatPeak':max(s['y']for s in trial(repeat,'jump_stationary'))-trial(repeat,'jump_stationary')[0]['y']},indent=2))
fontSource=Path(r'C:\Users\larp\AppData\Local\Roblox\Versions\version-9b554450a0fc4e65\content\fonts');out=ROOT/'assets/fonts';out.mkdir(exist_ok=True)
for name in ['BuilderSans-Regular.otf','BuilderSans-Medium.otf','BuilderSans-Bold.otf']:shutil.copy2(fontSource/name,out/name)
print(json.dumps({'launch':float(b),'nativePeak':max(y),'jumpRMSE':config['movement']['jumpBallisticRMSEStuds'],'airAccel':config['movement']['airAcceleration'],'groundProfile':profile[:4]}))

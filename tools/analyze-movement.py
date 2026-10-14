import json,math
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parent.parent
d=json.loads((ROOT/'source/movement-measurements.json').read_text())
trials=d['trials']
turns=[t for t in trials if t['label']in ['turn_45','turn_90','turn_-90']]
def target(t):return math.atan2(-t['direction'][0],-t['direction'][2])
best=(1e9,None,None)
for rate in np.linspace(7,10,301):
 for delay in np.linspace(0,.03,151):
  errors=[]
  for trial in turns:
   a=abs(target(trial))
   for s in trial['samples']:
    prediction=a*(1-math.exp(-rate*max(0,s['t']-delay)))
    errors.append(prediction-abs(s['yaw']))
  mse=np.mean(np.square(errors))
  if mse<best[0]:best=(mse,float(rate),float(delay))
rate,delay=best[1:]
validation=[]
for t in trials:
 if t['label'].startswith('turn_'):
  a=abs(target(t));errors=[math.degrees(a*(1-math.exp(-rate*max(0,s['t']-delay)))-abs(s['yaw']))for s in t['samples']]
  validation.append({'trial':t['label'],'rmseDegrees':float(np.sqrt(np.mean(np.square(errors)))),'maxErrorDegrees':float(max(map(abs,errors)))})
air=next(t for t in trials if t['label']=='air_reverse')['samples'];accels=[abs((b['vz']-a['vz'])/(b['t']-a['t']))for a,b in zip(air,air[1:])if .04<a['t']<.2]
j=next(t for t in trials if t['label']=='jump_stationary')['samples'];base=j[0]['y'];peak=max(s['y']-base for s in j);flight=[s for s in j if s['y']>base+.02]
fit={'engine':d['engine'],'source':'Measured temporary native R6 clone in Studio solo server physics; not a universal engine constant','rotation':{'responseRatePerSecond':rate,'observedPipelineDelaySeconds':delay,'fitRMSEDegrees':math.degrees(math.sqrt(best[0])),'validation':validation,'implementation':'shortest-arc exponential response calibrated to measured curve; engine angular-force solver remains an approximation'},'air':{'accelerationStudsPerSecondSquared':float(np.median(accels)),'sampleMin':min(accels),'sampleMax':max(accels)},'jump':{'rootPeakHeightStuds':peak,'observedFlightSeconds':flight[-1]['t']-flight[0]['t'] if flight else 0},'ground':{'releaseDisplacementStuds':abs(next(t for t in trials if t['label']=='release_forward')['samples'][-1]['z']-next(t for t in trials if t['label']=='release_forward')['samples'][0]['z'])}}
(ROOT/'audit/movement-calibration.json').write_text(json.dumps(fit,indent=2));print(json.dumps(fit,indent=2))

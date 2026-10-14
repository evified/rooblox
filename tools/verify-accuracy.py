import json,math,hashlib
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent
URL='http://127.0.0.1:8766/'
errors=[];external=[];websockets=[]
with sync_playwright()as p:
 browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=1)
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('websocket',lambda s:websockets.append(s.url));page.on('request',lambda r:external.append(r.url)if r.url.startswith(('http://','https://'))and not r.url.startswith(URL)else None)
 page.goto(URL,wait_until='networkidle');page.wait_for_function('window.avatarReady===true');page.evaluate('baseplateGame.renderer.setAnimationLoop(null)')
 page.screenshot(path=str(ROOT/'audit/accuracy-desktop.png'))
 result=page.evaluate('''async()=>{
 const g=baseplateGame,T=g.THREE,{MotionController,wrapAngle}=await import('./motion-controller.js'),{SourceCamera}=await import('./camera-controller.js');
 const profile=[];for(const fps of [30,60,120,240]){const m=new MotionController(g.config.settings,g.fidelity);for(let i=0;i<fps;i++)m.step(1/fps,{x:-1,z:-1});profile.push({fps,x:m.x,z:m.z,yaw:m.yaw,speed:Math.hypot(m.vx,m.vz)});}
 const turning=new MotionController(g.config.settings,g.fidelity);turning.step(1/60,{x:-1});const firstYaw=turning.yaw;for(let i=0;i<60;i++)turning.step(1/60,{x:-1});const finalYaw=turning.yaw;
 const wrap=new MotionController(g.config.settings,g.fidelity);wrap.yaw=179*Math.PI/180;wrap.step(1/60,{cameraRelative:true,cameraYaw:-179*Math.PI/180});const wrapStep=Math.abs(wrapAngle(wrap.yaw-179*Math.PI/180));
 const walk=new MotionController(g.config.settings,g.fidelity);for(let i=0;i<240;i++)walk.step(1/240,{z:-1});const walkDistance=-walk.z,walkSpeed=Math.hypot(walk.vx,walk.vz),stopPosition=walk.z;walk.step(1/120,{});const releaseSpeed=Math.hypot(walk.vx,walk.vz);for(let i=0;i<120;i++)walk.step(1/240,{});const stopDistance=Math.abs(walk.z-stopPosition);
 const air=new MotionController(g.config.settings,g.fidelity);for(let i=0;i<60;i++)air.step(1/60,{z:-1});air.jump();air.step(1/60,{z:1});const firstAirVelocity=air.vz;
 const jump=new MotionController(g.config.settings,g.fidelity);jump.jump();let peak=0,time=0;while(!jump.grounded&&time<2){jump.step(1/240,{});time+=1/240;peak=Math.max(peak,jump.y);}
 const held=new MotionController(g.config.settings,g.fidelity);let jumps=0,previous=true;for(let i=0;i<500;i++){held.step(1/240,{jumpHeld:true});if(previous&&!held.grounded)jumps++;previous=held.grounded;}
 const cameraFixtures=[];for(const fps of [30,60,120]){const cam=new T.PerspectiveCamera(70,1,.05,3000),c=new SourceCamera(cam,g.config.settings,g.fidelity);c.zoom(100);const goal=c.goal;for(let i=0;i<fps;i++)c.step(1/fps,g.player,null);cameraFixtures.push({fps,distance:c.distance,goal,target:c.target.toArray()});}
 const cf=new SourceCamera(new T.PerspectiveCamera(),g.config.settings,g.fidelity);cf.rotate(100,100);const sensitivity={yaw:cf.yaw,pitch:cf.pitch};cf.rotate(0,10000);const maxPitch=cf.pitch;cf.zoom(-10000);cf.step(1,g.player,null);const firstPerson={goal:cf.goal,first:cf.firstPerson,opacity:cf.opacity};
 let keyframes=0,maxPoseError=0;for(const [id,clip]of Object.entries(g.animator.clips))for(const [part,channel]of Object.entries(clip.channels))for(const key of channel){g.animator.apply(g.animator.sample(id,key.time));const c=key.source,pose=new T.Matrix4().set(c[3],c[4],c[5],c[0],c[6],c[7],c[8],c[1],c[9],c[10],c[11],c[2],0,0,0,1),expected=g.animator.joints[part].rest.clone().multiply(pose),actual=g.animator.joints[part].node.matrix;for(let i=0;i<16;i++)maxPoseError=Math.max(maxPoseError,Math.abs(expected.elements[i]-actual.elements[i]));keyframes++;}
 g.reset();g.render();return {profile,firstYaw,finalYaw,wrapStep,walkDistance,walkSpeed,releaseSpeed,stopDistance,firstAirVelocity,jumpPeak:peak,jumpTime:time,heldJumps:jumps,cameraFixtures,sensitivity,maxPitch,firstPerson,keyframes,maxPoseError};
}''')
 assert 0<result['firstYaw']<math.pi/2 and abs(result['finalYaw']-math.pi/2)<.001,result
 assert result['wrapStep']<math.radians(2),result
 assert all(abs(v['speed']-16)<1e-8 for v in result['profile']),result
 assert max(v['yaw']for v in result['profile'])-min(v['yaw']for v in result['profile'])<1e-8,result
 assert max(v['x']for v in result['profile'])-min(v['x']for v in result['profile'])<1e-8,result
 assert 0<result['releaseSpeed']<16 and result['firstAirVelocity']<0,result
 assert abs(result['jumpPeak']-7.528898477554321)<.01 and result['heldJumps']>=3,result
 assert all(abs(c['distance']-c['goal'])<1e-7 for c in result['cameraFixtures']),result
 assert result['maxPoseError']==0 and result['keyframes']==3006,result
 assert result['firstPerson']['first']and result['firstPerson']['opacity']==0,result
 # Native traces are held independently of the implementation.
 motion=json.loads((ROOT/'source/movement-measurements.json').read_text());fit=basefit=json.loads((ROOT/'assets/fidelity-config.json').read_text())
 trace=next(t for t in motion['trials']if t['label']=='turn_90')
 comparisons=page.evaluate('''async data=>{const {MotionController}=await import('./motion-controller.js');const g=baseplateGame,m=new MotionController(g.config.settings,g.fidelity);let previous=0;return data.map(s=>{m.step(s.t-previous,{x:-1});previous=s.t;return {t:s.t,observed:s.yaw,browser:m.yaw};});}''',trace['samples'])
 # Plugin command scheduling latency is separated from browser input latency.
 adjusted=[math.degrees((math.pi/2)*(1-math.exp(-fit['movement']['rotationRate']*max(0,r['t']-fit['movement']['observedCommandPipelineDelay'])))-r['observed'])for r in comparisons]
 result['nativeTurn90Comparison']={'rmseDegrees':math.sqrt(sum(e*e for e in adjusted)/len(adjusted)),'maxErrorDegrees':max(map(abs,adjusted)),'pipelineAlignmentSeconds':fit['movement']['observedCommandPipelineDelay']}
 native_release=next(t for t in motion['trials']if t['label']=='release_forward')['samples']
 native_stop=abs(native_release[-1]['z']-native_release[0]['z'])
 result['nativeGroundReleaseComparison']={'nativeStopDistance':native_stop,'browserStopDistance':result['stopDistance'],'absoluteDifferenceStuds':abs(native_stop-result['stopDistance']),'scope':'Velocity gain/cap at 1/120s inferred from phase-aligned Studio samples; flat R6 scope.'}
 phase=json.loads((ROOT/'source/physics-phases.json').read_text())
 result['phaseAlignedGroundTraces']=page.evaluate('''async phase=>{const {MotionController}=await import('./motion-controller.js'),g=baseplateGame;return phase.trials.map(trial=>{const m=new MotionController(g.config.settings,g.fidelity),rows=trial.samples,initial=rows[0];m.vx=initial.vx;m.vz=initial.vz;let maxPosition=0,maxVelocity=0;for(let i=2;i<rows.length;i++){m.step(1/60,{x:trial.direction[0],z:trial.direction[2]});const row=rows[i],reference=rows[1];maxPosition=Math.max(maxPosition,Math.hypot(m.x-(row.x-reference.x),m.z-(row.z-reference.z)));maxVelocity=Math.max(maxVelocity,Math.hypot(m.vx-row.vx,m.vz-row.vz));}return {trial:trial.label,maxPositionErrorStuds:maxPosition,maxVelocityErrorStudsPerSecond:maxVelocity,commandDelaySeconds:rows[1].t};});}''',phase)
 assert all(t['maxPositionErrorStuds']<.001 and t['maxVelocityErrorStudsPerSecond']<.0001 for t in result['phaseAlignedGroundTraces']),result
 result['nativeJumpComparison']={'nativePeak':fit['movement']['nativeJumpMeasuredPeak'],'browserPeak':result['jumpPeak'],'absoluteDifferenceStuds':abs(result['jumpPeak']-fit['movement']['nativeJumpMeasuredPeak'])}
 assert result['nativeTurn90Comparison']['rmseDegrees']<.6,result
 # Chat focus owns the keyboard; literal markup never executes.
 page.keyboard.down('w');page.evaluate('for(let i=0;i<30;i++)baseplateGame.simulate(1/240)');page.keyboard.press('/');assert page.locator('#chat-input').evaluate('(e)=>e===document.activeElement')
 assert page.evaluate('baseplateGame.keys.size')==0
 page.keyboard.up('w');page.locator('#chat-input').fill('Player1 says hello 👋 <img src=x onerror=alert(1)>');page.keyboard.press('Space');assert page.evaluate('baseplateGame.motion.grounded')
 page.keyboard.press('Enter');assert 'Player1: Player1 says hello' in page.locator('#messages').inner_text();assert page.locator('#messages img').count()==0
 page.evaluate('for(let i=0;i<120;i++)baseplateGame.simulate(1/240);baseplateGame.render()');assert page.locator('.bubble').count()==1
 page.keyboard.press('/');page.locator('#chat-input').fill('/e wave');page.keyboard.press('Enter');assert page.evaluate('baseplateGame.animator.current.name')=='wave'
 page.evaluate('for(let i=0;i<450;i++)baseplateGame.simulate(1/240)');assert page.evaluate('baseplateGame.animator.current.name')=='idle'
 page.keyboard.press('/');page.locator('#chat-input').fill('draft');page.keyboard.press('Escape');assert page.locator('#chat-input').input_value()=='draft';assert page.locator('#menu-overlay').is_hidden()
 page.keyboard.press('Escape');assert page.locator('#menu-overlay').is_visible();assert page.locator('.player-row').count()==1
 page.click('[data-menu-tab=settings]');page.locator('#sensitivity').fill('2');page.locator('#sensitivity').dispatch_event('input');assert page.evaluate('baseplateGame.view.sensitivity')==2
 page.context.grant_permissions(['clipboard-read','clipboard-write']);page.click('#copy');page.wait_for_function('document.querySelector("#copy").textContent==="Copied"');copied=json.loads(page.evaluate('navigator.clipboard.readText()'));assert copied['current']['username']=='Player1'and 'fidelity'in copied and 'extractedDefaults'in copied
 page.click('[data-menu-tab=animations]');values=page.locator('#animation option').evaluate_all('(items)=>items.map(i=>i.value)')
 for value in values:page.select_option('#animation',value);page.evaluate('for(let i=0;i<60;i++)baseplateGame.simulate(1/240);baseplateGame.render()')
 page.click('#reset');page.click('#cancel-reset');assert page.locator('#menu-overlay').is_visible();page.click('#reset');page.click('#confirm-reset');assert page.locator('#menu-overlay').is_hidden();assert page.evaluate('baseplateGame.player.position.length()')==0
 page.click('#chat-toggle');assert page.locator('#chat-panel').is_hidden();page.keyboard.down('w');page.evaluate('for(let i=0;i<240;i++)baseplateGame.simulate(1/240)');page.keyboard.up('w');assert page.evaluate('baseplateGame.player.position.z')<-15
 page.evaluate('window.dispatchEvent(new Event("blur"))');assert page.evaluate('baseplateGame.keys.size')==0
 page.evaluate('baseplateGame.reset();baseplateGame.ui.submit("Test one");baseplateGame.ui.submit("Test two");baseplateGame.ui.submit("Test three");baseplateGame.ui.submit("Test four");baseplateGame.render()');assert page.evaluate('baseplateGame.ui.bubbles.length')==3
 page.evaluate('baseplateGame.ui.update(16,baseplateGame)');assert page.evaluate('baseplateGame.ui.bubbles.length')==0
 page.evaluate('baseplateGame.player.position.x=1100;for(let i=0;i<800;i++)baseplateGame.simulate(1/240)');assert page.evaluate('baseplateGame.player.health')==0
 page.evaluate('for(let i=0;i<730;i++)baseplateGame.simulate(1/240)');assert page.evaluate('baseplateGame.player.health')==100
 page.evaluate('baseplateGame.reset()');page.mouse.move(800,600);page.mouse.down(button='right');page.mouse.move(900,600);page.mouse.up(button='right');assert abs(page.evaluate('baseplateGame.view.yaw')+1.7454000189900398)<1e-6
 page.keyboard.press('Shift');assert page.evaluate('baseplateGame.view.shiftLock')
 page.evaluate('baseplateGame.ui.openMenu()');assert page.evaluate('baseplateGame.keys.size')==0;page.evaluate('baseplateGame.ui.actions.setShiftLock(false);baseplateGame.ui.closeMenu()')
 page.evaluate('baseplateGame.reset();baseplateGame.ui.submit("Bubble range test");baseplateGame.avatar.updateMatrixWorld(true);baseplateGame.camera.position.set(0,4.5,70);baseplateGame.camera.lookAt(0,4.5,0);baseplateGame.ui.update(0,baseplateGame)');assert page.locator('.bubble').inner_text()=='•••'
 page.evaluate('baseplateGame.camera.position.z=110;baseplateGame.ui.update(0,baseplateGame)');assert page.locator('.bubble-stack').is_hidden()
 page.evaluate('baseplateGame.camera.position.set(0,4.5,12);baseplateGame.camera.lookAt(0,4.5,20);baseplateGame.ui.update(0,baseplateGame)');assert page.locator('.bubble-stack').is_hidden()
 if page.locator('#chat-panel').is_hidden():page.click('#chat-toggle')
 page.evaluate('for(let i=0;i<70;i++)baseplateGame.ui.append({kind:"player",username:"Player1",text:"History message "+i});document.querySelector("#messages").scrollTop=0;baseplateGame.ui.submit("New while reading history")');assert page.locator('#messages').evaluate('(e)=>e.scrollTop')==0;assert page.locator('#latest-message').is_visible()
 page.evaluate('baseplateGame.reset();baseplateGame.ui.messages=[];baseplateGame.ui.bubbles=[];baseplateGame.ui.renderMessages(true);baseplateGame.ui.system("Local chat · only Player1 is here.");baseplateGame.ui.system("👋 Say hi! Press / to chat.");document.querySelector("#chat-input").value="";baseplateGame.ui.submit("Hi! The animations work.");baseplateGame.render()');page.screenshot(path=str(ROOT/'audit/accuracy-chat.png'))
 page.set_viewport_size({'width':656,'height':600});page.screenshot(path=str(ROOT/'audit/accuracy-reference-size.png'));box=page.locator('#chat-panel').bounding_box();assert box['x']==10 and box['y']==81 and box['width']==594 and box['height']==368,box
 mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=2);mobile.goto(URL,wait_until='networkidle');mobile.wait_for_function('window.avatarReady===true');mobile.evaluate('baseplateGame.renderer.setAnimationLoop(null)');assert mobile.locator('#jump').is_visible();mobile.locator('#jump').tap();assert mobile.evaluate('!baseplateGame.motion.grounded');mobile.screenshot(path=str(ROOT/'audit/accuracy-mobile.png'));assert mobile.locator('#chat-panel').bounding_box()['width']==370
 result.update({'pageErrors':errors,'externalRequests':external,'websockets':websockets,'menuOptionsExercised':len(values),'chatPlayer1LiteralMarkup':True,'chatKeyboardIsolation':True,'emoteCommand':True,'menuResetSettings':True,'clipboard':True,'bubbleExpiryAndCap':True,'deathRespawn':True,'mobileControlsAndLayout':True,'referenceChatRectangle':box,'rightMouseSensitivity':True,'shiftLockToggle':True,'bubbleDistanceAndBehindCamera':True,'historyScrollPreserved':True})
 assert not errors and not external and not websockets,result
 (ROOT/'audit/accuracy-verification.json').write_text(json.dumps(result,indent=2));print(json.dumps(result));browser.close()

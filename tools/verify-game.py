import json
from pathlib import Path
from playwright.sync_api import sync_playwright
root=Path(__file__).resolve().parent.parent
errors=[]
with sync_playwright()as p:
 browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader'])
 page=browser.new_page(viewport={'width':1440,'height':900},device_scale_factor=2)
 page.on('pageerror',lambda error:errors.append(str(error)))
 page.goto('http://127.0.0.1:8765',wait_until='networkidle')
 page.wait_for_function('window.avatarReady===true')
 page.evaluate('baseplateGame.renderer.setAnimationLoop(null)')
 data=page.evaluate('''()=>{
 const g=baseplateGame,T=g.THREE,a=g.animator;let maxError=0,poses=0;
 const matrix=c=>new T.Matrix4().set(c[3],c[4],c[5],c[0],c[6],c[7],c[8],c[1],c[9],c[10],c[11],c[2],0,0,0,1);
 for(const [id,clip]of Object.entries(a.clips))for(const [part,channel]of Object.entries(clip.channels))for(const key of channel){a.apply(a.sample(id,key.time));const expected=a.joints[part].rest.clone().multiply(matrix(key.source));const got=a.joints[part].node.matrix;for(let i=0;i<16;i++)maxError=Math.max(maxError,Math.abs(expected.elements[i]-got.elements[i]));poses++;}
 g.reset();g.keys.add('KeyW');for(let i=0;i<120;i++)g.simulate(1/120);g.keys.clear();const walkDistance=-g.player.position.z,walkSpeed=a.speed,walkAnimation=a.current.id;
 g.reset();g.jump();let jumpHeight=0,jumpDuration=0,sawFall=false;while(!g.player.grounded&&jumpDuration<2){g.simulate(1/120);jumpDuration+=1/120;jumpHeight=Math.max(jumpHeight,g.player.position.y);sawFall ||=a.current.name==='fall';}
 g.reset();g.keys.add('KeyW');g.keys.add('KeyD');for(let i=0;i<120;i++)g.simulate(1/120);const diagonalDistance=g.player.position.length();g.keys.clear();
 g.reset();g.player.position.x=1100;for(let i=0;i<400;i++)g.simulate(1/120);const died=g.player.health===0;for(let i=0;i<370;i++)g.simulate(1/120);const respawned=g.player.health===100&&g.player.position.length()===0;
 g.reset();a.play('idle',{id:'180435571',fade:0,restart:true});a.update(.01);g.render();const hair=g.avatar.getObjectByName('Handle');
 return {clips:Object.keys(a.clips).length,animationOptions:document.querySelector('#animation').options.length,posesCompared:poses,maxPoseMatrixError:maxError,walkDistance,walkSpeed,walkAnimation,jumpHeight,jumpDuration,sawFall,diagonalDistance,died,respawned,hairDoubleSided:hair.material.side===T.DoubleSide,textureAnisotropy:hair.material.map.anisotropy,pixelRatio:g.renderer.getPixelRatio(),cameraFov:g.camera.fov,baseplateSize:g.config.settings.baseplate.Size};
}''')
 assert data['clips']==23 and data['animationOptions']==25,data
 assert data['maxPoseMatrixError']<1e-5,data
 assert abs(data['walkDistance']-16)<1e-8 and abs(data['diagonalDistance']-16)<1e-8,data
 assert abs(data['jumpHeight']-7.2)<.002 and data['sawFall'],data
 assert data['died'] and data['respawned'] and data['hairDoubleSided'],data
 page.screenshot(path=str(root/'audit'/'baseplate.png'))
 for value in page.locator('#animation option').evaluate_all('(options)=>options.map(o=>o.value)'):
  page.select_option('#animation',value);page.evaluate('for(let i=0;i<60;i++)baseplateGame.simulate(1/120);baseplateGame.render()')
 page.select_option('#animation','walk:180426354');page.evaluate('for(let i=0;i<35;i++)baseplateGame.simulate(1/120);baseplateGame.render()')
 page.screenshot(path=str(root/'audit'/'walking.png'))
 page.click('#reset');page.locator('canvas').click(position={'x':700,'y':500});page.keyboard.down('w');page.evaluate('for(let i=0;i<120;i++)baseplateGame.simulate(1/120)');page.keyboard.up('w');assert page.evaluate('Math.abs(baseplateGame.player.position.z+16)<1e-8')
 page.keyboard.press('Space');assert page.evaluate('!baseplateGame.player.grounded')
 page.keyboard.press('Shift');assert page.locator('#lock').get_attribute('aria-pressed')=='true'
 page.mouse.wheel(0,-10000);assert page.evaluate('baseplateGame.camera.fov===70');page.evaluate('baseplateGame.render()');assert not page.evaluate('baseplateGame.avatar.visible')
 assert not errors,errors
 page.context.grant_permissions(['clipboard-read','clipboard-write'])
 page.click('#copy');page.wait_for_function('document.querySelector("#copy").textContent==="Copied"');copied=page.evaluate('navigator.clipboard.readText()');assert json.loads(copied)['studio']['settings']['workspace']['Gravity']==196.1999969482422
 assert 'extractedDefaults' in json.loads(copied)
 page.select_option('#animation','wave:128777973');page.evaluate('for(let i=0;i<1000;i++)baseplateGame.simulate(1/120)');assert page.evaluate('baseplateGame.animator.current.name')=='idle'
 mobile=browser.new_page(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,device_scale_factor=2)
 mobile.goto('http://127.0.0.1:8765',wait_until='networkidle');mobile.wait_for_function('window.avatarReady===true');mobile.evaluate('baseplateGame.renderer.setAnimationLoop(null)')
 assert mobile.locator('#touch').is_visible() and not mobile.locator('aside details').get_attribute('open')
 mobile.locator('#jump').tap();assert mobile.evaluate('!baseplateGame.player.grounded')
 mobile.screenshot(path=str(root/'audit'/'mobile.png'));mobile.close()
 data['pageErrors']=errors;data['everyMenuClipPlayed']=True;data['keyboardJumpAndShiftLock']=True
 data['clipboardFullCapture']=True;data['mobileTouchJump']=True;data['emoteReturnsToIdle']=True
 (root/'audit'/'game-verification.json').write_text(json.dumps(data,indent=2));print(json.dumps(data))
 browser.close()

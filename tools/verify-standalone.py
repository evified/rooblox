import json
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parent.parent;artifact=ROOT.parent/'Rooblox-Accuracy.html';errors=[];network=[]
with sync_playwright()as p:
 browser=p.chromium.launch(headless=True,args=['--enable-unsafe-swiftshader']);page=browser.new_page(viewport={'width':1440,'height':900})
 page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:network.append(r.url)if r.url.startswith(('http://','https://'))else None)
 page.goto(artifact.as_uri());page.wait_for_function('window.avatarReady===true',timeout=30000);page.evaluate('baseplateGame.renderer.setAnimationLoop(null);baseplateGame.ui.toggleChat();baseplateGame.keys.add("KeyA");for(let i=0;i<12;i++)baseplateGame.simulate(1/240);baseplateGame.render()')
 yaw=page.evaluate('baseplateGame.motion.yaw');assert 0<yaw<1.57
 page.evaluate('baseplateGame.keys.clear();baseplateGame.reset()');page.keyboard.press('/');page.locator('#chat-input').fill('The offline version works.');page.keyboard.press('Enter');assert 'Player1: The offline version works.'in page.locator('#messages').inner_text()
 page.evaluate('baseplateGame.render()');page.screenshot(path=str(ROOT/'audit/accuracy-standalone.png'))
 assert not errors and not network,(errors,network)
 data={'fileUrlTested':True,'gradualTurning':True,'Player1Chat':True,'pageErrors':errors,'externalHttpRequests':network,'htmlBytes':artifact.stat().st_size}
 (ROOT/'audit/standalone-verification.json').write_text(json.dumps(data,indent=2));print(json.dumps(data));browser.close()

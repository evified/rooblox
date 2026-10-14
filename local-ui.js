import * as THREE from 'three';
const $=selector=>document.querySelector(selector);
export class LocalUI{
 constructor(fidelity,actions){this.fidelity=fidelity;this.actions=actions;this.messages=[];this.bubbles=[];this.elapsed=0;this.menuOpen=false;this.composing=false;this.allowLock=true;this.bubbleStack=document.createElement('div');this.bubbleStack.className='bubble-stack';$('#bubble-layer').append(this.bubbleStack);
  $('#chat-toggle').onclick=()=>this.toggleChat();$('#roblox-menu').onclick=()=>this.openMenu();$('#menu-close').onclick=$('#resume').onclick=()=>this.closeMenu();
  $('#chat-input').onfocus=()=>{actions.clearInput();actions.releasePointer();};$('#chat-input').oncompositionstart=()=>this.composing=true;$('#chat-input').oncompositionend=()=>this.composing=false;
  $('#chat-form').onsubmit=e=>{e.preventDefault();if(this.composing)return;const input=$('#chat-input'),text=input.value.trim();if(!text)return;this.submit(text);input.value='';input.blur();};
  $('#chat-options').onclick=()=>{const menu=$('#chat-options-menu');menu.hidden=!menu.hidden;$('#chat-options').setAttribute('aria-expanded',String(!menu.hidden));};$('#clear-chat').onclick=()=>{this.messages=[];this.bubbles=[];this.renderMessages(true);$('#chat-options-menu').hidden=true;this.system('Local history cleared.');};
  $('#latest-message').onclick=()=>this.scrollBottom();$('#messages').onscroll=()=>{if(this.atBottom())$('#latest-message').hidden=true;};
  document.querySelectorAll('.chat-tabs [aria-disabled=true]').forEach(b=>b.onclick=()=>this.system(`${b.textContent} chat is unavailable in this local session.`));
  document.querySelectorAll('[data-menu-tab]').forEach(b=>b.onclick=()=>this.selectMenuTab(b.dataset.menuTab));
  $('#reset').onclick=()=>{$('#reset-overlay').hidden=false;$('#cancel-reset').focus();};$('#cancel-reset').onclick=()=>this.cancelReset();$('#confirm-reset').onclick=()=>{actions.reset();$('#reset-overlay').hidden=true;this.closeMenu();};
  $('#allow-lock').onchange=()=>{this.allowLock=$('#allow-lock').checked;if(!this.allowLock)actions.setShiftLock(false);};
  $('#sensitivity').oninput=()=>{const v=Number($('#sensitivity').value);$('#sensitivity-value').value=v.toFixed(1);actions.setSensitivity(v);};
  document.addEventListener('keydown',e=>this.keyboard(e),true);
  this.system('Local chat · only Player1 is here.');this.system('👋 Say hi! Press / to chat.');
 }
 get inputBlocked(){return this.menuOpen||!$('#reset-overlay').hidden||document.activeElement?.matches('input,textarea,select,[contenteditable=true]');}
 keyboard(e){
  if(e.code==='Escape'){e.preventDefault();e.stopImmediatePropagation();if(!$('#reset-overlay').hidden)this.cancelReset();else if(document.activeElement===$('#chat-input'))$('#chat-input').blur();else if(this.menuOpen)this.closeMenu();else this.openMenu();return;}
  if(e.code==='Slash'&&!this.inputBlocked){e.preventDefault();e.stopImmediatePropagation();this.focusChat();return;}
  if(e.code==='Tab'&&this.menuOpen){const container=$('#reset-overlay').hidden?$('#menu-dialog'):$('#reset-overlay');const buttons=[...container.querySelectorAll('button,input,select,[tabindex="0"]')].filter(b=>b.getClientRects().length&&!b.disabled),first=buttons[0],last=buttons.at(-1);if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}}
 }
 openMenu(){this.menuOpen=true;$('#menu-overlay').hidden=false;$('#roblox-menu').setAttribute('aria-expanded','true');this.actions.clearInput();this.actions.releasePointer();$('#menu-dialog').focus();}
 closeMenu(){this.menuOpen=false;$('#menu-overlay').hidden=true;$('#reset-overlay').hidden=true;$('#roblox-menu').setAttribute('aria-expanded','false');document.activeElement?.blur();this.actions.clearInput();}
 cancelReset(){$('#reset-overlay').hidden=true;$('#reset').focus();}
 selectMenuTab(name){for(const n of ['people','settings','help','animations'])$(`#${n}-page`).hidden=n!==name;document.querySelectorAll('[data-menu-tab]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.menuTab===name)));}
 toggleChat(){const panel=$('#chat-panel');panel.hidden=!panel.hidden;$('#chat-toggle').setAttribute('aria-expanded',String(!panel.hidden));if(panel.hidden)$('#chat-input').blur();document.activeElement?.blur();}
 focusChat(){$('#chat-panel').hidden=false;$('#chat-toggle').setAttribute('aria-expanded','true');$('#chat-input').focus();this.actions.clearInput();}
 system(text){this.append({kind:'system',text});}
 submit(text){const bounded=text.slice(0,this.fidelity.chat.maxMessageCharacters);if(bounded.startsWith('/')){const m=bounded.match(/^\/(?:e|emote)\s+(\w+)\s*$/i);if(m){const result=this.actions.emote(m[1].toLowerCase());if(result!==true)this.system(result);return;}if(bounded==='/help'){this.system('Emotes: /e wave, point, dance, dance1, dance2, dance3, laugh, cheer.');return;}this.system('Unknown command. Try /help.');return;}
  this.append({kind:'player',username:'Player1',text:bounded});this.bubbles.push({text:bounded,expires:this.elapsed+this.fidelity.chat.runtimeConfiguration.BubbleChatConfiguration.BubbleDuration});this.bubbles=this.bubbles.slice(-this.fidelity.chat.runtimeConfiguration.BubbleChatConfiguration.MaxBubbles);
 }
 atBottom(){const log=$('#messages');return log.scrollHeight-log.scrollTop-log.clientHeight<32;}
 scrollBottom(){const log=$('#messages');log.scrollTop=log.scrollHeight;$('#latest-message').hidden=true;}
 append(message){const follow=this.atBottom();this.messages.push({...message,time:this.elapsed});this.messages=this.messages.slice(-this.fidelity.chat.historyLimit);this.renderMessages(follow);if(!follow)$('#latest-message').hidden=false;}
 renderMessages(follow){const log=$('#messages'),scroll=log.scrollTop;log.replaceChildren();for(const m of this.messages){const row=document.createElement('div');row.className=`message ${m.kind}`;if(m.kind==='player'){const name=document.createElement('span');name.className='name';name.textContent=`${m.username}: `;row.append(name);}row.append(document.createTextNode(m.text));log.append(row);}if(follow)this.scrollBottom();else log.scrollTop=scroll;}
 update(dt,game){this.elapsed+=dt;this.bubbles=this.bubbles.filter(b=>b.expires>this.elapsed);const {avatar,camera,player,view}=game,cfg=this.fidelity.chat.runtimeConfiguration.BubbleChatConfiguration;
  avatar.updateMatrixWorld(true);const head=avatar.getObjectByName('Head'),box=new THREE.Box3().setFromObject(head),anchor=new THREE.Vector3((box.min.x+box.max.x)/2,box.max.y+cfg.VerticalStudsOffset,(box.min.z+box.max.z)/2),distance=camera.position.distanceTo(anchor),forward=new THREE.Vector3();camera.getWorldDirection(forward);const inFront=anchor.clone().sub(camera.position).dot(forward)>0,p=anchor.clone().project(camera);
  this.bubbleStack.hidden=!this.bubbles.length||!inFront||distance>cfg.MaxDistance||player.health<=0||view.firstPerson||p.z>1;
  this.bubbleStack.style.left=`${(p.x*.5+.5)*innerWidth}px`;this.bubbleStack.style.top=`${(-p.y*.5+.5)*innerHeight-18}px`;this.bubbleStack.replaceChildren();
  for(const bubble of distance>cfg.MinimizeDistance?[{text:'•••'}]:this.bubbles){const node=document.createElement('div');node.className='bubble';node.textContent=bubble.text;this.bubbleStack.append(node);}
 }
}

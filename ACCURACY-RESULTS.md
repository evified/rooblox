---
tags: [rooblox, implementation, evidence, ui, local-chat]
date: 2026-10-13
status: implemented-and-tested-locally-publication-blocked
---

# Rooblox accuracy implementation results

Related plan: [[Projects/Rooblox - Accuracy implementation plan]]. Project: [[Projects/Rooblox]]. This is the continuation ledger for the five-area, twenty-five-subsection plan, saved so future context can recover both source decisions and actual results.

## Outcome

The local implementation is complete for the flat baseplate scope and has passed browser QA. It adds measured gradual body turning and physical movement response, current Studio camera constants/source math, source animation state handling, the screenshot-based topbar and menu, and functioning local text chat as **Player1**. No multiplayer is implemented. The existing published Site has not been updated: its connector repeatedly returns `Sites project not found` for the retained ID. The original Site ID/audience was preserved and no replacement was created.

## Implementation matrix

| Plan item | Topic | Outcome |
| --- | --- | --- |
| 1.1 | Input basis / normalized speed | Implemented; settled straight/diagonal16; camera-relative input |
| 1.2 | Ground start / braking | Implemented; six phase-aligned traces verified |
| 1.3 | Gradual body yaw | Implemented measured fit; shortest arc and frame-rate checks |
| 1.4 | Jump / held jump / gravity / landing | Implemented ballistic fit to repeated native jump; hold repeats |
| 1.5 | Air control / death / respawn / focus | Implemented measured143 horizontal authority, -500 destruction,3s respawn |
| 2.1 | Subject / default orbit / limits | Source root+1.5,12.5 distance,15° angle,±80°,70FOV |
| 2.2 | Mouse / touch / focus | Source unequal sensitivity bindings; right drag; pointer lock on gesture |
| 2.3 | Zoom curve / spring / ground collision | Source0.5 curve and4.5Hz analytic spring; ground-box ray |
| 2.4 | Shift lock / first person / transparency | Source1.75 offset; camera-relative facing; source fade curve |
| 2.5 | Camera lifecycle / responsive / diagnostics | Reset, resize, finite catch-up, Copy settings |
| 3.1 | Direct-port protection | GLB/PNG/clip bytes unchanged; corner and pose checks pass |
| 3.2 | Velocity-driven locomotion | Source speed/14.5, idle weights, no per-tick restart |
| 3.3 | Jump / fall / landing timing | Source0.3 hold /0.3 fall transition; no invented landing clip |
| 3.4 | Emotes / preview suite | /e and /emote standing-only source clips;25 menu options |
| 3.5 | World / shading / test separation | Original plate/sun; shader approximation explicit; tester in menu |
| 4.1 | Roblox + chat pill | Screenshot-derived SVG geometry; source BuilderSans; functional buttons |
| 4.2 | Menu / Player1 roster | Single local player, Resume/Reset confirmation and focused tabs |
| 4.3 | Settings | Sensitivity, lock option, clipboard tied to actual behavior |
| 4.4 | Reference chat layout | Exact594×368 rectangle at(10,81); responsive clamping |
| 4.5 | Layering / keyboard / touch | DOM layer/focus separation; no typing movement; mobile tested |
| 5.1 | Message model | Local Player1, text/time/channel, bounded in-memory history |
| 5.2 | Keyboard chat | Slash focus, Enter send, Escape blur, IME guard, input cleanup |
| 5.3 | History / tabs / notices | Scroll retention tested; Global/Friends explicitly unavailable |
| 5.4 | Bubbles | Source15s/max3/distance100/minimize40; follows actual head |
| 5.5 | Commands / no transport | Allowlisted emotes/help, literal text, zero external sends/WebSockets |

## Evidence and measurement refinement

The first capture used Heartbeat timestamps. It supported gradual rotation, a fast ground response, slower airborne reversal, and repeated native root jump peak7.528898477554321. The first velocity interpolation reproduced sampled velocities but had0.07810-stud excess braking displacement. That concern prompted a **second phase-aligned experiment**, not an aesthetic parameter guess.

The final experiment writes Humanoid:Move at PreSimulation and samples root position/velocity at PostSimulation while accumulating deltaTimeSim. It captures start_forward, stop_forward, turn_90, stop_left, turn_diagonal, and stop_diagonal. The first frame includes command scheduling latency; comparison aligns to the first active frame and records that delay separately.

Ground response is modeled at 0.008333333333333333 seconds. From two substeps per active frame, measured residual velocity gives retention=sqrt(secondResidual/firstResidual), velocity gain=(1-retention)/substep, and initial capped acceleration=(16-firstResidual)/(2×substep). This yields:

- Fitted velocity gain: 103.125000532/s.
- Fitted acceleration cap: 741.63599968 studs/s².
- Semi-implicit velocity/displacement updates at1/120s reproduce native per-frame displacement and velocity. These are inferred **for the selected native R6 rig on this baseplate**, not documented universal engine properties or a complete Humanoid solver.
- Maximum position discrepancy across six native ground traces: 0.000243351607526 studs.
- Maximum velocity discrepancy: 1.15515798494e-06 studs/s.
- Native post-active-release stop distance: 0.117115020752; browser: 0.11712198474; difference: 6.96398842059e-06 studs.

Gradual rotation remains an exponential shortest-arc fit at8.77/s. The native+90° comparison is 0.457114632° RMS / 2.50491986° max after0.0194s plugin command-pipeline alignment. Browser input does not deliberately add that plugin-specific delay. At the first1/60s fixture, body rotation is about 12.239° toward90°, then converges progressively. The underlying native angular-force solver is not fully reproduced.

Jump launch is fitted from repeated native vertical trajectory, yielding 54.3796037261 studs/s. This differs from the earlier nominal sqrt(2gh) shortcut. Nominal JumpHeight remains7.199999809265137; native solver peak is7.528898477554321; browser peak is 7.53557864007, a 0.00668016252017-stud difference. Gravity remains196.1999969482422. Held Space repeats after landing. Airborne horizontal authority is fitted at 143.000004888 studs/s².

## Camera evidence and behavior

Current Studio BaseCamera, ClassicCamera, ZoomController, MouseLockController, CameraInput, TransparencyController, ControlModule/ActionController sources were captured, with SHA-256 hashes in fidelity-config.json. Capturing the actual package avoids trusting stale script-header dates or old forum snippets.

Source values applied:12.5 default distance,15° initial pitch,±80° pitch bounds, R6 subject1.5 studs above normalized root (feet+4.5), FOV70, zoom0.5–128, first-person threshold1, shift-lock offset1.75, zoom curve0.5, critically damped zoom spring4.5Hz, mouse scales0.008727/0.00672, source touch bindings, default measured sensitivity1, and source transparency curve/rate2.8.

Mouse pans with right drag; shift lock requests pointer lock from a user gesture. Pointer-lock refusal leaves right-drag/click recovery available. Browser wheel pixels-to-step conversion is explicitly an adapter choice. Camera ground occlusion raycasts the actual baseplate; it is not the complete Roblox Popper near-plane algorithm. Reset releases pointer lock and clears old motion/camera velocities; sensitivity preference persists.

## UI and chat implementation

The attached screenshot is authoritative for the requested pill/icon/chat variant. Roblox and chat SVGs reproduce the supplied shapes; they are not claimed to be exported CoreGui assets. The native font files BuilderSans Medium/Bold/Regular were copied unchanged from the installed Studio runtime. Runtime chat configuration supplies colors, typography, and bubble settings. Responsive size adaptations and the menu shell are engineering implementations, not measured copies of every Roblox menu screen.

The desktop reference chat rectangle is exactly x10/y81/width594/height368. Here/Global/Friends headers, selected underline, translucent message body, dark footer, input, microphone and lightning-style affordances follow the screenshot. Only Here works locally. Global/Friends produce a clear local-unavailable notice; voice and summaries are disabled rather than pretending they transmit or summarize anything.

Menu contains People (onlyPlayer1), Settings (sensitivity/shift-lock/Copy settings), Help, and Animation test. Reset uses a cancel/confirm dialog. Old developer overlays are removed from default gameplay. Character physics continues while UI focuses input; motion commands clear so typing cannot walk/jump/orbit the avatar.

Chat uses Player1, plain safe text, Unicode/emoji wrapping, Enter submit, Slash focus, Escape blur, draft retention, IME guard, manual-scroll retention/new-message affordance, and bounded200-message history with200-character local policy. Those bounds are engineering policies, not Roblox constants. History stays through character reset but is not persisted after reload. No WebSocket, remote-send endpoint, voice permission, friend lookup, or multiplayer transport was added.

Bubble settings from native configuration:15s duration, max3, max distance100, minimize distance40, text20, background RGB250/transparency0.1, and head-based projected placement. Bubbles expire using wall elapsed time, hide behind camera/dead/first person, and follow native animated head bounds. The0-padding/arrow styling is a reference adaptation.

Supported commands: /e or /emote wave, point, dance (random default set), dance1/2/3, laugh, cheer; /help gives local help. Emotes require standing, movement interrupts, and one-shots return to idle. Unsupported command text does not execute code. All23 original native clips remain; R6 run still shares walk and there is no separate source swim clip.

## Validation results

- Straight/diagonal settled speed16; all30/60/120/240fps direction/displacement/rotation fixtures agree.
- Camera zoom spring at30/60/120fps converges to the same19.75-stud goal fixture; focus target is feet+4.5. Pitch, first person, shoulder mode, pointer input and right-drag sensitivity checked.
- All3,006 animated joint keyframe transforms still have zero matrix difference. All25 menu options exercised. The23 clips and GLB are byte-identical to prior GitHub source.
- OBJ/GLB verification still checks all7,884 corners and the unchanged PNG. Texture SHA-256 c515a121ae42a4d233cc739230db900dbc597421c4050230c3cff8b7f4e11782.
- Chat Player1/markup literal rendering, keyboard isolation, source emotes, Escape, menu/roster/reset/settings, clipboard, bubble cap/expiry/distance/behind-camera, manual history scroll, death/respawn, mobile controls/layout all passed.
- Browser page errors: []. External HTTP requests during gameplay QA: []. WebSockets: [].
- Native source still exists with anchored display root; temporary measurement model removed; owned Studio playtests stopped.

## Files and restart points

- Canonical source: `C:/Users/larp/Downloads/bacon-studio-port`.
- Local static build: `C:/Users/larp/Downloads/rooblox-accuracy-preview`.
- Local preview used `http://127.0.0.1:8766/` during QA. It is a temporary local server, not a new hosted deployment.
- GitHub checkout for publishing attempt: `C:/Users/larp/Downloads/rooblox-github-accuracy`; cloned verified existing main at b3b82ea10461706edf1705f7b5bf85397e56d869.
- Existing Site checkout remains `C:/Users/larp/Downloads/rooblox-baseplate`, with original `.openai/hosting.json` untouched while connector access is unavailable.
- Code: motion-controller.js, camera-controller.js, local-ui.js, game.js, ui.css, index.html; native animation player gained correct non-looping hold/preview handling.
- Configuration: assets/fidelity-config.json with source hashes, derivations, scope, UI data, and browser adapter choices.
- Raw evidence: source/movement-measurements.json, movement-repeat.json, physics-phases.json, runtime-evidence.json, input-evidence.json, core-ui.json, runtime-scripts/.
- Tools: capture-runtime-evidence.luau, capture-inputs.luau, inspect-live-scripts.luau, measure-movement.luau, measure-physics-phases.luau, analyze-movement.py, build-fidelity-config.py, verify-accuracy.py, prepare-game.py.
- Reports/screenshots: audit/accuracy-verification.json, movement-calibration.json, jump-calibration.json, accuracy-desktop.png, accuracy-chat.png, accuracy-reference-size.png, accuracy-mobile.png.

For local reproduction, run `python tools/prepare-game.py --output <build-directory>`, then serve that directory with `python -m http.server 8766 --bind 127.0.0.1` and open the local URL. `python tools/verify-accuracy.py` expects that local preview. The installed runtime Python used here is `C:/Users/larp/AppData/Local/Programs/Python/Python312/python.exe` with NumPy/Pillow/Playwright available.

## Remaining scope and honest accuracy limits

The full private Roblox renderer, angular-force solver, full Popper, R15, terrain/obstacles/moving-platform physics, real account chat filtering/moderation, voice, and multiplayer are still outside this flat/local phase. Menu screen styling is Roblox-inspired; only the provided topbar/chat layout has screenshot measurements. Source settings and fitted constants must not be generalized to every avatar. Original shader/lighting differences remain. Do not label the whole game pixel- or engine-identical because individual data/trace tests pass.

## Publication state

The connected Sites service returned NOT_FOUND/project_not_found for `appgprj_6aced3ce72488191bbc82152b8aca883` on lookup and credential request. The same ID was retried after implementation and remained inaccessible. Existing published URL remains `https://rooblox-bacon-baseplate.sturdygrebe2.chatgpt.site/`, but these new changes are not verified on that URL. No replacement Site or audience change was attempted. GitHub connector was absent; a normal Git checkout was prepared for a noninteractive push using existing local credential support. Record the actual push outcome below rather than assume success.

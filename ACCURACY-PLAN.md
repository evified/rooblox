---
tags: [rooblox, plan, fidelity, movement, camera, ui, chat]
date: 2026-10-13
status: implemented-and-tested-locally-publication-blocked
---

# Rooblox accuracy implementation plan

Related: [[Projects/Rooblox]], [[Reference/Roblox player defaults - 2026-10-13]], [[Daily/2026-10-13 - Roblox Studio and browser remake]].

## Objective and completion contract

Improve the existing browser remake through five areas, with five concrete subsections per area. This phase implements those subsections in the existing flat baseplate scope, rather than merely proposing a roadmap. The avatar and animation data remain directly ported from Studio. Username is **Player1**. Chat is local only; there is no functional multiplayer, server messaging, friend graph, microphone transmission, or Roblox account authentication.

The user specifically called out instant facing changes: a short A/D input should rotate the character partway toward the target, then continue while held. We will separately model movement direction, horizontal velocity, body orientation, and camera orientation. None of them should be conflated with an immediate rotation assignment.

Evidence is collected before implementation. Every Roblox-specific numerical constant must name an actual Studio property, a captured current controller source line, or a measured trace. Fits to traces are labeled fits, not undocumented universal engine constants. Layout measurements from the supplied screenshot are allowed for the explicitly requested UI reference. Engineering choices (browser event mapping, bounded history, responsive placement, accessibility) are distinguished from Roblox defaults. Outdated community snippets will not supply behavior values.

### Implementation-wide evidence hierarchy

1. The actual selected Place1 and native R6 BaconHair source, including current live controller modules.
2. Current Roblox Creator Hub documentation, checked during this task.
3. The user-supplied current screenshot, for the requested topbar/chat appearance.
4. Public forum material only if current, corroborated, and consistent with the above. No forum constants were needed; authoritative Studio source and measurement were available.
5. Unmeasured behavior is explicitly deferred or described as an approximation; do not invent a default and imply it is verified.

## Evidence already collected

- Engine 0.742.0.7421053, Studio solo playtest of Place1, temporary native R6 clone with WalkSpeed=16 and the place's UseJumpPower=false/JumpHeight=7.199999809265137.
- Heartbeat traces: turns of +45°, +90°, 180°, -90°; forward and diagonal acceleration; release/braking; stationary jump; reversal in midair. A repeat capture checks stability. The temporary clone is removed and the source character is not changed.
- A 90° turn's early observed headings: 0°, 10.831°, 21.489°, 30.760°, 38.778°. The result is gradual. The 45° trace has the same normalized response.
- Ground velocities rise to approximately 12.3606, 15.9280, 15.9986, 16 studs/s across early observed physics frames. On release, 16 falls to 3.6394, 0.07197, 0.001423. Initial samples can include command/Heartbeat scheduling latency; retain raw timestamps.
- The fitted ground rotation response rate is 8.77/s with observed pipeline delay around 0.0194 s. Fit error over ±90°/45° calibration is about 0.284° RMS. Held-out 180° trial error is about 1.21° RMS / 4.27° maximum. The first-order browser fit is not a full angular-force solver.
- Midair velocity reversals imply around 143 studs/s² horizontal authority in this measured rig. Refit using physical frame velocity differences and repeat evidence before finalizing.
- The actual root jump peak was around 7.529 studs, differing from the nominal 7.2 property. Determine the measured launch velocity/solver integration, preserve both nominal property and measured effect, and do not silently assume sqrt(2gh) reproduces the native solver exactly.
- Captured source modules: BaseCamera, ClassicCamera, ZoomController, MouseLockController, CameraInput, ControlModule, PlayerModule, ActionController, TransparencyController, CameraUtils, DynamicThumbstick, TouchJump. Preserve the sources and hashes with the plan.
- Source camera: default distance 12.5 studs; initial downward angle 15°; pitch limit ±80°; first-person threshold 1 stud; R6 subject offset 1.5 studs above root; shoulder offset (1.75,0,0); zoom spring 4.5 Hz; zoom curve factor 0.5; camera mouse bindings (0.008727,0.00672), touch bindings (0.01745,0.01152), measured user MouseSensitivity=1.
- Current chat configuration: window RGB 25/27/29 with 0.3 transparency, input same RGB with 0.2 transparency; text 18 in this place; BuilderSans Medium; placeholder RGB178; channel-tab text18/bold; inactive RGB175; selected white. Bubble duration15s, max3, max distance100, minimize40, text20, background RGB250/transparency0.1.
- Default Studio channel tabs are disabled; the screenshot's Here/Global/Friends tabs are a requested reference variant, not a universal default. Their local-only behavior must be clear.
- Screenshot: topbar pill at roughly x14,y18, width120,height55; chat x10,y81,width595,height368; tab strip to y130; message body to y354; input footer thereafter. This image is a crop, so these are reference crop pixels, not whole-screen percentages. Match appearance and keep responsive clamping separate.

## Area 1 — movement and physical response

### 1.1 Input direction, camera basis, and speed

- **Existing defect:** direct displacement at 16 studs/s begins instantly; body yaw and movement are coupled; no physical velocity state.
- **Evidence:** captured ControlModule/ActionController plus actual WalkSpeed and direction trials.
- **Implementation:** maintain local input X/Z separately; combine WASD and arrow keys; opposite directions cancel; normalize diagonal vectors; rotate input by the horizontal camera yaw, not character yaw; preserve analog magnitude for touch.
- **Data:** input vector, target velocity, current horizontal velocity, grounded state, timestamps. Use a fixed simulation step and elapsed-seconds units.
- **Acceptance:** settled straight and diagonal speed=16 within float tolerance; opposite keys produce zero target; a rotated camera changes world direction correctly; movement still works after interacting with UI.
- **Regression:** source avatar transform scale remains1; no sprint or unexplained speed multiplier is added.

### 1.2 Ground acceleration and braking

- **Existing defect:** motion starts/stops immediately, unlike captured Humanoid velocity traces.
- **Evidence:** start/release samples from the native clone and repeated capture; sample intervals and command delay are recorded.
- **Implementation:** derive a monotonic response from measured velocity progress and use it to approach changing target velocity; retain release response separately if the data supports different timing. Avoid hand-selected aesthetic acceleration values.
- **Fit handling:** keep raw traces, fitting method, derived parameters, RMS/max errors, and fit scope in a calibration JSON. Do not generalize this to every avatar/material/framerate.
- **Acceptance:** run deterministic input schedules in the browser and compare velocity/distance against native samples; report tolerance and actual residual. Releasing a key produces brief braking rather than continuous drift.
- **Boundary:** no terrain friction/material matrix or full Roblox force/constraint solver in this phase.

### 1.3 Gradual body rotation and wrap-around

- **Existing defect:** avatar.rotation.y is directly assigned atan2(input), so a short tap snaps immediately.
- **Evidence:** live AutoRotate traces; Creator Hub says turning is gradual; live rotation preferences are MovementRelative.
- **Implementation:** retain yaw, desired yaw, and response progress; compute shortest signed angular difference with atan2(sin(delta),cos(delta)); apply the measured response over time; preserve last facing when input is zero; no long-way spin at ±π.
- **Modes:** third-person follows movement direction; first-person/shift-lock follows camera facing. Do not make the camera orbit automatically just because the body rotates.
- **Acceptance:** after a short diagonal tap, heading is strictly between start and target; continued hold converges; ±179° crossing travels about2°, not358°; rotation is stable at30/60/120fps; compare +45°, ±90°, and180° profiles to native traces.
- **Accuracy declaration:** fitted exponential response is an approximation to measured R6 AutoRotate. Keep the measured error visible in the audit.

### 1.4 Jump launch, held jump, gravity, and landing

- **Evidence:** actual StarterPlayer setting uses jump height; source rig's display Humanoid uses jump power, so the two must remain distinguished. Native jump trace records height and vertical velocity.
- **Implementation:** use captured gravity196.1999969482422; derive effective height-mode launch from the measured native jump rather than a guessed extra impulse. Record nominal JumpHeight=7.2 separately from measured peak. Integrate vertical motion consistently with calibration.
- **Input:** Space/touch jump may remain held to request a new jump after landing; no midair double jump, arbitrary jump buffer, or coyote-time mechanic without source evidence.
- **Landing:** solve crossing of the flat baseplate upper plane; snap feet to that plane only while descending; reset vertical velocity; re-enable jump request after landing. Leaving the plate falls normally.
- **Acceptance:** native and browser launch/peak/airtime compared; same gravity at different frame rates; jump/fall/land sequence correct; holding jump produces repeat jumps, releasing prevents them; resetting while airborne clears motion.
- **Boundary:** step climbing, slopes, moving platforms, and complex collision geometry require future dedicated measurements.

### 1.5 Air control, fall destruction, respawn, and focus

- **Evidence:** native midair reverse trial, FallenPartsDestroyHeight=-500, RespawnTime=3, player health100.
- **Implementation:** horizontal velocity in air approaches commanded velocity with the measured lower authority; no instantaneous reversal. Continue gravity while chat/menu has focus, but clear gameplay input and disable character commands there.
- **Lifecycle:** falling below destruction threshold removes avatar from view, updates health, waits measured respawn delay, restores feet/camera/controller/idle state. Preserve chat history across respawn.
- **Focus:** keyup is always processed; window blur, visibility loss, and opening chat/menu clear held keys to avoid stuck movement. Browser UI buttons must not leave WASD inert indefinitely.
- **Acceptance:** midair reversal takes time; no movement while typing; Enter/Space in chat never jumps; held key followed by blur stops commands; death and3s respawn work; no leaked event handlers.
- **Boundary:** no damage/combat/regen system is invented for a test that only has falling death.

## Area 2 — camera and viewing modes

### 2.1 Subject framing, initial pose, and orbit limits

- Use captured BaseCamera R6 root subject offset1.5: normalized root at feet+3, so camera subject is feet+4.5, not the old feet+3 target.
- Start at captured distance12.5 and15° downward viewing angle; keep FOV70 and min/max0.5/128 from actual place.
- Clamp pitch to ±80°, sourced from BaseCamera. Calculate camera from world-space subject and orbit yaw/pitch, not the animated torso's pose.
- Maintain camera yaw independent of movement-relative body yaw; no arbitrary camera bob or follow smoothing is added as a claimed default.
- Test exact starting framing, extremes, head clearance, resize/aspect update, and no clipping at normal camera distance.

### 2.2 Mouse, touch, and focus-aware camera input

- Use current captured CameraRotationAction sensitivities and measured MouseSensitivity=1. Mouse X/Y have different scales; replace the old uniform0.006.
- Native pan binding uses right mouse; implement right-button drag, touch orbit, and pointer-locked relative movement in shift lock/first person. Keep browser pointer-lock requests tied to an actual user gesture.
- Browser wheel delta units differ from Roblox input; specify the adapter conversion and clamp bounds. This adapter is an engineering mapping, not a Roblox property.
- UI/chat interaction must not orbit or trigger pointer lock; release pointer lock when opening focused UI; recover after Escape/blur without trapping the pointer.
- Test mouse right-drag, trackpad wheel, touch orbit, pointer lock denial, and return from UI to gameplay.

### 2.3 Source zoom curve and constrained spring

- Port the relevant BaseCamera zoom in/out curve factor0.5 and ZoomController critically damped spring4.5Hz into browser math; retain min/max and snap-to-first-person boundary.
- Hold target zoom and actual zoom separately; derive analytic spring position/velocity from the captured formula to avoid frame-rate-dependent lerp.
- Prevent spring overshoot outside limits; reset velocity when clamped; do not use the old exponential wheel scaling as a claimed Roblox match.
- Keep camera collision limited to the present baseplate geometry; shorten the ray from subject to camera when it intersects the actual ground box. This is not the full Popper near-plane occlusion algorithm.
- Test curve fixtures, spring convergence30/60/120fps, extreme scroll, downward camera/ground intersection, and no camera below plate surface.

### 2.4 Shift lock and first-person character orientation

- Use captured shoulder offset1.75 studs; in camera-relative modes rotate body toward camera yaw even when strafing. Do not rotate body to strafe direction.
- Provide the user-facing shift-lock setting and shortcut; reflect availability from captured developer option. The measured native user's ControlMode was Classic, so this is a setting, not automatically forced on.
- First-person threshold1 and minimum0.5 come from source. Ensure local avatar disappears/fades when close, rather than letting the hair block the camera.
- Port source TransparencyController goal curve for distance<2 and max tween rate2.8/s, with the source behavior at near-full transparency preserved.
- Test strafe/body relationship, pointer cursor/lock state, first-person yaw, opacity progression, and recovery when zooming back out.

### 2.5 Camera reset, lifecycle, responsive view, and diagnostics

- Respawn/reset clears old spring velocity and controller targets; ordinary animation preview does not reset orbit.
- Resize preserves world-space subject, FOV70, zoom target, and aspect; avoid fixed canvas dimensions or DPR assumptions.
- Keep near plane small enough for0.5-stud mode, with far plane appropriate for2048-stud baseplate; these renderer distances are implementation choices, not exported camera engine defaults.
- Copy settings includes camera state, motion fit, and source provenance so future discrepancies can be reproduced without losing context.
- Test reset after zoom/shift lock, portrait/tall windows, visibility restoration, and bounded simulation time after a long background pause.

## Area 3 — avatar, animation, and world fidelity

### 3.1 Protect direct-port geometry, source scale, and appearance

- Keep current seven visible meshes/2,628 triangles, all7,884 source corners, the exact1024×512 atlas, native hair geometry, and C0/C1 hierarchy.
- Do not replace the model with generated primitives, resample clothing, apply the head's SpecialMesh scale twice, or reintroduce a floating face plane.
- Hair alone remains double-sided; preserve original normals/UVs. Use source hashes before/after implementation.
- Current game changes are controller/UI changes; they must not alter the asset source. Future rendering edits require matched-angle comparisons.
- Acceptance: independent OBJ/GLB round-trip check still passes and PNG hash remains unchanged.

### 3.2 Locomotion playback from actual velocity

- Preserve extracted23 unique native clips. The current R6 run set points to walk180426354, so no new sprint clip is invented.
- Drive walk playback speed with actual measured horizontal speed/rigScale/14.5, not just whether a key is pressed. Retain0.01 standing threshold from source Animate.
- Idle selection stays9:1; only choose a new idle variant at legitimate cycle boundaries. Avoid restarting walk each simulation tick.
- Smooth crossfades follow source transition timings; preview selection remains available through a separate test panel.
- Test walking acceleration/braking, diagonal speed, loop continuity, playback rates, and all keyframe transform fixtures.

### 3.3 Jump, fall, landing, and source timing

- Jump asset125750702, fall180436148, jump-animation hold0.3s, and source fall transition0.3s remain authoritative.
- Do not accidentally loop the jump's non-looping sequence before switching to fall. If a non-looping pose reaches its end, hold or follow the appropriate source end behavior rather than modulo by duration unconditionally.
- Grounded landing returns to actual idle/walk; fall delay is state-specific, not a hard-coded timer disconnected from jump.
- No authored landing animation is added: none exists in this R6 source set.
- Test interruption by reset/death, low-frame-rate jump, held jump, walking jumps, and fall off edge without a preceding jump.

### 3.4 Emotes, tool previews, sitting, and chat commands

- Use source /e and /emote hooks for wave, point, dance/dance1/2/3, laugh, cheer. Emotes only start while standing; movement cancels them.
- Random /e dance selects among source dance sets; exact selected preview variants stay pinned. One-shot emotes return to idle. Respect actual loop flags.
- Sit/climb/toolnone/toolslash/toollunge remain exact clips available in the test UI; they do not imply a ladder, water, weapon, or seat gameplay system.
- Tool-preview overrides and sparse channels must not reset unrelated joints incorrectly. Do not claim a full Roblox AnimationTrack priority stack if it is not implemented.
- Test source IDs, standing requirement, valid/invalid command, repeated calls, movement interruption, and one-shot completion.

### 3.5 Baseplate, lighting evidence, render quality, and debug separation

- Preserve source baseplate2048×16×2048 at(0,-8,0), Plastic RGB91. Existing floor grid is a browser visibility aid; mark it as a representation, not the exact Roblox shader.
- Preserve source sun direction; current outdoor light/shadow/color response remains an approximation. Do not change it just to mimic an unrelated online R15 reference.
- Retain anisotropy/AA/DPR support and self-contained vendored Three.js; new font/icon assets are source/screenshot-derived and documented.
- Move animation/testing statistics away from the default gameplay overlay so requested Roblox topbar/chat can be evaluated cleanly. Put the test panel behind a clear menu action.
- Validate close hair views, turn/jump poses, transparent first-person materials, and desktop/mobile rendering without touching asset data.

## Area 4 — Roblox-style interface and menus

### 4.1 Top-left Roblox and chat icons

- Use the supplied screenshot as current visual authority: dark rounded pill, white tilted square-hole Roblox mark, white chat bubble with two horizontal lines, wide enough hit areas, and correct relative spacing.
- Capture source topbar geometry/corner data for corroboration. Current core icons are not accessible as simple image URI assets; reproduce the supplied shapes as SVG and label this method honestly.
- Use source BuilderSans where the installed runtime supplies the font; preserve original file bytes. Keep a system fallback so an unavailable font never hides the UI.
- Roblox icon opens menu; chat icon toggles chat. Show hover/focus/pressed states and ARIA labels; do not send browser events through to the canvas.
- Test opening/closing, keyboard focus, pointer/touch targets, and the reference crop at its measured dimensions.

### 4.2 Menu shell, People tab, and local Player1 identity

- Build a Roblox-inspired menu with People/Settings/Help/Animation test sections and Resume/Reset actions appropriate to the local game.
- People shows onlyPlayer1, since no multiplayer is implemented. Do not fake online users, friend requests, report actions, server ping, or network connections.
- Escape opens menu or dismisses the current focused layer; menu opening clears movement and releases pointer lock. Physics continues, as a live Roblox client menu does not stop its server world.
- Menu/confirmation controls use DOM focus management and return focus to gameplay on resume; reset request should be deliberate via a local confirmation panel.
- Test Escape nesting, tab changes, resume, reset cancel/confirm, single-player roster, and no stuck keyboard focus.

### 4.3 Settings tied to implemented behavior

- Expose mouse sensitivity and shift-lock availability; initialize with measured native preference1 and actual developer option. FOV70 and source zoom limits are retained.
- Settings alter the implemented camera/control path immediately and are scoped to this browser. Do not present volume, graphics, moderation, or multiplayer settings as working if no system exists for them.
- Source user preference controls are not identical to every player's configuration; record measured defaults and distinguish user-selected values.
- Keep Copy settings and animation tester accessible in the menu. The copy payload contains source data and current calibration/state.
- Test sensitivity changes and restoration, shift-lock disabled/enabled, full clipboard output, accessibility labels, and menu focus suppression.

### 4.4 Screenshot chat layout and UI scale

- Reference the screenshot's topbar, Here/Global/Friends strip, selected underline, translucent history, dark footer, rounded input, and icon positions. Derive colors from captured Studio configuration plus screenshot observation, not a random theme.
- At the reference layout size aim for chat x10,y81,width594,height368, with tabs49px and footer about94px. Responsive clamping on smaller screens is an explicit engineering adaptation.
- Do not treat screenshot crop dimensions as the user's full viewport. Keep width bounded and scale text/control dimensions coherently.
- Here is functional local chat; Global/Friends are visibly disabled/non-networked with short explanation. Microphone and summary/lightning affordances may match reference appearance but are disabled because those services are not implemented.
- Test reference-size screenshot, large desktop,390px portrait, collapsed chat, input focus, and no overlapping critical jump controls.

### 4.5 UI layering, keyboard ownership, and touch

- Establish layer order: world/canvas, bubbles, topbar/chat, menu, reset dialog, loading/error. A hidden overlay must not intercept pointer input.
- Slash/Enter/chat focus belongs to chat; WASD/Space belongs to gameplay only when no textbox/menu owns input. Keyup cleanup is unconditional.
- Prevent HTML button focus from permanently disabling gameplay. Escape handling must avoid double processing across menu, input, and pointer-lock exit.
- Preserve touch locomotion/jump and right-side look gestures; chat/menu controls cancel relevant gameplay pointer streams. Responsive adaptation is documented rather than called exact CoreGui behavior.
- Test keyboard-only navigation, repeated toggles, pointer cancellation, window blur, portrait input keyboard, and screen-reader labels.

## Area 5 — functioning local text chat

### 5.1 Message model, Player1, and local delivery

- Each normal submission creates a local message with display namePlayer1, text, timestamp, and local channel identifier. Nothing is transmitted to another player or a server.
- Display user prefixes, message text, wrapped lines, and optional system notices with stable identity; use screenshot-derived prefix color unless native color generation can be captured and verified.
- Local messages are not Roblox TextChatService messages and do not receive Roblox account-based filtering/moderation. Do not display fake filter/AI-summary claims or fake remote delivery receipts.
- Keep messages in memory for this session (including across character reset); bounded history is an engineering memory limit, not a Roblox default. Refresh starts a new local session.
- Test empty/whitespace text, emoji/Unicode, multiline wrapping, oversized message policy, repeated submissions, and no network send requests.

### 5.2 Slash-to-focus, Enter-to-send, Escape-to-dismiss

- Source ChatInputBarConfiguration keyboard shortcut is Slash. Focusing opens chat and removes the focusing slash from normal typed text.
- Enter submits trimmed text; empty messages do not appear. Escape dismisses focus without submitting; chat toggle can hide panel while preserving current draft/history.
- IME composition must not submit prematurely; text input/wheel interaction must not jump, walk, rotate, or zoom the player.
- Clear held movement keys on focus, and always handle releases. After input blur, gameplay resumes on the next deliberate input.
- Test / focus, commands starting slash, Enter, Escape, composing text, long wrapped text, drafts, and heldW followed by focus.

### 5.3 History, scrolling, tabs, and announcements

- Message list appends safely, autoscrolls only if already near bottom, retains manual scroll position otherwise, and exposes a newest-message affordance if needed.
- Here is local history. Global and Friends have non-functional-network status; no invented data. Match reference tab styling without pretending accounts/channels exist.
- Initial system text explains local testing; replace screenshot's account summaries/other user's stand command with accurate local information. Do not copy a third-party player's message as actual local game output.
- Provide clear local system response for invalid commands and commands unavailable while moving. Clear/reset chat is distinct from resetting character.
- Test channel affordances, history cap, scroll behavior, resizing, line breaks, and safe rendering using textContent rather than innerHTML.

### 5.4 Bubble chat with captured configuration

- Project local messages above the native head with source max3 bubbles/duration15s; background/text/font size from captured BubbleChatConfiguration.
- Place by projecting actual animated head bounds to screen; avoid a guessed detached avatar marker. UI padding/triangle pointer are screenshot/engineering styling, recorded as such.
- Hide beyond source max distance100; minimize beyond40; hide behind the camera and when avatar is dead/in first-person. Expire with simulation/session elapsed time independent of render framerate.
- Keep safe text wrapping and no bubble clipping into chat/topbar overlays. Use exact source avatar coordinates; no geometry changes.
- Test expiry, stack cap, Unicode wrapping, dead/respawn, first-person, behind-camera, zoomed distance thresholds, and following animated head.

### 5.5 Commands, safety, and separation from future multiplayer

- Recognize verified source /e and /emote emotes; expose local help for supported commands. Do not evaluate JavaScript/Luau from chat or introduce arbitrary command execution.
- Avatar emotes are local source clips; other chat text stays plain text. Valid command parsing uses a fixed allowlist.
- No WebSocket, backend, microphone permission, voice transcription, friend API, account lookup, or remote player messaging is created in this phase.
- Keep transport separated conceptually from UI/message model so future multiplayer requires an explicit new task and real filtering/identity/server authority.
- Test script-like input displayed literally, invalid/emote commands, namePlayer1 throughout, absence of transport connections, and no per-frame network traffic.

## Implementation sequence and evidence gates

1. Finish live repeat capture, store raw source, fit/calibrate motion, and record uncertainty. Restore/stop owned playtest and prove no temporary clone remains.
2. Save this plan in Obsidian and a repository Markdown copy before editing gameplay source. Link from Home/project. Preserve original notes and earlier artifact snapshot.
3. Create fidelity config with source provenance and measured models. Refactor movement/camera math into readable modules; add deterministic trace replay QA.
4. Wire controller and animator using actual velocity/state. Protect original GLB/PNG/clip hashes and previous keyframe verification.
5. Build topbar/menu/chat UI from screenshot/source evidence; implementPlayer1 messages, keyboard ownership, source emotes, and bubble projection. Keep all networking absent.
6. Stage the local build and show preview; compare screenshot, movement curves, FPS invariance, controls, chat, clipboard, and mobile cases. Repair observed defects and rerun only relevant checks.
7. Save an implementation ledger and audit report in Obsidian, including files, measurements, residual errors, successes, unresolved features, and literal latest commit/deployment identifiers.
8. Publish the existing Site with its existing audience after verified source synchronization. Current connector reports `Sites project not found` for the retained ID; never replace/re-create it as a workaround. Preserve local source and explain limitation if access remains unavailable. GitHub connector is currently absent; do not claim a GitHub push without actual authorization/tool success.

## Verification matrix

| Area | Required evidence/check | Passing interpretation |
| --- | --- | --- |
| Direction/speed | Native movement capture + settled speed fixtures | Straight/diagonal16, camera basis correct, cancellation |
| Turning | Saved±90/45/180 curves; RMS/max residual | Gradual shortest arc with measured fit, residual disclosed |
| Ground response | Native accelerate/release versus browser replay | Profile reproduced within recorded tolerance; no fake universal constant |
| Jump/air | Native repeated jump/reverse trace | Nominal setting and measured peak separate; calibrated dynamics |
| Camera | Captured modules/bindings plus spring fixtures | Correct source offsets, angles, curve, spring, modes |
| Avatar | Existing round-trip/keyframe tests | Source geometry/texture/clip data unchanged |
| UI | Attached screenshot + current CoreGui/config | Reference layout, working icons/menu, responsive adaptation explicit |
| Chat | Local input/history/bubble/command tests | Player1, no gameplay input bleed, no network delivery |
| Persistence | Obsidian plan/evidence/ledger links and hashes | Context survives compaction; no credentials stored |
| Publication | Source helper + native deployment result | Only claim published when existing Site confirms success |

## Limitations deliberately not disguised

This phase improves a local flat baseplate and requested UI, not the whole Roblox platform. The core renderer, Humanoid force solver, full Popper camera, R15, terrain/obstacle physics, all menu systems, actual moderation, global/friends channels, voice, and multiplayer need separate work and evidence. Gradual rotation is a fit to real data, not possession of private engine internals. Screenshot-derived SVG/UI layout is an intentional reference reproduction; it is not a direct export of Roblox's CoreGui rendering system.

## Current authoritative sources

- [Humanoid AutoRotate and movement](https://create.roblox.com/docs/reference/engine/classes/Humanoid).
- [Current chat overview](https://create.roblox.com/docs/chat/in-experience-text-chat).
- [Chat window configuration](https://create.roblox.com/docs/chat/chat-window).
- [Current text chat custom frontend](https://create.roblox.com/docs/chat/examples/simple-custom-frontend-ui).
- Local `source/runtime-scripts/` contains the current modules captured from this exact Studio session; code header dates alone are not the evidence timestamp. The current runtime capture is the provenance.
- Local `source/movement-measurements.json`, `source/movement-repeat-response.json`, `source/input-evidence.json`, `source/runtime-evidence.json`, `source/core-ui.json`, and `audit/movement-calibration.json` contain measured data and parameters.
- User attachment: `codex-clipboard-86e0d00b-7d9e-4a7d-b5ea-848163164f11.png`, preserved with this task's Obsidian evidence.


## Implementation completion addendum

All25 subsections are implemented for the declared flat/local scope; see [[Projects/Rooblox - Accuracy implementation results]] for final checks, fidelity residuals, and publication state. A phase-aligned capture replaced the provisional velocity interpolation with a fitted1/120s ground solver; all six native ground traces agree within0.00025 studs. The intermediate0.07810-stud braking mismatch documented above is resolved. Rotation remains a measured fit and full platform fidelity remains outside this phase.

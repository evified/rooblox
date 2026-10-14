# Rooblox — Bacon baseplate and direct Studio avatar port

[Play the baseplate](https://rooblox-bacon-baseplate.sturdygrebe2.chatgpt.site) (owner-private Site).

Open `index.html` over HTTP for the playable baseplate. WASD/arrows move, Space jumps, dragging orbits, scrolling zooms, and Shift toggles mouse lock. Touch controls are included. The animation menu exposes every captured R6 default clip and variant. Copy settings includes the original comprehensive property capture as well as this character's actual settings.

The baseplate is 2048 × 16 × 2048 studs, matching the source place. Movement uses 16 studs/s, gravity 196.1999969482422 studs/s², and the place's height-based 7.199999809265137-stud jump setting. The display rig itself has UseJumpPower=true and an anchored root; the playable controller uses StarterPlayer.CharacterUseJumpPower=false and allows movement. Camera FOV=70, zoom=0.5–128, health=100, fall destruction height=-500, and respawn delay=3 seconds come from the capture.

`assets/bacon.glb` is packaged directly from the selected `Workspace.BaconHair` character's native Roblox Studio OBJ export. It replaces the earlier reconstructed model.

The source geometry, triangle order, vertex normals, UVs, and Studio-composited appearance are retained. The `1024 × 512` PNG is embedded byte-for-byte. No body primitives were rebuilt, no head shape was inferred, no face plane was added, and no clothing atlas was redrawn or resampled.

## Load in Three.js

```js
import { loadBacon } from './load-bacon.js';

const { avatar, joints } = await loadBacon(scene, './assets/bacon.glb');
```

Stable URLs can use a commit SHA in place of `main`:

```text
https://raw.githubusercontent.com/evified/rooblox/main/assets/bacon.glb
https://cdn.jsdelivr.net/gh/evified/rooblox@main/assets/bacon.glb
```

The asset has seven visible meshes and 2,628 triangles. One unit remains one Roblox stud; a single translation places the feet at the origin. Native Motor6D/Weld C0/C1 values and rest transforms are retained as rigid joint nodes. The selected source model is R6 with peach skin; online bacon references also show white-skin R15 variants, which are different avatars.

## Source and verification

- `source/bacon-studio.obj`, `.mtl`, and `Handle1_diff.png`: original Studio export.
- `source/BaconHair.rbxm`: selected character serialized through the Studio MCP.
- `source/studio-metadata.json`: source transforms, joint frames, material settings, and Lighting values.
- `tools/port-native.py`: deterministic OBJ-to-GLB packaging.
- `tools/verify-data.py`: independent verification of every triangle corner and the embedded image.
- `audit/round-trip-verification.json`: 7,884 checked triangle corners and the texture byte comparison.
- `QUALITY-AUDIT.md`: differences found, corrections made, and remaining renderer differences.
- `audit/comparison.png`: Studio, previous model, and direct port under aligned front cameras.
- `audit/views/`: unchanged Studio and browser screenshots for all five reference angles.

The maximum source-to-GLB position difference is under `6e-8` studs from float32 encoding. `assets/animations.json` contains all 23 actual KeyframeSequences extracted in Studio. `source/Animate.luau` is the unmodified source script, with its configured child overrides captured in `assets/game-config.json`. `animation-player.js` applies native poses through the original C0/C1 hierarchy; no motions are authored by hand. All captured poses use Linear easing and weight 1. Browser validation checks all 3,006 animated joint keyframe transforms with zero matrix difference. Walk playback follows the source script's speed/14.5 scaling; climbing follows speed/12, idle selection uses 9:1 weights, jump lasts 0.3 seconds before fall, and the relevant transition times are retained. Non-looping emotes return to idle; movement interrupts previews.

R6 uses the walking clip for run; its default script has no separate swim clip. The menu includes sit, climb, tools, and emotes for animation testing. This deliberately simple baseplate has no ladders, seats, water, or weapons. The browser implements a flat-ground controller, camera, and selected Animate behavior; it does not execute Roblox's proprietary Humanoid physics, PlayerModule, terrain, networking, collisions with arbitrary objects, or full state machine. Captured properties that have no effect on this flat test remain reference data, not silently implemented engine features. Roblox lighting and between-frame engine blending are not claimed pixel-identical.

Hair quality: only the hair material renders both sides of its open strand surfaces. All 1,562 native hair triangles remain unchanged. Maximum available anisotropic filtering, antialiasing, high-DPI rendering, and a 4096-pixel game shadow map improve display quality without resizing the character or altering the PNG. Three.js r180 is vendored with its license so the game makes no runtime CDN requests.

`audit/game-verification.json` records the actual pose, distance, jump, death/respawn, camera, menu, and control checks. `tools/verify-game.py` exercises the browser game. `tools/extract-game.py` captures source settings and animation sequences through the Studio MCP and preserves a complete existing sequence capture. `tools/prepare-game.py` stages the static Site build from this repository.

## Preview

Serve the repository over HTTP and open `viewer.html`:

```sh
python -m http.server 8080
```

Front, back, side, and three-quarter buttons use the same cameras as the captured Studio reference images. The texture-colors button displays the unchanged atlas without lighting. The lit preview approximates Studio's outdoor lighting; Roblox and Three.js use different lighting, shadow, antialiasing, and material pipelines, so rendered screenshots are not claimed to be identical pixels.

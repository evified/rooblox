# Rooblox — direct Studio avatar port

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

The maximum source-to-GLB position difference is under `6e-8` studs from float32 encoding. This is an appearance/geometry port with source joint frames, not a port of executable Humanoid, physics, Animate, or PlayerModule code. No animation clips are claimed.

## Preview

Serve the repository over HTTP and open `viewer.html`:

```sh
python -m http.server 8080
```

Front, back, side, and three-quarter buttons use the same cameras as the captured Studio reference images. The texture-colors button displays the unchanged atlas without lighting. The lit preview approximates Studio's outdoor lighting; Roblox and Three.js use different lighting, shadow, antialiasing, and material pipelines, so rendered screenshots are not claimed to be identical pixels.

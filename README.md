# Rooblox browser avatar

`assets/bacon.glb` is a self-contained browser version of `Workspace.BaconHair`, the classic R6 avatar placed in Roblox Studio.

The model includes the actual Pal Hair mesh and texture, blue motorcycle shirt, dark green jeans, and classic smile. Textures are embedded in the GLB; it makes no Roblox asset requests when loaded in the browser.

## Import into a Three.js game

```js
import { loadBacon } from './load-bacon.js';

const { avatar, joints } = await loadBacon(scene, './assets/bacon.glb');
avatar.position.set(0, 0, 0);
```

One model unit corresponds to one Roblox stud. Feet start at `y = 0`, the exported model uses glTF's Y-up coordinates, and the character faces `-Z`.

Named rigid joint nodes are `RootJoint`, `Neck`, `Left_Shoulder`, `Right_Shoulder`, `Left_Hip`, and `Right_Hip`. Body meshes are separate, so these pivots can drive R6 movement animations. This is a rest-pose model with rigid pivot nodes, not a skinned avatar or a copy of Roblox's animation scripts. Walking, jumping, collisions, Humanoid behavior, and camera control must be implemented by the browser game.

## Hosting URLs

GitHub Raw:

```text
https://raw.githubusercontent.com/evified/rooblox/main/assets/bacon.glb
```

GitHub through jsDelivr:

```text
https://cdn.jsdelivr.net/gh/evified/rooblox@main/assets/bacon.glb
```

For stable releases, replace `main` with the desired commit SHA. If the game is hosted with this repository's assets, prefer the relative `./assets/bacon.glb` URL. Remote hosting must permit browser requests through CORS and the game's content security policy.

## Preview locally

Serve this directory over HTTP, then open `viewer.html`:

```sh
python -m http.server 8080
```

The viewer uses Three.js 0.180.0 from jsDelivr. It is an asset preview, not the full browser game.

## Source assets and conversion

The character's part dimensions, rest pose, body colors, and Motor6D joint positions were read from the selected Studio model. Native R6 body primitives and classic clothing UV regions were rebuilt for glTF; the hair and rounded head use their original mesh geometry. The facial image is applied as a transparent decal.

Original Roblox assets:

- Pal Hair accessory: `63690008`
- Hair mesh: `83293901`; hair texture: `6858317867`
- Shirt: `144076358`; shirt texture: `144076357`
- Pants: `144076760`; pants texture: `144076759`
- Head mesh and smile: Roblox Studio's built-in content

These original assets belong to their respective creators. Conversion does not transfer ownership or grant a new license.

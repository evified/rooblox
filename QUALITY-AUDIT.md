# Bacon avatar fidelity audit

## Authority and comparison method

The selected `Workspace.BaconHair` in Studio is the authoritative avatar. Its native OBJ, MTL, and composited PNG are included. Five Studio screenshots were captured from front, back, left, right, and three-quarter cameras, then the browser asset was rendered at the same camera positions, targets, FOV, and 1290 × 726 resolution. The previous avatar is included in the front comparison under the same browser lighting and camera as the direct port.

The complete data comparison checks all 7,884 triangle corners, not just a silhouette or a handful of bounding boxes. Position, normal, and UV errors are reported per part. The entire embedded PNG is compared byte-for-byte with Studio's output.

Paired reference captures:

| View | Placed Studio character | Direct port in Three.js |
|---|---|---|
| Front | [Studio](audit/views/front-studio.png) | [Browser](audit/views/front-browser.png) |
| Back | [Studio](audit/views/back-studio.png) | [Browser](audit/views/back-browser.png) |
| Left | [Studio](audit/views/left-studio.png) | [Browser](audit/views/left-browser.png) |
| Right | [Studio](audit/views/right-studio.png) | [Browser](audit/views/right-browser.png) |
| Three-quarter | [Studio](audit/views/three-quarter-studio.png) | [Browser](audit/views/three-quarter-browser.png) |

## Identified errors and corrections

| Area | Earlier conversion | Direct port correction |
|---|---|---|
| Source method | Rebuilt from primitives, raw mesh assets, texture crops, and guessed face placement. | Native Studio OBJ export is the geometry and appearance source. |
| Head size | Applied an additional 1.25 scale to the built-in head mesh, making each head dimension about 25% too large. | Uses the rendered head mesh dimensions from Studio: approximately 1.19784 × 1.20240 × 1.19785 studs. |
| Head silhouette and neck overlap | Oversized head altered the jaw, side profile, hair-to-head proportions, and intersection with the torso. | Native source head vertices and its rest placement are preserved. |
| Face geometry | Added a separate two-triangle transparent plane in front of the head. | Face is already baked into Studio's native head atlas; the extra mesh is removed. |
| Face depth | The handmade plane was about 0.15 studs ahead of the native head's front surface. | No detached decal surface, incorrect plane shadows, or arbitrary offset. |
| Face size and mapping | A manually chosen rectangle stretched and positioned the face separately from Studio's compositor. | Native head UVs sample the exact Studio-baked face. |
| Body edge shape | Five bodies were plain 12-triangle cubes. | Each native body piece retains all 44 exported triangles, including the edge geometry. |
| Triangle count | 2,470 triangles, including a face plane absent from the source. | All 2,628 source triangles across seven visible meshes. |
| Normals and surface boundaries | Recomputed primitive normals and imported raw mesh normals rather than the actual exported per-corner normals. | Every native OBJ corner normal is copied and verified after GLB encoding. |
| Clothing UVs | Hand-assigned face rectangles and face orientation, rather than native UVs. | Exact source UVs, with only the standard OBJ/glTF V-origin conversion. |
| Clothing resolution and seams | Cropped and resized clothing into a new 792 × 660 atlas, introducing resampling and an independently assigned seam layout. | Original 1024 × 512 Studio atlas is embedded unchanged. |
| Body/skin/face composition | Composited separately by the conversion code. | Uses Studio's own complete baked appearance. |
| Hair appearance | Used a separately fetched raw hair texture and generic material settings. | Uses the hair region that Studio produced in the same native atlas as the character. Hair mesh remains all 1,562 source triangles. |
| Material tint | Body color, clothing, and hair were handled with independently chosen materials and separate image composition. | The complete Studio-baked appearance uses a white base-color multiplier, preserving its already-composited skin and accessory colors. |
| Joint structure | Added simplified translated pivot nodes without all original C0/C1 orientation and accessory weld information. | Carries actual Motor6D and AccessoryWeld frames and source rest transforms from Studio. |
| Camera evidence | Initial browser and Studio views were different cameras, projections, angles, and environments. | Five matched cameras are included; model-space data is independently compared. |
| Lighting evidence | Initial browser light direction, ambient balance, and brightness were arbitrary. | Uses Studio's captured sun direction and a calibrated outdoor-light approximation; remaining engine differences are explicit. |

## Reference images and avatar variants

The [Roblox-hosted avatar reference](https://www.roblox.com/fr/users/9102491440/profile) inspected during this audit shows the recognizable Pal Hair, blue motorcycle shirt, black jacket, and dark jeans, but has white skin and an R15 body with articulated hands and feet. That differs from the placed R6 character. It cannot be used to justify changing the source avatar's skin, limb shape, rig, or clothes while claiming a direct port.

Roblox's [MeshPart documentation](https://create.roblox.com/docs/reference/engine/classes/MeshPart) describes native Export Selection and its exported texture file. Studio's OBJ route exported the complete placed appearance. Its newer glTF route reported permission restrictions for the hair and omitted the classic appearance; that incomplete output was not used for the browser asset.

## Remaining rendering differences

The mesh and appearance data are direct and verified. The browser renderer is not Roblox's renderer. Remaining visible differences include hair highlight response, face shadows, environment reflections, outdoor color balance, shadow softness/filtering, floor and sky rendering, and edge antialiasing. The original Studio environment and its shader implementation are not contained in an OBJ or GLB.

The lit viewer was calibrated to improve the source comparison, but it does not claim identical screenshots down to the last rendered pixel. The exact pixel-level guarantee is for every byte of the exported PNG. The geometry/normal/UV guarantee is the measured float32 round-trip tolerance in `audit/round-trip-verification.json`. Texture-only viewing separates exported appearance from renderer lighting.

## Baseplate and animation update

The hair mesh has 1,022 open OBJ edges and 210 faces whose average exported normal points opposite their geometric face winding. Single-sided browser culling could discard strand surfaces at some angles. The GLB now gives the unchanged hair a separate double-sided material; other parts retain their original single-sided rendering. The image, UVs, normals, positions, and triangle counts are unchanged. This corrects a browser rendering issue without rebuilding hair. Anisotropy and high-DPI antialiasing improve sampling; native texture resolution is retained.

Studio's actual R6 Animate script and all 23 referenced animation assets are now captured. All 3,006 animated joint keyframes were compared in the browser against original C0 × Pose.CFrame matrices with zero matrix error. This validates source keyframe data and application, not a pixel-for-pixel comparison of Roblox and browser playback between frames.

The playable controller uses source walk speed, gravity, height-based jumping, camera FOV/zoom, fall destruction height, health, and respawn timing. The menu provides all default R6 motions, including the nine dance variants and two idle variants. R6's run shares the walk clip and there is no separate default R6 swim clip in this source. Climbing, sitting, and tool animations can be previewed on the flat baseplate; those environments/game systems are not present.

Browser physics is a flat-ground integration of the captured movement settings. Roblox's complete Humanoid solver, PlayerModule, multiplayer simulation, terrain, collision system, and all engine/service properties are not portable through a model export. The original comprehensive property capture is included by Copy settings as reference data. Full engine or rendered-pixel equivalence is not claimed.

## Accuracy follow-up

See `ACCURACY-PLAN.md` and `ACCURACY-RESULTS.md` for the subsequent five-area plan and implemented movement/camera/UI/chat changes. Additional phase-aligned Studio tests now calibrate a ground velocity-gain/cap model at 1/120s; six native ground traces match within 0.00025 studs of position and 0.000002 studs/s of velocity. Turning is gradual with a documented fit, source camera math/constants are applied, and local chat uses Player1. Geometry/PNG/animation bytes remain unchanged. The existing hosted Site is not yet updated because its connector returns project-not-found; the GitHub source and local/offline build contain the follow-up.

import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

/** Load the self-contained R6 avatar; one model unit equals one Roblox stud. */
export async function loadBacon(scene, url = './assets/bacon.glb') {
  const gltf = await new GLTFLoader().loadAsync(url);
  const avatar = gltf.scene;
  avatar.name = 'BaconHair';
  avatar.traverse((object) => {
    if (object.isMesh) {
      object.castShadow = true;
      object.receiveShadow = true;
    }
  });
  scene.add(avatar);
  return {
    avatar,
    joints: {
      root: avatar.getObjectByName('RootJoint'),
      neck: avatar.getObjectByName('Neck'),
      leftShoulder: avatar.getObjectByName('Left_Shoulder'),
      rightShoulder: avatar.getObjectByName('Right_Shoulder'),
      leftHip: avatar.getObjectByName('Left_Hip'),
      rightHip: avatar.getObjectByName('Right_Hip'),
    },
  };
}

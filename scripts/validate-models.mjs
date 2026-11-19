import { readFile } from 'node:fs/promises';
import assert from 'node:assert/strict';
import validator from 'gltf-validator';

let original;
for (const file of ['gordia-static.glb', 'gordia-mobile.glb']) {
  const data = await readFile(new URL('../models/' + file, import.meta.url));
  const gltf = JSON.parse(data.subarray(20, 20 + data.readUInt32LE(12)));
  const result = await validator.validateBytes(data, { uri: file });
  assert.equal(result.issues.numErrors + result.issues.numWarnings, 0, JSON.stringify(result.issues));
  const names = gltf.nodes.map(node => node.name).sort();
  const socket = gltf.nodes.find(node => node.name === 'WeaponSocket.R');
  assert.ok(socket?.children?.length >= 3, 'Missing independent weapon attachment');
  if (original) {
    assert.deepEqual(names, original, 'Part hierarchy lost during simplification');
    assert.ok(result.info.totalTriangleCount <= 45000);
  } else {
    original = names;
  }
  console.log(JSON.stringify({ file, bytes: data.length, nodes: names.length, meshes: gltf.meshes.length,
    triangles: result.info.totalTriangleCount, errors: result.issues.numErrors, warnings: result.issues.numWarnings }));
}

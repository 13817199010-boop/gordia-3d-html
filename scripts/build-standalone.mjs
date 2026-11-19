import { build } from 'vite';
import { mkdir, writeFile } from 'node:fs/promises';
import assert from 'node:assert/strict';

const result = await build({ build: { write: false, assetsInlineLimit: 4_000_000, modulePreload: false } });
const [{ output }] = [].concat(result);
const chunks = output.filter(file => file.type === 'chunk');
assert.equal(chunks.length, 1, 'The offline page requires one self-contained JS bundle');
const entry = output.find(file => file.fileName === 'index.html');
assert.ok(chunks[0].code.includes('base64,'), 'Missing embedded model data');
const html = entry.source.replace(/<script\b[^>]*\bsrc="[^"]+"[^>]*><\/script>/, () =>
  '<script type="module">' + chunks[0].code.replace(/<\/script/gi, '<\\/script') + '</script>');
assert.notEqual(html, entry.source, 'Vite entry script was not inlined');
await mkdir('preview', { recursive: true });
await writeFile('preview/gordia.html', html);

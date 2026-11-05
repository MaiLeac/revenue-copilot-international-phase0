const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'experiments', 'exp02-catalogue-qa-pilot', 'index.html'), 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
assert.ok(scripts.length, 'CatalogueQA script exists');

const elements = new Map();
function element(id) {
  if (!elements.has(id)) {
    elements.set(id, {
      style: {},
      listeners: {},
      addEventListener(event, handler) { this.listeners[event] = handler; },
      click() { this.listeners.click?.({ stopPropagation() {} }); },
      textContent: '',
      innerHTML: '',
      disabled: false,
      files: [],
    });
  }
  return elements.get(id);
}

let exported = '';
const alerts = [];
class FakeFileReader {
  readAsText(file) { this.onload({ target: { result: file.content } }); }
}
class FakeBlob {
  constructor(chunks) { this.content = chunks.join(''); }
}
const context = {
  document: {
    getElementById: element,
    createElement: () => ({ click() {} }),
  },
  window: { alert: message => alerts.push(message) },
  FileReader: FakeFileReader,
  Blob: FakeBlob,
  URL: { createObjectURL: blob => { exported = blob.content; return 'blob:fake'; } },
};
vm.runInNewContext(scripts.at(-1)[1], context);

function upload(content) {
  element('fileInput').files = [{ name: 'sample.csv', content }];
  element('fileInput').listeners.change({ target: element('fileInput') });
}

upload('Handle,Title,Variant SKU,Unit Cost,Variant Price\r\na,"One, two",SKU-A,3,2\r\nb,"Line\nBreak",SKU-A,4,5');
assert.equal(element('kpiTotalRows').textContent, 2, 'quoted newlines remain inside one record');
assert.equal(element('kpiDupSkus').textContent, 1, 'duplicate SKU is flagged');
assert.equal(element('downloadCleanBtn').disabled, true, 'unresolved duplicate blocks export');
assert.ok(element('tableBody').innerHTML.includes('One, two'));
assert.ok(!element('tableBody').innerHTML.includes('SKU-A-REV'), 'SKU is never invented');

upload('Handle,Title,Variant SKU,Unit Cost,Variant Price\r\na,"One, two",SKU-A,3,2\r\nb,"He said ""yes""\nthen left",SKU-B,4,5');
assert.equal(element('downloadCleanBtn').disabled, false);
element('downloadCleanBtn').click();
assert.ok(exported.includes('"One, two"'), 'comma is quoted on export');
assert.ok(exported.includes('"He said ""yes""\nthen left"'), 'quotes and newline round-trip');

upload('<img onerror=alert(1)>,Title,Variant SKU,Unit Cost,Variant Price\r\na,Safe,SKU-C,3,4');
assert.ok(element('tableHeaderRow').innerHTML.includes('&lt;img'), 'CSV headers cannot inject HTML');

upload('Handle,Title,Variant SKU\r\na,Broken');
assert.ok(alerts.at(-1).includes('expected 3'), 'uneven records are rejected instead of silently skipped');
console.log('CatalogueQA CSV parsing, export and safety checks passed');

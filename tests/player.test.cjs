const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const template = fs.readFileSync(path.join(__dirname, '../skills/serve-gif/assets/player.html'), 'utf8');
const script = template.match(/<script>\s*([\s\S]*?)<\/script>/)[1];

function player({loop = 0, reduced = false} = {}) {
  const timers = new Map();
  const events = {};
  const motionEvents = {};
  let nextId = 0;
  const elements = Object.fromEntries(['image', 'toggle', 'counter', 'status', 'frames'].map(name => [name, {
    textContent: '', attrs: {}, listeners: {},
    setAttribute(key, value) { this.attrs[key] = value; },
    addEventListener(key, fn) { this.listeners[key] = fn; }
  }]));
  elements.frames.textContent = JSON.stringify({loop, frames: [
    {src: 'frame-0', ms: 40}, {src: 'frame-1', ms: 100}, {src: 'frame-2', ms: 300}
  ]});
  const root = {isConnected: true, querySelector: selector => elements[selector.slice(6, -1)]};
  const document = {hidden: false, getElementById: () => root,
    addEventListener: (name, fn) => { events[name] = fn; }};
  const motion = {matches: reduced, addEventListener: (name, fn) => { motionEvents[name] = fn; }};
  vm.runInNewContext(script, {document, window: {matchMedia: () => motion}, Image: class {},
    setTimeout: (fn, ms) => { const id = ++nextId; timers.set(id, {fn, ms}); return id; },
    clearTimeout: id => timers.delete(id)});
  return {elements, timers, root, document, events, motion, motionEvents,
    click: () => elements.toggle.listeners.click(),
    tick: () => {
      const [id, timer] = [...timers][0];
      timers.delete(id); timer.fn(); return timer.ms;
    }};
}

test('cycles frames at their own delays and pauses/resumes', () => {
  const p = player();
  assert.equal(p.elements.image.src, 'frame-0');
  assert.equal(p.tick(), 40);
  assert.equal(p.elements.image.src, 'frame-1');
  assert.equal(p.tick(), 100);
  assert.equal(p.elements.image.src, 'frame-2');
  assert.equal(p.tick(), 300);
  assert.equal(p.elements.image.src, 'frame-0');
  p.click(); assert.equal(p.timers.size, 0);
  assert.equal(p.elements.toggle.attrs['aria-pressed'], 'false');
  p.click(); assert.equal(p.timers.size, 1);
});

test('finite loops finish on the last frame and can replay', () => {
  for (const [loop, ticks] of [[null, 3], [1, 6]]) {
    const p = player({loop});
    for (let index = 0; index < ticks; index++) p.tick();
    assert.equal(p.timers.size, 0);
    assert.equal(p.elements.image.src, 'frame-2');
    assert.equal(p.elements.toggle.textContent, 'Replay');
    p.click(); assert.equal(p.elements.image.src, 'frame-0');
    assert.equal(p.timers.size, 1);
  }
});

test('reduced motion prevents autoplay, still allowing an explicit play', () => {
  const p = player({reduced: true});
  assert.equal(p.timers.size, 0);
  p.click(); assert.equal(p.timers.size, 1);
  p.motionEvents.change(); assert.equal(p.timers.size, 0);
});

test('hidden or detached players stop scheduling frames', () => {
  const hidden = player();
  hidden.document.hidden = true; hidden.events.visibilitychange();
  assert.equal(hidden.timers.size, 0);
  const detached = player();
  detached.root.isConnected = false; detached.tick();
  assert.equal(detached.timers.size, 0);
});

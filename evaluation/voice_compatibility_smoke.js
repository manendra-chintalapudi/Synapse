/* Smoke-test the inline voice controller without microphone hardware or a real browser. */
const fs = require("fs");
const assert = require("assert");

const html = fs.readFileSync("frontend/chat.html", "utf8");
const start = html.indexOf("/* ---------------- speech-to-text");
const end = html.indexOf("/* ---------------- boot ---------------- */", start);
assert(start >= 0 && end > start, "voice controller block not found");
const voiceSource = html.slice(start, end);

class FakeClassList {
  constructor() { this.values = new Set(); }
  add(value) { this.values.add(value); }
  remove(value) { this.values.delete(value); }
  toggle(value, force) {
    const enabled = force === undefined ? !this.values.has(value) : Boolean(force);
    enabled ? this.values.add(value) : this.values.delete(value);
    return enabled;
  }
}

class FakeElement {
  constructor(id) {
    this.id = id;
    this.value = "";
    this.hidden = false;
    this.disabled = false;
    this.focused = false;
    this.listeners = {};
    this.children = Array.from({ length: 29 }, () => ({ style: { setProperty() {} } }));
    this.classList = new FakeClassList();
    this.style = { setProperty() {} };
  }
  addEventListener(type, handler) { this.listeners[type] = handler; }
  dispatchEvent(event) { this.listeners[event.type]?.(event); }
  setAttribute(name, value) { this[name] = value; }
  focus() { this.focused = true; }
  set innerHTML(value) { this._innerHTML = value; }
  get innerHTML() { return this._innerHTML || ""; }
}

class FakeRecognition {
  constructor() { this.continuous = true; this.interimResults = false; this.lang = ""; }
  start() {
    this.onstart?.();
    const result = [{ transcript: "show failure F1186" }];
    result.isFinal = true;
    this.onresult?.({ results: [result] });
  }
  stop() { this.onend?.(); }
}

function environment(withRecognition) {
  const ids = ["mic", "voiceLang", "voiceShell", "voicePanel", "voiceState", "voiceHint",
    "voiceTranscript", "voiceError", "voiceMic", "voiceSend", "voiceEq", "voiceFallback"];
  const elements = Object.fromEntries(ids.map(id => [id, new FakeElement(id)]));
  const qEl = new FakeElement("q");
  const document = {
    body: { classList: new FakeClassList() },
    getElementById: id => elements[id],
    addEventListener() {},
  };
  const window = {
    SpeechRecognition: withRecognition ? FakeRecognition : undefined,
    webkitSpeechRecognition: undefined,
    isSecureContext: true,
  };
  const navigator = {
    userAgent: "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X)",
    language: "en-US",
    languages: ["en-US"],
  };
  const localStorage = { getItem() { return "en-IN"; }, setItem() {} };
  return { elements, qEl, document, window, navigator, localStorage };
}

function run(withRecognition) {
  const env = environment(withRecognition);
  const execute = new Function(
    "window", "document", "navigator", "matchMedia", "localStorage", "qEl",
    "requestAnimationFrame", "cancelAnimationFrame", "performance", "setTimeout",
    "clearTimeout", "Event", "assert", `${voiceSource}
      openVoiceMode();
      if (${withRecognition}) {
        assert.strictEqual(recog.continuous, false, "mobile recognition must not use continuous mode");
        assert.strictEqual(recog.lang, "en-IN", "selected language must reach recognition");
        assert.strictEqual(voiceTranscript.value, "show failure F1186");
        assert.strictEqual(qEl.value, "show failure F1186");
        assert.strictEqual(voiceSend.disabled, false);
        toggleVoiceListening();
        assert.strictEqual(listening, false);
      } else {
        assert.strictEqual(voiceFallback.hidden, false);
        assert.strictEqual(voiceTranscript.focused, true);
        voiceTranscript.value = "keyboard dictated question";
        voiceTranscript.dispatchEvent(new Event("input"));
        assert.strictEqual(qEl.value, "keyboard dictated question");
        assert.strictEqual(voiceSend.disabled, false);
      }
      closeVoiceMode();
      return { transcript:qEl.value, fallback:!voiceFallback.hidden };
    `,
  );
  return execute(
    env.window, env.document, env.navigator, () => ({ matches: true }), env.localStorage, env.qEl,
    () => 1, () => {}, { now: () => 1000 }, () => 1, () => {},
    class Event { constructor(type) { this.type = type; } }, assert,
  );
}

console.log("mobile_native", run(true));
console.log("unsupported_fallback", run(false));
console.log("voice_compatibility_smoke_ok");

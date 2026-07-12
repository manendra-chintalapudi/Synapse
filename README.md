# Synapse
### Industrial Knowledge Intelligence — A Unified Asset & Operations Brain

## Voice input compatibility

Synapse uses the browser Web Speech API when available. Mobile/touch browsers use non-continuous
recognition with safe restarts, while desktop Chromium may use a separate audio meter for the
reactive visual. Browsers without Web Speech receive an editable transcript with device-keyboard
dictation support instead of a non-functional microphone state. Users can select automatic,
English (India/US/UK), or Hindi recognition.

Run the hardware-free compatibility smoke test with:

```bash
node evaluation/voice_compatibility_smoke.js
```


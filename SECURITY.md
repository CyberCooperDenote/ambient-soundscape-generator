# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | ✅        |
| 0.5.x   | ⚠️ security fixes only |
| < 0.5   | ❌        |

## Reporting a vulnerability

Email `security@ambient-soundscape-generator.dev` with:

- A description of the issue.
- Repro steps (config + prompt + device).
- Whether it requires local code execution, a crafted model file, or a
  malicious preset.

We aim to acknowledge within 72 hours and ship a patch within 14 days for
confirmed issues.

## Threat model

This is a **local desktop tool**. It does not phone home, does not upload
generated audio, and does not require a network connection after model
weights are downloaded.

Known surfaces we care about:

1. **Model file loading** — ONNX/GGUF weights from third parties are parsed
   by `models/registry.py`. We validate magic bytes and reject malformed
   headers, but a hostile model can still crash the process. Run untrusted
   models in a sandbox.
2. **Preset files** — YAML presets are loaded with `yaml.safe_load`. Do not
   contribute code that uses `yaml.load`.
3. **Plugin stage discovery** — stages registered via entry points run in
   the host process. Only install stage packages you trust.
4. **Virtual audio cable drivers** — the `drivers/virtual_cable.py` path
   writes to a named pipe. Ensure the pipe ACL is restricted to the current
   user.

## Out of scope

- Audio glitches caused by third-party ASIO drivers.
- GPU driver crashes during ONNX Runtime inference.
- Anything requiring an attacker who already has code execution as the user.
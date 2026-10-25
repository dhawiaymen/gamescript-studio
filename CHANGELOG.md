# Changelog

## 0.1.0 — Initial public release

### Available

See the README for supported functionality and deliberate limits. This version is an
early tool release, with no production certification or community adoption claim.

### Stabilization before release

- Normalize integer-valued JSON settings before editing; huge integers now produce validation errors.
- Protect unsaved work, add Save as and built-in examples, retain rule selection after edits.
- Bound and clean up preview folders; isolate the runtime from changes to its input configuration.

- Add regression coverage, authentic screenshots and reproducible synthetic workloads.
- Add contribution, conduct, troubleshooting and roadmap documents.
- Verify extracted Windows executables before attaching release assets; include checksums
  and dependency notices. Record actual CI evidence with each build.

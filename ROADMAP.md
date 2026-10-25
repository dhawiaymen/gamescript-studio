# GameScript Studio roadmap

This is a proposal list, not a delivery promise. Reliability and reproducible bugs take
priority over feature count. Discuss a concrete use case before starting large changes.

## Current release

- Normalize integer-valued JSON settings before editing; huge integers now produce validation errors.
- Protect unsaved work, add Save as and built-in examples, retain rule selection after edits.
- Bound and clean up preview folders; isolate the runtime from changes to its input configuration.

## Candidate contributions

- [ ] Keyboard shortcut help and focus-navigation checks.
- [ ] Sprite-image import with explicit export licensing and size limits.
- [ ] Additional mechanics only after concrete user examples.

## Feedback and evidence

For each accepted improvement record its issue, minimal reproduction, fix PR and test.
Ask early testers which task they tried, whether they completed it, their OS and the
first obstacle. Record distinct willing testers only with consent; do not identify
anonymous downloads as users. No telemetry is installed in the applications.

Track real stars/forks, external merged PRs, resolved user bugs and release asset download
counts with a dated GitHub snapshot. Raw asset downloads include possible repeats/automation
and are not unique users. Exclude maintainer validation downloads from adoption claims.
Never buy/exchange stars, create fake accounts, manufacture testimonials, or submit
trivial contributions to reach an eligibility threshold.

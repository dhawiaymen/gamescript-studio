# Project format, version 1

The examples are executable specifications. Unknown and missing fields are
rejected to catch mistakes early. JSON files are limited to 1 MB.

| Field | Meaning / range |
|---|---|
| version | Integer 1 |
| title | 1–120 non-blank characters |
| mode | tap, catch, dodge |
| width, height | Integer canvas dimensions, 240–1920 |
| duration | Simulation seconds, 1–3600 |
| target_score | Integer win threshold, 1–100000 |
| lives | Integer initial lives, 1–100 |
| speed | Falling pixels/second, 10–1500 |
| spawn_interval | Seconds between objects, 0.1–30 |
| seed | Unsigned 32-bit integer |
| background, accent | #RRGGBB colors |
| rules | Up to 100 ordered rules |

Each rule contains exactly `event`, `field`, `op`, `value`, `action`, and `amount`.
Events: `start`, `tap`, `collect`, `miss`. Conditions read `score`, `time`, or
`lives`; `always` ignores the numeric comparison. Operators: `>=`, `<=`, `==`,
`>`, `<`. Actions: `add_score`, `add_time`, `lose_life`, `win`, `lose`.

```json
{"event":"tap","field":"score","op":">=","value":5,"action":"win","amount":0}
```

Rules only run while the game is running. Terminal states are immutable until
reset. JSON strings are serialized as data in an external JavaScript file; no
rule is evaluated with `eval`. Rule edits can be undone up to 50 operations;
settings edits are saved with the project but are not part of rule undo.

## Test adapter

Exported games expose `window.gameTest` version 1:

```javascript
gameTest.reset(42);
gameTest.step({tap: true, x: 240}, 0.1);
gameTest.snapshot();
```

`dt` is 0–10 seconds, subdivided into at most 1/120-second physics steps.
Snapshots are independent copies with `score`, `time`, `lives`, `status`,
`playerX`, `items`, `elapsed`, and `events`. Open `index.html?test=1` to disable
the real-time animation loop while using the adapter. Pointer/keyboard events
still work in test mode. The seed selects a reproducible LCG spawn sequence;
it is not a cryptographic random generator.

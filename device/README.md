# Max for Live device

One **combined** Max for Live device that:

- drives Ableton Live's transport via the Live Object Model (`transport.js`),
- draws a face-mesh + per-gesture meter overlay (`jsui face_overlay.js`),
- shows a **camera dropdown** so you pick your webcam from inside Live.

The Python detector (`./detect`) is the brain: it owns the camera, runs the
face/gesture ML, and talks to this device over OSC. **No raw video runs in the
device** — it draws the mesh from landmark OSC instead, which is why the camera
picker can be a clean dropdown (Python is the single camera owner).

## OSC contract

Device **listens** on UDP **7400**; device **sends** on UDP **7500**
(must match `detector/config.py`).

### Python → device (7400)

| OSC address            | Handled by        | Effect                                  |
|------------------------|-------------------|-----------------------------------------|
| `/transport/playstop`  | `transport.js`    | toggle play/stop (reads Live's state)   |
| `/transport/return`    | `transport.js`    | playhead to song start (1.1.1)          |
| `/transport/recordarm` | `transport.js`    | toggle Arrangement Record               |
| `/transport/undo`      | `transport.js`    | undo                                    |
| `/status/landmarks`    | `face_overlay.js` | face-mesh dots (normalized x0 y0 …)     |
| `/status/gesture`      | `face_overlay.js` | per-gesture meter (name val thr prog armed) |
| `/status/meters`       | `face_overlay.js` | fallback bars if no gesture status      |
| `/status/face`         | `face_overlay.js` | face-detected LED (0/1)                 |
| `/camera/list`         | `umenu`           | labels → camera dropdown items          |

### device → Python (7500)

| OSC address          | Sent when                | Python action                   |
|----------------------|--------------------------|---------------------------------|
| `/camera/select <i>` | user picks a dropdown row | live-switch to that camera      |
| `/camera/refresh 1`  | device load (loadbang) + Refresh button | resend the camera list |

## Files

- `LookMahNoHands.amxd` — **the prebuilt device.** Already assembled; just keep it
  in this folder (it loads `transport.js` / `face_overlay.js` / `launch_detector.js`
  from beside it). The build steps below are only for rebuilding from scratch.
- `LookMahNoHands.maxpat` — editable source of the device (same patch, plain Max).
  Open it to test standalone before building the `.amxd`.
- `transport.js` — LiveAPI transport logic (`js transport.js`).
- `face_overlay.js` — the `jsui` overlay (face mesh + meters + face LED).
- `launch_detector.js` — Node for Max launcher for the start/stop buttons.
- `camera_picker_test.maxpat` — standalone test of just the camera dropdown.
- `face_overlay_test.maxpat` — standalone test of just the overlay.
- `maxpat/*` — older/experimental patches (raw `jit.grab` camera, Phase-1 sniff,
  the decoupled two-device split). Superseded by the combined device; kept for
  reference only.

## CRITICAL: copy patches in PATCHING mode, not presentation

Patch cords are invisible in **presentation** mode, so Select-All + Copy there
grabs the objects but **none of the connections**. Always copy/inspect in
**patching** view (View ▸ Patching) so the cords come along. The provided
`.maxpat` files open in patching mode for this reason.

## Build the device (one-time — only if rebuilding)

> The repo already ships a working `LookMahNoHands.amxd`. You only need these
> steps to rebuild it from the `.maxpat` source.

It's a **Max MIDI Effect on a dedicated MIDI track** — a MIDI effect never
touches your guitar audio; the device only needs to exist in the set to drive
transport. `midiin → midiout` passes MIDI through untouched.

1. First, **smoke-test outside Live**: open `LookMahNoHands.maxpat` in Max, run
   `./detect`, and confirm the overlay reacts and the camera dropdown fills.
2. In Live, create a **MIDI track**, drag on a **Max MIDI Effect**, click its
   **edit (pencil)** button.
3. In the device editor: **Select All ▸ Delete** (clear ALL default objects —
   stray objects cause duplicate `js`), then paste in the contents of
   `LookMahNoHands.maxpat` **from patching view**.
4. **Save the device into this `device/` folder** (File ▸ Save As) so the `.amxd`
   sits next to `transport.js` and `face_overlay.js`. Saving elsewhere gives
   `js • can't find file transport.js` / the `jsui` renders blank.
5. Open the **Max Console**: `js transport.js` and `jsui face_overlay.js` should
   load with no "can't find file" errors, and exactly ONE `js transport.js`.
6. **Keep the device UNFROZEN while developing** so edits to `transport.js` /
   `face_overlay.js` hot-reload (autowatch). **Freeze** only for distribution.

### Live Object Model reference (Song functions used)

`start_playing` / `stop_playing` (not `*_playback`), `undo`, plus properties
`is_playing`, `current_song_time`, `record_mode`.

### CRITICAL: threading + why `undo` is NOT in the JS

`udpreceive` delivers its messages on Max's **high-priority (scheduler)
thread**, and LiveAPI calls from that thread are unsupported. So play/stop,
return, and record-arm go through a **`deferlow`** before `js transport.js` to
run on the low-priority thread.

`undo` is special and gets its own path. Driving `undo` through `js` crashed
Live every time: the crash sits inside `js.mxo` (`js_calljsfun → object_error →
postrow_new`) — the `undo` call raises an error, and Max's attempt to post that
error crashes the M4L JS host (the same `object_error → postrow_new` fragility
`transport.js` already warns about). `deferlow` fixed the thread but not this,
because the JS engine itself is in the failing path.

Fix: `undo` is handled by **native Max objects, no JS**:

```
loadbang ─► live.path live_set ─► (id) ─┐
                                         ▼
/transport/undo ─► [call undo] ─► deferlow ─► live.object
```

`live.path live_set` resolves the Song's id at load and sets it on
`live.object`; the `undo` gesture sends `call undo` to that `live.object`. The
JS object never touches `undo`, so `js.mxo` is out of the crash path entirely.
The `undo()` function still exists in `transport.js` but is unused — leave the
native path in place.

## Launch the detector from the device (optional)

The device has **start** / **stop** buttons (bottom row, in presentation) that
spawn/kill the Python detector via **Node for Max** (`node.script
launch_detector.js`) — so you don't need a Terminal. It launches headless
(`--no-show`): no OpenCV preview window, since the device's overlay already shows
the face mesh + meters.

- **start** → spawns `detector/.venv/bin/python detector/detect.py --no-show`
  (cwd = repo root), detached so it survives Live quitting. Watch the Max Console
  for `detector launched (pid …)`.
- **stop** → sends SIGTERM to that process group.

> **CAMERA PERMISSION CAVEAT.** Launched this way the detector is a child of
> **Ableton Live**, so macOS attributes camera access to Live, not Terminal. The
> first start may prompt "Ableton Live would like to access the camera" — allow
> it (System Settings ▸ Privacy & Security ▸ Camera ▸ Ableton Live). If no frames
> arrive, that permission is almost always why. Running `./detect` from a Terminal
> is the always-works fallback and needs no device button.

Node for Max ships with Max 9; `launch_detector.js` uses only built-in modules
(no `npm install`). The button path is isolated from transport/overlay/camera, so
if Node isn't available the rest of the device still works.

## Test it end-to-end

1. Make sure nothing else holds UDP 7400 (standalone `osc_listen.py`, the Phase-1
   patch). Only one listener can bind the port.
2. Run the detector **with OSC on**:
   ```bash
   ./detect
   ```
   (macOS may ask to let Max receive network connections — allow it.)
3. Pick your camera from the device dropdown; Python should print
   `switched to camera N`. Hit **Refresh** if the list is empty (e.g. Python
   started after the device loaded).
4. Check each gesture (final v1 set):
   - **Both brows up** → Live starts playing; again → stops.
   - **Head tilt right** (ear toward shoulder) → Arrangement Record toggles.
   - **Head tilt left** → Live undoes the last action.
   Each fire also prints `[LookMahNoHands] <action>` in the Max Console.

> Toggle logic (play/stop, record-arm) is decided **in the device** from Live's
> actual state, so the detector and Live can never drift out of sync.

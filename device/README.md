# Max for Live device

Receives OSC transport messages from the Python detector and drives Ableton
Live's transport via the Live Object Model (LiveAPI).

## OSC contract

Listens on UDP **port 7400** (must match `detector/config.py`):

| OSC address            | transport.js fn | Action in Live                          |
|------------------------|-----------------|-----------------------------------------|
| `/transport/playstop`  | `playstop`      | toggle play/stop (reads Live's state)   |
| `/transport/return`    | `rtz`           | playhead to song start (1.1.1)          |
| `/transport/recordarm` | `recordarm`     | toggle Arrangement Record               |
| `/transport/undo`      | `undo`          | undo                                    |

Two simple devices (decoupled — combining them into one hand-pasted patch proved
too fragile to assemble reliably):
- `transport.js` + `maxpat/transport.maxpat` — the **transport device**
  (`udpreceive` → `route` → `js transport.js`). Must be saved next to
  `transport.js`. Drives Live's transport from OSC.
- `maxpat/camera.maxpat` — the **camera device**: `jit.grab` → `jit.pwindow` +
  picker, in presentation mode so the iPhone feed shows in Live. No external file
  deps, so it can be saved anywhere. Put it on the same dedicated MIDI track.
- `maxpat/camera_test.maxpat` — standalone camera test (plain Max, no Live).
- `maxpat/device.maxpat` — combined experiment (NOT recommended; assembly is
  error-prone). Use the two separate devices instead.
- `maxpat/transport_phase1.maxpat` — Phase 1 OSC sniff test (plain Max, no Live).

## CRITICAL: copy patches in PATCHING mode, not presentation

Patch cords are invisible in **presentation** mode, so Select-All + Copy there
grabs the objects but **none of the connections** — you paste a pile of
disconnected boxes. Before copying any `.maxpat` into a device, make sure you're
in **patching** view (View ▸ Patching, or the bottom-bar presentation toggle is
OFF) so the cords are visible and get copied too. The provided `.maxpat` files
open in patching mode for this reason.

## Build the device (one-time)

It's a **Max MIDI Effect on a dedicated MIDI track** — a MIDI effect never
touches your guitar audio, and the device only needs to exist in the set to
control transport.

1. In Live, create a **MIDI track** and name it e.g. `Transport`.
2. From the browser (Max for Live ▸ Max MIDI Effect), drag **Max MIDI Effect**
   onto that track.
3. Click the device's **edit (pencil)** button — the Max editor opens.
4. Open `maxpat/transport.maxpat` in Max → **Edit ▸ Select All ▸ Copy**. Back in
   the device editor → **Select All ▸ Delete** (clear ALL default objects — leaving
   any behind causes duplicate `js` objects), then **Paste**. (Camera is a
   separate device — see `camera.maxpat`.)
5. **Save the device into this `device/` folder** via File ▸ Save As, so the
   `.amxd` sits next to `transport.js`. This is what makes `js transport.js`
   resolvable — if the device is saved elsewhere (e.g. the User Library) you get
   `js • can't find file transport.js`.
6. Open the **Max Console** (Window ▸ Max Console). `js transport.js` should load
   with no "can't find file" and no "no function" errors. Exactly ONE
   `js transport.js` object should exist in the patch.
7. **While developing/debugging, keep the device UNFROZEN** so edits to
   `transport.js` reload automatically (autowatch). Only **Freeze** (snowflake)
   for distribution once everything works — freezing embeds a copy and disk edits
   stop taking effect.

### Live Object Model reference (Song functions used)

`start_playing` / `stop_playing` (not `*_playback`), `undo`, plus properties
`is_playing`, `current_song_time`, `record_mode`.

## Test it end-to-end

1. Close anything else bound to UDP 7400 (the standalone `osc_listen.py`, the
   Phase 1 patch). Only one listener can hold the port.
2. In Live, the `Transport` device should show the comment text and (in the Max
   Console) be ready.
3. Run the detector **with OSC on**:
   ```bash
   ./detect
   ```
   (macOS may ask to let Max receive network connections — allow it.)
4. Check each gesture:
   - **Both brows up** → Live starts playing; do it again → stops.
   - **Mouth open** → playhead jumps to 1.1.1.
   - **Pucker** → the Arrangement Record button toggles on/off.
   - **Left brow up** → Live undoes the last action.
   Each fire also prints `[LookMahNoHands] <action>` in the Max Console.

> Toggle logic (play/stop, record-arm) is decided **in the device** from Live's
> actual state, so the detector and Live can never drift out of sync.

// face_overlay.js — jsui overlay for the "Look Mah, No Hands" device.
//
// A jsui drawing surface that visualizes the Python detector's /status/* OSC:
//   * the live face mesh as dots          (from /status/landmarks),
//   * one meter per gesture with a threshold tick + hold-progress underline
//                                          (from /status/gesture),
//   * a face-detected LED.
//
// The patch routes each /status/* address, prepends a selector symbol, and
// sends it to this object's inlet, so these named functions receive the data:
//   landmarks x0 y0 x1 y1 ...     normalized 0..1, flat (stride-sampled)
//   gesture   name value thr prog armed
//   meters    v0 v1 ...           fallback bars if no gesture status arrives
//   face      0|1
//   mirror    0|1                 flip horizontally (default 1 = mirror view)
//   clear                         wipe all state
//
// Standalone test patch: device/face_overlay_test.maxpat. Final home: next to
// the .amxd in device/ so the combined device resolves this file.

autowatch = 1;

mgraphics.init();
mgraphics.relative_coords = 0;   // pixel coordinates, origin top-left
mgraphics.autofill = 0;

// --- state -----------------------------------------------------------------
var pts = [];            // [x0,y0,x1,y1,...] normalized landmark coords
var faceOn = 0;
var mirrorX = 1;         // mirror horizontally so it reads like a mirror
var order = [];          // gesture names, in arrival order (config order)
var data = {};           // name -> {value, threshold, progress, armed}
var meterVals = [];      // fallback values if no /status/gesture seen

var METER_ROW = 22;      // px per gesture meter row
var PAD = 8;

// --- inbound messages ------------------------------------------------------
function landmarks() {
    pts = arrayfromargs(arguments);
    mgraphics.redraw();
}

function face(v) {
    faceOn = (v != 0) ? 1 : 0;
    mgraphics.redraw();
}

function mirror(v) {
    mirrorX = (v != 0) ? 1 : 0;
    mgraphics.redraw();
}

function meters() {
    meterVals = arrayfromargs(arguments);
    mgraphics.redraw();
}

function gesture(name, value, threshold, progress, armed) {
    if (data[name] === undefined) order.push(name);
    data[name] = {
        value: value,
        threshold: threshold,
        progress: progress,
        armed: armed
    };
    mgraphics.redraw();
}

function clear() {
    pts = [];
    faceOn = 0;
    order = [];
    data = {};
    meterVals = [];
    mgraphics.redraw();
}

// --- painting --------------------------------------------------------------
function paint() {
    // jsui pixel size — mgraphics.get_size() is absent in some Max builds, so
    // derive it from the object's patching rectangle instead.
    var r = this.box.rect;
    var W = r[2] - r[0];
    var H = r[3] - r[1];

    var rows = order.length > 0 ? order.length : meterVals.length;
    var meterH = rows > 0 ? (rows * METER_ROW + PAD) : 0;
    var faceH = H - meterH;
    if (faceH < 0) faceH = 0;

    // background
    mgraphics.set_source_rgba(0.10, 0.11, 0.13, 1.0);
    mgraphics.rectangle(0, 0, W, H);
    mgraphics.fill();

    drawFacePanel(W, faceH);
    drawMeters(W, faceH, rows);
}

function drawFacePanel(W, faceH) {
    // face-detected LED, top-right
    var r = 6;
    if (faceOn) mgraphics.set_source_rgba(0.30, 0.85, 0.40, 1.0);
    else        mgraphics.set_source_rgba(0.35, 0.35, 0.38, 1.0);
    mgraphics.ellipse(W - 2 * r - 6, 6, 2 * r, 2 * r);
    mgraphics.fill();

    if (pts.length < 2 || faceH <= 0) return;

    // face-mesh dots
    mgraphics.set_source_rgba(0.45, 0.85, 0.95, 0.9);
    var dot = 1.4;
    for (var i = 0; i + 1 < pts.length; i += 2) {
        var nx = pts[i];
        var ny = pts[i + 1];
        var px = (mirrorX ? (1.0 - nx) : nx) * W;
        var py = ny * faceH;
        mgraphics.ellipse(px - dot, py - dot, 2 * dot, 2 * dot);
        mgraphics.fill();
    }
}

function drawMeters(W, top, rows) {
    if (rows <= 0) return;
    mgraphics.select_font_face("Arial");
    mgraphics.set_font_size(11);

    var x = PAD;
    var barX = 96;
    var barW = W - barX - PAD;
    if (barW < 20) barW = 20;
    var barH = 12;

    for (var i = 0; i < rows; i++) {
        var name, value, threshold, progress, armed;
        if (order.length > 0) {
            name = order[i];
            var d = data[name];
            value = d.value; threshold = d.threshold;
            progress = d.progress; armed = d.armed;
        } else {
            name = "g" + i;
            value = meterVals[i]; threshold = -1;
            progress = 0; armed = 1;
        }

        var y = top + PAD + i * METER_ROW;
        var col = meterColor(value, threshold, armed);

        // label
        mgraphics.set_source_rgba(0.85, 0.85, 0.88, 1.0);
        mgraphics.move_to(x, y + barH);
        mgraphics.show_text(name);

        // track
        mgraphics.set_source_rgba(0.22, 0.23, 0.26, 1.0);
        mgraphics.rectangle(barX, y, barW, barH);
        mgraphics.fill();

        // value fill
        mgraphics.set_source_rgba(col[0], col[1], col[2], 1.0);
        mgraphics.rectangle(barX, y, barW * clamp01(value), barH);
        mgraphics.fill();

        // threshold tick
        if (threshold >= 0) {
            var tx = barX + barW * clamp01(threshold);
            mgraphics.set_source_rgba(1.0, 1.0, 1.0, 0.9);
            mgraphics.rectangle(tx, y - 2, 1, barH + 4);
            mgraphics.fill();
        }

        // hold-progress underline
        if (progress > 0) {
            mgraphics.set_source_rgba(0.30, 0.90, 0.40, 1.0);
            mgraphics.rectangle(barX, y + barH + 2, barW * clamp01(progress), 2);
            mgraphics.fill();
        }
    }
}

function meterColor(value, threshold, armed) {
    if (!armed) return [1.0, 0.78, 0.0];            // relax to re-arm (yellow)
    if (threshold >= 0 && value >= threshold)
        return [1.0, 0.55, 0.0];                    // counting toward fire (orange)
    return [0.55, 0.78, 0.85];                      // idle (cyan-gray)
}

function clamp01(v) {
    if (v < 0) return 0;
    if (v > 1) return 1;
    return v;
}

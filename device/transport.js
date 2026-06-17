// transport.js — Live transport control for the "Look Mah, No Hands" device.
//
// Loaded by the [js transport.js] object inside the Max for Live device. Each
// incoming OSC address is routed to a message that calls one of these functions.
// All transport actions use LiveAPI on "live_set" (the Live Object Model).
//
// Function names are the message selectors the patch sends:
//   playstop   <- /transport/playstop   (toggle, decided from Live's real state)
//   rtz        <- /transport/return     (return to zero / song start)
//   recordarm  <- /transport/recordarm  (toggle Arrangement record)
//   undo       <- /transport/undo
// NB: "return" is a reserved word in JS, hence "rtz".

autowatch = 1;
inlets = 1;
outlets = 1;  // bangs out the last action name (for an optional status display)

function _liveset() {
    return new LiveAPI("live_set");
}

function playstop() {
    var api = _liveset();
    var playing = parseInt(api.get("is_playing"));
    if (playing === 1) {
        api.call("stop_playing");
        _done("stop");
    } else {
        api.call("start_playing");
        _done("play");
    }
}

function rtz() {
    var api = _liveset();
    api.set("current_song_time", 0);
    _done("return");
}

function recordarm() {
    var api = _liveset();
    var rec = parseInt(api.get("record_mode"));
    var next = rec === 1 ? 0 : 1;
    api.set("record_mode", next);
    _done("recordarm " + next);
}

function undo() {
    var api = _liveset();
    api.call("undo");
    _done("undo");
}

function _done(label) {
    post("[LookMahNoHands] " + label + "\n");
    outlet(0, "action", label);
}

// Safety: silently ignore any unexpected message. Do NOT post here — a flood of
// console posts from misrouted/duplicate messages can crash Max's console
// (the object_error -> postrow_new path). Stray messages must be a no-op.
function anything() {
}

// launch_detector.js — Node for Max launcher for the "Look Mah, No Hands" device.
//
// Lets a button inside the Max for Live device start/stop the Python detector
// (the brain: camera + face ML + OSC) without opening a Terminal. Loaded by a
// [node.script launch_detector.js @autostart 1] object; clicking the device's
// "Start detector" / "Stop" buttons sends the "start" / "stop" messages here.
//
// It spawns the detector headless (--no-show): no OpenCV preview window, because
// the device's own jsui overlay already shows the face mesh + meters.
//
// CAMERA PERMISSION NOTE: when the detector is launched this way it is a child of
// Ableton Live, so macOS attributes camera access to *Live*, not Terminal. The
// first run may prompt "Ableton Live would like to access the camera" — allow it
// (System Settings ▸ Privacy & Security ▸ Camera ▸ Ableton Live). If frames never
// arrive, that permission is almost always why. Running ./detect from a Terminal
// remains the always-works fallback.

const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const Max = require('max-api');

// device/ -> repo root
const REPO = path.resolve(__dirname, '..');
const PY = path.join(REPO, 'detector', '.venv', 'bin', 'python');
const SCRIPT = path.join(REPO, 'detector', 'detect.py');

let child = null;

function running() {
    return child !== null && child.exitCode === null;
}

Max.addHandler('start', () => {
    if (running()) {
        Max.post('detector already running (pid ' + child.pid + ')');
        Max.outlet('running', 1);
        return;
    }
    if (!fs.existsSync(PY)) {
        Max.post('ERROR: venv python not found at ' + PY);
        Max.outlet('running', 0);
        return;
    }
    try {
        child = spawn(PY, [SCRIPT, '--no-show'], {
            cwd: REPO,
            detached: true,      // own process group so it survives Live quitting
            stdio: 'ignore',
        });
        child.unref();
        Max.post('detector launched (pid ' + child.pid + ')');
        Max.outlet('running', 1);
        child.on('exit', (code) => {
            Max.post('detector exited (code ' + code + ')');
            child = null;
            Max.outlet('running', 0);
        });
        child.on('error', (err) => {
            Max.post('ERROR launching detector: ' + err.message);
            child = null;
            Max.outlet('running', 0);
        });
    } catch (e) {
        Max.post('ERROR launching detector: ' + e.message);
        child = null;
        Max.outlet('running', 0);
    }
});

Max.addHandler('stop', () => {
    if (!running()) {
        Max.post('detector not running');
        Max.outlet('running', 0);
        return;
    }
    const pid = child.pid;
    // Kill the whole process group (negative pid) since it was detached.
    try { process.kill(-pid, 'SIGTERM'); } catch (e) {}
    try { process.kill(pid, 'SIGTERM'); } catch (e) {}
    Max.post('detector stop signal sent (pid ' + pid + ')');
});

Max.post('launch_detector ready. repo=' + REPO);

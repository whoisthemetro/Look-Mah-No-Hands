"""OSC client that sends transport actions to the Max for Live device.

Wraps python-osc so the rest of the detector calls semantic methods
(send_play(), send_return(), ...) instead of juggling raw addresses.
"""

from __future__ import annotations

from pythonosc import udp_client

import config


class TransportOSC:
    def __init__(self, host: str = config.OSC_HOST, port: int = config.OSC_PORT):
        self.host = host
        self.port = port
        self._client = udp_client.SimpleUDPClient(host, port)

    def _send(self, address: str, value=1):
        self._client.send_message(address, value)

    def send_osc(self, address: str, value=1):
        """Send any address (used by the classifier-driven detector)."""
        self._send(address, value)

    # --- v1 transport actions ---
    def send_play(self):
        self._send(config.ADDR_PLAY)

    def send_stop(self):
        self._send(config.ADDR_STOP)

    def send_return(self):
        self._send(config.ADDR_RETURN)

    def send_recordarm(self):
        self._send(config.ADDR_RECORDARM)

    def send_undo(self):
        self._send(config.ADDR_UNDO)

    # --- debug passthrough ---
    def send_gesture(self, name: str, confidence: float):
        self._send(f"{config.ADDR_GESTURE}/{name}", confidence)

    # --- status broadcast (for the device's overlay) ---
    def send_face(self, detected: bool):
        self._client.send_message(config.ADDR_STATUS_FACE, 1 if detected else 0)

    def send_meters(self, values):
        """Ordered gesture values [v0, v1, ...] -> a multislider in the device."""
        self._client.send_message(config.ADDR_STATUS_METERS, [float(v) for v in values])

    def send_gesture_status(self, name, value, threshold, progress, armed):
        self._client.send_message(
            config.ADDR_STATUS_GESTURE,
            [name, float(value), float(threshold), float(progress), 1 if armed else 0],
        )

    def send_landmarks(self, points):
        """points: iterable of (x, y) normalized floats -> flat [x0,y0,x1,y1,...]."""
        flat = []
        for x, y in points:
            flat.append(float(x))
            flat.append(float(y))
        self._client.send_message(config.ADDR_STATUS_LANDMARKS, flat)

    # --- camera handshake ---
    def send_camera_list(self, labels):
        """Send the camera labels so the device can build its dropdown."""
        self._client.send_message(config.ADDR_CAMERA_LIST, list(labels))

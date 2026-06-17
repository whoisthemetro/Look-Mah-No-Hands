"""Send the five v1 transport OSC messages once, for signal-path testing.

Point this at the standalone listener (osc_listen.py) or at the Max device.
    python detector/send_test_osc.py
"""

from __future__ import annotations

import time

import config
from osc_out import TransportOSC


def main():
    osc = TransportOSC()
    print(f"Sending test OSC to {config.OSC_HOST}:{config.OSC_PORT}")
    actions = [
        ("play", osc.send_play),
        ("return", osc.send_return),
        ("recordarm", osc.send_recordarm),
        ("undo", osc.send_undo),
        ("stop", osc.send_stop),
    ]
    for name, fn in actions:
        fn()
        print(f"  sent {name}")
        time.sleep(0.3)
    print("done.")


if __name__ == "__main__":
    main()

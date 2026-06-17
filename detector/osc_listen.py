"""Standalone OSC listener — a Max-free stand-in for the device.

Prints every OSC message received on the configured port so the signal path can
be verified without launching Max/Live.
    python detector/osc_listen.py
"""

from __future__ import annotations

from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import BlockingOSCUDPServer

import config


def _on_message(address, *args):
    print(f"recv {address}  args={list(args)}")


def main():
    dispatcher = Dispatcher()
    dispatcher.set_default_handler(_on_message)
    BlockingOSCUDPServer.allow_reuse_address = True
    server = BlockingOSCUDPServer((config.OSC_HOST, config.OSC_PORT), dispatcher)
    print(f"Listening for OSC on {config.OSC_HOST}:{config.OSC_PORT} (Ctrl-C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()

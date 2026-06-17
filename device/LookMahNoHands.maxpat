{
  "patcher": {
    "fileversion": 1,
    "appversion": {
      "major": 8,
      "minor": 6,
      "revision": 0,
      "architecture": "x64",
      "modernui": 1
    },
    "classnamespace": "box",
    "rect": [
      60.0,
      80.0,
      900.0,
      560.0
    ],
    "openinpresentation": 1,
    "boxes": [
      {
        "box": {
          "id": "obj-title",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40.0,
            14.0,
            820.0,
            20.0
          ],
          "text": "Look Mah, No Hands \u2014 combined device. Python detector (./detect) owns the camera and sends OSC on 7400; this device drives Live transport, draws the face/meters overlay, and sends camera selection back on 7500. No raw video by design."
        }
      },
      {
        "box": {
          "id": "obj-u",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40.0,
            48.0,
            110.0,
            22.0
          ],
          "text": "udpreceive 7400"
        }
      },
      {
        "box": {
          "id": "obj-route",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 10,
          "outlettype": [
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            ""
          ],
          "patching_rect": [
            40.0,
            86.0,
            800.0,
            22.0
          ],
          "text": "route /transport/playstop /transport/return /transport/recordarm /transport/undo /status/landmarks /status/gesture /status/meters /status/face /camera/list"
        }
      },
      {
        "box": {
          "id": "obj-mPlay",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40.0,
            134.0,
            70.0,
            22.0
          ],
          "text": "playstop"
        }
      },
      {
        "box": {
          "id": "obj-mRtz",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            120.0,
            134.0,
            50.0,
            22.0
          ],
          "text": "rtz"
        }
      },
      {
        "box": {
          "id": "obj-mRec",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            180.0,
            134.0,
            90.0,
            22.0
          ],
          "text": "recordarm"
        }
      },
      {
        "box": {
          "id": "obj-mUndo",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            280.0,
            134.0,
            60.0,
            22.0
          ],
          "text": "call undo"
        }
      },
      {
        "box": {
          "id": "obj-deferlow",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40.0,
            162.0,
            80.0,
            22.0
          ],
          "text": "deferlow"
        }
      },
      {
        "box": {
          "id": "obj-jsnote",
          "maxclass": "comment",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            130.0,
            165.0,
            360.0,
            18.0
          ],
          "text": "deferlow: run LiveAPI on the low-priority thread (udpreceive fires high-priority; calling undo there crashes Live)."
        }
      },
      {
        "box": {
          "id": "obj-js",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40.0,
            196.0,
            120.0,
            22.0
          ],
          "text": "js transport.js"
        }
      },
      {
        "box": {
          "id": "obj-pl",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            360.0,
            134.0,
            120.0,
            22.0
          ],
          "text": "prepend landmarks"
        }
      },
      {
        "box": {
          "id": "obj-pg",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            490.0,
            134.0,
            110.0,
            22.0
          ],
          "text": "prepend gesture"
        }
      },
      {
        "box": {
          "id": "obj-pm",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            610.0,
            134.0,
            100.0,
            22.0
          ],
          "text": "prepend meters"
        }
      },
      {
        "box": {
          "id": "obj-pf",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            720.0,
            134.0,
            90.0,
            22.0
          ],
          "text": "prepend face"
        }
      },
      {
        "box": {
          "id": "obj-jsui",
          "maxclass": "jsui",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "parameter_enable": 0,
          "filename": "face_overlay.js",
          "patching_rect": [
            360.0,
            174.0,
            360.0,
            300.0
          ],
          "presentation": 1,
          "presentation_rect": [
            10.0,
            10.0,
            360.0,
            300.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-trig",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "patching_rect": [
            40.0,
            226.0,
            60.0,
            22.0
          ],
          "text": "t l b"
        }
      },
      {
        "box": {
          "id": "obj-clearm",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            120.0,
            226.0,
            50.0,
            22.0
          ],
          "text": "clear"
        }
      },
      {
        "box": {
          "id": "obj-iter",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40.0,
            262.0,
            40.0,
            22.0
          ],
          "text": "iter"
        }
      },
      {
        "box": {
          "id": "obj-append",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40.0,
            298.0,
            110.0,
            22.0
          ],
          "text": "prepend append"
        }
      },
      {
        "box": {
          "id": "obj-menu",
          "maxclass": "umenu",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "int",
            "",
            ""
          ],
          "parameter_enable": 0,
          "patching_rect": [
            40.0,
            334.0,
            200.0,
            22.0
          ],
          "presentation": 1,
          "presentation_rect": [
            10.0,
            320.0,
            220.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-selpre",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            40.0,
            370.0,
            150.0,
            22.0
          ],
          "text": "prepend /camera/select"
        }
      },
      {
        "box": {
          "id": "obj-load",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "bang"
          ],
          "patching_rect": [
            260.0,
            298.0,
            64.0,
            22.0
          ],
          "text": "loadbang"
        }
      },
      {
        "box": {
          "id": "obj-refbtn",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            260.0,
            334.0,
            130.0,
            22.0
          ],
          "text": "/camera/refresh 1",
          "presentation": 1,
          "presentation_rect": [
            240.0,
            320.0,
            150.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-send",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            40.0,
            410.0,
            180.0,
            22.0
          ],
          "text": "udpsend 127.0.0.1 7500"
        }
      },
      {
        "box": {
          "id": "obj-midiin",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            "int"
          ],
          "patching_rect": [
            780.0,
            48.0,
            60.0,
            22.0
          ],
          "text": "midiin"
        }
      },
      {
        "box": {
          "id": "obj-midiout",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 0,
          "patching_rect": [
            780.0,
            86.0,
            60.0,
            22.0
          ],
          "text": "midiout"
        }
      },
      {
        "box": {
          "id": "obj-defU",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            360.0,
            300.0,
            80.0,
            20.0
          ],
          "text": "deferlow"
        }
      },
      {
        "box": {
          "id": "obj-lpath",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 3,
          "outlettype": [
            "",
            "",
            ""
          ],
          "patching_rect": [
            470.0,
            300.0,
            120.0,
            20.0
          ],
          "text": "live.path live_set"
        }
      },
      {
        "box": {
          "id": "obj-lobj",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            ""
          ],
          "patching_rect": [
            360.0,
            340.0,
            120.0,
            20.0
          ],
          "text": "live.object"
        }
      },
      {
        "box": {
          "id": "obj-node",
          "maxclass": "newobj",
          "numinlets": 1,
          "numoutlets": 2,
          "outlettype": [
            "",
            "bang"
          ],
          "patching_rect": [
            360.0,
            400.0,
            300.0,
            20.0
          ],
          "text": "node.script launch_detector.js @autostart 1"
        }
      },
      {
        "box": {
          "id": "obj-mStart",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            360.0,
            360.0,
            60.0,
            20.0
          ],
          "text": "start",
          "presentation": 1,
          "presentation_rect": [
            10.0,
            348.0,
            90.0,
            22.0
          ]
        }
      },
      {
        "box": {
          "id": "obj-mStop",
          "maxclass": "message",
          "numinlets": 2,
          "numoutlets": 1,
          "outlettype": [
            ""
          ],
          "patching_rect": [
            430.0,
            360.0,
            60.0,
            20.0
          ],
          "text": "stop",
          "presentation": 1,
          "presentation_rect": [
            110.0,
            348.0,
            90.0,
            22.0
          ]
        }
      }
    ],
    "lines": [
      {
        "patchline": {
          "source": [
            "obj-u",
            0
          ],
          "destination": [
            "obj-route",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            0
          ],
          "destination": [
            "obj-mPlay",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            1
          ],
          "destination": [
            "obj-mRtz",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            2
          ],
          "destination": [
            "obj-mRec",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            3
          ],
          "destination": [
            "obj-mUndo",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-mPlay",
            0
          ],
          "destination": [
            "obj-deferlow",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-mRtz",
            0
          ],
          "destination": [
            "obj-deferlow",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-mRec",
            0
          ],
          "destination": [
            "obj-deferlow",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-deferlow",
            0
          ],
          "destination": [
            "obj-js",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            4
          ],
          "destination": [
            "obj-pl",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            5
          ],
          "destination": [
            "obj-pg",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            6
          ],
          "destination": [
            "obj-pm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            7
          ],
          "destination": [
            "obj-pf",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-pl",
            0
          ],
          "destination": [
            "obj-jsui",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-pg",
            0
          ],
          "destination": [
            "obj-jsui",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-pm",
            0
          ],
          "destination": [
            "obj-jsui",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-pf",
            0
          ],
          "destination": [
            "obj-jsui",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-route",
            8
          ],
          "destination": [
            "obj-trig",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-trig",
            0
          ],
          "destination": [
            "obj-iter",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-trig",
            1
          ],
          "destination": [
            "obj-clearm",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-clearm",
            0
          ],
          "destination": [
            "obj-menu",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-iter",
            0
          ],
          "destination": [
            "obj-append",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-append",
            0
          ],
          "destination": [
            "obj-menu",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-menu",
            0
          ],
          "destination": [
            "obj-selpre",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-selpre",
            0
          ],
          "destination": [
            "obj-send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-load",
            0
          ],
          "destination": [
            "obj-refbtn",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-refbtn",
            0
          ],
          "destination": [
            "obj-send",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-midiin",
            0
          ],
          "destination": [
            "obj-midiout",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-mUndo",
            0
          ],
          "destination": [
            "obj-defU",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-defU",
            0
          ],
          "destination": [
            "obj-lobj",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-lpath",
            0
          ],
          "destination": [
            "obj-lobj",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-load",
            0
          ],
          "destination": [
            "obj-lpath",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-mStart",
            0
          ],
          "destination": [
            "obj-node",
            0
          ]
        }
      },
      {
        "patchline": {
          "source": [
            "obj-mStop",
            0
          ],
          "destination": [
            "obj-node",
            0
          ]
        }
      }
    ],
    "openrect": [
      0.0,
      0.0,
      400.0,
      388.0
    ]
  }
}
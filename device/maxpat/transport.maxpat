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
		"rect": [ 80.0, 100.0, 720.0, 460.0 ],
		"boxes": [
			{
				"box": {
					"id": "obj-c",
					"maxclass": "comment",
					"text": "Look Mah, No Hands — transport control. OSC in on UDP 7400 -> LiveAPI via transport.js. Put this device on a dedicated MIDI track.",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 40.0, 18.0, 620.0, 40.0 ]
				}
			},
			{
				"box": {
					"id": "obj-1",
					"maxclass": "newobj",
					"text": "udpreceive 7400",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 78.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-2",
					"maxclass": "newobj",
					"text": "route /transport/playstop /transport/return /transport/recordarm /transport/undo",
					"numinlets": 1,
					"numoutlets": 5,
					"outlettype": [ "", "", "", "", "" ],
					"patching_rect": [ 40.0, 128.0, 520.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-3",
					"maxclass": "message",
					"text": "playstop",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 188.0, 70.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-4",
					"maxclass": "message",
					"text": "rtz",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 130.0, 188.0, 50.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-5",
					"maxclass": "message",
					"text": "recordarm",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 200.0, 188.0, 90.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-6",
					"maxclass": "message",
					"text": "undo",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 310.0, 188.0, 60.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-7",
					"maxclass": "newobj",
					"text": "js transport.js",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 248.0, 120.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-status",
					"maxclass": "comment",
					"text": "(Open the Max Console to see each action printed.)",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 180.0, 251.0, 360.0, 20.0 ]
				}
			},
			{
				"box": {
					"id": "obj-8",
					"maxclass": "newobj",
					"text": "midiin",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "int" ],
					"patching_rect": [ 470.0, 78.0, 60.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-9",
					"maxclass": "newobj",
					"text": "midiout",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 470.0, 128.0, 60.0, 22.0 ]
				}
			}
		],
		"lines": [
			{ "patchline": { "source": [ "obj-1", 0 ], "destination": [ "obj-2", 0 ] } },
			{ "patchline": { "source": [ "obj-2", 0 ], "destination": [ "obj-3", 0 ] } },
			{ "patchline": { "source": [ "obj-2", 1 ], "destination": [ "obj-4", 0 ] } },
			{ "patchline": { "source": [ "obj-2", 2 ], "destination": [ "obj-5", 0 ] } },
			{ "patchline": { "source": [ "obj-2", 3 ], "destination": [ "obj-6", 0 ] } },
			{ "patchline": { "source": [ "obj-3", 0 ], "destination": [ "obj-7", 0 ] } },
			{ "patchline": { "source": [ "obj-4", 0 ], "destination": [ "obj-7", 0 ] } },
			{ "patchline": { "source": [ "obj-5", 0 ], "destination": [ "obj-7", 0 ] } },
			{ "patchline": { "source": [ "obj-6", 0 ], "destination": [ "obj-7", 0 ] } },
			{ "patchline": { "source": [ "obj-8", 0 ], "destination": [ "obj-9", 0 ] } }
		]
	}
}

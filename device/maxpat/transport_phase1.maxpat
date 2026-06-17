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
		"rect": [ 80.0, 100.0, 700.0, 420.0 ],
		"boxes": [
			{
				"box": {
					"id": "obj-comment-1",
					"maxclass": "comment",
					"text": "Phase 1 signal-path test: OSC from the Python detector on port 7400. Open the Max console (Window > Max Console) and run detector/send_test_osc.py.",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 40.0, 20.0, 600.0, 40.0 ]
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
					"patching_rect": [ 40.0, 80.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-2",
					"maxclass": "newobj",
					"text": "print RX",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 250.0, 130.0, 60.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-3",
					"maxclass": "newobj",
					"text": "route /transport/play /transport/stop /transport/return /transport/recordarm /transport/undo",
					"numinlets": 1,
					"numoutlets": 6,
					"outlettype": [ "", "", "", "", "", "" ],
					"patching_rect": [ 40.0, 180.0, 560.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-4",
					"maxclass": "newobj",
					"text": "print PLAY",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 40.0, 250.0, 70.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-5",
					"maxclass": "newobj",
					"text": "print STOP",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 130.0, 250.0, 70.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-6",
					"maxclass": "newobj",
					"text": "print RETURN",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 220.0, 250.0, 85.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-7",
					"maxclass": "newobj",
					"text": "print RECORDARM",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 325.0, 250.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-8",
					"maxclass": "newobj",
					"text": "print UNDO",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 455.0, 250.0, 70.0, 22.0 ]
				}
			}
		],
		"lines": [
			{ "patchline": { "source": [ "obj-1", 0 ], "destination": [ "obj-2", 0 ] } },
			{ "patchline": { "source": [ "obj-1", 0 ], "destination": [ "obj-3", 0 ] } },
			{ "patchline": { "source": [ "obj-3", 0 ], "destination": [ "obj-4", 0 ] } },
			{ "patchline": { "source": [ "obj-3", 1 ], "destination": [ "obj-5", 0 ] } },
			{ "patchline": { "source": [ "obj-3", 2 ], "destination": [ "obj-6", 0 ] } },
			{ "patchline": { "source": [ "obj-3", 3 ], "destination": [ "obj-7", 0 ] } },
			{ "patchline": { "source": [ "obj-3", 4 ], "destination": [ "obj-8", 0 ] } }
		]
	}
}

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
		"rect": [ 80.0, 100.0, 720.0, 560.0 ],
		"boxes": [
			{
				"box": {
					"id": "obj-c",
					"maxclass": "comment",
					"text": "Camera test (plain Max, no Live needed). 1) Click 'getvdevlist' and read the Max Console for the camera list + numbers. 2) Type the OBS Virtual Camera's number into the number box. 3) Flip the toggle ON to see live video.",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 40.0, 16.0, 640.0, 54.0 ]
				}
			},
			{
				"box": {
					"id": "obj-tog",
					"maxclass": "toggle",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "int" ],
					"patching_rect": [ 40.0, 84.0, 24.0, 24.0 ]
				}
			},
			{
				"box": {
					"id": "obj-met",
					"maxclass": "newobj",
					"text": "metro 33",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "bang" ],
					"patching_rect": [ 40.0, 120.0, 64.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-grab",
					"maxclass": "newobj",
					"text": "jit.grab 640 480",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [ "jit_matrix", "" ],
					"patching_rect": [ 40.0, 156.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-pwin",
					"maxclass": "jit.pwindow",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 200.0, 320.0, 240.0 ]
				}
			},
			{
				"box": {
					"id": "obj-getlist",
					"maxclass": "message",
					"text": "getvdevlist",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 420.0, 84.0, 90.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-num",
					"maxclass": "number",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [ "", "bang" ],
					"patching_rect": [ 420.0, 120.0, 60.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-vdev",
					"maxclass": "message",
					"text": "close, vdevice $1, open",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 420.0, 156.0, 160.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-print",
					"maxclass": "newobj",
					"text": "print VDEV",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 600.0, 200.0, 80.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-load",
					"maxclass": "newobj",
					"text": "loadbang",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "bang" ],
					"patching_rect": [ 120.0, 84.0, 64.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-on",
					"maxclass": "message",
					"text": "1",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 120.0, 50.0, 30.0, 22.0 ]
				}
			}
		],
		"lines": [
			{ "patchline": { "source": [ "obj-load", 0 ], "destination": [ "obj-on", 0 ] } },
			{ "patchline": { "source": [ "obj-on", 0 ], "destination": [ "obj-tog", 0 ] } },
			{ "patchline": { "source": [ "obj-tog", 0 ], "destination": [ "obj-met", 0 ] } },
			{ "patchline": { "source": [ "obj-met", 0 ], "destination": [ "obj-grab", 0 ] } },
			{ "patchline": { "source": [ "obj-grab", 0 ], "destination": [ "obj-pwin", 0 ] } },
			{ "patchline": { "source": [ "obj-grab", 1 ], "destination": [ "obj-print", 0 ] } },
			{ "patchline": { "source": [ "obj-getlist", 0 ], "destination": [ "obj-grab", 0 ] } },
			{ "patchline": { "source": [ "obj-num", 0 ], "destination": [ "obj-vdev", 0 ] } },
			{ "patchline": { "source": [ "obj-vdev", 0 ], "destination": [ "obj-grab", 0 ] } }
		]
	}
}

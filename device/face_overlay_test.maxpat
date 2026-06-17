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
		"rect": [ 80.0, 100.0, 760.0, 560.0 ],
		"boxes": [
			{
				"box": {
					"id": "obj-c",
					"maxclass": "comment",
					"text": "Look Mah, No Hands — face-mesh + meters overlay test. Run ./detect (OSC on); the jsui below draws /status/landmarks dots, /status/gesture meters, and the face LED. This is a plain Max test (no Live).",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 40.0, 14.0, 680.0, 40.0 ]
				}
			},
			{
				"box": {
					"id": "obj-recv",
					"maxclass": "newobj",
					"text": "udpreceive 7400",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 70.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-route",
					"maxclass": "newobj",
					"text": "route /status/landmarks /status/gesture /status/meters /status/face",
					"numinlets": 1,
					"numoutlets": 5,
					"outlettype": [ "", "", "", "", "" ],
					"patching_rect": [ 40.0, 106.0, 470.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-pl",
					"maxclass": "newobj",
					"text": "prepend landmarks",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 150.0, 120.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-pg",
					"maxclass": "newobj",
					"text": "prepend gesture",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 170.0, 150.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-pm",
					"maxclass": "newobj",
					"text": "prepend meters",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 290.0, 150.0, 100.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-pf",
					"maxclass": "newobj",
					"text": "prepend face",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 400.0, 150.0, 90.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-jsui",
					"maxclass": "jsui",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"parameter_enable": 0,
					"filename": "face_overlay.js",
					"patching_rect": [ 40.0, 200.0, 360.0, 300.0 ],
					"presentation": 1,
					"presentation_rect": [ 10.0, 10.0, 360.0, 300.0 ]
				}
			},
			{
				"box": {
					"id": "obj-clear",
					"maxclass": "message",
					"text": "clear",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 430.0, 200.0, 50.0, 22.0 ]
				}
			}
		],
		"lines": [
			{ "patchline": { "source": [ "obj-recv", 0 ], "destination": [ "obj-route", 0 ] } },
			{ "patchline": { "source": [ "obj-route", 0 ], "destination": [ "obj-pl", 0 ] } },
			{ "patchline": { "source": [ "obj-route", 1 ], "destination": [ "obj-pg", 0 ] } },
			{ "patchline": { "source": [ "obj-route", 2 ], "destination": [ "obj-pm", 0 ] } },
			{ "patchline": { "source": [ "obj-route", 3 ], "destination": [ "obj-pf", 0 ] } },
			{ "patchline": { "source": [ "obj-pl", 0 ], "destination": [ "obj-jsui", 0 ] } },
			{ "patchline": { "source": [ "obj-pg", 0 ], "destination": [ "obj-jsui", 0 ] } },
			{ "patchline": { "source": [ "obj-pm", 0 ], "destination": [ "obj-jsui", 0 ] } },
			{ "patchline": { "source": [ "obj-pf", 0 ], "destination": [ "obj-jsui", 0 ] } },
			{ "patchline": { "source": [ "obj-clear", 0 ], "destination": [ "obj-jsui", 0 ] } }
		]
	}
}

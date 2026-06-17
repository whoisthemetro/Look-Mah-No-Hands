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
		"rect": [ 80.0, 100.0, 720.0, 420.0 ],
		"boxes": [
			{
				"box": {
					"id": "obj-c",
					"maxclass": "comment",
					"text": "Look Mah, No Hands — camera picker test. /camera/list (7400) fills the umenu; picking one sends /camera/select <index> to Python:7500; Refresh asks Python to resend the list. Run ./detect; watch its console for 'switched to camera N'.",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 40.0, 14.0, 640.0, 54.0 ]
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
					"patching_rect": [ 40.0, 78.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-route",
					"maxclass": "newobj",
					"text": "route /camera/list",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [ "", "" ],
					"patching_rect": [ 40.0, 112.0, 130.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-trig",
					"maxclass": "newobj",
					"text": "t l b",
					"numinlets": 1,
					"numoutlets": 2,
					"outlettype": [ "", "bang" ],
					"patching_rect": [ 40.0, 146.0, 60.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-clearm",
					"maxclass": "message",
					"text": "clear",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 120.0, 180.0, 50.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-iter",
					"maxclass": "newobj",
					"text": "iter",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 180.0, 40.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-append",
					"maxclass": "newobj",
					"text": "prepend append",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 200.0, 110.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-menu",
					"maxclass": "umenu",
					"numinlets": 1,
					"numoutlets": 3,
					"outlettype": [ "int", "", "" ],
					"parameter_enable": 0,
					"patching_rect": [ 40.0, 220.0, 200.0, 22.0 ],
					"presentation": 1,
					"presentation_rect": [ 10.0, 10.0, 200.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-selpre",
					"maxclass": "newobj",
					"text": "prepend /camera/select",
					"numinlets": 1,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 40.0, 260.0, 150.0, 22.0 ]
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
					"patching_rect": [ 300.0, 180.0, 64.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-refbtn",
					"maxclass": "message",
					"text": "/camera/refresh 1",
					"numinlets": 2,
					"numoutlets": 1,
					"outlettype": [ "" ],
					"patching_rect": [ 300.0, 220.0, 130.0, 22.0 ],
					"presentation": 1,
					"presentation_rect": [ 10.0, 42.0, 130.0, 22.0 ]
				}
			},
			{
				"box": {
					"id": "obj-send",
					"maxclass": "newobj",
					"text": "udpsend 127.0.0.1 7500",
					"numinlets": 1,
					"numoutlets": 0,
					"patching_rect": [ 40.0, 320.0, 160.0, 22.0 ]
				}
			}
		],
		"lines": [
			{ "patchline": { "source": [ "obj-recv", 0 ], "destination": [ "obj-route", 0 ] } },
			{ "patchline": { "source": [ "obj-route", 0 ], "destination": [ "obj-trig", 0 ] } },
			{ "patchline": { "source": [ "obj-trig", 0 ], "destination": [ "obj-iter", 0 ] } },
			{ "patchline": { "source": [ "obj-iter", 0 ], "destination": [ "obj-append", 0 ] } },
			{ "patchline": { "source": [ "obj-trig", 1 ], "destination": [ "obj-clearm", 0 ] } },
			{ "patchline": { "source": [ "obj-clearm", 0 ], "destination": [ "obj-menu", 0 ] } },
			{ "patchline": { "source": [ "obj-append", 0 ], "destination": [ "obj-menu", 0 ] } },
			{ "patchline": { "source": [ "obj-menu", 0 ], "destination": [ "obj-selpre", 0 ] } },
			{ "patchline": { "source": [ "obj-selpre", 0 ], "destination": [ "obj-send", 0 ] } },
			{ "patchline": { "source": [ "obj-load", 0 ], "destination": [ "obj-refbtn", 0 ] } },
			{ "patchline": { "source": [ "obj-refbtn", 0 ], "destination": [ "obj-send", 0 ] } }
		]
	}
}

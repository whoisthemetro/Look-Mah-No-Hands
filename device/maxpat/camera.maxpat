{
	"patcher": {
		"fileversion": 1,
		"appversion": { "major": 8, "minor": 6, "revision": 0, "architecture": "x64", "modernui": 1 },
		"classnamespace": "box",
		"rect": [ 80.0, 100.0, 720.0, 600.0 ],
		"boxes": [
			{ "box": { "id": "obj-c", "maxclass": "comment", "numinlets": 1, "numoutlets": 0, "patching_rect": [ 40.0, 16.0, 600.0, 20.0 ], "text": "Look Mah, No Hands - camera monitor + gesture meters. Click getvdevlist, type your camera's number." } },
			{ "box": { "id": "obj-load", "maxclass": "newobj", "numinlets": 1, "numoutlets": 1, "outlettype": [ "bang" ], "patching_rect": [ 120.0, 50.0, 64.0, 22.0 ], "text": "loadbang" } },
			{ "box": { "id": "obj-on", "maxclass": "message", "numinlets": 2, "numoutlets": 1, "outlettype": [ "" ], "patching_rect": [ 120.0, 84.0, 30.0, 22.0 ], "text": "1" } },
			{ "box": { "id": "obj-tog", "maxclass": "toggle", "numinlets": 1, "numoutlets": 1, "outlettype": [ "int" ], "patching_rect": [ 40.0, 84.0, 24.0, 24.0 ], "presentation": 1, "presentation_rect": [ 10.0, 258.0, 24.0, 24.0 ] } },
			{ "box": { "id": "obj-met", "maxclass": "newobj", "numinlets": 2, "numoutlets": 1, "outlettype": [ "bang" ], "patching_rect": [ 40.0, 120.0, 64.0, 22.0 ], "text": "metro 33" } },
			{ "box": { "id": "obj-grab", "maxclass": "newobj", "numinlets": 1, "numoutlets": 2, "outlettype": [ "jit_matrix", "" ], "patching_rect": [ 40.0, 156.0, 110.0, 22.0 ], "text": "jit.grab 640 480" } },
			{ "box": { "id": "obj-pwin", "maxclass": "jit.pwindow", "numinlets": 1, "numoutlets": 1, "outlettype": [ "" ], "patching_rect": [ 40.0, 200.0, 320.0, 240.0 ], "presentation": 1, "presentation_rect": [ 10.0, 10.0, 320.0, 240.0 ] } },
			{ "box": { "id": "obj-getlist", "maxclass": "message", "numinlets": 2, "numoutlets": 1, "outlettype": [ "" ], "patching_rect": [ 420.0, 84.0, 90.0, 22.0 ], "text": "getvdevlist", "presentation": 1, "presentation_rect": [ 44.0, 258.0, 90.0, 22.0 ] } },
			{ "box": { "id": "obj-num", "maxclass": "number", "numinlets": 1, "numoutlets": 2, "outlettype": [ "", "bang" ], "patching_rect": [ 420.0, 120.0, 60.0, 22.0 ], "presentation": 1, "presentation_rect": [ 144.0, 258.0, 60.0, 22.0 ] } },
			{ "box": { "id": "obj-vdev", "maxclass": "message", "numinlets": 2, "numoutlets": 1, "outlettype": [ "" ], "patching_rect": [ 420.0, 156.0, 160.0, 22.0 ], "text": "close, vdevice $1, open", "presentation": 1, "presentation_rect": [ 214.0, 258.0, 116.0, 22.0 ] } },
			{ "box": { "id": "obj-print", "maxclass": "newobj", "numinlets": 1, "numoutlets": 0, "patching_rect": [ 600.0, 156.0, 80.0, 22.0 ], "text": "print VDEV" } },

			{ "box": { "id": "obj-status", "maxclass": "newobj", "numinlets": 1, "numoutlets": 1, "outlettype": [ "" ], "patching_rect": [ 400.0, 320.0, 110.0, 22.0 ], "text": "udpreceive 7401" } },
			{ "box": { "id": "obj-sroute", "maxclass": "newobj", "numinlets": 1, "numoutlets": 3, "outlettype": [ "", "", "" ], "patching_rect": [ 400.0, 356.0, 230.0, 22.0 ], "text": "route /status/meters /status/face" } },
			{ "box": { "id": "obj-meters", "maxclass": "multislider", "numinlets": 1, "numoutlets": 2, "outlettype": [ "", "" ], "patching_rect": [ 400.0, 396.0, 160.0, 80.0 ], "size": 3, "candicane2": [ 0.4, 0.85, 0.4, 1.0 ], "setminmax": [ 0.0, 1.0 ], "contdata": 1, "presentation": 1, "presentation_rect": [ 10.0, 292.0, 200.0, 60.0 ] } },
			{ "box": { "id": "obj-mlabel", "maxclass": "comment", "numinlets": 1, "numoutlets": 0, "patching_rect": [ 400.0, 480.0, 200.0, 18.0 ], "text": "play/stop   record   undo", "presentation": 1, "presentation_rect": [ 10.0, 354.0, 200.0, 18.0 ] } },
			{ "box": { "id": "obj-face", "maxclass": "led", "numinlets": 1, "numoutlets": 1, "outlettype": [ "int" ], "patching_rect": [ 600.0, 396.0, 24.0, 24.0 ], "presentation": 1, "presentation_rect": [ 230.0, 300.0, 24.0, 24.0 ] } },
			{ "box": { "id": "obj-flabel", "maxclass": "comment", "numinlets": 1, "numoutlets": 0, "patching_rect": [ 600.0, 424.0, 80.0, 18.0 ], "text": "face", "presentation": 1, "presentation_rect": [ 260.0, 302.0, 60.0, 18.0 ] } }
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
			{ "patchline": { "source": [ "obj-vdev", 0 ], "destination": [ "obj-grab", 0 ] } },
			{ "patchline": { "source": [ "obj-status", 0 ], "destination": [ "obj-sroute", 0 ] } },
			{ "patchline": { "source": [ "obj-sroute", 0 ], "destination": [ "obj-meters", 0 ] } },
			{ "patchline": { "source": [ "obj-sroute", 1 ], "destination": [ "obj-face", 0 ] } }
		]
	}
}

"""Camera picker: choose your camera from a live preview, save it for the detector.

Scans available cameras, lets you flip between them and see a live thumbnail,
then writes your choice to settings.json (which config.py reads). Works for any
webcam / iPhone / capture source — no need to know OpenCV index numbers.

    detector/.venv/bin/python detector/camera_picker.py
"""

from __future__ import annotations

import json
import tkinter as tk
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

import cameras
import config

PREVIEW_W, PREVIEW_H = 480, 360


def find_cameras():
    return cameras.find_cameras()


class PickerApp:
    def __init__(self, root):
        self.root = root
        root.title("Look Mah, No Hands - choose your camera")
        self.cap = None
        self.cam_index = None

        self.cameras = find_cameras()

        top = ttk.Frame(root, padding=10)
        top.pack(fill="x")
        ttk.Label(top, text="Camera:").pack(side="left")

        self.combo = ttk.Combobox(top, state="readonly", width=28,
                                   values=[label for _, label in self.cameras])
        self.combo.pack(side="left", padx=8)
        self.combo.bind("<<ComboboxSelected>>", self.on_select)

        self.preview = ttk.Label(root)
        self.preview.pack(padx=10, pady=10)

        bottom = ttk.Frame(root, padding=10)
        bottom.pack(fill="x")
        self.status = ttk.Label(bottom, text="")
        self.status.pack(side="left")
        ttk.Button(bottom, text="Use this camera", command=self.save).pack(side="right")

        if self.cameras:
            # Preselect the saved camera if it's present, else the first.
            idx = next((n for n, (i, _) in enumerate(self.cameras)
                        if i == config.CAM_INDEX), 0)
            self.combo.current(idx)
            self.open_camera(self.cameras[idx][0])
        else:
            self.status.config(text="No cameras found. Connect one and reopen.")

        self.update_preview()
        root.protocol("WM_DELETE_WINDOW", self.close)

    def on_select(self, _evt):
        i = self.cameras[self.combo.current()][0]
        self.open_camera(i)

    def open_camera(self, index):
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(index)
        self.cam_index = index
        self.status.config(text=f"Previewing camera {index}")

    def update_preview(self):
        if self.cap is not None:
            ok, frame = self.cap.read()
            if ok and frame is not None:
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb).resize((PREVIEW_W, PREVIEW_H))
                photo = ImageTk.PhotoImage(img)
                self.preview.configure(image=photo)
                self.preview.image = photo  # keep a reference
        self.root.after(33, self.update_preview)

    def save(self):
        if self.cam_index is None:
            return
        data = {"cam_index": int(self.cam_index), "cam_rotate": config.CAM_ROTATE}
        config.SETTINGS_PATH.write_text(json.dumps(data, indent=2) + "\n")
        self.status.config(text=f"Saved camera {self.cam_index}. You can close this.")

    def close(self):
        if self.cap is not None:
            self.cap.release()
        self.root.destroy()


def main():
    root = tk.Tk()
    PickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

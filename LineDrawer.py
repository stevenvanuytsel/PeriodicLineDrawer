# %%
import numpy as np
from skimage.feature import blob_dog
from scipy.optimize import curve_fit
from scipy.spatial.distance import cdist
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
%matplotlib qt

# %%
class LineDrawer:
    def __init__(self, image=None, max_lines=None):
        self.image = image
        self.max_lines = max_lines
        self.lines = []

        self.start_point = None
        self.end_point = None
        self.anchor_start = None
        self.anchor_end = None
        self.fixed_direction = None
        self.fixed_normal = None

        self.pending_artist = None
        self.start_marker = None
        self.end_marker = None

        self.fig, self.ax = plt.subplots()
        if self.image is not None:
            self.ax.imshow(self.image, cmap='gray')
        self.ax.set_title(
            "First line: click start, then end.\n"
            "Subsequent lines: click once to add parallel line.\n"
            "Press 'n' to save, 'd' to discard, close to finish."
        )

        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)

    def on_click(self, event):
        if self.fig.canvas.toolbar.mode != '' or event.inaxes != self.ax or event.button != 1:
            return

        click = np.array([event.xdata, event.ydata])
        print(f"\nCLICK at {event.xdata:.2f}, {event.ydata:.2f}")
        print(f"Current anchor_start: {self.anchor_start}")
        print(f"Current anchor_end: {self.anchor_end}")

        # First ever click
        if self.anchor_start is None and self.start_point is None:
            self.start_point = click
            self.draw_marker(click, marker_type='start')

        # Second click to define first line
        elif self.anchor_start is None and self.start_point is not None:
            self.end_point = click
            self.anchor_start = self.start_point.copy()
            self.anchor_end = self.end_point.copy()
            self.fixed_direction = self.anchor_end - self.anchor_start
            self.fixed_direction /= np.linalg.norm(self.fixed_direction)
            self.fixed_normal = np.array([-self.fixed_direction[1], self.fixed_direction[0]])

            self.draw_marker(click, marker_type='end')
            self.preview_line(self.anchor_start, self.anchor_end)

        # All other clicks → generate parallel line
        else:
            offset_vec = click - self.anchor_start
            offset = np.dot(offset_vec, self.fixed_normal)
            self.start_point = self.anchor_start + offset * self.fixed_normal
            self.end_point = self.anchor_end + offset * self.fixed_normal

            print("Generating parallel line...")
            print(f"Offset from anchor: {offset}")
            self.draw_marker(click, marker_type='start')
            self.preview_line(self.start_point, self.end_point)
    
    def preview_line(self, start, end):
        print(f"Previewing line from {start} to {end}")
        print(f"Line length: {np.linalg.norm(end - start):.2f}")
        if self.pending_artist:
            self.pending_artist.remove()
        self.pending_artist, = self.ax.plot(
            [start[0], end[0]], [start[1], end[1]],
            linestyle='--', color='yellow'
        )
        self.fig.canvas.draw()

    def on_key(self, event):
        if event.key == 'n':
            self.save_line()
        elif event.key == 'd':
            self.delete_line()

    def save_line(self):
        print(f"Trying to save: start={self.start_point}, end={self.end_point}")
        if self.start_point is None or self.end_point is None:
            print("No line to save.")
            return
        self.lines.append((self.start_point.copy(), self.end_point.copy()))
        print(f"Saved line #{len(self.lines)}")
        self.ax.plot(
            [self.start_point[0], self.end_point[0]],
            [self.start_point[1], self.end_point[1]],
            color='cyan'
        )
        self.cleanup_pending()
        self.fig.canvas.draw()
        if self.max_lines and len(self.lines) >= self.max_lines:
            print("Reached max_lines, exiting.")
            plt.close(self.fig)

    def delete_line(self):
        print("Line discarded.")
        self.cleanup_pending()
        self.fig.canvas.draw()

    def cleanup_pending(self):
        self.start_point = None
        self.end_point = None
        if self.pending_artist:
            self.pending_artist.remove()
            self.pending_artist = None
        if self.start_marker:
            self.start_marker.remove()
            self.start_marker = None
        if self.end_marker:
            self.end_marker.remove()
            self.end_marker = None

    def draw_marker(self, point, marker_type='start'):
        if marker_type == 'start':
            if self.start_marker:
                self.start_marker.remove()
            self.start_marker = self.ax.plot(
                point[0], point[1], marker='+', color='red', markersize=10
            )[0]
        elif marker_type == 'end':
            if self.end_marker:
                self.end_marker.remove()
            self.end_marker = self.ax.plot(
                point[0], point[1], marker='x', color='red', markersize=10
            )[0]
        self.fig.canvas.draw()

    def get_lines(self):
        return self.lines


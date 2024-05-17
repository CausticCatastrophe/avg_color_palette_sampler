import os
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from collections import deque
from math import sqrt
import numpy as np

def load_stac_chart():
    """Load the STAC Chart from an Excel file."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_file = os.path.join(script_dir, 'data', 'Cel Animation Color Charts.xlsx')
    df = pd.read_excel(data_file, sheet_name='STAC Chart (wide gamut)')
    stac_chart = {row['Code']: hex_to_rgb(row['Hex (sRGB)']) for _, row in df.iterrows() if isinstance(row['Hex (sRGB)'], str)}
    return stac_chart

def hex_to_rgb(hex_color):
    """Convert HEX color to RGB tuple."""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def average_colors(colors):
    """Averages a list of colors given in RGB format."""
    valid_colors = [color for color in colors if len(color) == 3]
    if not valid_colors:
        return (0, 0, 0)  # Return black if no valid colors are present

    colors_array = np.array(valid_colors)
    medians = np.median(colors_array, axis=0)
    abs_devs = np.abs(colors_array - medians)
    mad = np.median(abs_devs, axis=0)
    filtered_colors = [color for color in colors_array if np.all(np.abs(color - medians) <= 4 * mad)]

    if not filtered_colors:
        return (0, 0, 0)

    avg_color = np.mean(filtered_colors, axis=0).astype(int)
    return tuple(avg_color)

def color_distance(c1, c2):
    """Calculate the Euclidean distance between two colors."""
    return sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))

def find_closest_color(rgb, stac_chart):
    """Find the closest color in the STAC chart to the given RGB color."""
    closest_color, min_distance = min(stac_chart.items(), key=lambda item: color_distance(rgb, item[1]))
    return closest_color, stac_chart[closest_color]

class ImageCanvas(tk.Canvas):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.image = None
        self.photo_image = None
        self.zoom_factor = 1.0
        self.bind("<Button-1>", self.on_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<MouseWheel>", self.on_mousewheel)
        self.bind("<ButtonPress-2>", self.on_middle_button_press)
        self.bind("<B2-Motion>", self.on_middle_button_move)
        self.bind("<Configure>", self.on_resize)
        self.rect = None
        self.start_x = None
        self.start_y = None

    def set_image(self, image_path):
        """Load and display the image."""
        try:
            self.image = Image.open(image_path)
            self.zoom_factor = self.calculate_initial_zoom()
            self.update_image_display()
            print(f"Image loaded: {image_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")

    def calculate_initial_zoom(self):
        """Calculate the initial zoom factor to fit the image to the window size."""
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        image_width, image_height = self.image.size
        return min(canvas_width / image_width, canvas_height / image_height)

    def on_resize(self, event):
        """Handle the resizing of the canvas."""
        self.update_image_display()

    def on_click(self, event):
        """Handle mouse click on the canvas to start selection."""
        self.start_x = self.canvasx(event.x)
        self.start_y = self.canvasy(event.y)
        self.rect = self.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_drag(self, event):
        """Handle mouse drag to draw the selection rectangle."""
        if self.rect:
            self.coords(self.rect, self.start_x, self.start_y, self.canvasx(event.x), self.canvasy(event.y))

    def on_release(self, event):
        """Handle mouse release to finalize the selection."""
        if self.rect:
            self.delete(self.rect)
            self.rect = None
            x0, y0, x1, y1 = self.start_x, self.start_y, self.canvasx(event.x), self.canvasy(event.y)
            self.select_colors_in_rect(x0, y0, x1, y1)
            self.start_x = self.start_y = None

    def select_colors_in_rect(self, x0, y0, x1, y1):
        """Select and average colors within the given rectangle."""
        if self.image:
            bbox = self.bbox(self.find_withtag("image"))
            x0 = (x0 - bbox[0]) / self.zoom_factor
            y0 = (y0 - bbox[1]) / self.zoom_factor
            x1 = (x1 - bbox[0]) / self.zoom_factor
            y1 = (y1 - bbox[1]) / self.zoom_factor

            x0, x1 = sorted([int(x0), int(x1)])
            y0, y1 = sorted([int(y0), int(y1)])

            selected_colors = []
            for x in range(x0, x1):
                for y in range(y0, y1):
                    if 0 <= x < self.image.width and 0 <= y < self.image.height:
                        rgba = self.image.getpixel((x, y))
                        rgb = rgba[:3]
                        selected_colors.append(rgb)

            if selected_colors:
                avg_color = average_colors(selected_colors)
                if len(self.app.colors) >= 1024:
                    self.app.colors.popleft()
                self.app.colors.append(avg_color)
                self.app.update_visualization()
                self.app.update_average_color()

    def on_mousewheel(self, event):
        """Handle mouse wheel for zooming."""
        scale = 1.1 if event.delta > 0 else 0.9
        self.zoom(scale, event.x, event.y)

    def on_middle_button_press(self, event):
        """Handle middle button press for panning."""
        self.scan_mark(event.x, event.y)

    def on_middle_button_move(self, event):
        """Handle middle button movement for panning."""
        self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, factor, x=None, y=None):
        """Zoom in or out on the image."""
        self.zoom_factor *= factor
        if x is not None and y is not None:
            self.scale("all", self.canvasx(x), self.canvasy(y), factor, factor)
        else:
            self.scale("all", 0, 0, factor, factor)
        self.update_image_display()

    def update_image_display(self):
        """Update the image display on the canvas."""
        if self.image:
            resized_image = self.image.resize((int(self.image.width * self.zoom_factor),
                                               int(self.image.height * self.zoom_factor)),
                                              Image.LANCZOS)
            self.photo_image = ImageTk.PhotoImage(resized_image)
            self.delete("all")
            self.create_image(0, 0, image=self.photo_image, anchor=tk.NW, tags="image")
            self.configure(scrollregion=self.bbox("all"))

class ColorSamplerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.colors = deque(maxlen=1024)
        self.palette = []
        self.stac_chart = load_stac_chart()
        self.geometry("1000x600")
        self.title("Image Color Sampler")
        self.create_widgets()

    def quantize_to_stac(self):
        """Quantize the sampled colors to the closest STAC Chart colors."""
        quantized_colors = [
            (21, 21, 21) if color == (0, 0, 0) else
            (252, 252, 252) if color == (255, 255, 255) else
            find_closest_color(color, self.stac_chart)[1]
            for color in self.colors
        ]
        self.colors = deque(quantized_colors, maxlen=1024)
        self.update_visualization()
        self.update_average_color()

    def create_widgets(self):
        """Create and arrange widgets in the app."""
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.create_palette_area(top_frame)
        self.create_buttons(top_frame)

        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = ImageCanvas(frame, self, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar_y.set)

        self.create_visualization_area()

    def create_palette_area(self, top_frame):
        """Create the palette visualization area."""
        palette_frame = tk.Frame(top_frame)
        palette_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        tk.Label(palette_frame, text="Palette", font=("Arial", 14)).pack()
        self.palette_canvas = tk.Canvas(palette_frame, height=60)
        self.palette_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.palette_visualization = tk.Frame(self.palette_canvas)
        self.scrollbar_palette = tk.Scrollbar(palette_frame, orient="horizontal", command=self.palette_canvas.xview)
        self.scrollbar_palette.pack(side=tk.BOTTOM, fill=tk.X)
        self.palette_canvas.configure(xscrollcommand=self.scrollbar_palette.set)
        self.palette_canvas.create_window((0, 0), window=self.palette_visualization, anchor="nw")
        self.palette_visualization.bind("<Configure>", self.update_palette_scrollregion)

    def create_buttons(self, top_frame):
        """Create buttons for various actions."""
        button_frame = tk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.X, padx=10)

        tk.Button(button_frame, text="Open Image", command=self.load_image).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Clear Colors", command=self.clear_colors).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Save Palette", command=self.save_palette).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Save Palette as Image", command=self.save_palette_as_image).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Quantize to STAC", command=self.quantize_to_stac).pack(side=tk.LEFT, padx=10)

    def create_visualization_area(self):
        """Create the visualization area for sampled colors."""
        right_frame = tk.Frame(self, width=85)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        avg_frame = tk.Frame(right_frame)
        avg_frame.pack(fill=tk.X, pady=(10, 0))
        self.result_label = tk.Label(avg_frame, text="", font=("Arial", 16))
        self.result_label.pack(pady=(0, 10))
        self.add_to_palette_button = tk.Button(avg_frame, text="Add to Palette", width=20, height=2, command=self.add_avg_color_to_palette)
        self.add_to_palette_button.pack()

        divider = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
        divider.pack(fill=tk.X, pady=(0, 10))

        sampled_colors_frame = tk.Frame(right_frame)
        sampled_colors_frame.pack(fill=tk.BOTH, expand=True)

        self.visualization_canvas = tk.Canvas(sampled_colors_frame, width=150)
        self.visualization_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.color_visualization = tk.Frame(self.visualization_canvas)
        self.scrollbar_visualization = tk.Scrollbar(sampled_colors_frame, orient="vertical", command=self.visualization_canvas.yview)
        self.scrollbar_visualization.pack(side=tk.RIGHT, fill=tk.Y)
        self.visualization_canvas.configure(yscrollcommand=self.scrollbar_visualization.set)
        self.visualization_canvas.create_window((0, 0), window=self.color_visualization, anchor="nw")
        self.color_visualization.bind("<Configure>", self.update_scrollregion)
        self.visualization_canvas.bind_all("<MouseWheel>", self._on_mousewheel_scroll)

        tk.Label(self.color_visualization, text="Sampled Colors", font=("Arial", 14)).pack()

    def update_scrollregion(self, event=None):
        """Update the scroll region of the visualization canvas."""
        self.visualization_canvas.configure(scrollregion=self.visualization_canvas.bbox("all"))
        if self.visualization_canvas.bbox("all")[3] <= self.visualization_canvas.winfo_height():
            self.visualization_canvas.unbind_all("<MouseWheel>")
        else:
            self.visualization_canvas.bind_all("<MouseWheel>", self._on_mousewheel_scroll)

    def update_palette_scrollregion(self, event=None):
        """Update the scroll region of the palette canvas."""
        self.palette_canvas.configure(scrollregion=self.palette_canvas.bbox("all"))

    def _on_mousewheel_scroll(self, event):
        """Scroll the visualization canvas using the mouse wheel."""
        self.visualization_canvas.yview_scroll(-1 * (event.delta // 120), "units")

    def update_visualization(self):
        """Update the visualization pane with the sampled colors."""
        for widget in self.color_visualization.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        for i, color in enumerate(self.colors):
            color_hex = '#{:02x}{:02x}{:02x}'.format(*color)
            frame = tk.Frame(self.color_visualization, width=100, height=30)
            frame.pack_propagate(False)
            frame.pack(side=tk.TOP, padx=2, pady=2)
            color_label = tk.Label(frame, bg=color_hex, width=2, height=1)
            color_label.pack(fill=tk.BOTH, expand=True)
            color_label.bind("<Button-1>", lambda e, i=i: self.delete_color(i))
        self.update_scrollregion()

    def update_palette(self):
        """Update the palette visualization pane."""
        for widget in self.palette_visualization.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.destroy()
        for i, color in enumerate(self.palette):
            frame = tk.Frame(self.palette_visualization, width=30, height=30)
            frame.pack_propagate(False)
            frame.pack(side=tk.LEFT, padx=2, pady=2)
            color_label = tk.Label(frame, bg=color, width=4, height=2)
            color_label.pack(fill=tk.BOTH, expand=True)
            color_label.bind("<Button-1>", lambda e, color=color, i=i: self.confirm_delete_palette_color(color, i))

    def update_average_color(self):
        """Update the average color display."""
        if self.colors:
            avg_color_hex = '#{:02x}{:02x}{:02x}'.format(*average_colors(self.colors))
            self.result_label.config(text=f"Average Color")
            self.add_to_palette_button.config(bg=avg_color_hex, state=tk.NORMAL)
        else:
            self.result_label.config(text="")
            self.add_to_palette_button.config(bg="white", text="Add to Palette", state=tk.DISABLED)

    def add_avg_color_to_palette(self):
        """Add the current average color to the palette."""
        avg_color = self.add_to_palette_button.cget("bg")
        if avg_color and avg_color != "Add to Palette":
            self.palette.append(avg_color)
            self.update_palette()
            self.clear_colors()

    def copy_to_clipboard(self, color):
        """Copy a color hex value to the clipboard."""
        self.clipboard_clear()
        self.clipboard_append(color)
        messagebox.showinfo("Copied", f"Color {color} copied to clipboard.")

    def confirm_delete_palette_color(self, color, index):
        """Confirm deletion of a color from the palette."""
        if messagebox.askyesno("Delete Color", f"Are you sure you want to delete the color {color} from the palette?"):
            self.delete_palette_color(index)

    def delete_color(self, index):
        """Delete a color at a specific index."""
        self.colors.remove(self.colors[index])
        self.update_visualization()
        self.update_average_color()

    def delete_palette_color(self, index):
        """Delete a color from the palette."""
        del self.palette[index]
        self.update_palette()

    def load_image(self):
        """Open a file dialog to load an image."""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.canvas.set_image(file_path)

    def clear_colors(self):
        """Clear all sampled colors."""
        self.colors.clear()
        self.update_visualization()
        self.update_average_color()

    def save_palette(self):
        """Save the palette to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'w') as file:
                    file.write('\n'.join(self.palette))
                messagebox.showinfo("Success", f"Palette saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save palette: {e}")

    def save_palette_as_image(self):
        """Save the palette as an image file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("All files", "*.*")])
        if file_path:
            try:
                font = ImageFont.load_default()
                max_width = 300
                bar_height = 30
                image_height = bar_height * len(self.palette)
                image = Image.new('RGB', (max_width, image_height), 'white')
                draw = ImageDraw.Draw(image)

                for i, color in enumerate(self.palette):
                    rgb_color = tuple(int(color[j:j+2], 16) for j in (1, 3, 5))
                    y0 = i * bar_height
                    y1 = y0 + bar_height
                    draw.rectangle([0, y0, max_width - 100, y1], fill=rgb_color)
                    draw.text((max_width - 90, y0 + 5), color, fill='black', font=font)

                image.save(file_path)
                messagebox.showinfo("Success", f"Palette image saved to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save palette image: {e}")

if __name__ == "__main__":
    app = ColorSamplerApp()
    app.mainloop()

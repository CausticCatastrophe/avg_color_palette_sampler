import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from collections import deque

def average_colors(colors):
    """Averages a list of colors given in RGB format."""
    r = g = b = 0
    for color in colors:
        r += color[0]
        g += color[1]
        b += color[2]
    n = len(colors)
    avg_color = (r // n, g // n, b // n)
    return '#{:02x}{:02x}{:02x}'.format(avg_color[0], avg_color[1], avg_color[2])

class ImageCanvas(tk.Canvas):
    def __init__(self, master, app, **kwargs):
        super().__init__(master, **kwargs)
        self.app = app
        self.bind("<Button-1>", self.on_click)
        self.bind("<MouseWheel>", self.on_mousewheel)
        self.bind("<ButtonPress-2>", self.on_middle_button_press)
        self.bind("<B2-Motion>", self.on_middle_button_move)
        self.bind("<Configure>", self.on_resize)
        self.image = None
        self.photo_image = None
        self.zoom_factor = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0

    def set_image(self, image_path):
        try:
            self.image = Image.open(image_path)
            self.zoom_factor = self.calculate_initial_zoom()
            self.update_image_display()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image: {e}")

    def calculate_initial_zoom(self):
        """Calculate the initial zoom factor to fit the image to the window size."""
        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()
        image_width, image_height = self.image.size
        scale = min(canvas_width / image_width, canvas_height / image_height)
        return scale

    def on_resize(self, event):
        """Handle the resizing of the canvas."""
        self.update_image_display()

    def on_click(self, event):
        if self.image:
            bbox = self.bbox(self.find_withtag("image"))
            x = (self.canvasx(event.x) - bbox[0]) / self.zoom_factor
            y = (self.canvasy(event.y) - bbox[1]) / self.zoom_factor
            if 0 <= x < self.image.width and 0 <= y < self.image.height:
                rgb = self.image.getpixel((int(x), int(y)))
                if len(self.app.colors) >= 64:
                    self.app.colors.popleft()
                self.app.colors.append(rgb)
                self.app.update_visualization()
                self.app.update_average_color()
        else:
            self.app.load_image()

    def on_mousewheel(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.zoom(scale, event.x, event.y)

    def on_middle_button_press(self, event):
        self.scan_mark(event.x, event.y)

    def on_middle_button_move(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, factor, x=None, y=None):
        self.zoom_factor *= factor
        if x is not None and y is not None:
            self.scale("all", self.canvasx(x), self.canvasy(y), factor, factor)
        else:
            self.scale("all", 0, 0, factor, factor)
        self.update_image_display()

    def update_image_display(self):
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
        self.colors = deque(maxlen=64)
        self.palette = []
        self.geometry("1000x600")
        self.title("Image Color Sampler")
        self.create_widgets()

    def create_widgets(self):
        # Top frame for palette and buttons
        top_frame = tk.Frame(self)
        top_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        # Palette visualization
        palette_frame = tk.Frame(top_frame)
        palette_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        tk.Label(palette_frame, text="Palette", font=("Arial", 14)).pack()
        self.palette_canvas = tk.Canvas(palette_frame, height=60)  # Fixed height for the palette canvas
        self.palette_canvas.pack(side=tk.TOP, fill=tk.X, expand=True)
        self.palette_visualization = tk.Frame(self.palette_canvas)
        self.scrollbar_palette = tk.Scrollbar(palette_frame, orient="horizontal", command=self.palette_canvas.xview)
        self.scrollbar_palette.pack(side=tk.BOTTOM, fill=tk.X)
        self.palette_canvas.configure(xscrollcommand=self.scrollbar_palette.set)
        self.palette_canvas.create_window((0, 0), window=self.palette_visualization, anchor="nw")
        self.palette_visualization.bind("<Configure>", self.update_palette_scrollregion)

        # Buttons
        button_frame = tk.Frame(top_frame)
        button_frame.pack(side=tk.RIGHT, fill=tk.X, padx=10)

        open_image_button = tk.Button(button_frame, text="Open Image", command=self.load_image)
        open_image_button.pack(side=tk.LEFT, padx=10)

        clear_colors_button = tk.Button(button_frame, text="Clear Colors", command=self.clear_colors)
        clear_colors_button.pack(side=tk.LEFT, padx=10)

        frame = tk.Frame(self)
        frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = ImageCanvas(frame, self, bg='white')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_y = tk.Scrollbar(frame, orient="vertical", command=self.canvas.yview)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.configure(yscrollcommand=scrollbar_y.set)

        # Right frame for visualizations (narrower than before)
        right_frame = tk.Frame(self, width=85)  # Reduced width
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        # Average color display
        avg_frame = tk.Frame(right_frame)
        avg_frame.pack(fill=tk.X, pady=(10, 0))
        self.result_label = tk.Label(avg_frame, text="", font=("Arial", 16))
        self.result_label.pack(pady=(0, 10))
        self.add_to_palette_button = tk.Button(avg_frame, text="Add to Palette", width=20, height=2, command=self.add_avg_color_to_palette)
        self.add_to_palette_button.pack()

        # Divider
        divider = tk.Frame(right_frame, height=2, bd=1, relief=tk.SUNKEN)
        divider.pack(fill=tk.X, pady=(0, 10))

        # Scrollable area for sampled colors
        sampled_colors_frame = tk.Frame(right_frame)
        sampled_colors_frame.pack(fill=tk.BOTH, expand=True)

        self.visualization_canvas = tk.Canvas(sampled_colors_frame, width=150)  # Reduced width
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
            color_hex = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
            frame = tk.Frame(self.color_visualization, width=100, height=30)  # Small square for color preview
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
            frame = tk.Frame(self.palette_visualization, width=30, height=30)  # Fixed size for the palette squares
            frame.pack_propagate(False)
            frame.pack(side=tk.LEFT, padx=2, pady=2)
            color_label = tk.Label(frame, bg=color, width=4, height=2)
            color_label.pack(fill=tk.BOTH, expand=True)
            color_label.bind("<Button-1>", lambda e, color=color, i=i: self.confirm_delete_palette_color(color, i))

    def update_average_color(self):
        """Update the average color display."""
        if self.colors:
            avg_color = average_colors(self.colors)
            self.result_label.config(text=f"Average Color")
            self.add_to_palette_button.config(bg=avg_color, state=tk.NORMAL)
        else:
            self.result_label.config(text="")
            self.add_to_palette_button.config(bg="white", text="Add to Palette", state=tk.DISABLED)

    def add_avg_color_to_palette(self):
        """Add the current average color to the palette."""
        avg_color = self.add_to_palette_button.cget("bg")
        if avg_color and avg_color != "Add to Palette":
            self.palette.append(avg_color)
            self.update_palette()
            self.clear_colors()  # Clear the sampled colors after adding to palette

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
        file_path = filedialog.askopenfilename()
        if file_path:
            self.canvas.set_image(file_path)

    def clear_colors(self):
        self.colors.clear()
        self.update_visualization()
        self.update_average_color()

if __name__ == "__main__":
    app = ColorSamplerApp()
    app.mainloop()

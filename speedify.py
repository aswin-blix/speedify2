import tkinter as tk
import psutil
import time
import threading
from math import floor

class ModernCanvas(tk.Canvas):
    """Modern canvas with gradient and blur effects"""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.create_modern_background()
    
    def create_modern_background(self):
        """Create modern background with gradient and depth effects"""
        # Main background with gradient effect
        self.create_rounded_rectangle(0, 0, self.winfo_reqwidth(), self.winfo_reqheight(), 
                                    radius=16, fill='#1a1a1a', outline='#333333', width=1, tags='main_bg')
        
        # Inner glow effect
        self.create_rounded_rectangle(2, 2, self.winfo_reqwidth()-2, self.winfo_reqheight()-2, 
                                    radius=14, fill='#222222', outline='#444444', width=1, tags='inner_glow')
        
        # Top highlight for modern look
        self.create_rounded_rectangle(3, 3, self.winfo_reqwidth()-3, 20, 
                                    radius=13, fill='#2a2a2a', outline='', tags='highlight')

    def create_rounded_rectangle(self, x1, y1, x2, y2, radius=25, **kwargs):
        """Create a rounded rectangle on the canvas"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return self.create_polygon(points, **kwargs, smooth=True)

class NetworkSpeedMonitor:
    def __init__(self, root):
        self.root = root
        self.root.title("Speedify")
        self.root.overrideredirect(True)  # Remove window decorations
        self.root.wm_attributes("-topmost", True)  # Keep on top
        self.root.attributes("-alpha", 0.95)  # Slight transparency
        
        # Modern color scheme
        self.bg_color = "#1a1a1a"
        self.card_color = "#222222"
        self.border_color = "#444444"
        self.dl_color = "#00D4AA"  # Modern teal
        self.ul_color = "#FF6B6B"  # Modern coral
        self.text_color = "#FFFFFF"
        self.secondary_text = "#AAAAAA"
        self.accent_color = "#4A90E2"  # Modern blue
        
        # Window size - optimized for modern design
        self.window_width = 320
        self.window_height = 60
        
        # Center the window initially
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - self.window_width) // 2
        y = (screen_height - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        
        # Main frame
        self.frame = tk.Frame(root, bg='black', bd=0)
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Modern canvas
        self.canvas = ModernCanvas(self.frame, bg='black', highlightthickness=0, 
                                 width=self.window_width, height=self.window_height)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Modern close button
        self.create_modern_close_button()
        
        # Modern speed display
        self.create_modern_speed_display()
        
        # Dragging functionality
        self.root.bind("<ButtonPress-1>", self.start_move)
        self.root.bind("<ButtonRelease-1>", self.stop_move)
        self.root.bind("<B1-Motion>", self.do_move)
        
        # Prevent dragging when clicking the close button
        self.close_button.bind("<ButtonPress-1>", lambda e: e.widget.event_generate("<<CloseButton>>"))
        self.root.bind("<<CloseButton>>", lambda e: "break")

        # Network Speed Tracking
        self.initial_bytes = self.get_network_bytes()
        self.last_time = time.time()
        self.download_history = []
        self.upload_history = []
        self.sample_window = 10

        # Start monitoring
        self.monitoring = True
        self.network_thread = threading.Thread(target=self.update_network_speed, daemon=True)
        self.network_thread.start()

    def create_modern_close_button(self):
        """Create a modern close button with hover effects"""
        # Close button background
        self.canvas.create_oval(self.window_width-35, 12, self.window_width-12, 35, 
                               fill=self.card_color, outline=self.border_color, width=1, tags='close_bg')
        
        # Close button text
        self.close_button = tk.Button(self.canvas, text="×", font=("SF Pro Display", 14, "bold"),
                                    bg=self.card_color, fg=self.text_color, 
                                    borderwidth=0, command=self.exit_app,
                                    cursor="hand2", activebackground='#FF6B6B',
                                    activeforeground='#FFFFFF')
        self.close_button.place(x=self.window_width-30, y=10)
        
        # Hover effects
        self.close_button.bind("<Enter>", self.on_close_hover)
        self.close_button.bind("<Leave>", self.on_close_leave)

    def create_modern_speed_display(self):
        """Create modern speed display with cards"""
        # Download card
        dl_card_x = 20
        dl_card_y = 15
        dl_card_width = 120
        dl_card_height = 35
        
        # Download card background
        self.canvas.create_rounded_rectangle(dl_card_x, dl_card_y, 
                                           dl_card_x + dl_card_width, dl_card_y + dl_card_height,
                                           radius=10, fill=self.card_color, outline=self.border_color, width=1)
        
        # Download label
        self.download_label = tk.Label(self.canvas, text="↓ 0.0", 
                                     font=("SF Pro Display", 13, "bold"), bg=self.card_color, 
                                     fg=self.dl_color, padx=15, pady=5)
        self.download_label.place(x=dl_card_x + 10, y=dl_card_y + 8)
        
        # Download unit
        dl_unit_label = tk.Label(self.canvas, text="Mbps", 
                               font=("SF Pro Display", 9), bg=self.card_color, 
                               fg=self.secondary_text)
        dl_unit_label.place(x=dl_card_x + 85, y=dl_card_y + 10)

        # Upload card
        ul_card_x = 160
        ul_card_y = 15
        ul_card_width = 120
        ul_card_height = 35
        
        # Upload card background
        self.canvas.create_rounded_rectangle(ul_card_x, ul_card_y, 
                                           ul_card_x + ul_card_width, ul_card_y + ul_card_height,
                                           radius=10, fill=self.card_color, outline=self.border_color, width=1)
        
        # Upload label
        self.upload_label = tk.Label(self.canvas, text="↑ 0.0", 
                                   font=("SF Pro Display", 13, "bold"), bg=self.card_color, 
                                   fg=self.ul_color, padx=15, pady=5)
        self.upload_label.place(x=ul_card_x + 10, y=ul_card_y + 8)
        
        # Upload unit
        ul_unit_label = tk.Label(self.canvas, text="Mbps", 
                               font=("SF Pro Display", 9), bg=self.card_color, 
                               fg=self.secondary_text)
        ul_unit_label.place(x=ul_card_x + 85, y=ul_card_y + 10)

    def on_close_hover(self, event):
        """Handle close button hover effect"""
        self.close_button.config(fg='#FFFFFF', bg='#FF6B6B')
        self.canvas.itemconfig('close_bg', fill='#FF6B6B')

    def on_close_leave(self, event):
        """Handle close button leave effect"""
        self.close_button.config(fg=self.text_color, bg=self.card_color)
        self.canvas.itemconfig('close_bg', fill=self.card_color)

    def start_move(self, event):
        """Begin dragging the window"""
        self.x = event.x_root
        self.y = event.y_root

    def stop_move(self, event):
        """Stop dragging the window"""
        self.x = None
        self.y = None

    def do_move(self, event):
        """Handle window dragging"""
        if self.x is None or self.y is None:
            return
        deltax = event.x_root - self.x
        deltay = event.y_root - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
        self.x = event.x_root
        self.y = event.y_root

    def get_network_bytes(self):
        """Get current network bytes for all network interfaces."""
        net_io = psutil.net_io_counters()
        return {'download': net_io.bytes_recv, 'upload': net_io.bytes_sent, 'timestamp': time.time()}

    def calculate_network_speed(self, initial_bytes, current_bytes):
        """Calculate network speed with high accuracy."""
        time_diff = current_bytes['timestamp'] - initial_bytes['timestamp']
        if time_diff <= 0:
            return 0, 0
        download_bytes = current_bytes['download'] - initial_bytes['download']
        upload_bytes = current_bytes['upload'] - initial_bytes['upload']
        download_speed = (download_bytes * 8) / (time_diff * 1024 * 1024)
        upload_speed = (upload_bytes * 8) / (time_diff * 1024 * 1024)
        return download_speed, upload_speed

    def update_network_speed(self):
        """Continuously monitor network speed with smoothing."""
        while self.monitoring:
            try:
                current_bytes = self.get_network_bytes()
                dl_speed, ul_speed = self.calculate_network_speed(self.initial_bytes, current_bytes)
                
                self.download_history.append(dl_speed)
                self.upload_history.append(ul_speed)
                
                if len(self.download_history) > self.sample_window:
                    self.download_history.pop(0)
                    self.upload_history.pop(0)
                
                avg_dl = sum(self.download_history) / len(self.download_history)
                avg_ul = sum(self.upload_history) / len(self.upload_history)
                
                self.root.after(0, self.update_labels, avg_dl, avg_ul)
                self.initial_bytes = current_bytes
                
                elapsed = time.time() - current_bytes['timestamp']
                time.sleep(max(0.1, 1.0 - elapsed))

            except Exception as e:
                print(f"Error: {e}")
                break

    def update_labels(self, download, upload):
        """Update speed labels with dynamic colors and modern styling."""
        dl_text = f"↓ {download:.1f}" if download % 1 else f"↓ {floor(download)}"
        ul_text = f"↑ {upload:.1f}" if upload % 1 else f"↑ {floor(upload)}"
        
        self.download_label.config(text=dl_text)
        self.upload_label.config(text=ul_text)
        
        # Dynamic color intensity based on speed
        dl_intensity = min(100, int(download * 25))
        ul_intensity = min(100, int(upload * 25))
        
        # Enhanced color transitions
        dl_color = self._adjust_color(self.dl_color, dl_intensity)
        ul_color = self._adjust_color(self.ul_color, ul_intensity)
        
        self.download_label.config(fg=dl_color)
        self.upload_label.config(fg=ul_color)

    def _adjust_color(self, hex_color, intensity):
        """Adjust color brightness based on speed intensity with enhanced algorithm"""
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5))
        
        # Enhanced brightness adjustment
        brightness_factor = 1 + (intensity / 100) * 0.6
        r = min(255, int(r * brightness_factor))
        g = min(255, int(g * brightness_factor))
        b = min(255, int(b * brightness_factor))
        
        return f"#{r:02x}{g:02x}{b:02x}"

    def exit_app(self):
        """Clean up and exit the application"""
        self.monitoring = False
        self.root.destroy()

def main():
    root = tk.Tk()
    app = NetworkSpeedMonitor(root)
    root.mainloop()

if __name__ == "__main__":
    main()
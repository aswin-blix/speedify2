# Speedify - Network Speed Monitor

A beautiful, modern network speed monitoring application with glassmorphism UI effects.

## ✨ Features

### 🎨 **Glassmorphism UI**
- **Layered Glass Effects**: Multiple rounded rectangles creating depth and transparency
- **Modern Dark Theme**: Elegant dark color scheme with subtle gradients
- **Rounded Corners**: Smooth, modern rounded rectangles throughout the interface
- **Enhanced Typography**: Segoe UI font for better readability

### 📊 **Network Monitoring**
- **Real-time Speed Tracking**: Monitors download and upload speeds in real-time
- **Dynamic Color Changes**: Speed-based color intensity that brightens with higher speeds
- **Smooth Averaging**: 10-sample moving average for stable readings
- **High Accuracy**: Precise network speed calculations

### 🖱️ **Interactive Elements**
- **Draggable Window**: Click and drag to move the window anywhere on screen
- **Hover Effects**: Close button changes color and background on hover
- **Always on Top**: Stays visible above other applications
- **Minimal Interface**: Clean, distraction-free design

### 🎯 **Color Scheme**
- **Download Speed**: Bright green (`#00E676`) with dynamic intensity
- **Upload Speed**: Bright red (`#FF5252`) with dynamic intensity
- **Background**: Dark gray (`#1a1a1a`) with layered glass effects
- **Text**: White (`#FFFFFF`) for primary text, light gray (`#AAAAAA`) for secondary

## 🚀 Installation

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**:
   ```bash
   python speedify.py
   ```

## 📋 Requirements

- Python 3.6+
- psutil>=5.8.0

## 🎮 Usage

- **Move Window**: Click and drag anywhere on the window to reposition
- **Close Application**: Click the "✕" button in the top-right corner
- **Monitor Speeds**: Watch the real-time download (↓) and upload (↑) speeds
- **Speed Units**: Displayed in Mbps (Megabits per second)

## 🔧 Technical Details

- **Framework**: Tkinter (Python's standard GUI library)
- **Network Monitoring**: psutil for system-level network statistics
- **Threading**: Background thread for continuous speed monitoring
- **Cross-Platform**: Works on Windows, macOS, and Linux

## 🎨 UI Components

### Glassmorphism Effects
- **Layered Background**: Three layers of rounded rectangles creating depth
- **Highlight Effect**: Subtle lighter area at the top for glass-like appearance
- **Smooth Corners**: All elements use rounded rectangles with smooth edges
- **Transparency**: Window-level transparency (95%) for modern look

### Interactive Elements
- **Close Button**: Circular glassmorphism button with hover effects
- **Speed Display**: Main container with glass effect background
- **Separator**: Elegant bullet point separator between speeds
- **Dynamic Colors**: Speed-based color intensity adjustments

## 📱 Window Properties

- **Size**: 280x80 pixels
- **Position**: Centered on screen by default
- **Transparency**: 95% opacity
- **Always on Top**: Stays visible above other applications
- **Borderless**: No window decorations for clean appearance

## 🔄 Performance

- **Low CPU Usage**: Efficient threading and minimal resource consumption
- **Smooth Updates**: 1-second refresh rate with 10-sample averaging
- **Memory Efficient**: No heavy image processing or external dependencies
- **Responsive UI**: Immediate visual feedback for user interactions

---

**Enjoy monitoring your network speeds with style! 🚀**

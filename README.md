# Paint Application

A simple paint application built with Pygame.

## Controls & Features

### Main Toolbar Buttons

- SAVE - Ctrl+S - Save your drawing as PNG
- OPEN - Ctrl+O - Open an existing image
- CANC - Ctrl+N - Clear canvas (new drawing)
- FILL - F - Toggle fill mode (paint bucket)
- RGB - R - Toggle rainbow brush mode
- ↩ - Ctrl+Z - Undo last action
- ↪ - Ctrl+Shift+Z - Redo last undone action
- 🎨 - P - Open color picker

### Brush Sizes

Four circular size selectors at the bottom right:

- Small (4px radius)
- Medium-Small (6px radius)
- Medium (8px radius) - default
- Large (10px radius)

Shortcuts:

- + (Plus) - Increase brush size
- - (Minus) - Decrease brush size

### Color Palette

12 color squares on the left sidebar - click to select.

Quick Select Shortcuts:

- F1 - Black (top-left)
- F2 - White (top-right)
- F3 - Red
- F4 - Magenta
- F5 - Green
- F6 - Yellow
- F7 - Blue
- F8 - Cyan
- F9 - Brown
- F10 - Purple
- F11 - Orange
- F12 - Pink

### Color Picker Window

Press P or click 🎨 to open.

Features:

- Click on the gradient grid to select any color
- Adjust RGB sliders (0-255) for precise control
- Preview your current 12-color palette
- Click any palette slot to edit that color

Color Picker Controls:

- SAVE - Ctrl+S - Save palette changes
- CANCEL - Esc - Discard changes
- DEFAULT PALETTE - Ctrl+D - Reset to original colors

### Drawing Modes

Normal Mode (Default)

- Draw freely with selected color and brush size
- Smooth lines even with fast movements

Fill Mode (F key)

- Click any area to fill with your selected color
- Fills all connected pixels of the same color
- Paint bucket icon appears in sidebar when active

Rainbow Mode (R key)

- Brush automatically cycles through rainbow colors
- Rainbow arc indicator appears in sidebar when active
- Cannot be used with fill mode

### How to Draw

1. Select a color from the palette (or press F1-F12)
2. Choose a brush size (bottom-right circles or +/- keys)
3. Click and drag on the canvas to draw
4. Use undo/redo if needed (Ctrl+Z / Ctrl+Shift+Z)

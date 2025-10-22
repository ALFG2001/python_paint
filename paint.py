from copy import deepcopy
from dataclasses import dataclass, field
import os
from typing import Tuple, Optional, Callable, List
import pygame
import sys
from tkinter import Tk, filedialog, messagebox
from PIL import Image

pygame.init()
pygame.font.init()

# --- BRUSH CLASS ---
@dataclass
class Brush:
    """
    Represents the drawing brush with configurable size, color, and drawing modes.
    Supports normal drawing, fill mode, and rainbow mode.
    """
    size: int = field(default=8)
    color: Tuple[int, int, int] = field(default=(0, 0, 0))
    enable_last_position: bool = field(default=False, init=False)
    last_position: Tuple[int, int] = field(default=(0,0), init=False)
    fill: bool = field(default=False)       
    rainbow: bool = field(default=False)
    prev_color: Tuple[int, int, int] = None

    color_value: int = field(default=0, init=False)

    def set_color(self, color):
        """Set the brush color."""
        self.color = color

    def set_size(self, size):
        """Set the brush size (radius in pixels)."""
        self.size = size

    def floodFill(self, surface, position, fill_color):
        """
        Optimized scanline flood fill algorithm.
        Fills a connected region of the same color with a new color.
        """
        # Change cursor to indicate processing
        pygame.mouse.set_cursor(2)
        arr = pygame.surfarray.pixels2d(surface)
        x, y = position
        w, h = arr.shape
        orig_color = arr[x, y]
        fill_color_mapped = surface.map_rgb(fill_color)

        # Don't fill if already the target color
        if orig_color == fill_color_mapped:
            pygame.mouse.set_cursor(pygame.Cursor(11))
            return

        stack = [(x, y)]
        
        while stack:
            nx, ny = stack.pop()
            if nx < 0 or nx >= w or ny < 0 or ny >= h or arr[nx, ny] != orig_color:
                continue

            # Find west and east boundaries of the scanline
            west = nx
            east = nx
            while west > 0 and arr[west - 1, ny] == orig_color:
                west -= 1
            while east < w - 1 and arr[east + 1, ny] == orig_color:
                east += 1

            # Fill the entire scanline at once for efficiency
            arr[west:east + 1, ny] = fill_color_mapped

            # Check north/south neighbors only at segment boundaries to avoid duplicates
            if ny > 0:
                in_segment = False
                for i in range(west, east + 1):
                    is_target = arr[i, ny - 1] == orig_color
                    if is_target and not in_segment:
                        stack.append((i, ny - 1))
                        in_segment = True
                    elif not is_target:
                        in_segment = False
                        
            if ny < h - 1:
                in_segment = False
                for i in range(west, east + 1):
                    is_target = arr[i, ny + 1] == orig_color
                    if is_target and not in_segment:
                        stack.append((i, ny + 1))
                        in_segment = True
                    elif not is_target:
                        in_segment = False

        # Apply changes back to surface
        pygame.surfarray.blit_array(surface, arr)
        pygame.mouse.set_cursor(pygame.Cursor(11))

    def rainbowColor(self):
        """
        Returns a rainbow color based on the current color_value.
        Cycles through red -> yellow -> green -> cyan -> blue -> magenta.
        """
        step = (self.color_value // 256) % 6
        pos = self.color_value % 256
        if step == 0:
            return (255, pos, 0)
        if step == 1:
            return (255-pos, 255, 0)
        if step == 2:
            return (0, 255, pos)
        if step == 3:
            return (0, 255-pos, 255)
        if step == 4:
            return (pos, 0, 255)
        if step == 5:
            return (255, 0, 255-pos)

    def round_line(self, screen, start):
        """
        Draws a smooth interpolated line between the last position and current position.
        Prevents gaps when mouse moves quickly.
        """
        x_axis = self.last_position[0]-start[0]
        y_axis = self.last_position[1]-start[1]
        dist = max(abs(x_axis), abs(y_axis))
        for i in range(dist):
            x = int(start[0]+float(i)/dist*x_axis)
            y = int(start[1]+float(i)/dist*y_axis)
            pygame.draw.circle(screen, self.color, (x, y), self.size)

    def draw(self, screen, mouse_position):
        """
        Main drawing method. Handles fill mode, rainbow mode, and normal drawing.
        """
        if(self.fill):
            # Fill mode: flood fill the clicked area
            if screen.get_at(mouse_position)[:3] != self.color:
                self.floodFill(screen, mouse_position, self.color)

        elif(self.rainbow):
            # Rainbow mode: cycle through colors automatically
            self.color_value = (self.color_value + 8) % (256 * 6)
            self.color = self.rainbowColor()
            
        else:
            # Normal mode: draw a circle at mouse position
            pygame.draw.circle(screen, self.color, mouse_position, self.size)

        # Draw smooth line if we have a previous position
        if(self.enable_last_position):
            self.round_line(screen, mouse_position)

        self.last_position = mouse_position


# --- BUTTON CLASS ---
@dataclass
class RectButton:
    """
    Rectangular button with hover effects, click callbacks, and keyboard shortcuts.
    Can be selected and displays different outlines when selected.
    """
    x: int
    y: int
    width: int
    height: int
    color: Tuple[int, int, int]
    outline_color: Tuple[int, int, int] = (0,0,0)
    text: Optional[str] = None
    font: pygame.font.Font = field(default_factory=lambda: pygame.font.SysFont(None, 24))
    on_click: Optional[Callable[[], None]] = None
    on_hover_gradient_enabled: bool = field(default=True)
    enabled: bool = field(default=True)
    shortcut: Optional[Tuple[int, bool, bool]] = None  # (key, needs_ctrl, needs_shift)

    _is_hovered: bool = field(default=False, init=False)
    _is_selected: bool = field(default=False, init=False)

    default_outline: Tuple[int,int,int] = (0,0,0)
    selected_outline: Tuple[int,int,int] = (150,150,150)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value

    @property
    def rect(self) -> pygame.Rect:
        """Returns the button's bounding rectangle."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    @property
    def current_text_color(self) -> Tuple[int,int,int]:
        """Returns text color based on whether button is enabled."""
        return (50, 50, 50) if self.enabled else (150, 150, 150)

    def get_draw_outline(self):
        """Returns the appropriate outline color based on selection state."""
        return self.selected_outline if self.is_selected else self.default_outline

    def draw(self, surface: pygame.Surface) -> None:
        """Draws the button with its text and hover gradient if applicable."""
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, self.get_draw_outline(), self.rect, width=2)

        if self.text:
            txt_surf = self.font.render(self.text, True, self.current_text_color)
            txt_rect = txt_surf.get_rect(center=self.rect.center)
            surface.blit(txt_surf, txt_rect)

        # Draw hover gradient effect
        if self._is_hovered and self.on_hover_gradient_enabled and self.enabled:
            gradient = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for y in range(self.height):
                alpha = int(128 * (y / self.height))
                pygame.draw.line(gradient, (0, 0, 0, alpha), (0, y), (self.width, y))
            surface.blit(gradient, (self.x, self.y))

    def update(self) -> None:
        """Updates hover state and cursor based on mouse position."""
        mouse_pos = pygame.mouse.get_pos()
        hovering = self.rect.collidepoint(mouse_pos) if self.enabled else False

        if hovering and not self._is_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif (not hovering) and self._is_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self._is_hovered = hovering

    def click(self, event: pygame.event.Event) -> bool:
        """Handles mouse click events. Returns True if button was clicked."""
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def check_shortcut(self, event: pygame.event.Event) -> bool:
        """Check if the keyboard shortcut was pressed. Returns True if triggered."""
        if not self.enabled or self.shortcut is None:
            return False
        
        if event.type == pygame.KEYDOWN:
            key, needs_ctrl, needs_shift = self.shortcut
            
            # Get modifier key states
            mods = pygame.key.get_mods()
            ctrl_pressed = bool(mods & pygame.KMOD_CTRL)
            shift_pressed = bool(mods & pygame.KMOD_SHIFT)
            
            # Check if the key and modifiers match
            if event.key == key and ctrl_pressed == needs_ctrl and shift_pressed == needs_shift:
                if self.on_click:
                    self.on_click()
                return True
        
        return False

@dataclass
class UndoRedoButton(RectButton):
    """
    Special button that manages a history stack for undo/redo operations.
    Automatically enables/disables based on whether history is available.
    """
    _history_stack: List[pygame.Surface] = field(default_factory=list, init=False)

    @property
    def history_stack(self):
        return self._history_stack

    def push(self, surface: pygame.Surface):
        """Add a new state to the stack and enable button."""
        self._history_stack.append(surface)
        self.enabled = True

    def pop(self) -> pygame.Surface | None:
        """Remove the most recent state and disable button if empty."""
        if self._history_stack:
            removed = self._history_stack.pop()
            if not self._history_stack:
                self.enabled = False
            return removed
        
    def empty_history(self):
        """Clear all history and disable the button."""
        self._history_stack = []
        self.enabled = False

@dataclass
class PickerButton(RectButton):
    """
    Special button that displays the color picker grid image.
    Allows users to select colors from a visual palette.
    """
    path: str = "picker/color_grid.png"
    _image: pygame.surface.Surface = field(default=None, init=False)

    @property
    def image(self) -> pygame.surface.Surface:
        """Return the loaded color picker image."""
        return self._image

    @image.setter
    def image(self, value: pygame.surface.Surface):
        """Set the current color picker image."""
        self._image = value

    def check(self) -> bool:
        """Check if the image path exists and is accessible."""
        return os.path.isfile(self.path)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draws the color picker grid image at the specified position."""
        if not self.check():
            raise FileNotFoundError(f"Color picker image not found at: {self.path}")

        self.screenshot = surface.subsurface(self.rect).copy()
        color_picker_grid_image = pygame.image.load(self.path).convert_alpha()
        self.image = color_picker_grid_image
        surface.blit(self.image, (200, 0))

    def update(self) -> None:
        """Updates hover state with crosshair cursor for precise color selection."""
        mouse_pos = pygame.mouse.get_pos()
        hovering = self.rect.collidepoint(mouse_pos) if self.enabled else False

        if hovering and not self._is_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)
        elif not hovering and self._is_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self._is_hovered = hovering

    def click(self, event: pygame.event.Event) -> bool:
        """Handles mouse click events. Returns True if button was clicked."""
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False


@dataclass
class CircleButton:
    """
    Circular button used for size selection indicators.
    Uses exact circular collision detection instead of rectangular bounds.
    """
    x: int
    y: int
    radius: int
    color: Tuple[int, int, int]
    outline_color: Tuple[int, int, int] = (0, 0, 0)
    on_click: Optional[Callable[[], None]] = None
    enabled: bool = True
    size: int = field(default=8)
    shortcut: Optional[Tuple[int, bool, bool]] = None
    
    _is_hovered: bool = field(default=False, init=False)
    _is_selected: bool = field(default=False, init=False)

    default_color: Tuple[int,int,int] = (255,255,255)
    default_outline: Tuple[int,int,int] = (0,0,0)
    selected_color: Tuple[int,int,int] = (0,0,0)
    selected_outline: Tuple[int,int,int] = (255,255,255)

    @property
    def is_selected(self):
        return self._is_selected

    @is_selected.setter
    def is_selected(self, value: bool):
        self._is_selected = value

    @property
    def rect(self) -> pygame.Rect:
        """Returns bounding rectangle for the circle."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius*2, self.radius*2)

    def collide_point(self, point: Tuple[int,int]) -> bool:
        """Check if a point is inside the circle using distance formula."""
        px, py = point
        return (px - self.x)**2 + (py - self.y)**2 <= self.radius**2

    def get_draw_colors(self):
        """Returns fill and outline colors based on selection state."""
        if self.is_selected:
            return self.selected_color, self.selected_outline
        else:
            return self.default_color, self.default_outline

    def draw(self, surface):
        """Draws the circular button with appropriate colors."""
        fill, outline = self.get_draw_colors()
        pygame.draw.circle(surface, fill, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, outline, (self.x, self.y), self.radius, width=2)

    def update(self) -> None:
        """Updates hover state and cursor using circular collision."""
        mouse_pos = pygame.mouse.get_pos()
        hovering = self.enabled and self.collide_point(mouse_pos)

        if hovering and not self._is_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        elif (not hovering) and self._is_hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

        self._is_hovered = hovering

    def click(self, event: pygame.event.Event) -> bool:
        """Handles mouse click events using circular collision. Returns True if clicked."""
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.collide_point(event.pos):
                if self.on_click:
                    self.on_click()
                return True
        return False

    def check_shortcut(self, event: pygame.event.Event) -> bool:
        """Check if the keyboard shortcut was pressed. Returns True if triggered."""
        if not self.enabled or self.shortcut is None:
            return False
        
        if event.type == pygame.KEYDOWN:
            key, needs_ctrl, needs_shift = self.shortcut
            
            # Get modifier key states
            mods = pygame.key.get_mods()
            ctrl_pressed = bool(mods & pygame.KMOD_CTRL)
            shift_pressed = bool(mods & pygame.KMOD_SHIFT)
            
            # Check if the key and modifiers match
            if event.key == key and ctrl_pressed == needs_ctrl and shift_pressed == needs_shift:
                if self.on_click:
                    self.on_click()
                return True
        
        return False

# --- BUTTON MANAGER CLASS ---
class ButtonManager:
    """
    Manages a collection of buttons, handling their updates, drawing, and events.
    Maintains selection state across multiple buttons.
    """
    def __init__(self):
        self.buttons: List[RectButton|CircleButton|UndoRedoButton|PickerButton] = []
        self._selected_button: Optional[RectButton|CircleButton|UndoRedoButton|PickerButton] = None

    def add(self, button: RectButton|CircleButton|UndoRedoButton|PickerButton) -> None:
        """Add a button to the manager."""
        self.buttons.append(button)

    def update_all(self) -> None:
        """Update all buttons (hover states, etc.)."""
        for btn in self.buttons:
            btn.update()

    def draw_all(self, surface: pygame.Surface) -> None:
        """Draw all buttons to the surface."""
        for btn in self.buttons:
            btn.draw(surface)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Process events for all buttons (keyboard shortcuts and clicks)."""
        for btn in self.buttons:
            # Check for shortcuts first (keyboard)
            if hasattr(btn, 'check_shortcut'):
                shortcut_triggered = btn.check_shortcut(event)
                if shortcut_triggered:
                    self.select_button(btn)
                    return
            
            # Then check for clicks (mouse)
            clicked = btn.click(event)
            if clicked:
                self.select_button(btn)

    def select_button(self, button: RectButton|CircleButton|UndoRedoButton|PickerButton):
        """Select a button and deselect the previously selected button."""
        if self._selected_button and self._selected_button != button:
            self._selected_button.is_selected = False
        button.is_selected = True
        self._selected_button = button


# --- COLOR PICKER CLASS ---
@dataclass
class ColorPicker:
    """
    Modal color picker interface that allows users to select and customize palette colors.
    Displays a gradient grid for precise color selection and a customizable palette.
    """
    font: pygame.font
    colors: list[list[tuple[int, int, int]]]  # Main color palette
    new_colors: list[list[tuple[int, int, int]]]  # Temporary colors being edited
    default_colors: list[list[tuple[int, int, int]]]  # Default palette for reset
    filename: str = "picker/color_grid.png"
    on_close: callable = None
    on_cancel: callable = None 
    coord: int = 0  # Currently selected palette slot index
    row: int = 0  # Current row in palette
    col: int = 0  # Current column in palette
    color:Tuple[int, int, int] = None
    color_picker_palette_manager: ButtonManager = field(default_factory=ButtonManager)
    color_picker_button_manager: ButtonManager = field(default_factory=ButtonManager)

    _is_dragging: bool = field(default=False, init=False)
    _temp_hover_color: Tuple[int, int, int] = field(default=(255,255,255), init=False)

    _screenshot: pygame.Surface = field(default=None, init=False)
    _hover_color: Tuple[int, int, int] = field(default=(255,255,255), init=False)

    @property
    def hover_color(self) -> Tuple[int, int, int]:
        """Current color being hovered over in the picker grid."""
        return self._hover_color
    
    @hover_color.setter
    def hover_color(self, value: Tuple[int, int, int]):
        self._hover_color = value

    @property
    def screenshot(self) -> pygame.Surface:
        """Saved screenshot of the canvas before opening the picker."""
        return self._screenshot
    
    @screenshot.setter
    def screenshot(self, value: pygame.Surface):
        self._screenshot = value 

    @property
    def path(self) -> str:
        """Return the absolute path to the color picker grid image."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, self.filename)  
    
    def click_picker(self, screen):
        """
        Confirm the color selection from the picker grid.
        Only saves when mouse is released (not while dragging).
        """
        if not self._is_dragging:
            self.color = self.hover_color
            self.new_colors[self.row][self.col] = self.color

            # Update the picker palette button - BOTH color and outline
            picker_button = self.color_picker_palette_manager.buttons[self.coord]
            picker_button.color = self.color
            picker_button.default_outline = self.color
            
            # If this button is selected, also update selected outline
            if picker_button.is_selected:
                picker_button.selected_outline = (150, 150, 150)

            self.make_picker_ui(screen)

    def cancel_picker(self):
        """
        Cancel the picker without saving changes.
        Resets new_colors to the original colors.
        """
        # Reset new_colors to current colors (discard changes)
        self.new_colors = deepcopy(self.colors)
        
        # Close without saving
        if self.on_cancel:
            self.on_cancel()

    def save_picker(self):
        """
        Save the modified palette colors and close the picker.
        Commits new_colors to the main colors array.
        """
        # Save to actual palette
        for i in range(2):
            for j in range(6):
                self.colors[i][j] = self.new_colors[i][j]
        
        # Close and update UI
        if self.on_close:
            self.on_close()

    def default_picker(self, screen):
        """
        Reset the palette to default colors.
        Updates both the internal state and button visuals.
        """
        # Reset new_colors to default
        self.new_colors = deepcopy(self.default_colors)
        
        # Update all picker palette buttons with default colors
        for i in range(2):
            for j in range(6):
                coord = i * 6 + j
                button = self.color_picker_palette_manager.buttons[coord]
                button.color = self.default_colors[i][j]
                button.default_outline = self.default_colors[i][j]
        
        # Update the hover color to match currently selected palette slot
        self.hover_color = self.new_colors[self.row][self.col]
        
        self.make_picker_ui(screen)

    def pick_palette_picker(self, i, j):
        """
        Select a palette slot to edit.
        Updates the picker to show the selected slot's current color.
        """
        self.coord = i * 6 + j
        self.row = i
        self.col = j
        self.color = self.new_colors[i][j]
        self.hover_color = self.color


    def loadButton(self, screen):
        """
        Create and add all buttons for the color picker interface.
        Includes the picker grid, control buttons, and palette slots.
        """
        # Picker grid button (no on_click, handled in main loop)
        self.color_picker_button_manager.add(PickerButton(
            x=200, y=0, width=720, height=720, 
            color=(255,255,255), 
            path=self.path, 
            on_click=None
        ))
        
        # Save button
        self.color_picker_button_manager.add(RectButton(
            x=925, y=650, width=150, height=50, 
            color=(200,200,200), text="SAVE", 
            font=self.font, 
            on_click=self.save_picker, 
            default_outline=(0,0,0), 
            selected_outline=(0,0,0),
            shortcut=(pygame.K_s, True, False)  # Ctrl+S
        ))
        
        # Cancel button
        self.color_picker_button_manager.add(RectButton(
            x=1125, y=650, width=150, height=50, 
            color=(200,200,200), text="CANCEL", 
            font=self.font, 
            on_click=self.cancel_picker, 
            default_outline=(0,0,0), 
            selected_outline=(0,0,0),
            shortcut=(pygame.K_ESCAPE, False, False)  # Escape
        ))
        
        # Reset to default palette button
        self.color_picker_button_manager.add(RectButton(
            x=950, y=250, width=300, height=50, 
            color=(200,200,200), text="DEFAULT PALETTE", 
            font=self.font, 
            on_click=lambda s=screen: self.default_picker(s), 
            default_outline=(0,0,0), 
            selected_outline=(0,0,0),
            shortcut=(pygame.K_d, True, False)  # Ctrl+D
        ))

        # Create palette slot buttons (HORIZONTAL layout: rows then columns)
        for y in range(2):  # Rows (top, bottom)
            for x in range(6):  # Columns (left to right)
                size = 50
                color = self.new_colors[y][x]
                palette_button = RectButton(
                    x=930 + 58 * x, y=110 + 58 * y, 
                    width=size, height=size, 
                    color=color, 
                    on_hover_gradient_enabled=False, 
                    on_click=lambda i=y, j=x: self.pick_palette_picker(i, j)
                )
                palette_button.selected_outline = (150,150,150)
                palette_button.default_outline = palette_button.color
                self.color_picker_palette_manager.add(palette_button)
                # Select first button by default
                if (x == 0 and y == 0):
                    self.color_picker_palette_manager.select_button(palette_button)

    def make_picker_ui(self, screen: pygame.Surface):
        """
        Draw the picker interface background and color preview.
        Shows the currently hovered/selected color in a preview box.
        """
        pygame.draw.rect(screen, (50, 50, 50), (920, 0, 360, 720))
        pygame.draw.rect(screen, self.hover_color, (925, 5, 350, 90))

    def build(self, screen: pygame.Surface) -> None:
        """
        Initialize and display the color picker overlay.
        Sets up all buttons and initializes the hover color.
        """
        self.loadButton(screen)
        self.make_picker_ui(screen)
        
        # Initialize hover color to first palette slot
        self.hover_color = self.new_colors[0][0]
        self.color = self.new_colors[0][0]
        
    def destroy(self, screen: pygame.Surface) -> None:
        """
        Close the color picker and restore the previous screen state.
        Restores the canvas from the saved screenshot.
        """
        if self.screenshot is None:
            return
        pygame.surfarray.blit_array(screen.subsurface(pygame.Rect(200, 0, 1080, 720)), pygame.surfarray.pixels2d(self.screenshot))
        self.screenshot = None

    def update(self, screen: pygame.Surface):
        """Update the picker UI (refresh the preview and background)."""
        self.make_picker_ui(screen)

# --- UI CLASS ---
class UI:
    """
    Main application class managing the paint program interface.
    Handles the canvas, toolbars, color palette, and all user interactions.
    """
    def __init__(self, screen_size: Tuple[int,int], title: str = "UI"):
        self.screen_width, self.screen_height = screen_size
        self.screen = pygame.display.set_mode(screen_size)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.fps = 144

        # Global constants
        self.font = pygame.font.SysFont("segoeuisymbol", 30)
        self.toolbar_button_manager = ButtonManager()
        self.palette_button_manager = ButtonManager()
        self.size_changer_button_manager = ButtonManager()
        self.brush = Brush()

        self.selected = False
        # Main color palette: 2 columns x 6 rows
        self.colors = [[(0, 0, 0),(255, 0, 0),(0, 255, 0),(0, 0, 255),(165, 42, 42),(255, 165, 0)],
                [(255, 255, 255),(255, 0, 255),(255, 255, 0),(0, 255, 255),(128, 0, 128),(255, 192, 203)]]
        self.new_colors = deepcopy(self.colors)
        self.default_colors = deepcopy(self.colors)

        self.drawing = False
        self.undo_button = None
        self.redo_button = None

        self.picking_color = False
        self.waiting_for_mouse_release = False 
        # Initialize ColorPicker
        self.color_picker = ColorPicker(
            font=self.font, 
            colors=self.colors, 
            new_colors=self.new_colors, 
            default_colors=self.default_colors
        )
        self.holding_picking = False

    def save_project(self):
        """
        Save the current canvas as an image file.
        Opens a file dialog for the user to choose save location.
        """
        save_path = self.select_save_file()
        
        # Check if user cancelled the dialog
        if not save_path:
            return
        
        # Capture only the canvas area (exclude palette and toolbar)
        screenshot = self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50))
        
        try:
            pygame.image.save(screenshot, save_path)
            root = Tk()
            root.withdraw()
            messagebox.showinfo("Saved", f"Image saved to:\n{save_path}")
            root.destroy()
        except Exception as e:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to save image:\n{str(e)}")
            root.destroy()

    def open_project(self):
        """
        Open and display an image file on the canvas.
        Saves current state to undo history before loading.
        """
        path = self.select_image()
        
        # Check if user cancelled the dialog
        if not path:
            return
        
        try:
            # Save current state before opening
            undo_screen = self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50)).copy()
            self.undo_button.push(undo_screen)
            self.display_image(path)
        except Exception as e:
            root = Tk()
            root.withdraw()
            messagebox.showerror("Error", f"Failed to open image:\n{str(e)}")
            root.destroy()

    def cancel_action(self):
        """
        Clear the canvas and reset to default settings.
        Resets color, brush size, and clears redo history.
        """
        self.screen.fill((255, 255, 255))

        # Reset to default palette color (black)
        default_palette_button = self.palette_button_manager.buttons[0]
        self.palette_button_manager.select_button(default_palette_button)
        default_palette_button.on_click()

        # Reset to default brush size (8px)
        default_size_button = self.size_changer_button_manager.buttons[2]
        self.size_changer_button_manager.select_button(default_size_button)
        default_size_button.on_click()

        self.redo_button.empty_history()

    def fill_area(self):
        """
        Toggle fill mode on/off.
        Disables rainbow mode if it was active.
        """
        if (self.brush.fill):
            self.brush.fill = False

        else:
            if (self.brush.rainbow):
                self.brush.rainbow = False
                self.brush.color_value = 0
                self.brush.color = self.brush.prev_color
                self.brush.prev_color = None

            self.brush.fill = True

    def rgb_brush(self):
        """
        Toggle rainbow mode on/off.
        Saves/restores the previous color when toggling.
        Disables fill mode if it was active.
        """
        if (self.brush.rainbow):
            self.brush.rainbow = False
            self.brush.color = self.brush.prev_color
            self.brush.prev_color = None

        else:
            if (self.brush.fill):
                self.brush.fill = False

            self.brush.prev_color = self.brush.color
            self.brush.rainbow = True

        self.brush.color_value = 0
        
    def undo(self):
        """
        Undo the last drawing action.
        Saves current state to redo history before undoing.
        """
        redo_screen = self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50)).copy()
        self.redo_button.push(redo_screen)

        undo_screen = self.undo_button.pop()
        pygame.surfarray.blit_array(self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50)), pygame.surfarray.pixels2d(undo_screen))

    def redo(self):
        """
        Redo a previously undone action.
        Saves current state to undo history before redoing.
        """
        undo_screen = self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50)).copy()
        self.undo_button.push(undo_screen)

        redo_screen = self.redo_button.pop()
        pygame.surfarray.blit_array(self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50)), pygame.surfarray.pixels2d(redo_screen))

    def _close_color_picker_callback(self):
        """
        Callback executed when saving and closing the color picker.
        Updates UI palette buttons with the newly saved colors.
        """
        # Update UI palette buttons with the new saved colors
        # UI buttons are ordered vertically: column then row
        ui_button_index = 0
        for x in range(2):  # UI columns
            for y in range(6):  # UI rows
                ui_button = self.palette_button_manager.buttons[ui_button_index]
                # Update brush color if it matches the old color
                if self.brush.color == ui_button.color:
                    self.brush.color = self.colors[x][y]

                ui_button.color = self.colors[x][y]
                ui_button.default_outline = self.colors[x][y]
                self.new_colors[x][y] = ui_button.color
                ui_button_index += 1

        # Restore the screen
        self.color_picker.destroy(self.screen)
        self.picking_color = False

        self.waiting_for_mouse_release = True

        # Re-enable toolbar buttons
        for btn in self.toolbar_button_manager.buttons[:-3]:
            btn.enabled = True

        if self.undo_button.history_stack:
            self.undo_button.enabled = True

        if self.redo_button.history_stack:
            self.redo_button.enabled = True

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def pick_color(self):
        """
        Toggle the color picker interface.
        Opens the picker if closed, or cancels it if already open.
        """
        if self.picking_color:
            # Cancel without saving
            self.color_picker.cancel_picker()
        else:
            # Open color picker
            screenshot = self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50)).copy()
            self.color_picker.screenshot = screenshot
            self.color_picker.on_close = self._close_color_picker_callback
            self.color_picker.on_cancel = self._cancel_color_picker_callback
            
            # Reset new_colors to current state before opening
            self.color_picker.new_colors = deepcopy(self.colors)
            
            # Clear old buttons before rebuilding
            self.color_picker.color_picker_button_manager = ButtonManager()
            self.color_picker.color_picker_palette_manager = ButtonManager()
            
            # Build the picker UI
            self.color_picker.build(self.screen)
            self.picking_color = True

            # Disable toolbar buttons except the picker button
            for btn in self.toolbar_button_manager.buttons[:-1]:
                btn.enabled = False

    def _cancel_color_picker_callback(self):
        """
        Callback executed when canceling the color picker.
        Restores screen without saving any color changes.
        """
        # Just restore screen without updating palettes
        self.color_picker.destroy(self.screen)
        self.picking_color = False

        self.waiting_for_mouse_release = True

        # Re-enable toolbar buttons
        for btn in self.toolbar_button_manager.buttons[:-3]:
            btn.enabled = True

        if self.undo_button.history_stack:
            self.undo_button.enabled = True

        if self.redo_button.history_stack:
            self.redo_button.enabled = True

        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def select_color_from_palette(self, col, row):
        """
        Select a color from the main palette.
        Called when a palette button is clicked.
        """
        color = self.colors[col][row]
        self.brush.set_color(color)

    def size_changer(self, size):
        """Change the brush size."""
        self.brush.set_size(size)

    def load_buttons(self):
        """
        Create and initialize all UI buttons.
        Sets up toolbar, palette, and size selection buttons with their callbacks and shortcuts.
        """
        self.toolbar_button_manager.buttons = []
        self.palette_button_manager.buttons = []
        self.size_changer_button_manager.buttons = []

        y = self.screen_height - 50
        # Toolbar buttons
        self.toolbar_button_manager.add(RectButton(x=4, y=y, width=100, height=50, color=(200,200,200), text="SAVE", font=self.font, on_click=self.save_project, default_outline=(0,0,0), selected_outline=(0,0,0), shortcut=(pygame.K_s, True, False))) # Ctrl+S
        self.toolbar_button_manager.add(RectButton(x=108, y=y, width=100, height=50, color=(200,200,200), text="OPEN", font=self.font, on_click=self.open_project, default_outline=(0,0,0), selected_outline=(0,0,0), shortcut=(pygame.K_o, True, False))) # Ctrl+O
        self.toolbar_button_manager.add(RectButton(x=212, y=y, width=100, height=50, color=(200,200,200), text="CANC", font=self.font, on_click=self.cancel_action, default_outline=(0,0,0), selected_outline=(0,0,0), shortcut=(pygame.K_n, True, False))) # Ctrl+N
        self.toolbar_button_manager.add(RectButton(x=316, y=y, width=100, height=50, color=(200,200,200), text="FILL", font=self.font, on_click=self.fill_area, default_outline=(0,0,0), selected_outline=(0,0,0), shortcut=(pygame.K_f, False, False))) # F key
        self.toolbar_button_manager.add(RectButton(x=420, y=y, width=100, height=50, color=(200,200,200), text="RGB", font=self.font, on_click=self.rgb_brush, default_outline=(0,0,0), selected_outline=(0,0,0), shortcut=(pygame.K_r, False, False))) # R key
        self.toolbar_button_manager.add(UndoRedoButton(x=524, y=y, width=50, height=50, color=(200,200,200), text="↩", font=self.font, on_click=self.undo, default_outline=(0,0,0), selected_outline=(0,0,0), enabled=False, shortcut=(pygame.K_z, True, False))) # Ctrl+Z
        self.toolbar_button_manager.add(UndoRedoButton(x=578, y=y, width=50, height=50, color=(200,200,200), text="↪", font=self.font, on_click=self.redo, default_outline=(0,0,0), selected_outline=(0,0,0), enabled=False, shortcut=(pygame.K_z, True, True))) # Ctrl+Shift+Z
        self.toolbar_button_manager.add(RectButton(x=632, y=y, width=50, height=50, color=(200,200,200), text="🎨", font=self.font, on_click=self.pick_color, default_outline=(0,0,0), selected_outline=(0,0,0), shortcut=(pygame.K_p, False, False))) # P key

        # Store references to undo/redo buttons
        self.undo_button = self.toolbar_button_manager.buttons[5]
        self.redo_button = self.toolbar_button_manager.buttons[6]

        # Color palette buttons with F-key shortcuts
        f_key_list = [pygame.K_F1, pygame.K_F3,  pygame.K_F5,  pygame.K_F7, pygame.K_F9, pygame.K_F11,  pygame.K_F2, pygame.K_F4, pygame.K_F6, pygame.K_F8,  pygame.K_F10, pygame.K_F12]
        f_key_index = 0
        for x in range(2):  # Columns (left, right)
            for y in range(6):  # Rows (top to bottom)
                size = 90
                color = self.colors[x][y]
                palette_button = RectButton(
                    x=5+(100*x), y=5+(100*y), 
                    width=size, height=size, 
                    color=color, 
                    on_hover_gradient_enabled=False, 
                    on_click=lambda col=x, row=y: self.select_color_from_palette(col, row),
                    shortcut=(f_key_list[f_key_index], False, False)
                )
                f_key_index += 1
                palette_button.selected_outline = (50,50,50)
                palette_button.default_outline = palette_button.color
                self.palette_button_manager.add(palette_button)
                # Select first button by default
                if (x == 0 and y == 0):
                    self.palette_button_manager.select_button(palette_button)

        # Brush size selector buttons
        radii = [4, 6, 8, 10]
        x_positions = [self.screen_width - 200, self.screen_width - 150, self.screen_width - 100, self.screen_width - 50]

        for x, r in zip(x_positions, radii):
            size_button = CircleButton(x=x, y=self.screen_height - 25, radius=r, color=(255,255,255), outline_color=(0,0,0),on_click=lambda r=r: self.size_changer(r))
            self.size_changer_button_manager.add(size_button)
            # Select default size (8px)
            if (r == 8):
                self.size_changer_button_manager.select_button(size_button)

    def draw_ui_rectangles(self):
        """
        Draw the UI layout rectangles (palette sidebar and toolbar).
        Also draws visual indicators for active fill and rainbow modes.
        """
        palette_rect = pygame.Rect(0, 0, 200, self.screen_height-52)
        toolbar_rect = pygame.Rect(0, self.screen_height - 52, self.screen_width, 52)
        pygame.draw.rect(self.screen, (150,150,150), palette_rect)
        pygame.draw.rect(self.screen, (50, 50, 50), toolbar_rect)

        # Draw fill mode indicator
        if(self.brush.fill):
            pygame.draw.rect(self.screen, (50,50,50), (50, 610, 100, 80), border_radius=5)
            pygame.draw.polygon(self.screen, self.brush.color, ((55,615), (145,615),(120, 635),(100, 640), (80, 635)))
        
        # Draw rainbow mode indicator
        if(self.brush.rainbow):
            for i, color in enumerate([(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]):
                pygame.draw.circle(self.screen, color, (100, 690), 80 - i * 10, width=10, draw_top_right=True, draw_top_left=True)

    def select_save_file(self):
        """
        Open a file save dialog for the user to choose save location and filename.
        Returns the selected file path or None if cancelled.
        """
        root = Tk()
        root.withdraw()
        file_path = filedialog.asksaveasfilename(
            title="Save as",
            defaultextension=".png",
            filetypes=[("Image files", "*.png"), ("All files", "*.*")]
        )
        root.destroy()
        return file_path

    def select_image(self):
        """
        Open a file selection dialog for opening image files.
        Converts non-PNG images to PNG format.
        Returns the file path or None if cancelled.
        """
        root = Tk()
        root.withdraw()
            
        image_extensions = tuple(Image.registered_extensions().keys())

        # Open file dialog
        file_path = filedialog.askopenfilename(
            title="Select an image file",
            filetypes=[("Image files", image_extensions)]
        )

        if not file_path:
            root.iconify()
            root.destroy()
            return None

        # Convert to PNG if needed
        if file_path.lower().endswith(image_extensions) and file_path.lower().endswith('.png'):
            image = Image.open(file_path)
            png_file_path = file_path.rsplit('.', 1)[0] + '.png'
            image.save(png_file_path, 'PNG')
            root.iconify()
            root.destroy()
            return png_file_path
        else:
            root.iconify()
            root.destroy()
            return file_path

    def display_image(self, file_path):
        """
        Load and display an image file on the canvas.
        Scales the image to fit the canvas height while maintaining aspect ratio.
        Centers the image horizontally.
        """
        self.cancel_action()

        img = pygame.image.load(file_path)

        # Original image dimensions
        img_width, img_height = img.get_size()

        # Target height and scaling
        target_height = 720
        scale_ratio = target_height / img_height
        new_width = int(img_width * scale_ratio)
        new_height = target_height

        # Scale the image
        img = pygame.transform.scale(img, (new_width, new_height))

        # Window dimensions
        win_width, win_height = self.screen.get_size()

        # Center the image
        x = (win_width - new_width) // 2
        y = (win_height - new_height) // 2

        self.screen.blit(img, (x, y))
    
    def ask_yes_no(self):
        """
        Show a confirmation dialog when trying to quit.
        Returns False if user wants to quit, True to cancel quit.
        """
        return not messagebox.askyesno(title="Quit", message="Do you want to quit?")

    def run(self):
        """
        Main application loop.
        Handles all events, updates, and rendering.
        """
        running = True
        # Define canvas boundaries (drawing area)
        canvas_x_start = 200
        canvas_y_start = 0
        canvas_x_end = self.screen_width
        canvas_y_end = self.screen_height - 52

        self.screen.fill((255,255,255))

        while running:
            mouse_pos = pygame.mouse.get_pos()
            mx, my = mouse_pos

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = self.ask_yes_no()

                self.toolbar_button_manager.handle_event(event)

                if(not self.picking_color):
                    # Normal mode: handle palette and size buttons
                    self.palette_button_manager.handle_event(event)
                    self.size_changer_button_manager.handle_event(event)

                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if canvas_x_start <= mx <= canvas_x_end and canvas_y_start <= my <= canvas_y_end:
                            self.brush.enable_last_position = True
                            self.brush.last_position = (mx, my)

                    if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        self.brush.enable_last_position = False
                        self.brush.color_value = 0
                        self.drawing = False
                        # Clear the waiting flag when mouse is released
                        if self.waiting_for_mouse_release:
                            self.waiting_for_mouse_release = False

                else:
                    # Color picker mode: handle picker buttons
                    self.color_picker.color_picker_button_manager.handle_event(event)
                    self.color_picker.color_picker_palette_manager.handle_event(event)


                # Drawing logic (only in normal mode)
                if(not self.picking_color):
                    if canvas_x_start <= mx <= canvas_x_end and canvas_y_start <= my <= canvas_y_end:
                        if pygame.mouse.get_pressed()[0] and not self.waiting_for_mouse_release:
                            if(not self.brush.enable_last_position):
                                self.brush.enable_last_position = True
                                self.brush.last_position = (mx, my)

                            # Save to undo history on first draw
                            if(not self.drawing):
                                undo_screen = self.screen.subsurface(pygame.Rect(200, 0, self.screen_width-200, self.screen_height-50)).copy()
                                self.undo_button.push(undo_screen)
                                if(self.redo_button.history_stack):
                                    self.redo_button.empty_history()
                                self.drawing = True

                            self.brush.draw(self.screen, (mx, my))

                    else:
                        if pygame.mouse.get_pressed()[0]:
                            self.brush.enable_last_position = False

                # Color picker interaction logic
                elif self.picking_color:
                    picker_button = self.color_picker.color_picker_button_manager.buttons[0]
                    
                    # Picker grid boundaries
                    picker_left = 200
                    picker_top = 0
                    picker_width = 720
                    picker_height = 720
                    picker_right = picker_left + picker_width
                    picker_bottom = picker_top + picker_height

                    # Handle mouse down - start dragging
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if picker_left <= event.pos[0] <= picker_right and picker_top <= event.pos[1] <= picker_bottom:
                            self.color_picker._is_dragging = True

                    # Handle mouse up - confirm selection
                    elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                        if self.color_picker._is_dragging:
                            self.color_picker._is_dragging = False
                            self.color_picker.click_picker(self.screen)

                    # Update hover color while dragging or moving
                    if picker_left <= mx <= picker_right and picker_top <= my <= picker_bottom:
                        if self.color_picker._is_dragging or event.type == pygame.MOUSEMOTION:
                            # Convert to local coordinates
                            local_x = mx - picker_left
                            local_y = my - picker_top

                            # Get color at pixel
                            try:
                                selected_color = picker_button.image.get_at((local_x, local_y))
                                self.color_picker.hover_color = selected_color[0], selected_color[1], selected_color[2]
                            except (IndexError, pygame.error):
                                pass
                

            # Update all button states
            self.toolbar_button_manager.update_all()
            
            if(not self.picking_color):
                # Normal mode rendering
                self.palette_button_manager.update_all()
                self.size_changer_button_manager.update_all()
                self.draw_ui_rectangles()
                
                self.palette_button_manager.draw_all(self.screen)
                self.size_changer_button_manager.draw_all(self.screen)

            else:
                # Color picker mode rendering
                self.color_picker.color_picker_button_manager.update_all()
                self.color_picker.color_picker_palette_manager.update_all()

                self.color_picker.update(self.screen)
                self.color_picker.color_picker_button_manager.draw_all(self.screen)
                self.color_picker.color_picker_palette_manager.draw_all(self.screen)
            
            # Always draw toolbar
            self.toolbar_button_manager.draw_all(self.screen)

            pygame.display.flip()
            self.clock.tick(self.fps)

        pygame.quit()
        sys.exit()

# --- MAIN ENTRY POINT ---
if __name__ == "__main__":
    ui = UI((1280, 770), "Paint Application")
    ui.load_buttons()
    ui.run()
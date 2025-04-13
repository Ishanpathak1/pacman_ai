# graphicsUtils.py
# ----------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

import sys
import math
import time
import tkinter  # Use the standard library Tkinter interface

# Global variables for graphics state
_root_window = None  # The root window for graphics output
_canvas = None  # The canvas which holds graphics objects
_canvas_xs = None  # Size of canvas object in pixels (width)
_canvas_ys = None  # Size of canvas object in pixels (height)
_canvas_x = None  # Current drawing position x (not typically used directly)
_canvas_y = None  # Current drawing position y (not typically used directly)
_bg_color = 'black'  # Default background color

_keysdown = {}  # Tracks currently pressed keys
_keyswaiting = {}  # Tracks keys pressed since last check
_got_release = None  # Flag to handle key auto-repeat issues

_leftclick_loc = None  # Stores location of last left click
_rightclick_loc = None  # Stores location of last right click
_ctrl_leftclick_loc = None  # Stores location of last ctrl+left click


# Platform-specific font selection (less critical now, defaults usually work)
# _Windows = sys.platform == 'win32'
# if _Windows:
#     _canvas_tfonts = ['times new roman', 'lucida console']
# else:
#     _canvas_tfonts = ['times', 'lucidasans-24']

# --- COLOR FORMATTING ---

def formatColor(r, g, b):
    """ Converts RGB float values (0.0-1.0) to Tkinter color string '#rrggbb' """
    return '#%02x%02x%02x' % (int(r * 255), int(g * 255), int(b * 255))


def colorToVector(color):
    """ Converts Tkinter color string '#rrggbb' back to RGB float vector """
    # Ensure color string is valid
    if not isinstance(color, str) or len(color) != 7 or color[0] != '#':
        raise ValueError(f"Invalid color format: {color}")
    try:
        return [int(color[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
    except ValueError:
        raise ValueError(f"Invalid hex value in color string: {color}")


# --- GRAPHICS CONTROL ---

def sleep(secs):
    """ Halts execution for a specified number of seconds. """
    global _root_window
    if _root_window is None:
        # If no graphics window, use standard time.sleep
        time.sleep(secs)
    else:
        # If graphics window exists, use Tkinter's event loop for sleeping
        # This allows the window to remain responsive during sleep
        _root_window.update_idletasks()
        _root_window.after(int(1000 * secs), _root_window.quit)
        _root_window.mainloop()


def begin_graphics(width=640, height=480, color=formatColor(0, 0, 0), title="Pacman"):
    """ Initializes the graphics window. """
    global _root_window, _canvas, _canvas_xs, _canvas_ys, _bg_color

    # Handle potential re-initialization
    if _root_window is not None:
        _root_window.destroy()

    _canvas_xs, _canvas_ys = width - 1, height - 1
    _bg_color = color

    # Create the main Tkinter window
    _root_window = tkinter.Tk()
    _root_window.protocol('WM_DELETE_WINDOW', _destroy_window)
    _root_window.title(title)
    _root_window.resizable(False, False)  # Prevent resizing

    # Create the canvas widget for drawing
    try:
        _canvas = tkinter.Canvas(_root_window, width=width, height=height)
        _canvas.pack()  # Add canvas to the window
        draw_background()  # Draw initial background
        _canvas.update()  # Force initial draw
    except Exception as e:
        _root_window = None  # Ensure cleanup if error occurs
        print("Graphics Initialization Error:", e, file=sys.stderr)
        raise  # Re-raise the exception

    # Bind keyboard and mouse events
    _root_window.bind("<KeyPress>", _keypress)
    _root_window.bind("<KeyRelease>", _keyrelease)
    _root_window.bind("<FocusIn>", _clear_keys)  # Clear keys on focus gain
    _root_window.bind("<FocusOut>", _clear_keys)  # Clear keys on focus loss
    _root_window.bind("<Button-1>", _leftclick)  # Left mouse button
    _root_window.bind("<Button-2>", _rightclick)  # Middle mouse button (often mapped)
    _root_window.bind("<Button-3>", _rightclick)  # Right mouse button
    _root_window.bind("<Control-Button-1>", _ctrl_leftclick)  # Ctrl + Left click

    _clear_keys()  # Initialize key state


def draw_background():
    """ Fills the canvas with the background color. """
    if _canvas is None: return
    # Create a rectangle covering the whole canvas
    corners = [(0, 0), (0, _canvas_ys), (_canvas_xs, _canvas_ys), (_canvas_xs, 0)]
    polygon(corners, _bg_color, fillColor=_bg_color, filled=True, smoothed=False)


def _destroy_window(event=None):
    """ Handler for window close event. """
    # Instead of destroying here, just exit the program cleanly
    sys.exit(0)


def end_graphics():
    """ Cleans up the graphics window. """
    global _root_window, _canvas
    if _root_window is not None:
        try:
            # Short delay to allow final view before closing
            sleep(0.2)
            _root_window.destroy()
        except Exception as e:
            # Ignore potential errors during cleanup
            # print('Error closing graphics window:', e, file=sys.stderr)
            pass  # Continue cleanup
        finally:
            _root_window = None
            _canvas = None
            _clear_keys()  # Clear key state on exit


def clear_screen():
    """ Deletes all items from the canvas and redraws the background. """
    global _canvas
    if _canvas is None: return
    _canvas.delete('all')
    draw_background()


def refresh():
    """ Forces the canvas to update and process pending draw events. """
    if _canvas is not None:
        _canvas.update_idletasks()


# --- DRAWING PRIMITIVES ---

def polygon(coords, outlineColor, fillColor=None, filled=True, smoothed=False, behind=0, width=1):
    """ Draws a polygon """
    if _canvas is None: return None
    # Flatten coordinate list for Tkinter
    c = []
    for x, y in coords:
        c.extend([x, y])

    # Determine fill color
    finalFillColor = fillColor if fillColor is not None else outlineColor
    if not filled: finalFillColor = ""  # No fill if not filled

    # Create polygon object
    poly_id = _canvas.create_polygon(c, outline=outlineColor, fill=finalFillColor,
                                     smooth=smoothed, width=width)

    # Adjust stacking order if 'behind' is specified
    if behind > 0:
        try:
            # Attempt to lower the polygon behind the item with tag 'behind'
            # Note: This relies on 'behind' being a valid tag or item ID.
            # It might be simpler to use specific tags for layers (e.g., 'walls', 'agents').
            _canvas.tag_lower(poly_id, behind)
        except tkinter.TclError:
            # Ignore error if the 'behind' tag/ID doesn't exist
            pass
    return poly_id


def square(pos, r, color, filled=True, behind=0):
    """ Draws a square centered at pos with radius r. """
    x, y = pos
    # Define corners relative to center
    coords = [(x - r, y - r), (x + r, y - r), (x + r, y + r), (x - r, y + r)]
    return polygon(coords, color, color, filled, smoothed=False, behind=behind)


def circle(pos, r, outlineColor, fillColor, endpoints=None, style='pieslice', width=2):
    """ Draws a circle or arc. """
    if _canvas is None: return None
    x, y = pos
    # Define bounding box for the circle/arc
    x0, y0 = x - r, y - r
    x1, y1 = x + r, y + r

    # Handle arc endpoints
    start_angle, extent_angle = 0, 359.9  # Default to full circle
    if endpoints is not None:
        e = list(endpoints)
        # Ensure extent is positive
        while e[1] < e[0]: e[1] += 360
        start_angle = e[0]
        extent_angle = e[1] - e[0]
        # Prevent drawing > 360 degrees
        if extent_angle > 359.9: extent_angle = 359.9

    return _canvas.create_arc(x0, y0, x1, y1, outline=outlineColor, fill=fillColor,
                              extent=extent_angle, start=start_angle, style=style, width=width)


def text(pos, color, contents, font='Helvetica', size=12, style='normal', anchor="nw"):
    """ Draws text string at the specified position. """
    if _canvas is None: return None
    x, y = pos
    font_spec = (font, size, style)  # Tkinter font specification
    return _canvas.create_text(x, y, fill=color, text=contents, font=font_spec, anchor=anchor)


def line(here, there, color=formatColor(0, 0, 0), width=2):
    """ Draws a line segment between two points. """
    if _canvas is None: return None
    x0, y0 = here
    x1, y1 = there
    return _canvas.create_line(x0, y0, x1, y1, fill=color, width=width)


# --- ITEM MANIPULATION ---

def moveCircle(item_id, pos, r, endpoints=None):
    """ Moves and potentially reshapes a circle/arc item. """
    if _canvas is None: return
    x, y = pos
    # Recalculate bounding box
    x0, y0 = x - r, y - r
    x1, y1 = x + r, y + r

    # Handle arc endpoints update
    start_angle, extent_angle = 0, 359.9
    if endpoints is not None:
        e = list(endpoints)
        while e[1] < e[0]: e[1] += 360
        start_angle = e[0]
        extent_angle = e[1] - e[0]
        if extent_angle > 359.9: extent_angle = 359.9
        # Update start and extent angles
        edit(item_id, start=start_angle, extent=extent_angle)

    # Move the item by setting new coordinates for its bounding box
    _canvas.coords(item_id, x0, y0, x1, y1)
    # refresh() # Refresh might be needed here depending on animation loop


def edit(item_id, **kwargs):
    """ Modifies configuration options of a canvas item. """
    if _canvas is None: return
    try:
        _canvas.itemconfigure(item_id, **kwargs)
    except tkinter.TclError as e:
        # Ignore errors if item_id is invalid (e.g., already deleted)
        # print(f"Warning: Could not configure item {item_id}: {e}", file=sys.stderr)
        pass


def changeText(item_id, newText, font=None, size=12, style='normal'):
    """ Changes the text content and optionally the font of a text item. """
    edit(item_id, text=newText)
    if font is not None:
        font_spec = (font, size, style)
        edit(item_id, font=font_spec)


def changeColor(item_id, newColor):
    """ Changes the fill color of a canvas item. """
    edit(item_id, fill=newColor)


def remove_from_screen(item_id):
    """ Deletes a canvas item. """
    if _canvas is None: return
    try:
        _canvas.delete(item_id)
        # refresh() # Refresh might be needed if deleting during animation
    except tkinter.TclError as e:
        # Ignore errors if item_id is invalid
        # print(f"Warning: Could not delete item {item_id}: {e}", file=sys.stderr)
        pass


def move_to(item_id, x, y=None):
    """ Moves a canvas item so its bounding box top-left corner is at (x, y). """
    if _canvas is None: return
    if y is None:  # Allow passing position as a tuple
        try:
            x, y = x
        except Exception:
            print("Error: Invalid coordinates for move_to", file=sys.stderr)
            return

    try:
        current_coords = _canvas.coords(item_id)
        if not current_coords: return  # Item might not exist or have coords

        current_x, current_y = current_coords[0], current_coords[1]
        dx = x - current_x
        dy = y - current_y
        move_by(item_id, dx, dy)  # Use move_by for relative movement
    except tkinter.TclError as e:
        # print(f"Warning: Could not move item {item_id}: {e}", file=sys.stderr)
        pass
        # refresh() # Might need refresh


def move_by(item_id, x, y=None, lift=False):
    """ Moves a canvas item relatively by (x, y). """
    if _canvas is None: return
    if y is None:  # Allow passing delta as a tuple
        try:
            x, y = x
        except Exception:
            print("Error: Invalid delta for move_by", file=sys.stderr)
            return

    try:
        _canvas.move(item_id, x, y)
        if lift:
            _canvas.tag_raise(item_id)  # Bring item to the top
        # refresh() # Might need refresh
    except tkinter.TclError as e:
        # print(f"Warning: Could not move item {item_id}: {e}", file=sys.stderr)
        pass


# --- KEYPRESS HANDLING ---

def _keypress(event):
    """ Internal handler for key press events. """
    global _got_release
    keysym = event.keysym
    # Standardize modifiers (optional, but can be useful)
    # if event.state & 0x4: keysym = "Control-" + keysym # Check Control key
    # if event.state & 0x1: keysym = "Shift-" + keysym   # Check Shift key
    _keysdown[keysym] = 1
    _keyswaiting[keysym] = 1
    _got_release = None


def _keyrelease(event):
    """ Internal handler for key release events. """
    global _got_release
    keysym = event.keysym
    try:
        if keysym in _keysdown:
            del _keysdown[keysym]
    except:
        pass  # Ignore errors if key wasn't tracked
    _got_release = 1  # Flag that a release happened (for auto-repeat handling)


def _clear_keys(event=None):
    """ Clears the key state dictionaries. """
    global _keysdown, _got_release, _keyswaiting
    _keysdown = {}
    _keyswaiting = {}
    _got_release = None


def keys_pressed():
    """ Returns a list of keys currently held down. """
    global _got_release
    if _root_window is None: return []

    # Process pending events to get up-to-date key state
    _root_window.update()

    # Handle the delayed release flag to mitigate auto-repeat issues
    if _got_release:
        # If a release happened, update again to ensure release is processed
        _root_window.update()
        _got_release = None  # Reset the flag

    return list(_keysdown.keys())


def keys_waiting():
    """ Returns a list of keys pressed since the last call to this function. """
    global _keyswaiting
    # Return current waiting keys and clear the dictionary
    keys = list(_keyswaiting.keys())
    _keyswaiting = {}
    return keys


def wait_for_keys():
    """ Blocks until one or more keys are pressed, returns the list of keys. """
    keys = []
    while not keys:  # Loop until keys list is not empty
        keys = keys_pressed()  # Check currently pressed keys
        if not keys:  # If no keys pressed, sleep briefly
            sleep(0.05)
    return keys


# --- MOUSE CLICK HANDLING ---

def _leftclick(event):
    global _leftclick_loc
    _leftclick_loc = (event.x, event.y)


def _rightclick(event):
    global _rightclick_loc
    _rightclick_loc = (event.x, event.y)


def _ctrl_leftclick(event):
    global _ctrl_leftclick_loc
    _ctrl_leftclick_loc = (event.x, event.y)


def wait_for_click():
    """ Blocks until a mouse click occurs, returns (position, type). """
    while True:
        # Check global click location variables
        global _leftclick_loc, _rightclick_loc, _ctrl_leftclick_loc
        if _leftclick_loc is not None:
            val = _leftclick_loc
            _leftclick_loc = None  # Reset after consuming
            return val, 'left'
        if _rightclick_loc is not None:
            val = _rightclick_loc
            _rightclick_loc = None
            return val, 'right'
        if _ctrl_leftclick_loc is not None:
            val = _ctrl_leftclick_loc
            _ctrl_leftclick_loc = None
            return val, 'ctrl_left'

        # If no click detected, sleep briefly before checking again
        sleep(0.05)
import random
import tkinter
import tkinter.font

"""
File: graphics.py
Authors: Chris Piech, Lisa Yan and Nick Troccoli
Version Date: August 11, 2020

This file creates a standard Tkinter Canvas (in other
words it does the work of making the window pop up for you).
You can use any function that you would normally use on
a tk canvas (https://effbot.org/tkinterbook/canvas.htm)

In addition we added a few convenience functions:
- canvas.get_mouse_x()
- canvas.get_new_mouse_clicks()
- canvas.get_new_key_presses()
- canvas.wait_for_click()
"""


class Canvas(tkinter.Canvas):
    """
    Canvas is a simplified interface on top of the tkinter Canvas to allow for easier manipulation of graphical objects.
    Canvas has a variety of functionality to create, modify and delete graphical objects, and also get information
    about the canvas contents.  Canvas is a subclass of `tkinter.Canvas`, so all tkinter functionality is also available
    if needed.
    """

    DEFAULT_WIDTH = 754
    """The default width of the canvas is 754."""

    DEFAULT_HEIGHT = 492
    """The default height of the canvas is 492."""

    DEFAULT_TITLE = "Canvas"
    """The default text shown in the canvas window titlebar is 'Canvas'."""

    def __init__(self, width=DEFAULT_WIDTH, height=DEFAULT_HEIGHT, title=DEFAULT_TITLE):
        """
        When creating a canvas, you can optionally specify a width and height.  If no width and height are specified,
        the canvas is initialized with its default size.

        Args:
            width: the width of the Canvas to create (or if not specified, uses `Canvas.DEFAULT_WIDTH`)
            height: the height of the Canvas to create (or if not specified, uses `Canvas.DEFAULT_HEIGHT`)
        """

        # Create the main program window
        self.main_window = tkinter.Tk()
        self.main_window.geometry("{}x{}".format(width, height))
        self.main_window.title(title)

        # call the tkinter Canvas constructor
        super().__init__(self.main_window, width=width, height=height, bd=0, highlightthickness=0)

        # Optional callbacks the client can specify to be called on each event
        self.on_mouse_pressed = None
        self.on_mouse_released = None
        self.on_key_pressed = None

        # Tracks whether the mouse is currently on top of the canvas
        self.mouse_on_canvas = False

        # List of presses not handled by a callback
        self.mouse_presses = []

        # List of key presses not handled by a callback
        self.key_presses = []

        # These are state variables so wait_for_click knows when to stop waiting and to
        # not call handlers when we are waiting for click
        self.wait_for_click_click_happened = False
        self.currently_waiting_for_click = False

        # bind events
        self.focus_set()
        self.bind("<Button-1>", lambda event: self.__mouse_pressed(event))
        self.bind("<ButtonRelease-1>", lambda event: self.__mouse_released(event))
        self.bind("<Key>", lambda event: self.__key_pressed(event))
        self.bind("<Enter>", lambda event: self.__mouse_entered())
        self.bind("<Leave>", lambda event: self.__mouse_exited())

        self._image_gb_protection = {}
        self.pack()
        self.update()

    def set_canvas_background_color(self, color):
        """
        Sets the background color of the canvas to the specified color string.

        Args:
            color: the color (string) to make the background of the canvas.
        """
        self.config(background=color)

    def get_canvas_width(self):
        """
        Get the width of the canvas.

        Returns:
            the current width of the canvas.
        """

        return self.winfo_width()

    def get_canvas_height(self):
        """
        Get the height of the canvas.

        Returns:
            the current height of the canvas.
        """
        return self.winfo_height()

    def set_canvas_title(self, title):
        """
        Sets the title text displayed in the Canvas's window title bar to be the specified text.

        Args:
            title: the text to display in the title bar
        """
        self.main_window.title(title)

    def set_canvas_size(self, width, height):
        """
        Sets the size of the canvas and its containing window to the specified width and height.

        Args:
            width: the width to set for the canvas and containing window
            height: the height to set for the canvas and containing window
        """
        self.main_window.geometry("{}x{}".format(width, height))
        self.config(width=width, height=height)

    """ EVENT HANDLING """

    def set_on_mouse_pressed(self, callback):
        """
        Set the specified function to be called whenever the mouse is pressed.  If this function is called
        multiple times, only the last specified function is called when the mouse is pressed.

        Args:
            callback: a function to call whenever the mouse is pressed.  Must take in two parameters, which
                are the x and y coordinates (in that order) of the mouse press that just occurred.  E.g. func(x, y).  If
                this parameter is None, no function will be called when the mouse is pressed.
        """
        self.on_mouse_pressed = callback

    def set_on_mouse_released(self, callback):
        """
        Set the specified function to be called whenever the mouse is released.  If this function is called
        multiple times, only the last specified function is called when the mouse is released.

        Args:
            callback: a function to call whenever the mouse is released.  Must take in two parameters, which
                are the x and y coordinates (in that order) of the mouse release that just occurred.  E.g. func(x, y).
                If this parameter is None, no function will be called when the mouse is released.
        """
        self.on_mouse_released = callback

    def set_on_key_pressed(self, callback):
        """
        Set the specified function to be called whenever a keyboard key is pressed.  If this function is called
        multiple times, only the last specified function is called when a key is pressed.

        Args:
            callback: a function to call whenever a key is pressed.  Must take in one parameter, which
                is the text name of the key that was just pressed (e.g. 'a' for the a key, 'b' for the b key, etc).
                E.g. func(key_char).  If this parameter is None, no function will be called when a key is pressed.
        """
        self.on_key_pressed = callback

    def get_new_mouse_clicks(self):
        """
        Returns a list of all mouse clicks that have occurred since the last call to this method or any registered
        mouse handler.

        Returns:
            a list of all mouse clicks that have occurred since the last call to this method or any registered
                mouse handler.  Each mouse click contains x and y properties for the click location, e.g.
                clicks = canvas.get_new_mouse_clicks(); print(clicks[0].x).
        """
        presses = self.mouse_presses
        self.mouse_presses = []
        return presses

    def get_new_key_presses(self):
        """
        Returns a list of all key presses that have occurred since the last call to this method or any registered
        key handler.

        Returns:
            a list of all key presses that have occurred since the last call to this method or any registered
                key handler.  Each key press contains a keysym property for the key pressed, e.g.
                presses = canvas.get_new_key_presses(); print(presses[0].keysym).
        """
        presses = self.key_presses
        self.key_presses = []
        return presses

    def __mouse_pressed(self, event):
        """
        Called every time the mouse is pressed.  If we are currently waiting for a mouse click via
        wait_for_click, do nothing.  Otherwise, if we have a registered mouse press handler, call that.  Otherwise,
        append the press to the list of mouse presses to be handled later.

        Args:
            event: an object representing the mouse press that just occurred.  Assumed to have x and y properties
                containing the x and y coordinates for this mouse press.
        """
        if not self.currently_waiting_for_click and self.on_mouse_pressed:
            self.on_mouse_pressed(event.x, event.y)
        elif not self.currently_waiting_for_click:
            self.mouse_presses.append(event)

    def __mouse_released(self, event):
        """
        Called every time the mouse is released.  If we are currently waiting for a mouse click via
        wait_for_click, update our state to reflect that a click happened.  Otherwise, if we have a registered mouse
        release handler, call that.

        Args:
            event: an object representing the mouse release that just occurred.  Assumed to have x and y properties
                containing the x and y coordinates for this mouse release.
        """

        # Do this all in one go to avoid setting click happened to True,
        # then having wait for click set currently waiting to false, then we go
        if self.currently_waiting_for_click:
            self.wait_for_click_click_happened = True
            return

        self.wait_for_click_click_happened = True
        if self.on_mouse_released:
            self.on_mouse_released(event.x, event.y)

    def __key_pressed(self, event):
        """
        Called every time a keyboard key is pressed.  If we have a registered key press handler, call that.  Otherwise,
        append the key press to the list of key presses to be handled later.

        Args:
            event: an object representing the key press that just occurred.  Assumed to have a keysym property
                containing the name of this key press.
        """
        if self.on_key_pressed:
            self.on_key_pressed(event.keysym)
        else:
            self.key_presses.append(event)

    def __mouse_entered(self):
        """
        Called every time the mouse enters the canvas.  Updates the internal state to record that
        the mouse is currently on the canvas.
        """
        self.mouse_on_canvas = True

    def __mouse_exited(self):
        """
        Called every time the mouse exits the canvas.  Updates the internal state to record that
        the mouse is currently not on the canvas.
        """
        self.mouse_on_canvas = False

    def mouse_is_on_canvas(self):
        """
        Returns whether or not the mouse is currently on the canvas.

        Returns:
            True if the mouse is currently on the canvas, or False otherwise.
        """
        return self.mouse_on_canvas

    def wait_for_click(self):
        """
        Waits until a mouse click occurs, and then returns.
        """
        self.currently_waiting_for_click = True
        self.wait_for_click_click_happened = False
        while not self.wait_for_click_click_happened:
            self.update()
        self.currently_waiting_for_click = False
        self.wait_for_click_click_happened = False

    def get_mouse_x(self):
        """
        Returns the mouse's current X location on the canvas.

        Returns:
            the mouses's current X location on the canvas.
        """
        """
        Note: winfo_pointerx is absolute mouse position (to screen, not window),
              winfo_rootx is absolute window position (to screen)
        Since move takes into account relative position to window,
        we adjust this mouse_x to be relative position to window.
        """
        return self.winfo_pointerx() - self.winfo_rootx()

    def get_mouse_y(self):
        """
        Returns the mouse's current Y location on the canvas.

        Returns:
            the mouse's current Y location on the canvas.
        """
        """
        Note: winfo_pointery is absolute mouse position (to screen, not window),
              winfo_rooty is absolute window position (to screen)
        Since move takes into account relative position to window,
        we adjust this mouse_y to be relative position to window.
        """
        return self.winfo_pointery() - self.winfo_rooty()

    """ GRAPHICAL OBJECT MANIPULATION """

    def get_left_x(self, obj):
        """
        Returns the leftmost x coordinate of the specified graphical object.

        Args:
            obj: the object for which to calculate the leftmost x coordinate

        Returns:
            the leftmost x coordinate of the specified graphical object.
        """
        if self.type(obj) != "text":
            return self.coords(obj)[0]
        else:
            return self.coords(obj)[0] - self.get_width(obj) / 2

    def get_top_y(self, obj):
        """
        Returns the topmost y coordinate of the specified graphical object.

        Args:
            obj: the object for which to calculate the topmost y coordinate

        Returns:
            the topmost y coordinate of the specified graphical object.
        """
        if self.type(obj) != "text":
            return self.coords(obj)[1]
        else:
            return self.coords(obj)[1] - self.get_height(obj) / 2

    def move_to(self, obj, new_x, new_y):
        """
        Same as `Canvas.moveto`.
        """
        # Note: Implements manually due to inconsistencies on some machines of bbox vs. coord.
        old_x = self.get_left_x(obj)
        old_y = self.get_top_y(obj)
        self.move(obj, new_x - old_x, new_y - old_y)

    def moveto(self, obj, x='', y=''):
        """
        Moves the specified graphical object to the specified location, which is its bounding box's
        new upper-left corner.

        Args:
            obj: the object to move
            x: the new x coordinate of the upper-left corner for the object
            y: the new y coordinate of the upper-left corner for the object
        """
        self.move_to(obj, float(x), float(y))

    def set_hidden(self, obj, hidden):
        """
        Sets the given graphical object to be either hidden or visible on the canvas.

        Args:
            obj: the graphical object to make hidden or visible on the canvas.
            hidden: True if the object should be hidden, False if the object should be visible.
        """
        self.itemconfig(obj, state='hidden' if hidden else 'normal')

    def set_fill_color(self, obj, fill_color):
        """
        Sets the fill color of the specified graphical object.  Cannot be used to change the fill color
        of non-fillable objects such as images - throws a tkinter.TclError.

        Args:
            obj: the object for which to set the fill color
            fill_color: the color to set the fill color to be, as a string.  If this is the empty string,
                the object will be set to be not filled.
        """
        try:
            self.itemconfig(obj, fill=fill_color)
        except tkinter.TclError:
            raise tkinter.TclError("You can't set the fill color on this object")

    def set_outline_color(self, obj, outline_color):
        """
        Sets the outline color of the specified graphical object.  Cannot be used to change the outline color
        of non-outlined objects such as images or text  - throws a tkinter.TclError.

        Args:
            obj: the object for which to set the outline color
            outline_color: the color to set the outline color to be, as a string.  If this is the empty string,
                the object will be set to not have an outline.
        """
        try:
            self.itemconfig(obj, outline=outline_color)
        except tkinter.TclError as e:
            raise tkinter.TclError("You can't set the outline color on this object")

    def set_outline_width(self, obj, width):
        """
        Sets the thickness of the outline of the specified graphical object.  Cannot be used on objects
        that are not outline-able, such as images or text.

        Args:
            obj: the object for which to set the outline width
            width: the width to set the outline to be.
        """
        self.itemconfig(obj, width=width)

    def set_text(self, obj, text):
        """
        Sets the text displayed by the given text object.  Cannot be used on any non-text graphical object.

        Args:
            obj: the text object for which to set the displayed text
            text: the new text for this graphical object to display
        """
        self.itemconfig(obj, text=text)

    def get_text(self, obj):
        """
        Returns the text displayed by the given text object.  Cannot be used on any non-text graphical object.

        Args:
            obj: the text object for which to get the displayed text

        Returns:
            the text currently displayed by this graphical object.
        """
        return self.itemcget(obj, 'text')

    def set_font(self, obj, font, size):
        """
        Sets the font and size for the text displayed by the given text object.  Cannot be used on any non-text
        graphical object.

        Args:
            obj: the text object for which to set the font and size
            font: the name of the font, as a string
            size: the size of the font
        """
        self.itemconfig(obj, font=(font, size))

    def raise_to_front(self, obj):
        """
        Sends the given object to the very front of all the other objects on the canvas.

        Args:
            obj: the object to bring to the front of the objects on the canvas
        """
        self.raise_in_front_of(obj, 'all')

    def raise_in_front_of(self, obj, above):
        """
        Sets the first object to be directly in front of the second object in Z-ordering on the canvas.  In other words,
        the first object will now appear in front of the second object and all objects behind the second object,
        but behind all objects that the second object is also behind.

        Args:
            obj: the object to put in front of the second object
            above: the object to put the first object directly in front of
        """
        self.tag_raise(obj, above)

    def lower_to_back(self, obj):
        """
        Sends the given object to be behind all the other objects on the canvas

        Args:
            obj: the object to put behind all other objects on the canvas
        """
        self.lower_behind(obj, 'all')

    def lower_behind(self, obj, behind):
        """
        Sets the first object to be directly behind the second object in Z-ordering on the canvas.  In other words,
        the first object will now appear directly behind the second object and all objects in front of the
        second object, but in front of all objects that the second object is also in front of.

        Args:
            obj: the object to put in front of the second object
            behind: the object to put the first object directly behind
        """
        self.tag_lower(obj, behind)


    def create_image_with_size(self, x, y, width, height, file_path, **kwargs):
        """
        Creates an image with the specified filename at the specified position on the canvas, and resized
        to the specified width and height.

        Args:
            x: the x coordinate of the top-left corner of the image on the canvas
            y: the y coordinate of the top-left corner of the image on the canvas
            width: the width to set for the image
            height: the height to set for the image
            file_path: the path to the image file to load and display on the canvas
            kwargs: other tkinter keyword args

        Returns:
            the graphical image object that is displaying the specified image at the specified location with the
                specified size.
        """
        return self.__create_image_with_optional_size(x, y, file_path, width=width, height=height, **kwargs)

    def __create_image_with_optional_size(self, x, y, file_path, width=None, height=None, **kwargs):
        """
        Creates an image with the specified filename at the specified position on the canvas.
        Optionally specify the width and height to resize the image.

        Args:
            x: the x coordinate of the top-left corner of the image on the canvas
            y: the y coordinate of the top-left corner of the image on the canvas
            file_path: the path to the image file to load and display on the canvas
            width: optional width to include for the image.  If none, uses the width of the image file.
            height: optional height to include for the image  If none, uses the height of the image file.
            kwargs: other tkinter keyword args

        Returns:
            the graphical image object that is displaying the specified image at the specified location.
        """
        from PIL import ImageTk
        from PIL import Image
        image = Image.open(file_path)

        # Resize the image if another width and height is specified
        if width is not None and height is not None:
            image = image.resize((width, height))

        image = ImageTk.PhotoImage(image)
        img_obj = super().create_image(x, y, anchor="nw", image=image, **kwargs)
        # note: if you don't do this, the image gets garbage collected!!!
        # this introduces a memory leak which can be fixed by overloading delete
        self._image_gb_protection[img_obj] = image
        return img_obj

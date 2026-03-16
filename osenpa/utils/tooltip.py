import tkinter as tk
from ui.theme import T

class Tooltip:
    """A lightweight tooltip for Tkinter widgets."""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._after_id = None
        self._tw = None
        
        self.widget.bind("<Enter>", self.schedule, add="+")
        self.widget.bind("<Leave>", self.unschedule, add="+")
        self.widget.bind("<ButtonPress>", self.unschedule, add="+")

    def schedule(self, event=None):
        self.unschedule()
        self._after_id = self.widget.after(self.delay, self.show)

    def unschedule(self, event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self.hide()

    def show(self):
        if self._tw:
            return
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        
        self._tw = tk.Toplevel(self.widget)
        self._tw.wm_overrideredirect(True)
        self._tw.wm_geometry(f"+{x}+{y}")
        
        label = tk.Label(
            self._tw, text=self.text, justify='left',
            bg=T("PRIMARY_BG"), fg=T("PRIMARY_FG"),
            relief='solid', borderwidth=1,
            font=("Segoe UI", 9)
        )
        label.pack(ipadx=4)

    def hide(self):
        if self._tw:
            self._tw.destroy()
            self._tw = None

def add_tooltip(widget, text):
    return Tooltip(widget, text)

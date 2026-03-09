"""
help_panel.py — Osenpa Auto Clicker Help & Guide
Responsive, scrollable help guide for all users.
"""
import tkinter as tk
from ui.theme import T, divider
from utils.i18n import tr

def get_sections():
    return [
        (
            tr("👋  What is Osenpa Auto Clicker?"),
            tr("Osenpa Auto Clicker is a desktop automation tool. It lets your computer click "
               "the mouse, press keyboard keys, and find colors or images on screen — all "
               "automatically, as many times as you want.\n\n"
               "Think of it like a robot that copies exactly what you tell it to do, "
               "and repeats it perfectly every time.")
        ),
        (
            tr("📋  Steps — The Heart of Automation"),
            tr("Everything you want the computer to do is called a Step. You build a list "
               "of steps, and Osenpa Auto Clicker runs them in order.\n\n"
               "• KEYBOARD step — presses a key (e.g. Enter, Space, A, Ctrl+C)\n"
               "• MOUSE step — clicks at a position on screen\n"
               "• COLOR step — waits until a color appears, then clicks it\n"
               "• IMAGE step — waits until a picture appears on screen, then clicks it\n"
               "• DELAY step — pauses for a moment before continuing\n"
               "• IF COLOR / IF IMAGE — checks if something is there, and does one "
               "thing if yes, another if no\n\n"
               "TIP: Double-click any step in the list to edit it. "
               "Drag steps up and down to reorder them.")
        ),
        (
            tr("⌨️  Keyboard Panel"),
            tr("Use the Keyboard panel to press any key or key combination.\n\n"
               "• SINGLE KEY — press one key at a time (e.g. press F5 to refresh)\n"
               "• HOTKEY COMBO — press multiple keys at once "
               "(e.g. ctrl+z to undo, ctrl+shift+s to save as)\n"
               "• REPEAT — how many times to press the key\n"
               "• INTERVAL — how long to wait between each press\n\n"
               "TIP: Click inside the KEY box and press the key you want — "
               "it gets captured automatically. No typing required.")
        ),
        (
            tr("🖱️  Mouse Panel"),
            tr("Use the Mouse panel to click anywhere on the screen.\n\n"
               "• FIXED COORDINATES — click at a specific X,Y position on screen\n"
               "• CURRENT CURSOR POSITION — click wherever your mouse is at the time\n"
               "• LEFT / RIGHT / MIDDLE button — choose which mouse button to click\n"
               "• DRAG — click and drag from one point to another (like drag-and-drop)\n\n"
               "TIP: Use the PICK TARGET button to click on the screen and "
               "automatically fill in the X,Y coordinates. No manual typing!")
        ),
        (
            tr("🎨  Color Detection"),
            tr("Color Detection watches the screen and clicks as soon as it spots "
               "a color you have defined.\n\n"
               "• PICK COLOR — opens a color picker to choose an exact color\n"
               "• PICK FROM SCREEN — click anywhere on your screen to grab that pixel's color\n"
               "• TOLERANCE — how exact the color match must be. "
               "A value of 15–30 works well for most cases. "
               "Higher value = more forgiving (catches similar shades too). "
               "Lower value = very strict exact match only.\n"
               "• SCAN INTERVAL — how often to check the screen (e.g. every 0.5 seconds)\n"
               "• STEP INTERVAL — how long to wait after each click before scanning again\n\n"
               "TIP: You can add multiple colors. The detector will click when ANY of "
               "them appears on screen — whichever it finds first.")
        ),
        (
            tr("🖼️  Image Detection"),
            tr("Image Detection looks for a picture (called a template) on your screen "
               "and clicks it as soon as it finds it.\n\n"
               "• LOAD IMAGE FILE — pick a .png or .jpg file from your computer\n"
               "• FROM CLIPBOARD — if you copied a screenshot, paste it directly here\n"
               "• CONFIDENCE — how closely the screen must match your template image. "
               "0.8 (80%) is a good starting point. Lower = more lenient match.\n\n"
               "TIP: After each click, the mouse automatically moves to the corner of your "
               "screen so it does not block the image on the next scan. This is built-in.\n\n"
               "TIP: Use a small, unique part of a button or icon as your template — "
               "not the whole screen. Smaller templates match faster and more reliably.")
        ),
        (
            tr("🔀  IF COLOR / IF IMAGE — Conditional Steps"),
            tr("IF steps are like a decision point in your automation — imagine a fork in "
               "the road where the computer looks at the screen and chooses which path to take.\n\n"
               "How it works:\n"
               "1. The computer looks at the screen for a specific color or image\n"
               "2. IF it FINDS it → it does the THEN action\n"
               "3. IF it does NOT find it → it does the ELSE action\n\n"
               "Example — IF COLOR:\n"
               "• You are playing a game and you want the bot to click a green button when it "
               "appears, but skip and wait when it's not there yet.\n"
               "• IF COLOR = green → THEN = click it → ELSE = do nothing\n\n"
               "Example — IF IMAGE:\n"
               "• You want to check if a 'Loading...' spinner is visible.\n"
               "• IF IMAGE = spinner.png → THEN = wait 2 seconds → ELSE = continue clicking\n\n"
               "Available actions for THEN and ELSE:\n"
               "• CLICK FOUND — click exactly where the color/image was found\n"
               "• CLICK (fixed position) — click a specific coordinate\n"
               "• PRESS KEY — press a keyboard key\n"
               "• DELAY — wait a number of seconds\n"
               "• STOP — stop the automation completely\n"
               "• DO NOTHING — skip and move to the next step\n\n"
               "TIP: IF steps are great for automations that need to react differently "
               "depending on what's happening on screen — like a game that changes state, "
               "or a website that shows different buttons at different times.\n\n"
               "TIP: You can set a TIMEOUT for IF steps. If the color/image is not found "
               "within that many seconds, the ELSE branch runs automatically.")
        ),
        (
            tr("🔴  Record Actions (Macro)"),
            tr("The Macro Recorder watches everything you do on the keyboard and mouse, "
               "then converts your actions into steps automatically.\n\n"
               "1. Open the Record Actions panel\n"
               "2. Click START RECORDING (or press the hotkey)\n"
               "3. Do whatever you want to automate — type, click, navigate\n"
               "4. Press the hotkey again to stop recording\n"
               "5. Osenpa Auto Clicker will add all your actions as steps\n\n"
               "TIP: Record once, then run as many times as you like.")
        ),
        (
            tr(">  Running Steps"),
            tr("Once you have steps in your list, click RUN STEPS at the bottom "
               "(or press F7) to start.\n\n"
               "• LOOP — run the steps more than once\n"
               "• INFINITE — keep repeating until you press STOP\n"
               "• STEP INTERVAL — add extra wait time between each step\n"
               "• RUN FROM HERE — use the button to start from a specific step "
               "instead of from the beginning\n\n"
               "TIP: Press F7 to start and stop at any time, even when the "
               "app is minimized in the taskbar.")
        ),
        (
            tr("💾  Profiles"),
            tr("Profiles let you save your panel settings and reload them any time.\n\n"
               "• Enter a name and click SAVE CURRENT to save your current settings\n"
               "• Select a profile from the list and click LOAD PROFILE to restore it\n"
               "• You can save settings from all panels, or just one specific panel\n\n"
               "TIP: Create different profiles for different tasks — "
               "one for gaming, one for work, one for web automation.")
        ),
        (
            tr("⚙  Settings"),
            tr("The Settings panel lets you customize the app:\n\n"
               "• SHOW ACTIVE TASK INDICATOR — a small overlay in the bottom-right "
               "corner shows what is running while automation is active\n"
               "• SHOW SCAN AREA BORDER — highlights the region being scanned "
               "for color or image detection\n"
               "• HOTKEYS — see all current keyboard shortcuts at a glance\n"
               "• AUTO-CLOSE TIMER — set the app to close itself after a chosen amount "
               "of time (great for setting a session limit)\n"
               "• RESET ALL — clear everything and start fresh "
               "(your saved profiles are always kept)")
        ),
        (
            tr("💡  Tips & Tricks"),
            tr("• Use Ctrl+Z to undo the last change to your step list. Ctrl+Y to redo.\n\n"
               "• Add a DELAY step between fast actions to give the computer time "
               "to respond. 0.5–1 second is often enough.\n\n"
               "• For web automation, use Image Detection to find buttons — "
               "it works even when button positions shift around.\n\n"
               "• For game automation, Color Detection is faster and more reliable "
               "than image matching when targeting a single colored pixel or area.\n\n"
               "• Use the PICK AREA button in Color/Image panels to limit scanning "
               "to a small part of the screen — this makes detection much faster.\n\n"
               "• Export your steps to a JSON file to share them or back them up.\n\n"
               "• Press F7 any time to stop an automation — even in the middle of a step.")
        ),
        (
            tr("❓  Frequently Asked Questions"),
            tr("Q: Why doesn't Color Detection find my color?\n"
               "A: Try raising the Tolerance value (15–30 is recommended). "
               "Lighting, screen scaling, and image compression can all shift colors slightly.\n\n"
               "Q: Why doesn't Image Detection find my image?\n"
               "A: Make sure the template looks exactly like what's on screen. "
               "Try lowering Confidence to 0.7. Use a tight crop of the unique element — "
               "avoid templates with lots of background or changing content.\n\n"
               "Q: Can I run steps while the app is minimized?\n"
               "A: Yes. Once started, automation continues in the background. "
               "Use the F7 hotkey to stop it at any time.\n\n"
               "Q: Steps are running too fast or too slow — what do I do?\n"
               "A: Adjust the INTERVAL on each individual step, or use the STEP INTERVAL "
               "in the footer to add a global delay between all steps.\n\n"
               "Q: I accidentally deleted my steps. Can I undo?\n"
               "A: Yes! Press Ctrl+Z to undo. Osenpa Auto Clicker keeps full undo history.\n\n"
               "Q: What is IF COLOR / IF IMAGE used for?\n"
               "A: They let your automation make decisions. For example: "
               "if a green button appears on screen, click it; otherwise wait. "
               "See the IF COLOR / IF IMAGE section above for full details.")
        ),
        (
            tr("❤  About & Support"),
            tr("Osenpa Auto Clicker is built by an independent developer with a passion "
               "for saving people time. If this tool has made your life a little easier, "
               "please consider visiting the Support & Donate panel to buy me a coffee! "
               "Your support is what keeps this project alive and free for everyone.") + "\n\nosenpacom@gmail.com"
        ),
    ]


class HelpPanel:
    def __init__(self, parent):
        self.box = tk.Frame(parent, bg=T("SURFACE"))
        self.box.pack(fill="both", expand=True)
        self._section_labels = []   # (body_label, …) for responsive wraplength
        self._build()

    def _build(self):
        box = self.box

        # ── Scrollable canvas ──────────────────────────────────────
        canvas = tk.Canvas(box, bg=T("SURFACE"), highlightthickness=0)
        sb = tk.Scrollbar(box, orient="vertical", command=canvas.yview,
                           bg=T("SCROLL_BG"), troughcolor=T("SCROLL_BG"),
                           activebackground=T("SCROLL_ACTIVE"),
                           relief="flat", bd=0, width=10)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        wrap = tk.Frame(canvas, bg=T("SURFACE"))
        win_id = canvas.create_window((0, 0), window=wrap, anchor="nw")

        def on_frame_resize(e):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_resize(e):
            # Resize wrap to canvas width and update all label wraplengths
            canvas.itemconfig(win_id, width=e.width)
            new_wl = max(200, e.width - 80)
            for lbl in self._section_labels:
                try:
                    lbl.config(wraplength=new_wl)
                except Exception:
                    pass

        wrap.bind("<Configure>", on_frame_resize)
        canvas.bind("<Configure>", on_canvas_resize)

        canvas.bind("<Enter>",
            lambda e: canvas.bind_all("<MouseWheel>",
                lambda ev: canvas.yview_scroll(int(-1*(ev.delta/120)), "units")))
        canvas.bind("<Leave>",
            lambda e: canvas.unbind_all("<MouseWheel>"))

        # ── Title ──────────────────────────────────────────────────
        title_bar = tk.Frame(wrap, bg=T("SURFACE"))
        title_bar.pack(fill="x", padx=36, pady=(28, 6))
        tk.Label(title_bar, text=tr("HELP & GUIDE"),
                  bg=T("SURFACE"), fg=T("FG"),
                  font=("Segoe UI", 13, "bold")).pack(anchor="w")
        tk.Label(title_bar,
                  text=tr("Everything you need to know about Osenpa Auto Clicker"),
                  bg=T("SURFACE"), fg=T("FG2"),
                  font=("Segoe UI", 9)).pack(anchor="w", pady=(3, 0))

        divider(wrap, padx=36, pady=(14, 0))

        # ── Sections ───────────────────────────────────────────────
        for title, body in get_sections():
            section_frame = tk.Frame(wrap, bg=T("SURFACE"))
            section_frame.pack(fill="x", padx=36, pady=(22, 0))

            tk.Label(
                section_frame,
                text=title,
                bg=T("SURFACE"), fg=T("FG"),
                font=("Segoe UI", 11, "bold"),
                anchor="w", justify="left"
            ).pack(anchor="w", pady=(0, 8))

            body_lbl = tk.Label(
                section_frame,
                text=body,
                bg=T("SURFACE"), fg=T("FG2"),
                font=("Segoe UI", 9),
                anchor="w", justify="left",
                wraplength=600   # initial — updated on canvas resize
            )
            body_lbl.pack(anchor="w", fill="x")
            self._section_labels.append(body_lbl)

            tk.Frame(wrap, bg=T("BORDER"), height=1).pack(
                fill="x", padx=36, pady=(18, 0))

        tk.Frame(wrap, bg=T("SURFACE"), height=40).pack()

    def refresh_labels(self):
        pass

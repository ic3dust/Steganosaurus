import tkinter as tk
from pathlib import Path
from PIL import Image, ImageTk


def show():
    win = tk.Tk()
    win.overrideredirect(True) # no window sefault style
    win.attributes("-topmost", True)
    win.configure(bg="black") # create-remove bg
    win.wm_attributes("-transparentcolor", "black")
    win.attributes("-alpha", 0.0)

    ROOT = Path(__file__).resolve().parent.parent # ../ ../
    LOGO = ROOT / "icons" / "logo.png"

    image = Image.open(LOGO)
    photo = ImageTk.PhotoImage(image) # convert into tkinter format 

    # center
    width, height = image.size
    w = win.winfo_screenwidth()
    h = win.winfo_screenheight()
    x = (w - width) // 2
    y = (h - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")

    # box for img and add label
    label = tk.Label(win, image=photo, bg="black", borderwidth=0)
    label.pack() 

    # cool stuff
    def fade(alpha=0.0):
        alpha += 0.05
        if alpha <= 1.1:
            win.attributes("-alpha", alpha)
            win.after(30, lambda: fade(alpha))
        else:
            win.after(1500, win.destroy)

    fade()
    win.mainloop() # but to be destroyed after 1500 
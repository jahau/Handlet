#!/usr/bin/env python3
"""Full-screen test patterns for checking the 5" display: dead pixels,
colour, alignment and touch. Uses Tkinter (preinstalled with Raspberry Pi
OS desktop).

  ./screen-test.py
  DISPLAY=:0 ./screen-test.py      # when started over SSH (X11)

Keys / taps: next pattern = tap, Space or Right arrow; quit = Esc or q.
In the touch pattern, drag a finger to draw.
"""
import tkinter as tk

PATTERNS = ["#FF0000", "#00FF00", "#0000FF", "#FFFFFF", "#000000",
            "grid", "gradient", "touch"]


class ScreenTest:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="none")
        self.w = self.root.winfo_screenwidth()
        self.h = self.root.winfo_screenheight()
        self.c = tk.Canvas(self.root, width=self.w, height=self.h,
                           highlightthickness=0)
        self.c.pack()
        self.i = 0
        self.last = None
        for k in ("<space>", "<Right>"):
            self.root.bind(k, self.next)
        for k in ("<Escape>", "q"):
            self.root.bind(k, lambda e: self.root.destroy())
        self.c.bind("<Button-1>", self.on_press)
        self.c.bind("<B1-Motion>", self.on_drag)
        self.draw()

    def draw(self) -> None:
        p = PATTERNS[self.i]
        self.c.delete("all")
        if p.startswith("#"):
            self.c.config(bg=p)
        elif p == "grid":
            self.c.config(bg="black")
            for x in range(0, self.w, 40):
                self.c.create_line(x, 0, x, self.h, fill="white")
            for y in range(0, self.h, 40):
                self.c.create_line(0, y, self.w, y, fill="white")
            self.c.create_rectangle(1, 1, self.w - 1, self.h - 1, outline="red", width=2)
        elif p == "gradient":
            for x in range(self.w):
                v = int(255 * x / max(1, self.w - 1))
                self.c.create_line(x, 0, x, self.h, fill=f"#{v:02x}{v:02x}{v:02x}")
        elif p == "touch":
            self.c.config(bg="black")
            self.c.create_text(self.w // 2, 20, fill="gray",
                               text="Draw to test touch - Space/Right for next, Esc to quit")
        self.c.create_text(self.w - 10, self.h - 10, anchor="se", fill="gray",
                           text=f"{self.w}x{self.h}  {self.i + 1}/{len(PATTERNS)}")

    def next(self, _e=None) -> None:
        self.i = (self.i + 1) % len(PATTERNS)
        self.draw()

    def on_press(self, e) -> None:
        if PATTERNS[self.i] == "touch":
            self.last = (e.x, e.y)
        else:
            self.next()

    def on_drag(self, e) -> None:
        if PATTERNS[self.i] == "touch" and self.last:
            self.c.create_line(*self.last, e.x, e.y, fill="cyan", width=3)
            self.last = (e.x, e.y)


if __name__ == "__main__":
    ScreenTest().root.mainloop()

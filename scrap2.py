from tkinter import *

class Example(object):
    def __init__(self):
        self.master = Tk()
        self.l1 = Button(self.master)
        self.l2 = Button(self.master)
        self.b1 = Button(self.master)

        self.l1.grid()
        self.l2.grid()
        self.b1.grid()
        self.l1.description = "This is label 1"
        self.l2.description = "This is label 2"
        self.b1.description = "This is the OK button"

        for widget in (self.l1, self.l2, self.b1):
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)


        self.master.mainloop()

    def on_enter(self, event):
        description = getattr(event.widget, "description", "")
        self.l2.configure(text=description)
        for item in dir(event):
            print(item)

    def on_leave(self, enter):
        self.l2.configure(text="")

Example()

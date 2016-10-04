import Tkinter
import tkMessageBox

top = Tkinter.Tk()
def deleteme():
    tkMessageBox.askquestion("Delete", "Are You Sure?", icon='warning')
    if 'yes':
        print "Deleted"
    else:
        print "I'm Not Deleted Yet"
B1 = Tkinter.Button(top, text = "Delete", command = deleteme)
B1.pack()
top.mainloop()
import os
import sys
import sqlite3
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Example for your background image
bg_image_path = resource_path("assets/bg.jpg")
bg_image = Image.open(bg_image_path)


class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login - Billing System")
        self.root.state("zoomed")  # maximize window

        # ✅ Use dynamic path for .exe compatibility
        self.base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        self.bg_path = resource_path( "assets/bg.jpg")
        self.db_path = resource_path( "billing.db")

        # Load and resize background
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        self.original_bg = Image.open(self.bg_path)
        self.bg_image = self.original_bg.resize((screen_width, screen_height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(self.bg_image)
        self.bg_label = Label(self.root, image=self.bg_photo)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.bind("<Configure>", self.resize_bg)

        # White login frame at center
        self.frame = Frame(self.root, bd=4, relief=RIDGE, bg="grey")
        self.frame.place(relx=0.5, rely=0.4, anchor="center", width=350, height=300)

        title = Label(self.frame, text="Admin Login", font=("times new roman", 22, "bold"), bg="grey", fg="black")
        title.pack(pady=20)

        lbl_user = Label(self.frame, text="Username", font=("times new roman", 14), bg="grey", anchor="w")
        lbl_user.pack(padx=20, fill='x')

        self.txt_user = Entry(self.frame, font=("times new roman", 14))
        self.txt_user.pack(padx=20, fill='x', pady=5)

        lbl_pass = Label(self.frame, text="Password", font=("times new roman", 14), bg="grey", anchor="w")
        lbl_pass.pack(padx=20, fill='x')

        self.txt_pass = Entry(self.frame, font=("times new roman", 14), show="*")
        self.txt_pass.pack(padx=20, fill='x', pady=5)

        self.btn_toggle = Button(self.frame, text="Show", command=self.toggle_password,
                                 font=("times new roman", 10), bg="white", fg="blue", bd=0)
        self.btn_toggle.pack(pady=2)

        btn_login = Button(self.frame, text="Login", command=self.login, font=("times new roman", 12),
                           bg="green", fg="white", width=10, height=1, relief=RAISED, bd=3)
        btn_login.pack(pady=5)



    def resize_bg(self, event):
        new_width = event.width
        new_height = event.height
        resized_image = self.original_bg.resize((new_width, new_height), Image.LANCZOS)
        self.bg_photo = ImageTk.PhotoImage(resized_image)
        self.bg_label.configure(image=self.bg_photo)
        self.bg_label.image = self.bg_photo

    def toggle_password(self):
        if self.txt_pass.cget("show") == "":
            self.txt_pass.config(show="*")
            self.btn_toggle.config(text="Show")
        else:
            self.txt_pass.config(show="")
            self.btn_toggle.config(text="Hide")

    def login(self):
        username = self.txt_user.get()
        password = self.txt_pass.get()

        if username == "" or password == "":
            messagebox.showerror("Error", "All fields are required!", parent=self.root)
            return

        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            row = cur.fetchone()
            con.close()

            if row is None:
                messagebox.showerror("Error", "Invalid Username or Password", parent=self.root)
            else:
                messagebox.showinfo("Success", "Login Successful!", parent=self.root)
                self.root.destroy()

                # ✅ Open billing system
                from billing import billingClass
                new_root = Tk()
                billingClass(new_root)
                new_root.mainloop()

        except Exception as ex:
            messagebox.showerror("Error", f"Error due to: {str(ex)}", parent=self.root)




if __name__ == "__main__":
    root = Tk()
    obj = LoginWindow(root)
    root.mainloop()

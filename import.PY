import tkinter as tk
import hashlib
import random

# ========================
# Password strength and crack estimation
# ========================
def get_password_strength(password):
    length = len(password)
    if length < 8:
        return "Weak", "red"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_special = any(c in "!@#$%^&*_." for c in password)

    letters_only = password.isalpha()
    digits_only = password.isdigit()

    if letters_only or digits_only:
        return "Weak", "red"
    elif has_upper and has_lower and has_special:
        return "Very Strong", "lime"
    elif (any(c.isalpha() for c in password) and has_digit and has_special):
        return "Strong", "green"
    elif any(c.isalpha() for c in password) and has_digit:
        return "Medium", "orange"
    else:
        return "Weak", "red"

def estimate_crack_time(strength):
    if strength == "Weak":
        return "a few minutes"
    elif strength == "Medium":
        return "weeks to months"
    elif strength in ("Strong", "Very Strong"):
        return "many years"
    return "unknown"

# ========================
# Main Application
# ========================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Secure Authentication System")
        self.width = 400
        self.height = 520
        self.geometry(f"{self.width}x{self.height}")
        self.configure(bg="#1e1e2f")
        self.center_window(self)

        # shared data
        self.stored_username = ""
        self.stored_password = ""       # hashed
        self.attempts = 3
        self.generated_otp = ""
        self.locked = False

        # container for pages
        container = tk.Frame(self, bg="#1e1e2f")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for PageClass in (LoginPage, RegisterPage, WelcomePage):
            page_name = PageClass.__name__
            frame = PageClass(parent=container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("LoginPage")

    def center_window(self, window, width=None, height=None):
        window.update_idletasks()
        if width is None:
            width = window.winfo_width()
        if height is None:
            height = window.winfo_height()
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        window.geometry(f"{width}x{height}+{x}+{y}")

    def show_frame(self, page_name, **kwargs):
        frame = self.frames[page_name]
        if page_name == "LoginPage":
            frame.refresh()
        elif page_name == "RegisterPage":
            frame.clear_fields()
        elif page_name == "WelcomePage":
            frame.set_welcome(kwargs.get("username", ""))
        frame.tkraise()

    # OTP popup 
    def show_otp_notification(self, otp):
        popup = tk.Toplevel(self)
        popup.title("OTP Code")
        popup_width = 220
        popup_height = 100
        popup.configure(bg="#2c2c3e")
        popup.grab_set()
        tk.Label(popup, text="🔐 Your OTP Code", fg="white", bg="#2c2c3e",
                 font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(popup, text=otp, fg="cyan", bg="#2c2c3e",
                 font=("Arial", 16)).pack(pady=5)
        tk.Button(popup, text="OK", command=popup.destroy,
                  bg="#4CAF50", fg="white").pack(pady=5)
        popup.update_idletasks()
        screen_width = popup.winfo_screenwidth()
        x = screen_width - popup_width - 20  
        y = 20
        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")

    # OTP verification popup
    def create_otp_verification_popup(self, username):
        otp_win = tk.Toplevel(self)
        otp_win.title("OTP Verification")
        otp_win_width = 300
        otp_win_height = 200
        otp_win.configure(bg="#2c2c3e")
        otp_win.grab_set()
        tk.Label(otp_win, text="Enter OTP Code", fg="white", bg="#2c2c3e",
                 font=("Arial", 12)).pack(pady=5)
        otp_entry = tk.Entry(otp_win)
        otp_entry.pack(pady=5)

        error_frame = tk.Frame(otp_win, bg="#2c2c3e")
        error_label = tk.Label(error_frame, text="", fg="red", bg="#2c2c3e")
        error_label.pack(side="left")
        dismiss_btn = tk.Button(error_frame, text="OK", bg="#f44336", fg="white",
                                command=error_frame.pack_forget)
        dismiss_btn.pack(side="left", padx=5)

        def verify_otp():
            if otp_entry.get() == self.generated_otp:
                otp_win.destroy()
                self.show_frame("WelcomePage", username=username)
            else:
                otp_entry.delete(0, tk.END)
                error_label.config(text="❌ Wrong OTP!")
                error_frame.pack(pady=5)

        tk.Button(otp_win, text="Verify", command=verify_otp,
                  bg="#4CAF50", fg="white").pack(pady=10)
        self.center_window(otp_win, otp_win_width, otp_win_height)

    # Login logic
    def login_attempt(self, username, password):
        if self.locked or self.attempts <= 0:
            return "locked", 0

        hashed = hashlib.md5(password.encode()).hexdigest()
        if username == self.stored_username and hashed == self.stored_password:
            self.generated_otp = str(random.randint(1000, 9999))
            self.show_otp_notification(self.generated_otp)
            self.create_otp_verification_popup(username)
            return "otp", self.attempts
        else:
            self.attempts -= 1
            if self.attempts == 0:
                self.stored_username = ""
                self.stored_password = ""
                self.locked = True
            return "fail", self.attempts

    # Registration
    def register_user(self, username, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        self.stored_username = username
        self.stored_password = hashlib.md5(password.encode()).hexdigest()
        self.attempts = 3
        self.locked = False
        return True, "Registered successfully"

# ========================
# Pages (Frames)
# ========================

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#2c2c3e")
        self.controller = controller

        tk.Label(self, text="Secure System", font=("Arial", 20, "bold"),
                 fg="white", bg="#2c2c3e").pack(pady=20)

        tk.Label(self, text="Username", fg="white", bg="#2c2c3e").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        tk.Label(self, text="Password", fg="white", bg="#2c2c3e").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        # ----------- Toggle Button (Checkbutton) لإظهار/إخفاء كلمة المرور ----------
        self.show_password_var = tk.BooleanVar(value=False)
        self.toggle_check = tk.Checkbutton(
            self,
            text="Show Password",
            variable=self.show_password_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_password_visibility,
            bg="#2c2c3e",
            fg="white",
            selectcolor="#2c2c3e",   
            activebackground="#2c2c3e",
            activeforeground="white"
        )
        self.toggle_check.pack(pady=2)
        # -------------------------------------------------

        self.message_label = tk.Label(self, text="", fg="white", bg="#2c2c3e")
        self.message_label.pack(pady=5)

        tk.Button(self, text="Login", bg="#4CAF50", fg="white",
                  width=15, command=self.login).pack(pady=10)

        tk.Button(self, text="Don't have an account? Register",
                  bg="#2196F3", fg="white", command=self.go_to_register).pack(pady=5)

    def toggle_password_visibility(self):
        """تبديل إظهار/إخفاء كلمة المرور حسب حالة الـ Checkbutton"""
        if self.show_password_var.get():
            self.entry_pass.config(show="")
        else:
            self.entry_pass.config(show="*")

    def login(self):
        if self.controller.locked or self.controller.attempts <= 0:
            self.message_label.config(text="🔒 Account locked! Contact support.", fg="orange")
            return

        username = self.entry_user.get().strip()
        password = self.entry_pass.get().strip()

        if not username or not password:
            self.message_label.config(text="❌ Please enter all fields.", fg="red")
            return

        if self.controller.stored_username == "":
            self.message_label.config(text="❌ User does not exist.", fg="red")
            return

        status, attempts_left = self.controller.login_attempt(username, password)

        if status == "otp":
            self.message_label.config(text="OTP sent. Check popup.", fg="cyan")
        elif status == "fail":
            if attempts_left == 0:
                self.message_label.config(text="🔒 Account locked temporarily for security reasons.\nPlease contact support.", fg="orange")
            else:
                self.message_label.config(text=f"❌ Wrong! Attempts left: {attempts_left}", fg="red")
        elif status == "locked":
            self.message_label.config(text="🔒 Account locked! Contact support.", fg="orange")

    def go_to_register(self):
        self.controller.show_frame("RegisterPage")

    def refresh(self):
        self.entry_user.delete(0, tk.END)
        self.entry_pass.delete(0, tk.END)
        self.message_label.config(text="")
        # إعادة التعيين إلى مخفي
        self.entry_pass.config(show="*")
        self.show_password_var.set(False)

class RegisterPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#2c2c3e")
        self.controller = controller

        tk.Label(self, text="Create Account", font=("Arial", 18, "bold"),
                 fg="white", bg="#2c2c3e").pack(pady=15)

        tk.Label(self, text="Username", fg="white", bg="#2c2c3e").pack()
        self.entry_user = tk.Entry(self)
        self.entry_user.pack(pady=5)

        tk.Label(self, text="Password", fg="white", bg="#2c2c3e").pack()
        self.entry_pass = tk.Entry(self, show="*")
        self.entry_pass.pack(pady=5)

        # ----------- Toggle Button (Checkbutton) لإظهار/إخفاء كلمة المرور 
        self.show_password_var = tk.BooleanVar(value=False)
        self.toggle_check = tk.Checkbutton(
            self,
            text="Show Password",
            variable=self.show_password_var,
            onvalue=True,
            offvalue=False,
            command=self.toggle_password_visibility,
            bg="#2c2c3e",
            fg="white",
            selectcolor="#2c2c3e",
            activebackground="#2c2c3e",
            activeforeground="white"
        )
        self.toggle_check.pack(pady=2)
        # -------------------------------------------------

        self.strength_label = tk.Label(self, text="", bg="#2c2c3e")
        self.strength_label.pack(pady=5)

        self.password_var = tk.StringVar()
        self.entry_pass.config(textvariable=self.password_var)
        self.password_var.trace("w", self.update_strength)

        tk.Label(self, text="Want to check strength?", fg="white", bg="#2c2c3e").pack(pady=(10,0))
        self.attack_result = tk.Label(self, text="", bg="#2c2c3e")
        self.attack_result.pack()
        tk.Button(self, text="Attack", bg="#f44336", fg="white",
                  command=self.estimate_crack).pack(pady=5)

        self.feedback = tk.Label(self, text="", bg="#2c2c3e")
        self.feedback.pack(pady=5)

        tk.Button(self, text="Register", bg="#4CAF50", fg="white",
                  width=15, command=self.register).pack(pady=10)

    def toggle_password_visibility(self):
        
        if self.show_password_var.get():
            self.entry_pass.config(show="")
        else:
            self.entry_pass.config(show="*")

    def update_strength(self, *args):
        password = self.password_var.get()
        strength, color = get_password_strength(password)
        self.strength_label.config(text=f"Strength: {strength}", fg=color)

    def estimate_crack(self):
        password = self.entry_pass.get()
        if not password:
            self.attack_result.config(text="Enter a password first.", fg="white")
            return
        strength, _ = get_password_strength(password)
        time_str = estimate_crack_time(strength)
        self.attack_result.config(text=f"Estimated time to crack: {time_str}", fg="red")

    def register(self):
        username = self.entry_user.get().strip()
        password = self.entry_pass.get()
        if not username:
            self.feedback.config(text="Username cannot be empty.", fg="red")
            return
        if len(password) < 8:
            self.feedback.config(text="Password must be at least 8 characters.", fg="red")
            return

        success, message = self.controller.register_user(username, password)
        if success:
            self.feedback.config(text="Registered! Returning to login...", fg="lightgreen")
            self.after(1000, self.go_to_login)
        else:
            self.feedback.config(text=message, fg="red")

    def go_to_login(self):
        self.controller.show_frame("LoginPage")

    def clear_fields(self):
        self.entry_user.delete(0, tk.END)
        self.entry_pass.delete(0, tk.END)
        self.strength_label.config(text="")
        self.attack_result.config(text="")
        self.feedback.config(text="")
        
        self.entry_pass.config(show="*")
        self.show_password_var.set(False)

class WelcomePage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent, bg="#2c2c3e")
        self.controller = controller

        self.welcome_label = tk.Label(self, text="", font=("Arial", 18, "bold"),
                                      fg="white", bg="#2c2c3e")
        self.welcome_label.pack(pady=50)

        tk.Label(self, text="You can use the system.", fg="white", bg="#2c2c3e").pack(pady=10)

        tk.Button(self, text="Logout", bg="#f44336", fg="white",
                  width=15, command=self.logout).pack(pady=20)

    def set_welcome(self, username):
        self.welcome_label.config(text=f"Welcome, {username}!")

    def logout(self):
        self.controller.show_frame("LoginPage")

# ========================
# Run the application
# ========================
if __name__ == "__main__":
    app = App()
    app.mainloop()
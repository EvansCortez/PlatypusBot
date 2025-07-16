import tkinter as tk
from core.chatbot import Chatbot
from config import Config

class ChatGUI:
    def __init__(self, root):
        self.bot = Chatbot(Config)
        self.root = root
        self.root.title("PlatypusBot GUI")
        self.root.configure(bg="#23232f")

        # Sidebar
        sidebar = tk.Frame(root, bg="#181820", width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Button(
            sidebar,
            text="+ New chat",
            bg="#35354a",
            fg="#fff",
            font=("Segoe UI", 11, "bold"),
            bd=0,
            relief=tk.FLAT,
            padx=10,
            pady=10,
            anchor="w",
            command=self.clear_chat
        ).pack(fill=tk.X, pady=(20, 10), padx=10)

        for label in self.bot.conversation_starters:
            tk.Label(
                sidebar,
                text=label,
                bg="#181820",
                fg="#ececf1",
                anchor="w",
                padx=10,
                pady=6
            ).pack(fill=tk.X, padx=10)

        # Main area
        main_frame = tk.Frame(root, bg="#23232f")
        main_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.text_area = tk.Text(
            main_frame,
            state="disabled",
            bg="#23232f",
            fg="#ececf1",
            font=("Segoe UI", 12),
            bd=0,
            wrap=tk.WORD
        )
        self.text_area.pack(padx=20, pady=(20, 0), fill=tk.BOTH, expand=True)

        self.entry = tk.Entry(
            main_frame,
            font=("Segoe UI", 12),
            bg="#35354a",
            fg="#ececf1",
            insertbackground="#ececf1",
            bd=0
        )
        self.entry.pack(padx=20, pady=10, fill=tk.X)
        self.entry.bind("<Return>", self.send_message)

        self.speak_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            main_frame,
            text="Speak Responses",
            variable=self.speak_var,
            bg="#23232f",
            fg="#ececf1",
            selectcolor="#23232f"
        ).pack(anchor="w", padx=20)

        self.insert_greeting()

    def insert_greeting(self):
        self.text_area.config(state="normal")
        self.text_area.insert(
            tk.END,
            "Chatbot: Hello! Type 'exit' to quit or 'help' for options.\n"
        )
        self.text_area.config(state="disabled")

    def clear_chat(self):
        self.text_area.config(state="normal")
        self.text_area.delete(1.0, tk.END)
        self.insert_greeting()
        self.text_area.config(state="disabled")

    def send_message(self, event=None):
        user_input = self.entry.get()
        if not user_input:
            return

        self.text_area.config(state="normal")
        self.text_area.insert(tk.END, f"You: {user_input}\n")

        if user_input.lower() == "exit":
            self.text_area.insert(tk.END, "Chatbot: Goodbye!\n")
            self.text_area.config(state="disabled")
            self.root.quit()
            return

        result = self.bot.process_message(user_input)
        response = result.get("response", "Sorry, I have no response.")
        self.text_area.insert(tk.END, f"Chatbot: {response}\n")

        if self.speak_var.get():
            self.bot.services["tts"].speak(response)

        self.text_area.config(state="disabled")
        self.entry.delete(0, tk.END)

# IMPORTANT: This file is correct Python code.
# The "_tkinter" error is NOT caused by your code.
# It is caused by your Python installation missing Tkinter support.

# To fix this, do NOT change this file.
# Instead, follow these steps in your terminal (not in Python):

# 1. Make sure Tcl/Tk is installed:
#    brew install tcl-tk

# 2. Add these lines to your ~/.zshrc or ~/.bash_profile, then restart your terminal:
#    export LDFLAGS="-L$(brew --prefix tcl-tk)/lib"
#    export CPPFLAGS="-I$(brew --prefix tcl-tk)/include"
#    export PKG_CONFIG_PATH="$(brew --prefix tcl-tk)/lib/pkgconfig"
#    export PATH="$(brew --prefix tcl-tk)/bin:$PATH"

# 3. Open a new terminal and run:
#    pyenv uninstall 3.11.6
#    env PYTHON_CONFIGURE_OPTS="--with-tcltk-includes='-I$(brew --prefix tcl-tk)/include' --with-tcltk-libs='-L$(brew --prefix tcl-tk)/lib -ltcl8.6 -ltk8.6'" pyenv install 3.11.6

# 4. Set your local Python version:
#    pyenv local 3.11.6

# 5. Test Tkinter:
#    python3 -c "import tkinter; print(tkinter.TkVersion)"

# Only after you see a version number (not an error), run your chatbox_gui.py script.

# If you still have issues, run:
#    xcode-select --install
# to ensure you have all developer tools.

if __name__ == "__main__":
    root = tk.Tk()
    ChatGUI(root)
    root.mainloop()

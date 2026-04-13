from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import ttk

from platypusbot.core.chatbot import Chatbot


class ChatGUI:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.bot = Chatbot()
        self.root.title("PlatypusBot")
        self.root.geometry("1280x820")
        self.root.minsize(980, 680)
        self.root.configure(bg="#09121c")

        self._build_layout()
        self._append_message(
            "PlatypusBot",
            "Hello! I can switch between live services and an LLM chat layer. Ask in English, Spanish, French, German, Portuguese, or Italian.",
            role="assistant",
        )
        self._refresh_history_panel()
        self._refresh_system_badges()
        self.entry.focus_set()

    def _build_layout(self) -> None:
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("App.TFrame", background="#09121c")
        style.configure("Sidebar.TFrame", background="#0d1b2a")
        style.configure("Main.TFrame", background="#f4f7fb")
        style.configure("SidebarTitle.TLabel", background="#0d1b2a", foreground="#f8fbff", font=("Georgia", 22, "bold"))
        style.configure("SidebarBody.TLabel", background="#0d1b2a", foreground="#b8c6db", font=("Helvetica", 11))

        shell = ttk.Frame(self.root, style="App.TFrame")
        shell.pack(fill=tk.BOTH, expand=True)

        sidebar = ttk.Frame(shell, style="Sidebar.TFrame", width=280)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        hero = tk.Frame(sidebar, bg="#17324d", height=156)
        hero.pack(fill=tk.X, padx=18, pady=(18, 14))
        hero.pack_propagate(False)
        tk.Label(
            hero,
            text="Multilingual\nAI workspace",
            bg="#17324d",
            fg="#f8fbff",
            font=("Georgia", 20, "bold"),
            justify=tk.LEFT,
        ).pack(anchor="w", padx=16, pady=(18, 8))
        tk.Label(
            hero,
            text="LLM + live tools + memory",
            bg="#17324d",
            fg="#95b4d4",
            font=("Helvetica", 11),
        ).pack(anchor="w", padx=16)

        ttk.Label(sidebar, text="PlatypusBot", style="SidebarTitle.TLabel").pack(anchor="w", padx=22, pady=(0, 6))
        ttk.Label(
            sidebar,
            text="Hybrid desktop assistant with a live-data service layer, optional OpenAI model responses, and persistent memory.",
            style="SidebarBody.TLabel",
            wraplength=220,
            justify=tk.LEFT,
        ).pack(anchor="w", padx=22, pady=(0, 18))

        tk.Button(
            sidebar,
            text="New chat",
            command=self.clear_chat,
            bg="#49c6e5",
            fg="#062033",
            bd=0,
            padx=14,
            pady=10,
            activebackground="#7bdff2",
            activeforeground="#062033",
            font=("Helvetica", 11, "bold"),
        ).pack(fill=tk.X, padx=22, pady=(0, 18))

        tk.Label(
            sidebar,
            text="Quick actions",
            bg="#0d1b2a",
            fg="#7bdff2",
            font=("Helvetica", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, padx=22, pady=(0, 8))

        for prompt in [
            "weather in New York",
            "latest news about AI",
            "what time is it in Tokyo",
            "translate hello to Spanish",
            "Explain machine learning in French",
        ]:
            tk.Button(
                sidebar,
                text=prompt,
                command=lambda value=prompt: self._use_shortcut(value),
                bg="#17324d",
                fg="#edf6ff",
                bd=0,
                wraplength=200,
                justify=tk.LEFT,
                anchor="w",
                padx=12,
                pady=10,
                activebackground="#234566",
                activeforeground="#edf6ff",
            ).pack(fill=tk.X, padx=22, pady=5)

        tk.Label(
            sidebar,
            text="Recent memory",
            bg="#0d1b2a",
            fg="#7bdff2",
            font=("Helvetica", 10, "bold"),
            anchor="w",
        ).pack(fill=tk.X, padx=22, pady=(18, 8))
        self.history_panel = tk.Frame(sidebar, bg="#0d1b2a")
        self.history_panel.pack(fill=tk.BOTH, expand=True, padx=22, pady=(0, 22))

        main = ttk.Frame(shell, style="Main.TFrame")
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        topbar = tk.Frame(main, bg="#f4f7fb")
        topbar.pack(fill=tk.X, padx=24, pady=(24, 10))
        tk.Label(
            topbar,
            text="Current session",
            bg="#f4f7fb",
            fg="#17324d",
            font=("Georgia", 21, "bold"),
        ).pack(side=tk.LEFT)

        self.model_badge = tk.Label(
            topbar,
            text="Model: fallback",
            bg="#102840",
            fg="#f8fbff",
            padx=12,
            pady=6,
            font=("Helvetica", 10, "bold"),
        )
        self.model_badge.pack(side=tk.RIGHT)
        self.llm_badge = tk.Label(
            topbar,
            text="LLM offline",
            bg="#fde2e4",
            fg="#7f1d1d",
            padx=12,
            pady=6,
            font=("Helvetica", 10, "bold"),
        )
        self.llm_badge.pack(side=tk.RIGHT, padx=(0, 8))

        banner = tk.Frame(main, bg="#0f2d4d", height=98)
        banner.pack(fill=tk.X, padx=24, pady=(0, 14))
        banner.pack_propagate(False)
        tk.Label(
            banner,
            text="Modern assistant canvas",
            bg="#0f2d4d",
            fg="#f8fbff",
            font=("Georgia", 20, "bold"),
        ).pack(anchor="w", padx=20, pady=(14, 0))
        tk.Label(
            banner,
            text="Routing between realtime data, translation, a model-backed chat layer, and classic bot tools.",
            bg="#0f2d4d",
            fg="#b8c6db",
            font=("Helvetica", 11),
        ).pack(anchor="w", padx=18)

        badge_row = tk.Frame(main, bg="#f4f7fb")
        badge_row.pack(fill=tk.X, padx=24, pady=(0, 12))
        self.route_badge = tk.Label(
            badge_row,
            text="Route: general",
            bg="#d8f3dc",
            fg="#1b4332",
            padx=12,
            pady=6,
            font=("Helvetica", 10, "bold"),
        )
        self.route_badge.pack(side=tk.LEFT, padx=(0, 8))
        self.language_badge = tk.Label(
            badge_row,
            text="Language: english",
            bg="#e0c3fc",
            fg="#5b2a86",
            padx=12,
            pady=6,
            font=("Helvetica", 10, "bold"),
        )
        self.language_badge.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(
            badge_row,
            text="Realtime tools",
            bg="#fde68a",
            fg="#713f12",
            padx=12,
            pady=6,
            font=("Helvetica", 10, "bold"),
        ).pack(side=tk.LEFT)

        chat_card = tk.Frame(main, bg="#ffffff", highlightthickness=1, highlightbackground="#d7e3f4")
        chat_card.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 12))

        self.canvas = tk.Canvas(chat_card, bg="#ffffff", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(chat_card, orient="vertical", command=self.canvas.yview)
        self.messages_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.messages_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.messages_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        composer = tk.Frame(main, bg="#f4f7fb")
        composer.pack(fill=tk.X, padx=24, pady=(0, 24))
        self.status_label = tk.Label(
            composer,
            text="Ready for live, multilingual, and LLM-backed prompts",
            bg="#f4f7fb",
            fg="#46627f",
            anchor="w",
            font=("Helvetica", 10),
        )
        self.status_label.pack(fill=tk.X, pady=(0, 10))

        suggestion_row = tk.Frame(composer, bg="#f4f7fb")
        suggestion_row.pack(fill=tk.X, pady=(0, 10))
        for label in ["Summarize this topic", "Ask in Spanish", "Get live news", "Explain with examples"]:
            tk.Button(
                suggestion_row,
                text=label,
                command=lambda value=label: self._insert_suggestion(value),
                bg="#ffffff",
                fg="#17324d",
                bd=0,
                padx=12,
                pady=7,
                activebackground="#e6eef9",
                activeforeground="#17324d",
            ).pack(side=tk.LEFT, padx=(0, 8))

        input_row = tk.Frame(composer, bg="#f4f7fb")
        input_row.pack(fill=tk.X)
        self.entry = tk.Entry(
            input_row,
            bg="#ffffff",
            fg="#1c3552",
            relief=tk.FLAT,
            font=("Helvetica", 12),
            insertbackground="#1c3552",
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=14, padx=(0, 12))
        self.entry.bind("<Return>", self.send_message)

        tk.Button(
            input_row,
            text="Voice",
            command=self.use_voice_input,
            bg="#d7eafc",
            fg="#1c3552",
            bd=0,
            padx=14,
            pady=12,
            activebackground="#bfddf7",
            activeforeground="#1c3552",
        ).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(
            input_row,
            text="Send",
            command=self.send_message,
            bg="#1d8fe1",
            fg="#f8fbff",
            bd=0,
            padx=18,
            pady=12,
            activebackground="#49c6e5",
            activeforeground="#062033",
            font=("Helvetica", 11, "bold"),
        ).pack(side=tk.LEFT)

    def _insert_suggestion(self, label: str) -> None:
        templates = {
            "Summarize this topic": "Summarize the key ideas about renewable energy.",
            "Ask in Spanish": "Explica el aprendizaje automático de forma sencilla.",
            "Get live news": "latest news about technology",
            "Explain with examples": "Explain recursion with examples.",
        }
        self.entry.delete(0, tk.END)
        self.entry.insert(0, templates.get(label, label))
        self.entry.focus_set()

    def _use_shortcut(self, prompt: str) -> None:
        self.entry.delete(0, tk.END)
        self.entry.insert(0, prompt)
        self.send_message()

    def _message_time(self) -> str:
        return datetime.now().strftime("%I:%M %p").lstrip("0")

    def _append_message(self, speaker: str, message: str, role: str) -> None:
        outer = tk.Frame(self.messages_frame, bg="#ffffff")
        outer.pack(fill=tk.X, padx=18, pady=8, anchor="e" if role == "user" else "w")
        meta = tk.Label(
            outer,
            text=f"{speaker} • {self._message_time()}",
            bg="#ffffff",
            fg="#68809b",
            font=("Helvetica", 9, "bold"),
            anchor="e" if role == "user" else "w",
            justify=tk.RIGHT if role == "user" else tk.LEFT,
        )
        meta.pack(anchor="e" if role == "user" else "w", padx=6, pady=(0, 4))
        bubble = tk.Label(
            outer,
            text=message,
            bg="#1d8fe1" if role == "user" else "#eff6ff",
            fg="#f8fbff" if role == "user" else "#16324f",
            font=("Helvetica", 12),
            wraplength=680,
            justify=tk.LEFT,
            padx=16,
            pady=12,
            bd=0,
        )
        bubble.pack(anchor="e" if role == "user" else "w")
        self.root.after(20, lambda: self.canvas.yview_moveto(1.0))

    def _append_streaming_message(self, speaker: str, message: str, role: str) -> None:
        outer = tk.Frame(self.messages_frame, bg="#ffffff")
        outer.pack(fill=tk.X, padx=18, pady=8, anchor="e" if role == "user" else "w")
        meta = tk.Label(
            outer,
            text=f"{speaker} • {self._message_time()}",
            bg="#ffffff",
            fg="#68809b",
            font=("Helvetica", 9, "bold"),
            anchor="e" if role == "user" else "w",
            justify=tk.RIGHT if role == "user" else tk.LEFT,
        )
        meta.pack(anchor="e" if role == "user" else "w", padx=6, pady=(0, 4))
        bubble = tk.Label(
            outer,
            text="",
            bg="#1d8fe1" if role == "user" else "#eff6ff",
            fg="#f8fbff" if role == "user" else "#16324f",
            font=("Helvetica", 12),
            wraplength=680,
            justify=tk.LEFT,
            padx=16,
            pady=12,
            bd=0,
        )
        bubble.pack(anchor="e" if role == "user" else "w")
        chunks = self.bot.stream_response(message)

        def write_chunk(index: int = 0) -> None:
            if index >= len(chunks):
                self.root.after(20, lambda: self.canvas.yview_moveto(1.0))
                return
            bubble.configure(text=bubble.cget("text") + chunks[index])
            self.root.after(22, lambda: self.canvas.yview_moveto(1.0))
            self.root.after(24, lambda: write_chunk(index + 1))

        write_chunk()

    def _set_status(self, text: str) -> None:
        self.status_label.configure(text=text)

    def _show_typing(self) -> None:
        self._set_status("PlatypusBot is thinking across live tools and the LLM layer...")

    def _clear_typing(self) -> None:
        self._set_status("Ready for live, multilingual, and LLM-backed prompts")

    def _refresh_system_badges(self) -> None:
        status = self.bot.get_ui_status()
        self.route_badge.configure(text=f"Route: {status['route']}")
        self.language_badge.configure(text=f"Language: {status['language']}")
        self.model_badge.configure(text=f"Model: {status['model']}")
        llm_online = status["llm"] == "Connected"
        self.llm_badge.configure(
            text=f"LLM: {status['llm']}",
            bg="#d8f3dc" if llm_online else "#fde2e4",
            fg="#1b4332" if llm_online else "#7f1d1d",
        )

    def _refresh_history_panel(self) -> None:
        for child in self.history_panel.winfo_children():
            child.destroy()

        history = self.bot.database.get_history(limit=6)
        if not history:
            tk.Label(
                self.history_panel,
                text="No saved conversations yet.",
                bg="#0d1b2a",
                fg="#7f95ad",
                wraplength=200,
                justify=tk.LEFT,
                anchor="w",
            ).pack(fill=tk.X)
            return

        for user_input, response, _timestamp in history:
            card = tk.Frame(self.history_panel, bg="#11263b")
            card.pack(fill=tk.X, pady=5)
            tk.Label(
                card,
                text=f"You: {user_input[:40]}",
                bg="#11263b",
                fg="#edf6ff",
                anchor="w",
                justify=tk.LEFT,
                wraplength=200,
                padx=10,
                pady=8,
                font=("Helvetica", 10, "bold"),
            ).pack(fill=tk.X)
            tk.Label(
                card,
                text=f"Bot: {response[:58]}",
                bg="#11263b",
                fg="#a9bdd3",
                anchor="w",
                justify=tk.LEFT,
                wraplength=200,
                padx=10,
                pady=(0, 10),
                font=("Helvetica", 9),
            ).pack(fill=tk.X)

    def clear_chat(self) -> None:
        for child in self.messages_frame.winfo_children():
            child.destroy()
        self._append_message(
            "PlatypusBot",
            "Fresh chat started. Ask for weather, headlines, translation, multilingual help, or anything else in the toolkit.",
            role="assistant",
        )
        self._clear_typing()
        self.bot.set_preference("interface", "gui")
        self._refresh_system_badges()

    def use_voice_input(self) -> None:
        self._set_status("Listening for voice input...")
        spoken_text = self.bot.listen()
        self.entry.delete(0, tk.END)
        self.entry.insert(0, spoken_text)
        self._set_status("Voice captured. Review or send it.")

    def _finish_message(self, user_input: str) -> None:
        if user_input.lower() == "exit":
            self._append_message("PlatypusBot", "Goodbye!", role="assistant")
            self.bot.close()
            self.root.after(250, self.root.destroy)
            return

        response = self.bot.handle_message(user_input)
        self.bot.set_preference("interface", "gui")
        self._append_streaming_message("PlatypusBot", response, role="assistant")
        self._clear_typing()
        self._refresh_history_panel()
        self._refresh_system_badges()

    def send_message(self, event: object | None = None) -> None:
        user_input = self.entry.get().strip()
        if not user_input:
            return

        self._append_message("You", user_input, role="user")
        self.entry.delete(0, tk.END)
        self._show_typing()
        self.root.after(180, lambda value=user_input: self._finish_message(value))


def run_gui() -> None:
    root = tk.Tk()
    app = ChatGUI(root)
    root.protocol("WM_DELETE_WINDOW", lambda: (app.bot.close(), root.destroy()))
    root.mainloop()


if __name__ == "__main__":
    run_gui()

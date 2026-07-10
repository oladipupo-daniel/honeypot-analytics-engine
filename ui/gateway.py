# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
import os
import sys

import customtkinter as ctk
from tkinter import messagebox

# Ensure the project root is on sys.path so package-relative imports work when
# running modules directly from the ui package.
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import auth_utils
from core.theme_manager import get_active_theme


class IdentityGateway(ctk.CTkFrame):
    def __init__(self, master):
        self.theme = get_active_theme()
        super().__init__(
            master,
            width=600,
            height=520,
            corner_radius=24,
            fg_color=self.theme["bg_panel"],
            border_width=1,
            border_color=self.theme["border"],
        )
        self.master = master
        self.failed_attempts = 0
        self.max_attempts = 5

        self.pack_propagate(False)
        self.create_widgets()

    def create_widgets(self):
        t = self.theme

        self.title_label = ctk.CTkLabel(
            self,
            text="H O N E Y P O T",
            font=ctk.CTkFont(family="Segoe UI", size=30, weight="bold"),
            text_color=t["text_color"],
        )
        self.title_label.pack(pady=(60, 2))

        self.subtitle_label = ctk.CTkLabel(
            self,
            text="SOVEREIGN LOCAL DATA INGESTION ENGINE\n[ Privacy by Design ]",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=t["muted_text"],
        )
        self.subtitle_label.pack(pady=(0, 26))

        welcome_username = auth_utils.get_stored_username()
        if welcome_username:
            welcome_lbl = ctk.CTkLabel(
                self,
                text=f"Welcome back, {welcome_username} 👋",
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                text_color=t["honey"],
            )
            welcome_lbl.pack(pady=(0, 14))

        entry_kwargs = dict(
            width=280,
            height=44,
            corner_radius=12,
            border_color=t["border"],
            fg_color=t["bg_main"],
            text_color=t["text_color"],
        )

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Username", **entry_kwargs)
        self.username_entry.pack(pady=(0, 12))
        self.username_entry.bind("<Button-1>", lambda e: self.show_recent_usernames())
        self.username_entry.bind("<FocusIn>", lambda e: self.show_recent_usernames())

        # Hidden until there's history to show; populated on demand so it
        # always reflects the latest recent-usernames list.
        self.recent_usernames_frame = ctk.CTkFrame(
            self, fg_color=t["bg_main"], corner_radius=10,
            border_width=1, border_color=t["border"]
        )

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Password", show="•", **entry_kwargs)
        self.password_entry.pack(pady=(0, 6))
        self.password_entry.bind("<Return>", lambda event: self.handle_login())

        # Error / status message (hidden until needed)
        self.error_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=t["danger"]
        )
        self.error_label.pack(pady=(0, 6))

        self.sign_in_btn = ctk.CTkButton(
            self,
            text="Sign In",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=52,
            width=240,
            fg_color=t["honey"],
            hover_color=t["honey_hover"],
            text_color=t["honey_text"],
            corner_radius=16,
            command=self.handle_login,
        )
        self.sign_in_btn.pack(pady=(6, 6))

        links_frame = ctk.CTkFrame(self, fg_color="transparent")
        links_frame.pack(pady=(2, 10))

        self.forgot_btn = ctk.CTkButton(
            links_frame,
            text="Forgot password?",
            font=ctk.CTkFont(family="Segoe UI", size=11, underline=True),
            fg_color="transparent",
            hover_color=t["bg_main"],
            text_color=t["accent"],
            width=120,
            height=26,
            command=self.show_hint,
        )
        self.forgot_btn.pack(side="left", padx=6)

        self.reset_btn = ctk.CTkButton(
            links_frame,
            text="Reset my account",
            font=ctk.CTkFont(family="Segoe UI", size=11, underline=True),
            fg_color="transparent",
            hover_color=t["bg_main"],
            text_color=t["muted_text"],
            width=120,
            height=26,
            command=self.trigger_reset,
        )
        self.reset_btn.pack(side="left", padx=6)

        self.footer_label = ctk.CTkLabel(
            self,
            text="Hermetically Sealed Local Memory Sandbox Active",
            font=ctk.CTkFont(family="Segoe UI", size=10, slant="italic"),
            text_color=t["muted_text"],
        )
        self.footer_label.pack(pady=(16, 0))

        self.signature_lbl = ctk.CTkLabel(
            self,
            text="by Daniel Oladipupo",
            font=("Lucida Handwriting", 11, "italic"),
            text_color=t["muted_text"],
        )
        self.signature_lbl.pack(side="bottom", anchor="e", padx=20, pady=(10, 0))

    def show_recent_usernames(self):
        """Populates and reveals the recent-usernames dropdown, right under the username field."""
        recents = auth_utils.get_recent_usernames()
        for w in self.recent_usernames_frame.winfo_children():
            w.destroy()

        if not recents:
            self.recent_usernames_frame.pack_forget()
            return

        t = self.theme
        ctk.CTkLabel(
            self.recent_usernames_frame, text="RECENT USERNAMES",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"), text_color=t["muted_text"]
        ).pack(anchor="w", padx=8, pady=(6, 2))

        for name in recents[:5]:
            btn = ctk.CTkButton(
                self.recent_usernames_frame, text=name, anchor="w",
                fg_color="transparent", hover_color=t["bg_panel"], text_color=t["text_color"],
                height=28, corner_radius=6, font=ctk.CTkFont(family="Segoe UI", size=12),
                command=lambda n=name: self.pick_recent_username(n)
            )
            btn.pack(fill="x", padx=6, pady=1)

        ctk.CTkLabel(self.recent_usernames_frame, text="", height=2).pack()
        # Always re-inserted directly under the username field, regardless
        # of how many times it's been shown/hidden before.
        self.recent_usernames_frame.pack(fill="x", padx=40, pady=(0, 6), before=self.password_entry)

    def pick_recent_username(self, username):
        self.username_entry.delete(0, "end")
        self.username_entry.insert(0, username)
        self.recent_usernames_frame.pack_forget()
        self.password_entry.focus_set()

    def handle_login(self):
        self.recent_usernames_frame.pack_forget()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if username:
            auth_utils.remember_username(username)

        if auth_utils.verify_login(username, password):
            self.error_label.configure(text="", text_color="green")
            self.master.current_role = "Admin"
            from ui.dashboard import MainDashboard
            self.master.switch_screen(MainDashboard, identity_profile=username or "Admin")
        else:
            self.failed_attempts += 1
            if self.failed_attempts >= 3:
                hint = auth_utils.get_stored_hint()
                self.error_label.configure(text=f"Invalid credentials. Hint: {hint}", text_color="orange")
            else:
                self.error_label.configure(text="Invalid credentials.", text_color="red")

    def show_hint(self):
        if not auth_utils.vault_exists():
            messagebox.showinfo("No account yet", "No account has been set up on this device yet.")
            return
        hint = auth_utils.get_stored_hint()
        messagebox.showinfo("Your password hint", hint)

    def trigger_reset(self):
        confirmed = messagebox.askyesno(
            "Reset local account?",
            "This permanently deletes your local credentials on this device.\n\n"
            "You'll be asked to create a brand new username and password. "
            "This cannot be undone. Continue?",
        )
        if not confirmed:
            return

        auth_utils.reset_vault()
        messagebox.showinfo("Account reset", "Your local credentials were cleared. Let's set up a new account.")
        from ui.onboarding import OnboardingScreen
        self.master.switch_screen(OnboardingScreen)

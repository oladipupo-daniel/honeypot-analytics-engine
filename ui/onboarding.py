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

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import auth_utils
from core.theme_manager import get_active_theme


class OnboardingScreen(ctk.CTkFrame):
    """
    First-run registration screen. Shown once, the very first time the app is
    launched on a machine (no vault.json yet). The user picks their own
    username, password and a personal hint - all of it stays local to this
    PC, nothing is emailed or uploaded anywhere.
    """

    def __init__(self, master):
        self.theme = get_active_theme()
        super().__init__(
            master,
            width=600,
            height=560,
            corner_radius=24,
            fg_color=self.theme["bg_panel"],
            border_width=1,
            border_color=self.theme["border"],
        )
        self.master = master
        self.pack_propagate(False)
        self.create_widgets()

    def create_widgets(self):
        t = self.theme

        icon_lbl = ctk.CTkLabel(self, text="🍯", font=ctk.CTkFont(size=40))
        icon_lbl.pack(pady=(36, 0))

        title_lbl = ctk.CTkLabel(
            self,
            text="WELCOME TO HONEYPOT",
            font=ctk.CTkFont(family="Segoe UI", size=26, weight="bold"),
            text_color=t["text_color"],
        )
        title_lbl.pack(pady=(4, 2))

        subtitle_lbl = ctk.CTkLabel(
            self,
            text="Let's set up your account. This stays on your device only —\nno email, no server, just yours.",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=t["muted_text"],
            justify="center",
        )
        subtitle_lbl.pack(pady=(0, 22))

        entry_kwargs = dict(
            width=320,
            height=42,
            corner_radius=12,
            border_color=t["border"],
            fg_color=t["bg_main"],
            text_color=t["text_color"],
        )

        self.username_entry = ctk.CTkEntry(self, placeholder_text="Choose a username", **entry_kwargs)
        self.username_entry.pack(pady=(0, 10))

        self.password_entry = ctk.CTkEntry(self, placeholder_text="Choose a password", show="•", **entry_kwargs)
        self.password_entry.pack(pady=(0, 10))

        self.confirm_entry = ctk.CTkEntry(self, placeholder_text="Confirm password", show="•", **entry_kwargs)
        self.confirm_entry.pack(pady=(0, 10))

        self.hint_entry = ctk.CTkEntry(self, placeholder_text="Password hint (in case you forget)", **entry_kwargs)
        self.hint_entry.pack(pady=(0, 8))
        self.confirm_entry.bind("<Return>", lambda e: self.handle_register())
        self.hint_entry.bind("<Return>", lambda e: self.handle_register())

        self.status_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(family="Segoe UI", size=11), text_color=t["danger"]
        )
        self.status_label.pack(pady=(0, 8))

        self.register_btn = ctk.CTkButton(
            self,
            text="Create My Account",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=52,
            width=240,
            fg_color=t["honey"],
            hover_color=t["honey_hover"],
            text_color=t["honey_text"],
            corner_radius=16,
            command=self.handle_register,
        )
        self.register_btn.pack(pady=(4, 16))

        footer_lbl = ctk.CTkLabel(
            self,
            text="🔒 Stored locally with salted PBKDF2 hashing — your password itself is never saved.",
            font=ctk.CTkFont(family="Segoe UI", size=10, slant="italic"),
            text_color=t["muted_text"],
        )
        footer_lbl.pack(side="bottom", pady=(0, 18))

    def handle_register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        hint = self.hint_entry.get().strip()

        if not username:
            self.status_label.configure(text="Please choose a username.")
            return
        if len(password) < 4:
            self.status_label.configure(text="Password should be at least 4 characters.")
            return
        if password != confirm:
            self.status_label.configure(text="Passwords don't match — try again.")
            return
        if not hint:
            proceed = messagebox.askyesno(
                "No hint set",
                "You didn't set a password hint. If you forget your password later, "
                "you'll need to fully reset your account and lose saved preferences. Continue anyway?",
            )
            if not proceed:
                return

        auth_utils.initialize_vault(username, password, hint)
        auth_utils.remember_username(username)
        messagebox.showinfo(
            "Account created",
            f"Welcome, {username}! Your account is ready on this device. Please sign in to continue.",
        )
        from ui.gateway import IdentityGateway
        self.master.switch_screen(IdentityGateway)

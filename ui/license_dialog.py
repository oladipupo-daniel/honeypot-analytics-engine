import customtkinter as ctk
from tkinter import messagebox
from core.hardware_id import get_machine_id
import os

class LicenseWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("License Activation")
        self.geometry("400x300")
        
        # UI Elements
        ctk.CTkLabel(self, text="Trial Expired", font=("Segoe UI", 20, "bold")).pack(pady=20)
        
        ctk.CTkLabel(self, text="Your Machine ID:").pack()
        self.id_entry = ctk.CTkEntry(self, width=300)
        self.id_entry.insert(0, get_machine_id())
        self.id_entry.configure(state="disabled") # Users should not edit this
        self.id_entry.pack(pady=5)
        
        ctk.CTkLabel(self, text="Enter License Key:").pack(pady=(10, 0))
        self.key_input = ctk.CTkEntry(self, width=300)
        self.key_input.pack(pady=5)
        
        ctk.CTkButton(self, text="Activate", command=self.submit_key).pack(pady=20)

    def submit_key(self):
        user_key = self.key_input.get()
        # Verify key against your hash logic here
        # For simplicity, we just save it; logic should be in license_manager.py
        with open("license.key", "w") as f:
            f.write(user_key)
        
        messagebox.showinfo("Success", "Key saved. Please restart the app.")
        self.destroy()
        self.master.quit() # Close the app so they restart it
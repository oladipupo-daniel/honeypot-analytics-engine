# core/task_manager.py
import threading
from tkinter import messagebox

def run_in_background(target_func, args=(), callback=None):
    """
    Generic wrapper to run any function in the background.
    target_func: The function doing the heavy work (like pd.read_csv)
    args: The arguments to pass to that function
    callback: The function to run once done (to update the UI)
    """
    def wrapper():
        try:
            result = target_func(*args)
            if callback:
                # Safely return to the main thread to update UI
                import tkinter as tk
                root = tk._get_default_root()
                root.after(0, lambda: callback(result))
        except Exception as e:
            # Handle errors globally so the app doesn't just die
            print(f"Task Failed: {e}")

    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
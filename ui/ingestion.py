# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
import customtkinter as ctk
import random

class DataIngestionScreen(ctk.CTkFrame) :
    def __init__(self, master) :
        super().__init__(
            master,
            width=600,
            height=500,
            corner_radius=24,
            fg_color="#F9F9FB",
            border_width=1,
            border_color="#E4E4E7"
        )
        self.master = master
        self.pack_propagate(False)
        
        # Simulation properties
        self.progress_value = 0.0
        self.trend_points = []
        self.current_x = 40
        self.max_x = 560
        
        # Build layout structure
        self.create_widgets()
        
    def create_widgets(self) :
        # Title Header
        self.header_lbl = ctk.CTkLabel(
            self,
            text="DATA PIPELINE INGESTION",
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color="#18181B"
        )
        self.header_lbl.pack(pady=(40, 5))
        
        self.status_lbl = ctk.CTkLabel(
            self,
            text="System idling. Awaiting source dataset upload...",
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color="#71717A"
        )
        self.status_lbl.pack(pady=(0, 20))
        
        # 1. Main Action Trigger: Simulates dropping/uploading a file
        self.upload_btn = ctk.CTkButton(
            self,
            text="Simulate Source Dataset Upload",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=44,
            width=280,
            fg_color="#18181B",
            hover_color="#27272A",
            text_color="#FFFFFF",
            corner_radius=12,
            command=self.start_whisper_ingestion
        )
        self.upload_btn.pack(pady=10)
        
        # 2. Whisper Progress Bar Frame (Hidden initially)
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=340,
            height=6,
            fg_color="#E4E4E7",
            progress_color="#22C55E" # Emerald Green Progress
        )
        self.progress_bar.set(0)
        
        # 3. Appetizing Live Trendline Canvas Area (Hidden initially)
        self.trend_canvas = ctk.CTkCanvas(
            self,
            width=600,
            height=160,
            bg="#F9F9FB",
            highlightthickness=0
        )
        
        # 4. Post-Ingestion Bottom Dashboard Menu Control Bar (Hidden initially)
        self.action_frame = ctk.CTkFrame(self, fg_color="transparent")
        
        self.deduction_btn = ctk.CTkButton(
            self.action_frame,
            text="Get Data-Driven Deduction",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            fg_color="#22C55E",
            hover_color="#16A34A",
            text_color="#FFFFFF",
            corner_radius=8
        )
        self.deduction_btn.pack(side="left", padx=10)
        
        self.think_btn = ctk.CTkButton(
            self.action_frame,
            text="Think Data",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            height=40,
            fg_color="#18181B",
            hover_color="#27272A",
            text_color="#FFFFFF",
            corner_radius=8,
            command=self.trigger_think_data_action
        )
        self.think_btn.pack(side="left", padx=10)

    def start_whisper_ingestion(self) :
        """Resets layout and smoothly increments the quiet system loading tracking pipeline."""
        self.upload_btn.pack_forget()
        self.trend_canvas.pack_forget()
        self.action_frame.pack_forget()
        
        self.status_lbl.configure(text="Whispering data streams into memory pipeline...")
        self.progress_bar.pack(pady=40)
        self.progress_value = 0.0
        self.animate_loader()

    def animate_loader(self) :
        """Increments tracking loaders smoothly."""
        if self.progress_value < 1.0 :
            self.progress_value += 0.04
            self.progress_bar.set(self.progress_value)
            self.master.after(50, self.animate_loader)
        else :
            # Loader complete! Transition instantly to live line plotting
            self.progress_bar.pack_forget()
            self.status_lbl.configure(text="Dataset ingestion approved. Analyzing trends...")
            self.setup_canvas_grid()
            self.trend_canvas.pack(pady=10)
            self.animate_live_trendline()

    def setup_canvas_grid(self) :
        """Draws the clean background baseline layout grids seen in the trend mock image."""
        self.trend_canvas.delete("all")
        self.trend_points.clear()
        self.current_x = 40
        
        # Horizontal faint baseline rules
        self.trend_canvas.create_line(40, 30, 560, 30, fill="#E4E4E7", width=1)
        self.trend_canvas.create_line(40, 80, 560, 80, fill="#E4E4E7", width=1)
        self.trend_canvas.create_line(40, 130, 560, 130, fill="#E4E4E7", width=1)
        
        # Baseline Metric Axis Text Labels
        self.trend_canvas.create_text(25, 30, text="400", fill="#A1A1AA", font=("Segoe UI", 9))
        self.trend_canvas.create_text(25, 80, text="200", fill="#A1A1AA", font=("Segoe UI", 9))
        self.trend_canvas.create_text(25, 130, text="0", fill="#A1A1AA", font=("Segoe UI", 9))

    def animate_live_trendline(self) :
        """Plots points dynamically across the screen like a live stock ticker or forex chart."""
        if self.current_x <= self.max_x :
            # Create appetizing analytics fluctuations (lower line value means higher visually on canvas)
            if 240 <= self.current_x <= 300 :
                # Simulate a massive spike peak (like the mid-month burst in your image)
                y_target = random.randint(20, 50)
            elif 380 <= self.current_x <= 440 :
                # Secondary mini wave hill
                y_target = random.randint(60, 90)
            else :
                # Stable low variance running floor line
                y_target = random.randint(110, 130)
                
            new_point = (self.current_x, y_target)
            self.trend_points.append(new_point)
            
            # Connect the nodes if we have at least 2 coordinate keys mapped out
            if len(self.trend_points) > 1 :
                self.trend_canvas.create_line(
                    self.trend_points[-2][0], self.trend_points[-2][1],
                    self.trend_points[-1][0], self.trend_points[-1][1],
                    fill="#15803D", # Deep Forest Green Trend Color Line
                    width=2,
                    smooth=True,
                    tags="trend"
                )
                
            self.current_x += 15
            # Faster update loop creates an elegant "sketching" illusion effect
            self.master.after(30, self.animate_live_trendline)
        else :
            # Once graph plotting finishes, unveil actionable dashboard paths
            self.status_lbl.configure(text="Pipeline processing verified. Select evaluation matrix:")
            self.action_frame.pack(pady=20)

    def trigger_think_data_action(self) :
        print("[System Matrix Context Log] 'Think Data' sequence selected.")
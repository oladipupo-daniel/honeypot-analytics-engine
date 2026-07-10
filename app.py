# =====================================================================
# HONEYPOT ANALYTICS — Proprietary Software
# Copyright (c) 2026 Daniel Oladipupo. All Rights Reserved.
# Unauthorized copying, modification, or redistribution of this file,
# in whole or in part, is strictly prohibited. See core/license_notice.py.
# =====================================================================
import sys
import time
from tkinter import filedialog, messagebox
import customtkinter as ctk
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

import auth_utils
from core.theme_manager import get_active_theme
from ui.gateway import IdentityGateway
from ui.onboarding import OnboardingScreen
from core.analytics_engine import process_general_reliability


# =====================================================================
# DYNAMIC TRANSLATION LAYER (COLD JARGON TO MARKET WOMAN COMMON SENSE)
# =====================================================================
def generate_market_insights(metric_name, connection_strength, accuracy_score, status_flag):
    """
    Takes real analysis results and structures them into two distinct viewpoints:
    1. A formal executive corporate briefing.
    2. A plain, practical, warm "market woman" common-sense breakdown.
    Both describe the SAME underlying numbers - just different voice/register.
    """
    strength_pct = abs(connection_strength) * 100
    accuracy_pct = accuracy_score * 100

    corporate_text = (
        f"Metric [{metric_name}] shows a directional connection strength of {connection_strength:.4f} "
        f"({strength_pct:.1f}% magnitude) against its primary driver, yielding a system accuracy "
        f"score of {accuracy_score:.4f} ({accuracy_pct:.1f}%). Current status classification: {status_flag}."
    )

    if status_flag == "OPTIMAL":
        vibe = "things dey match well well"
    elif status_flag == "STABLE":
        vibe = "e dey steady, no wahala"
    else:
        vibe = "the numbers no too gree agree"

    market_text = (
        f"For [{metric_name}], {vibe} — the connection between am and the other factor "
        f"na about {strength_pct:.0f} out of 100. Our accuracy score na {accuracy_pct:.0f} out of 100, "
        f"so e dey reasonably trustworthy based on wetin we see for the data. Status be: {status_flag}."
    )

    return {
        "corporate": corporate_text,
        "market_woman": market_text
    }


class HoneypotSplash(ctk.CTkToplevel):
    """
    A sleek intro splash curtain that displays on launch before the app reveals itself.
    Emulates the visual initialization sequence of high-tier data ecosystems.
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        theme = get_active_theme()

        width, height = 550, 320
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.configure(fg_color=theme["bg_main"])

        self.logo_label = ctk.CTkLabel(
            self, text="🍯", font=ctk.CTkFont(size=56)
        )
        self.logo_label.pack(pady=(50, 5))

        self.title_label = ctk.CTkLabel(
            self, text="Honeypot Analytics",
            font=ctk.CTkFont(family="Helvetica", size=28, weight="bold"),
            text_color=theme["text_color"]
        )
        self.title_label.pack(pady=5)

        self.version_label = ctk.CTkLabel(
            self, text="Version 1.1.0",
            font=ctk.CTkFont(family="Courier", size=13),
            text_color=theme["text_color"]
        )
        self.version_label.pack(pady=(0, 25))

        self.status_label = ctk.CTkLabel(
            self, text="Initializing localized causal analysis modules...",
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color=theme["muted_text"]
        )
        self.status_label.pack(pady=5)

        self.progress_bar = ctk.CTkProgressBar(self, width=380, progress_color=theme["honey"], fg_color=theme["bg_panel"])
        self.progress_bar.set(0.0)
        self.progress_bar.pack(pady=10)

        self.loading_step(0.0)

    def loading_step(self, val):
        if val <= 1.0:
            self.progress_bar.set(val)
            if val > 0.4:
                self.status_label.configure(text="Securing memory parameters & template matrix keys...")
            if val > 0.8:
                self.status_label.configure(text="Ready.")
            self.after(20, lambda: self.loading_step(val + 0.05))
        else:
            self.destroy()


class HoneypotApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.withdraw()

        self.title("HONEYPOT Analytics v1.1.0 - Sovereign Engine by Daniel Oladpupo (CIPM, CISSP, AIGP)")
        self.geometry("1100x680")
        self.resizable(True, True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # GLOBAL STATE DATA CONTEXTS
        self.current_role = None
        self.current_screen = None
        self.active_file_name = "No File Analyzed"
        self.active_dataframe = None   # populated by DataIngestionScreen once a real file is loaded
        self.active_metric_col = None  # populated by DataIngestionScreen once a metric is chosen

        self.protocol("WM_DELETE_WINDOW", self.terminate_session)

        self.run_splash()

    def run_splash(self):
        splash = HoneypotSplash(self)

        def monitor_splash():
            if splash.winfo_exists():
                self.after(100, monitor_splash)
            else:
                self.deiconify()
                # First launch on this PC -> let the user register their own
                # credentials. Otherwise -> straight to sign in.
                if auth_utils.vault_exists():
                    self.switch_screen(IdentityGateway)
                else:
                    self.switch_screen(OnboardingScreen)

        self.after(100, monitor_splash)

    def switch_screen(self, screen_class, *args, **kwargs):
        if self.current_screen is not None:
            self.current_screen.destroy()

        self.current_screen = screen_class(self, *args, **kwargs)
        self.current_screen.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def apply_theme(self):
        """Re-applies the currently saved skin's light/dark appearance mode
        and rebuilds whatever screen is currently showing so the new colors
        take effect immediately."""
        theme = get_active_theme()
        ctk.set_appearance_mode(theme["appearance"])
        if self.current_screen is not None:
            self.switch_screen(type(self.current_screen), *getattr(self.current_screen, "_init_args", ()))

    def export_to_pdf(self):
        """Generates a real data summary brief from whatever dataset is currently loaded."""
        if self.active_dataframe is None or self.active_metric_col is None:
            messagebox.showwarning(
                "No Data Loaded",
                "Upload and analyze a dataset before exporting a report."
            )
            return

        results = process_general_reliability(
            self.active_dataframe,
            entity_col="Platform",
            metric_col=self.active_metric_col
        )

        if results is None:
            messagebox.showerror(
                "Analysis Error",
                "Could not generate analysis from the currently loaded dataset."
            )
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF Documents", "*.pdf")],
            title="Export Analytics Brief"
        )

        if not file_path:
            return

        try:
            doc = SimpleDocTemplate(
                file_path, pagesize=letter,
                rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
            )
            story = []
            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'DocTitle', parent=styles['Heading1'], fontSize=22, leading=26,
                textColor=colors.HexColor("#1E3A8A"), spaceAfter=4
            )

            meta_style = ParagraphStyle(
                'DocMeta', parent=styles['Normal'], fontSize=9,
                textColor=colors.HexColor("#4B5563"), spaceAfter=15
            )

            section_heading = ParagraphStyle(
                'SectionHead', parent=styles['Heading2'], fontSize=12, leading=16,
                textColor=colors.HexColor("#1A365D"), spaceBefore=12, spaceAfter=6
            )

            body_style = ParagraphStyle(
                'TableBody', parent=styles['Normal'], fontSize=9, leading=12
            )

            market_vibe_style = ParagraphStyle(
                'MarketVibe', parent=styles['Normal'], fontSize=9, leading=13,
                textColor=colors.HexColor("#2B6CB0"), fontName="Helvetica-Oblique"
            )

            story.append(Paragraph("Honeypot Analytics Brief", title_style))
            story.append(Paragraph(f"Active Analysis Target Context: {self.active_file_name}", meta_style))
            story.append(Paragraph(
                "Generated locally. Security practices: hashed credential check, no plaintext "
                "password storage, no external data transmission.",
                meta_style
            ))
            story.append(Spacer(1, 10))

            is_single_record_report = results.get("mode") == "single_record_variance"

            # 1. CORE PARAMETERS TABLE
            if is_single_record_report:
                # Only one row was ingested - correlation is undefined, so the
                # summary reports the variance-based descriptive statistics
                # across that record's numeric fields instead.
                story.append(Paragraph("Single-Record Variance Summary", section_heading))
                data_summary = [
                    ["Metric Parameter", "Current Value", "Status Evaluation"],
                    ["Analyzed Metric", results["actual_target"].title(), "Target Column"],
                    ["Fields Compared", str(len(results.get("numeric_columns", []))), "Numeric Columns on Record"],
                    ["Mean Across Fields", f"{results['mean']:.4f}", "Central Tendency"],
                    ["Median Across Fields", f"{results['median']:.4f}", "Central Tendency"],
                    ["Variance", f"{results['variance']:.4f}", "Spread"],
                    ["Standard Deviation", f"{results['std_dev']:.4f}", "Spread"],
                    ["Coefficient of Variation", f"{results['coefficient_of_variation']*100:.1f}%", "Relative Spread"],
                    ["Rows Evaluated", str(len(self.active_dataframe)), "Dataset Size (single record)"],
                ]
            else:
                # 1. CORE PARAMETERS TABLE - real values from process_general_reliability
                story.append(Paragraph("Operational Metrics Summary", section_heading))
                data_summary = [
                    ["Metric Parameter", "Current Value", "Status Evaluation"],
                    ["Analyzed Metric", results["actual_target"].title(), "Target Column"],
                    ["Compared Against", results["primary_driver"].title(), "Primary Driver"],
                    ["Connection Strength", f"{results['connection_strength']:.4f}", "Pearson Correlation"],
                    ["Fluke Chance (p-value)", f"{results['fluke_chance']:.4e}", "Statistical Significance"],
                    ["System Accuracy Score", f"{results['accuracy_score']:.4f}", "1 - |correlation|"],
                    ["Rows Evaluated", str(len(self.active_dataframe)), "Dataset Size"],
                ]

            summary_table = Table(data_summary, colWidths=[180, 170, 170])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('VALIGN', (0,0), (-1,-1), 'LEFT'),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0,0), (-1,0), 6),
                ('BACKGROUND', (1,1), (-1,-1), colors.HexColor("#F9FAFB")),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,0), (-1,-1), 9),
                ('TOPPADDING', (0,0), (-1,-1), 6),
                ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 15))

            # 2. DYNAMIC TRANSLATION SPLIT ANALYSIS BLOCK - real numbers, two voices
            story.append(Paragraph("Data Interpretation Framework", section_heading))

            status_flag = results.get("status_flag") or (
                "OPTIMAL" if abs(results["connection_strength"]) > 0.8
                else "STABLE" if abs(results["connection_strength"]) > 0.4
                else "VOLATILE"
            )

            insights = generate_market_insights(
                results["actual_target"],
                results["connection_strength"],
                results["accuracy_score"],
                status_flag
            )

            interpretation_data = [
                [
                    Paragraph("<b>COLD CORPORATE BRIEFING</b>", body_style),
                    Paragraph("<b>MARKET WOMAN TRANSLATION</b>", body_style)
                ],
                [
                    Paragraph(insights["corporate"], body_style),
                    Paragraph(insights["market_woman"], market_vibe_style)
                ]
            ]

            interp_table = Table(interpretation_data, colWidths=[260, 260])
            interp_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E5E7EB")),
                ('ALIGN', (0,0), (-1,-1), 'TOP'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
                ('TOPPADDING', (0,0), (-1,-1), 10),
                ('BOTTOMPADDING', (0,0), (-1,-1), 10),
                ('LEFTPADDING', (0,0), (-1,-1), 10),
                ('RIGHTPADDING', (0,0), (-1,-1), 10),
                ('BACKGROUND', (1,1), (1,1), colors.HexColor("#F0F4F8")),
            ]))

            story.append(interp_table)

            # 3. CLASSROOM / PERFORMANCE DIAGNOSTIC - Top/Bottom performers,
            # Performance Gap, Benchmarking, Pass/Fail, Class Variance,
            # Difficulty Analysis - only meaningful for multi-row datasets.
            classroom_diagnostics = results.get("classroom_diagnostics")
            if classroom_diagnostics:
                cd = classroom_diagnostics
                story.append(Spacer(1, 15))
                story.append(Paragraph("Classroom / Performance Diagnostic", section_heading))
                story.append(Paragraph(
                    "Every figure below compares each row against the group's own mean and standard "
                    "deviation - not a fitted trend - so ordinary spread is never mistaken for a false pattern.",
                    meta_style
                ))

                diagnostic_summary = [
                    ["Diagnostic", "Result", "Detail"],
                    ["Performance Gap", f"{cd['performance_gap']:.2f}",
                     f"Highest {cd['highest_value']:.2f} vs Lowest {cd['lowest_value']:.2f}"],
                    ["Pass/Fail Distribution", f"{cd['pass_rate']:.1f}% pass",
                     f"{cd['pass_count']} pass / {cd['fail_count']} fail (threshold {cd['pass_threshold']:.2f})"],
                    ["Class Variance", f"{cd['class_variance']:.4f}",
                     f"Std Dev {cd['class_std_dev']:.4f}, Mean {cd['class_mean']:.2f}"],
                ]
                if cd.get("hardest_column") and cd.get("easiest_column"):
                    diagnostic_summary.append([
                        "Difficulty Analysis",
                        cd["hardest_column"]["column"].title(),
                        f"Toughest area (avg {cd['hardest_column']['mean']:.2f}); "
                        f"easiest is {cd['easiest_column']['column'].title()} (avg {cd['easiest_column']['mean']:.2f})"
                    ])

                diagnostic_table = Table(diagnostic_summary, colWidths=[150, 130, 240])
                diagnostic_table.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                    ('FONTSIZE', (0,0), (-1,-1), 8.5),
                    ('TOPPADDING', (0,0), (-1,-1), 6),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 6),
                    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F9FAFB")),
                ]))
                story.append(diagnostic_table)
                story.append(Spacer(1, 12))

                # Top/Bottom performers table with CONDITIONAL FORMATTING:
                # green rows = top performers, red rows = bottom performers
                # (an if/else on each row's position, exactly as requested).
                story.append(Paragraph("Top & Bottom Performers (Z-Score Benchmarking)", section_heading))
                perf_rows = [["Rank", "Entity", "Value", "Status"]]
                row_styles = []
                for i, row in enumerate(cd["top_performers"], start=1):
                    perf_rows.append([str(i), str(row["entity"]), f"{row['value']:.2f}", "TOP PERFORMER"])
                for i, row in enumerate(cd["bottom_performers"], start=1):
                    perf_rows.append([f"-{i}", str(row["entity"]), f"{row['value']:.2f}", "NEEDS ATTENTION"])

                perf_table = Table(perf_rows, colWidths=[50, 180, 90, 200])
                base_style = [
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
                    ('FONTSIZE', (0,0), (-1,-1), 8.5),
                    ('TOPPADDING', (0,0), (-1,-1), 5),
                    ('BOTTOMPADDING', (0,0), (-1,-1), 5),
                ]
                n_top = len(cd["top_performers"])
                for idx in range(1, len(perf_rows)):
                    # if/else conditional formatting: top rows -> green tint, bottom rows -> red tint
                    if idx <= n_top:
                        base_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor("#DCFCE7")))
                        base_style.append(('TEXTCOLOR', (3, idx), (3, idx), colors.HexColor("#15803D")))
                    else:
                        base_style.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor("#FEE2E2")))
                        base_style.append(('TEXTCOLOR', (3, idx), (3, idx), colors.HexColor("#B91C1C")))
                perf_table.setStyle(TableStyle(base_style))
                story.append(perf_table)

            doc.build(story)
            messagebox.showinfo("Success", f"Analytics brief saved successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to generate PDF report:\n{str(e)}")

    def get_decision_narrative(self, metric_name, current_val, forecast_val, avg_val):
        trend = "encouraging" if forecast_val > current_val else "cautious"
        comparison = "above" if current_val > avg_val else "below"

        return (f"The {metric_name} score of {current_val:.2f} is {trend} "
                f"(forecast is {forecast_val:.2f}). It is currently {comparison} "
                f"the dataset average of {avg_val:.2f}, indicating a {trend} outlook.")

    def terminate_session(self):
        try:
            self.destroy()
        except Exception:
            pass
        finally:
            sys.exit(0)


if __name__ == "__main__":
    # Appearance mode follows whichever skin was last chosen on this PC
    # (defaults to Midnight Sovereign / dark on first-ever launch).
    _startup_theme = get_active_theme()
    ctk.set_appearance_mode(_startup_theme["appearance"])
    ctk.set_default_color_theme("blue")

    app = HoneypotApp()
    app.mainloop()

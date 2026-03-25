import customtkinter as ctk
from tkinter import messagebox
import math
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from PIL import Image, ImageDraw, ImageFont

ctk.set_appearance_mode("dark")

class SolarApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🌞 Solar Power Calculator - Engineer Ahmed")
        self.root.geometry("960x800")
        self.root.resizable(True, True)

        # Header
        header = ctk.CTkFrame(self.root, fg_color="#1a1a1a", height=150)
        header.pack(fill="x", pady=10)

        ctk.CTkLabel(header, text="⚡ SOLAR POWER CALCULATOR", 
                     font=ctk.CTkFont(size=38, weight="bold"), text_color="#ff3333").pack(pady=10)
        ctk.CTkLabel(header, text="Engineer Ahmed", 
                     font=ctk.CTkFont(size=24, weight="bold"), text_color="white").pack()
        ctk.CTkLabel(header, text="Off-Grid & Hybrid Solar System Designer", 
                     font=ctk.CTkFont(size=15), text_color="#aaaaaa").pack(pady=5)

        main = ctk.CTkFrame(self.root, fg_color="#121212")
        main.pack(fill="both", expand=True, padx=25, pady=15)

        # Inputs
        left = ctk.CTkFrame(main, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=20)

        ctk.CTkLabel(left, text="Daily Consumption (Wh/day):", text_color="#ffdddd").pack(anchor="w")
        self.daily = ctk.CTkEntry(left, placeholder_text="6500", height=40)
        self.daily.pack(fill="x", pady=8)

        ctk.CTkLabel(left, text="Peak Sun Hours (PSH):", text_color="#ffdddd").pack(anchor="w")
        self.psh = ctk.CTkEntry(left, placeholder_text="5.3", height=40)
        self.psh.pack(fill="x", pady=8)

        ctk.CTkLabel(left, text="Peak Load (Watts):", text_color="#ffdddd").pack(anchor="w")
        self.peak = ctk.CTkEntry(left, placeholder_text="4200", height=40)
        self.peak.pack(fill="x", pady=8)

        right = ctk.CTkFrame(main, fg_color="transparent")
        right.pack(side="right", fill="both", expand=True, padx=20)

        ctk.CTkLabel(right, text="System Type:", text_color="#ffdddd").pack(anchor="w")
        self.type_combo = ctk.CTkComboBox(right, values=["Hybrid", "Off-Grid"], height=40)
        self.type_combo.pack(fill="x", pady=8)

        ctk.CTkLabel(right, text="Panel Wattage (Wp):", text_color="#ffdddd").pack(anchor="w")
        self.panel = ctk.CTkEntry(right, placeholder_text="550", height=40)
        self.panel.pack(fill="x", pady=8)

        ctk.CTkLabel(right, text="Panel Isc (A):", text_color="#ffdddd").pack(anchor="w")
        self.isc = ctk.CTkEntry(right, placeholder_text="13.5", height=40)
        self.isc.pack(fill="x", pady=8)

        # Buttons
        btn_frame = ctk.CTkFrame(main, fg_color="transparent")
        btn_frame.pack(pady=25)

        calc_btn = ctk.CTkButton(btn_frame, text="🚀 Calculate", width=220, height=50,
                                 font=ctk.CTkFont(size=18, weight="bold"),
                                 fg_color="#ff3333", hover_color="#cc0000",
                                 command=self.calculate)
        calc_btn.pack(side="left", padx=15)

        self.save_btn = ctk.CTkButton(btn_frame, text="💾 Save as PDF", width=220, height=50,
                                      font=ctk.CTkFont(size=18, weight="bold"),
                                      fg_color="#00aa00", hover_color="#008800",
                                      state="disabled", command=self.save_pdf)
        self.save_btn.pack(side="left", padx=15)

        # Result
        self.result = ctk.CTkTextbox(main, height=320, font=ctk.CTkFont(size=15))
        self.result.pack(fill="both", expand=True, padx=20, pady=10)

        self.calc_data = ""

    def calculate(self):
        try:
            daily = float(self.daily.get())
            psh = float(self.psh.get())
            peak = float(self.peak.get())
            panel = float(self.panel.get())
            isc = float(self.isc.get())
            sys_type = self.type_combo.get()

            pv_power = (daily * 1.25) / (psh * 0.78)
            num_panels = math.ceil(pv_power / panel)
            inverter = peak * 1.3

            if sys_type == "Off-Grid":
                battery = (daily * 3) / (48 * 0.85 * 0.92 * 0.9)
                bat_text = f"Battery: {battery:.0f} Ah (3 days autonomy)"
            else:
                battery = (daily * 0.25) / (48 * 0.85 * 0.92 * 0.9)
                bat_text = f"Battery: {battery:.0f} Ah (Hybrid backup)"

            controller = isc * num_panels * 1.3

            self.calc_data = f"""System Type          : {sys_type}
Daily Consumption    : {daily/1000:.2f} kWh
PV Array             : {pv_power:.0f} Wp → {num_panels} panels
Inverter             : {inverter:.0f} W
{bat_text}
Charge Controller    : {controller:.1f} A
Safety Factor        : 25%"""

            self.result.delete("1.0", "end")
            self.result.insert("1.0", f"✅ Calculation Completed Successfully!\n\n{self.calc_data}")
            self.save_btn.configure(state="normal")

        except ValueError:
            messagebox.showerror("خطأ", "يرجى إدخال أرقام صحيحة في جميع الحقول")

    def save_pdf(self):
        if not self.calc_data:
            return

        if not messagebox.askyesno("تأكيد", "هل تريد حفظ التقرير كملف PDF؟"):
            return

        try:
            filename = "Solar_Report_Engineer_Ahmed.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)

            logo_path = "logo_temp.png"
            self.make_logo(logo_path)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', fontSize=26, textColor=colors.red, alignment=1)
            normal = ParagraphStyle('Normal', fontSize=14, leading=20)

            story = []
            story.append(RLImage(logo_path, width=140*mm, height=45*mm))
            story.append(Spacer(1, 25*mm))
            story.append(Paragraph("Solar Power System Design Report", title_style))
            story.append(Paragraph("Engineer Ahmed", ParagraphStyle('Eng', fontSize=18, alignment=1)))
            story.append(Spacer(1, 25*mm))

            for line in self.calc_data.split('\n'):
                if line.strip():
                    story.append(Paragraph(line, normal))

            doc.build(story)
            os.remove(logo_path)

            messagebox.showinfo("نجح", f"تم حفظ التقرير بنجاح!\nالملف: {filename}")

        except Exception as e:
            messagebox.showerror("خطأ", f"فشل في حفظ الملف:\n{str(e)}")

    def make_logo(self, path):
        img = Image.new("RGB", (900, 250), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0,0),(900,250)], outline="#ff3333", width=15)
        try:
            big = ImageFont.truetype("arial.ttf", 85)
            small = ImageFont.truetype("arial.ttf", 48)
        except:
            big = ImageFont.load_default()
            small = ImageFont.load_default()
        draw.text((70, 50), "⚡ SOLAR", fill="#ff3333", font=big)
        draw.text((460, 70), "POWER", fill="#ffffff", font=big)
        draw.text((280, 155), "Engineer Ahmed", fill="#ffdddd", font=small)
        img.save(path, "PNG")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = SolarApp()
    app.run()

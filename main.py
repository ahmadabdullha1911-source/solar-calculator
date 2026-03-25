import os
os.environ["KIVY_GL_BACKEND"] = "angle_sdl2"

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.spinner import MDSpinner
from kivy.uix.scrollview import ScrollView
from kivymd.uix.dialog import MDDialog
import math
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from PIL import Image, ImageDraw, ImageFont

class SolarCalculatorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calculation_data = ""

        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)

        header = MDBoxLayout(orientation='vertical', size_hint_y=None, height=180, md_bg_color=[0.1, 0.1, 0.1, 1])
        title = MDLabel(text="⚡ SOLAR POWER CALCULATOR", halign="center", font_style="H4", text_color=[1, 0.2, 0.2, 1])
        engineer = MDLabel(text="Engineer Ahmed", halign="center", font_style="H5", text_color=[1, 1, 1, 1])
        subtitle = MDLabel(text="Off-Grid & Hybrid Solar System Designer", halign="center", font_style="Subtitle1", theme_text_color="Secondary")
        header.add_widget(title)
        header.add_widget(engineer)
        header.add_widget(subtitle)
        layout.add_widget(header)

        scroll = ScrollView()
        inputs = MDGridLayout(cols=1, spacing=15, padding=10, adaptive_height=True)

        self.daily = MDTextField(hint_text="Daily Consumption (Wh/day)", helper_text="مثال: 6500")
        self.psh = MDTextField(hint_text="Peak Sun Hours (PSH)", helper_text="مثال: 5.3")
        self.peak = MDTextField(hint_text="Peak Load (Watts)", helper_text="مثال: 4200")
        self.panel = MDTextField(hint_text="Panel Wattage (Wp)", helper_text="550")
        self.isc = MDTextField(hint_text="Panel Isc (A)", helper_text="13.5")

        self.sys_type = MDSpinner(text="Hybrid", values=["Hybrid", "Off-Grid"], size_hint_y=None, height=50)

        inputs.add_widget(self.daily)
        inputs.add_widget(self.psh)
        inputs.add_widget(self.peak)
        inputs.add_widget(self.panel)
        inputs.add_widget(self.isc)
        inputs.add_widget(MDLabel(text="System Type:"))
        inputs.add_widget(self.sys_type)

        scroll.add_widget(inputs)
        layout.add_widget(scroll)

        btn_layout = MDBoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=60)
        calc_btn = MDRaisedButton(text="🚀 Calculate", md_bg_color=[1, 0.2, 0.2, 1], on_release=self.calculate)
        save_btn = MDRaisedButton(text="💾 Save as PDF", md_bg_color=[0, 0.7, 0, 1], on_release=self.save_pdf)
        btn_layout.add_widget(calc_btn)
        btn_layout.add_widget(save_btn)
        layout.add_widget(btn_layout)

        self.result_label = MDLabel(text="Result will appear here...", halign="left", text_color=[0.9, 0.9, 0.9, 1], height=320)
        layout.add_widget(self.result_label)

        self.add_widget(layout)

    def calculate(self, instance):
        try:
            daily = float(self.daily.text or 0)
            psh = float(self.psh.text or 0)
            peak = float(self.peak.text or 0)
            panel_wp = float(self.panel.text or 550)
            isc_a = float(self.isc.text or 13)
            sys_type = self.sys_type.text

            pv = (daily * 1.25) / (psh * 0.78)
            num_panels = math.ceil(pv / panel_wp)
            inverter = peak * 1.3

            if sys_type == "Off-Grid":
                bat = (daily * 3) / (48 * 0.85 * 0.92 * 0.9)
                bat_str = f"Battery: {bat:.0f} Ah (3 days autonomy)"
            else:
                bat = (daily * 0.25) / (48 * 0.85 * 0.92 * 0.9)
                bat_str = f"Battery: {bat:.0f} Ah (Hybrid backup)"

            controller = isc_a * num_panels * 1.3

            self.calculation_data = f"""System Type: {sys_type}
Daily Consumption: {daily/1000:.2f} kWh
PV Array: {pv:.0f} Wp → {num_panels} panels
Inverter: {inverter:.0f} W
{bat_str}
Charge Controller: {controller:.1f} A
Safety Factor: 25%"""

            self.result_label.text = f"✅ Calculation Done!\n\n{self.calculation_data}"
        except:
            self.result_label.text = "❌ Please enter valid numbers!"

    def save_pdf(self, instance):
        if not self.calculation_data:
            self.show_dialog("Warning", "Please calculate first!")
            return
        def confirm(*args):
            self.generate_pdf()
        self.show_dialog("Confirm Save", "Save the report as PDF with logo?", confirm)

    def show_dialog(self, title, text, callback=None):
        dialog = MDDialog(title=title, text=text, buttons=[
            MDRaisedButton(text="Cancel"),
            MDRaisedButton(text="Yes", on_release=lambda x: (dialog.dismiss(), callback() if callback else None))
        ])
        dialog.open()

    def generate_pdf(self):
        try:
            filename = "Solar_Report_Engineer_Ahmed.pdf"
            doc = SimpleDocTemplate(filename, pagesize=A4)
            logo_path = "logo_temp.png"
            self.create_logo_image(logo_path)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', fontSize=24, textColor=colors.red, alignment=1)
            normal = ParagraphStyle('Normal', fontSize=14, leading=18)
            story = []
            story.append(RLImage(logo_path, width=140*mm, height=45*mm))
            story.append(Spacer(1, 20*mm))
            story.append(Paragraph("Solar Power System Design Report", title_style))
            story.append(Paragraph("Engineer Ahmed", ParagraphStyle('Eng', fontSize=18, alignment=1)))
            story.append(Spacer(1, 20*mm))
            for line in self.calculation_data.split('\n'):
                if line.strip():
                    story.append(Paragraph(line, normal))
            doc.build(story)
            if os.path.exists(logo_path):
                os.remove(logo_path)
            self.show_dialog("Success", f"PDF saved!\n{filename}")
        except Exception as e:
            self.show_dialog("Error", f"Failed to save PDF:\n{str(e)}")

    def create_logo_image(self, path):
        img = Image.new("RGB", (900, 250), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0,0),(900,250)], outline="#ff3333", width=15)
        try:
            font_big = ImageFont.truetype("arial.ttf", 80)
            font_small = ImageFont.truetype("arial.ttf", 45)
        except:
            font_big = ImageFont.load_default()
            font_small = ImageFont.load_default()
        draw.text((70, 50), "⚡ SOLAR", fill="#ff3333", font=font_big)
        draw.text((460, 65), "POWER", fill="#ffffff", font=font_big)
        draw.text((280, 160), "Engineer Ahmed", fill="#ffdddd", font=font_small)
        img.save(path, "PNG")


class SolarApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        return SolarCalculatorScreen()

if __name__ == '__main__':
    SolarApp().run()

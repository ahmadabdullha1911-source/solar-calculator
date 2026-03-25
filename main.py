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

class SolarScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calc_data = ""

        layout = MDBoxLayout(orientation='vertical', padding=20, spacing=15)

        # Header
        header = MDBoxLayout(orientation='vertical', size_hint_y=None, height=170, md_bg_color=[0.1, 0.1, 0.1, 1])
        header.add_widget(MDLabel(text="⚡ SOLAR POWER CALCULATOR", halign="center", font_style="H4", text_color=[1, 0.2, 0.2, 1]))
        header.add_widget(MDLabel(text="Engineer Ahmed", halign="center", font_style="H5", text_color=[1,1,1,1]))
        header.add_widget(MDLabel(text="Off-Grid & Hybrid Solar Designer", halign="center", font_style="Subtitle1", theme_text_color="Secondary"))
        layout.add_widget(header)

        # Inputs
        scroll = ScrollView()
        inputs = MDGridLayout(cols=1, spacing=15, padding=10, adaptive_height=True)

        self.daily = MDTextField(hint_text="Daily Consumption (Wh/day)", helper_text="مثال: 6500")
        self.psh = MDTextField(hint_text="Peak Sun Hours (PSH)", helper_text="مثال: 5.3")
        self.peak = MDTextField(hint_text="Peak Load (Watts)", helper_text="مثال: 4200")
        self.panel = MDTextField(hint_text="Panel Wattage (Wp)", helper_text="550")
        self.isc = MDTextField(hint_text="Panel Isc (A)", helper_text="13.5")

        self.sys_type = MDSpinner(text="Hybrid", values=["Hybrid", "Off-Grid"], size_hint_y=None, height=50)

        for w in [self.daily, self.psh, self.peak, self.panel, self.isc]:
            inputs.add_widget(w)
        inputs.add_widget(MDLabel(text="System Type:"))
        inputs.add_widget(self.sys_type)

        scroll.add_widget(inputs)
        layout.add_widget(scroll)

        # Buttons
        btn_box = MDBoxLayout(orientation='horizontal', spacing=20, size_hint_y=None, height=60)
        btn_box.add_widget(MDRaisedButton(text="🚀 Calculate", md_bg_color=[1,0.2,0.2,1], on_release=self.calculate))
        btn_box.add_widget(MDRaisedButton(text="💾 Save PDF", md_bg_color=[0,0.7,0,1], on_release=self.save_pdf))
        layout.add_widget(btn_box)

        self.result = MDLabel(text="النتيجة ستظهر هنا...", halign="left", text_color=[0.9,0.9,0.9,1], height=300)
        layout.add_widget(self.result)

        self.add_widget(layout)

    def calculate(self, instance):
        try:
            d = float(self.daily.text or 0)
            p = float(self.psh.text or 0)
            pk = float(self.peak.text or 0)
            pnl = float(self.panel.text or 550)
            i = float(self.isc.text or 13)
            typ = self.sys_type.text

            pv = (d * 1.25) / (p * 0.78)
            panels = math.ceil(pv / pnl)
            inv = pk * 1.3

            if typ == "Off-Grid":
                bat = (d * 3) / (48 * 0.85 * 0.92 * 0.9)
                bat_str = f"Battery: {bat:.0f} Ah (3 أيام استقلالية)"
            else:
                bat = (d * 0.25) / (48 * 0.85 * 0.92 * 0.9)
                bat_str = f"Battery: {bat:.0f} Ah (احتياطي)"

            ctrl = i * panels * 1.3

            self.calc_data = f"""نوع النظام: {typ}
الاستهلاك اليومي: {d/1000:.2f} كيلووات ساعة
الألواح: {pv:.0f} واط → {panels} لوح
العاكس: {inv:.0f} واط
{bat_str}
منظم الشحن: {ctrl:.1f} أمبير"""

            self.result.text = f"✅ تم الحساب بنجاح!\n\n{self.calc_data}"
        except:
            self.result.text = "❌ يرجى إدخال أرقام صحيحة"

    def save_pdf(self, instance):
        if not self.calc_data:
            self.show_dialog("تحذير", "احسب أولاً!")
            return
        def confirm(*args):
            self.generate_pdf()
        self.show_dialog("تأكيد", "حفظ التقرير كـ PDF مع اللوغو؟", confirm)

    def show_dialog(self, title, text, callback=None):
        dialog = MDDialog(title=title, text=text, buttons=[
            MDRaisedButton(text="إلغاء"),
            MDRaisedButton(text="نعم", on_release=lambda x: (dialog.dismiss(), callback() if callback else None))
        ])
        dialog.open()

    def generate_pdf(self):
        try:
            doc = SimpleDocTemplate("Solar_Report_Engineer_Ahmed.pdf", pagesize=A4)
            logo_path = "logo.png"
            self.create_logo(logo_path)

            styles = getSampleStyleSheet()
            title_style = ParagraphStyle('Title', fontSize=24, textColor=colors.red, alignment=1)
            normal = ParagraphStyle('Normal', fontSize=14, leading=18)

            story = [RLImage(logo_path, width=140*mm, height=45*mm), Spacer(1,20*mm)]
            story.append(Paragraph("تقرير منظومة الطاقة الشمسية", title_style))
            story.append(Paragraph("المهندس أحمد", ParagraphStyle('Eng', fontSize=18, alignment=1)))
            story.append(Spacer(1,20*mm))

            for line in self.calc_data.split('\n'):
                if line.strip():
                    story.append(Paragraph(line, normal))

            doc.build(story)
            os.remove(logo_path)
            self.show_dialog("نجح", "تم حفظ الملف باسم Solar_Report_Engineer_Ahmed.pdf")
        except Exception as e:
            self.show_dialog("خطأ", str(e))

    def create_logo(self, path):
        img = Image.new("RGB", (900, 250), "#1a1a1a")
        draw = ImageDraw.Draw(img)
        draw.rectangle([(0,0),(900,250)], outline="#ff3333", width=15)
        try:
            big = ImageFont.truetype("arial.ttf", 80)
            small = ImageFont.truetype("arial.ttf", 45)
        except:
            big = ImageFont.load_default()
            small = ImageFont.load_default()
        draw.text((70, 50), "⚡ SOLAR", fill="#ff3333", font=big)
        draw.text((460, 65), "POWER", fill="#ffffff", font=big)
        draw.text((280, 160), "Engineer Ahmed", fill="#ffdddd", font=small)
        img.save(path, "PNG")


class SolarApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        return SolarScreen()

SolarApp().run()

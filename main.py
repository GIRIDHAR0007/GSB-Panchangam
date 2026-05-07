from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.calendar import Calendar
from datetime import date, timedelta
import panchangam

class PanchangamApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.title_label = Label(text="GSB Panchang", font_size=32, size_hint_y=None, height=50)
        self.layout.add_widget(self.title_label)
        
        self.date_input = TextInput(text=date.today().isoformat(), multiline=False, size_hint_y=None, height=40)
        self.layout.add_widget(self.date_input)
        
        self.select_date_button = Button(text="Select Date", size_hint_y=None, height=40)
        self.select_date_button.bind(on_press=self.show_date_picker)
        self.layout.add_widget(self.select_date_button)
        
        self.prev_button = Button(text="Previous Day", size_hint_y=None, height=40)
        self.prev_button.bind(on_press=lambda x: self.change_day(-1))
        self.next_button = Button(text="Next Day", size_hint_y=None, height=40)
        self.next_button.bind(on_press=lambda x: self.change_day(1))
        
        button_layout = BoxLayout(size_hint_y=None, height=40)
        button_layout.add_widget(self.prev_button)
        button_layout.add_widget(self.next_button)
        self.layout.add_widget(button_layout)
        
        self.info_label = Label(text="", size_hint_y=None, height=400, halign='left', valign='top')
        self.info_label.bind(size=self.info_label.setter('text_size'))
        self.layout.add_widget(self.info_label)
        
        self.update_panchangam(date.today())
        
        return self.layout
    
    def show_date_picker(self, instance):
        self.cal = Calendar()
        self.cal.bind(on_touch_down=self.select_date)
        self.popup = Popup(title="Select Date", content=self.cal, size_hint=(0.8, 0.8))
        self.popup.open()
    
    def select_date(self, instance, touch):
        if self.cal.collide_point(*touch.pos):
            selected_date = date.fromordinal(self.cal.active_date)
            self.date_input.text = selected_date.isoformat()
            self.update_panchangam(selected_date)
            self.popup.dismiss()
    
    def change_day(self, delta):
        current = date.fromisoformat(self.date_input.text)
        new_date = current + timedelta(days=delta)
        self.date_input.text = new_date.isoformat()
        self.update_panchangam(new_date)
    
    def update_panchangam(self, selected_date):
        values = panchangam.get_panchangam_for_date(selected_date)
        info = f"Date: {values['date']} ({values['day']})\n"
        info += f"Sunrise: {values['sunrise']}\n"
        info += f"Sunset: {values['sunset']}\n"
        info += f"Moonrise: {values['moonrise']}\n"
        info += f"Moonset: {values['moonset']}\n"
        info += f"Rahu Kaal: {values['rahu_kaal']}\n"
        info += f"Tithi: {values['tithi']}\n{values['tithi_ml']}\n"
        info += f"Nakshatra: {values['nakshatra']}\n{values['nakshatra_ml']}\n"
        info += f"Ritu: {values['ritu']}\n{values['ritu_ml']}\n"
        info += f"Masu/month: {values['masu']}\n{values['masu_ml']}\n"
        info += f"Ayana: {values['ayana']}\n{values['ayana_ml']}\n"
        info += f"Lunar Month: {values['lunar_month']}\n{values['lunar_month_ml']}\n"
        info += f"Samvatsara: {values['samvatsara']}\n{values['samvatsara_ml']}\n"
        self.info_label.text = info

if __name__ == '__main__':
    PanchangamApp().run()

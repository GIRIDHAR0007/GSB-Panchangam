import flet as ft
import panchangam
from datetime import date, timedelta

def main(page: ft.Page):
    page.title = "GSB Panchang"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.LIGHT
    page.padding = 30

    title = ft.Text("GSB Panchang", size=32, weight="bold", color="orange")
    selected_date_text = ft.Text("", size=18, weight="bold")
    sunrise_text = ft.Text("", size=16)
    sunset_text = ft.Text("", size=16)
    moonrise_text = ft.Text("", size=16)
    moonset_text = ft.Text("", size=16)
    rahu_text = ft.Text("", size=16)
    tithi_text = ft.Text("", size=16)
    nakshatra_text = ft.Text("", size=16)
    ritu_text = ft.Text("", size=16)
    masu_text = ft.Text("", size=16)
    ayana_text = ft.Text("", size=16)
    lunar_month_text = ft.Text("", size=16)
    samvatsara_text = ft.Text("", size=16)

    def update_panchangam(selected_date):
        if not selected_date:
            return
        values = panchangam.get_panchangam_for_date(selected_date)
        selected_date_text.value = f"Date: {values['date']} ({values['day']})"
        sunrise_text.value = f"Sunrise: {values['sunrise']}"
        sunset_text.value = f"Sunset: {values['sunset']}"
        moonrise_text.value = f"Moonrise: {values['moonrise']}"
        moonset_text.value = f"Moonset: {values['moonset']}"
        rahu_text.value = f"Rahu Kaal: {values['rahu_kaal']}"
        tithi_text.value = f"Tithi: {values['tithi']}\n{values['tithi_ml']}"
        nakshatra_text.value = f"Nakshatra: {values['nakshatra']}\n{values['nakshatra_ml']}"
        ritu_text.value = f"Ritu: {values['ritu']}\n{values['ritu_ml']}"
        masu_text.value = f"Masu/month: {values['masu']}\n{values['masu_ml']}"
        ayana_text.value = f"Ayana: {values['ayana']}\n{values['ayana_ml']}"
        lunar_month_text.value = f"Lunar Month: {values['lunar_month']}\n{values['lunar_month_ml']}"
        samvatsara_text.value = f"Samvatsara: {values['samvatsara']}\n{values['samvatsara_ml']}"
        page.update()

    def on_date_change(e):
        update_panchangam(date_picker.value)

    def change_day(delta):
        current = date_picker.value
        if current:
            next_date = current + timedelta(days=delta)
            date_picker.value = next_date
            update_panchangam(next_date)

    date_picker = ft.DatePicker(
        value=date.today(),
        first_date=date(2000, 1, 1),
        last_date=date(2030, 12, 31),
        on_change=on_date_change,
    )

    prev_button = ft.ElevatedButton("Previous Day", on_click=lambda _: change_day(-1))
    next_button = ft.ElevatedButton("Next Day", on_click=lambda _: change_day(1))

    panchangam_card = ft.Card(
        content=ft.Container(
            content=ft.Column([
                selected_date_text,
                sunrise_text,
                sunset_text,
                moonrise_text,
                moonset_text,
                rahu_text,
                tithi_text,
                nakshatra_text,
                ritu_text,
                masu_text,
                ayana_text,
                lunar_month_text,
                samvatsara_text,
            ]),
            padding=20,
            width=380,
        )
    )

    page.add(
        title,
        ft.Divider(height=20, color="transparent"),
        ft.Row([prev_button, next_button], alignment=ft.MainAxisAlignment.CENTER),
        ft.Divider(height=20, color="transparent"),
        date_picker,
        ft.Divider(height=20, color="transparent"),
        panchangam_card,
    )

    update_panchangam(date_picker.value)

ft.app(target=main)

import flet as ft
from datetime import datetime, date, timedelta
import panchangam

DEFAULT_LATITUDE = 8.5241
DEFAULT_LONGITUDE = 76.9366


def main(page: ft.Page):
    page.title = "GSB Panchang"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 800

    selected_date = date.today()
    date_picker = ft.DatePicker(
        first_date=datetime(2000, 1, 1),
        last_date=datetime(2050, 12, 31),
    )

    date_button = ft.ElevatedButton(
        "Select Date",
        icon=ft.Icons.CALENDAR_TODAY,
        on_click=lambda _: page.open(date_picker),
    )

    info_text = ft.Text("", size=14, selectable=True)

    def change_date(e):
        nonlocal selected_date
        selected_date = e.control.value.date()
        update_panchangam()

    date_picker.on_change = change_date

    prev_button = ft.ElevatedButton(
        "Previous Day",
        icon=ft.Icons.ARROW_BACK,
        on_click=lambda _: change_day(-1),
    )

    next_button = ft.ElevatedButton(
        "Next Day",
        icon=ft.Icons.ARROW_FORWARD,
        on_click=lambda _: change_day(1),
    )

    def change_day(delta):
        nonlocal selected_date
        selected_date += timedelta(days=delta)
        update_panchangam()

    def update_panchangam():
        data = panchangam.get_panchangam_for_date(
            selected_date,
            latitude=DEFAULT_LATITUDE,
            longitude=DEFAULT_LONGITUDE,
        )
        info = f"""
Date: {data['date']}
Day: {data['day']}

Sunrise: {data['sunrise']}
Sunset: {data['sunset']}
Moonrise: {data['moonrise']}
Moonset: {data['moonset']}
Rahu Kaal: {data['rahu_kaal']}

Tithi: {data['tithi']} ({data['tithi_ml']})
Nakshatra: {data['nakshatra']} ({data['nakshatra_ml']})
Rashi: {data['masu']} ({data['masu_ml']})

Ayana: {data['ayana']} ({data['ayana_ml']})
Ritu: {data['ritu']} ({data['ritu_ml']})

Lunar Month: {data['lunar_month']} ({data['lunar_month_ml']})
Samvatsara: {data['samvatsara']} ({data['samvatsara_ml']})

Location: {data['latitude']}, {data['longitude']}
"""
        info_text.value = info
        page.update()

    page.overlay.append(date_picker)

    page.add(
        ft.Container(
            content=ft.Column([
                ft.Text("GSB Panchang", size=32, weight=ft.FontWeight.BOLD),
                ft.Row([prev_button, date_button, next_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Container(height=20),
                ft.Container(
                    content=info_text,
                    height=500,
                    padding=10,
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=10,
                ),
            ], scroll=ft.ScrollMode.AUTO),
            padding=20,
        )
    )

    update_panchangam()


if __name__ == "__main__":
    ft.app(target=main)

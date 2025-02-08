import flet as ft
import numpy as np
from scipy import interpolate
import sqlite3
import os

class WeightCalculator:
    def __init__(self):
        self.calibration_points = []
        self.db_path = "calibration.db"
        self.init_db()
        self.load_points()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS calibration_points
                    (pressure REAL, weight REAL)''')
        conn.commit()
        conn.close()

    def load_points(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM calibration_points ORDER BY pressure")
        self.calibration_points = c.fetchall()
        conn.close()

    def add_point(self, pressure, weight):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO calibration_points VALUES (?, ?)", (pressure, weight))
        conn.commit()
        conn.close()
        self.load_points()

    def calculate_weight(self, pressure):
        if len(self.calibration_points) < 2:
            return None

        pressures = np.array([p[0] for p in self.calibration_points])
        weights = np.array([p[1] for p in self.calibration_points])

        if len(self.calibration_points) == 2:
            f = interpolate.interp1d(pressures, weights, kind='linear', fill_value='extrapolate')
        else:
            f = interpolate.interp1d(pressures, weights, kind='quadratic', fill_value='extrapolate')

        return float(f(pressure))

def main(page: ft.Page):
    page.title = "Прогноз веса"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window_width = 400
    page.window_height = 800
    page.padding = 20
    page.scroll = ft.ScrollMode.AUTO
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)

    calc = WeightCalculator()

    welcome_text = ft.Text(
        "Добро пожаловать в приложение для прогнозирования веса!",
        size=16,
        text_align=ft.TextAlign.CENTER,
        weight=ft.FontWeight.BOLD
    )

    calibration_title = ft.Text(
        "Калибровка",
        size=20,
        weight=ft.FontWeight.BOLD
    )

    pressure_input = ft.TextField(
        label="Введите давление:",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.LEFT,
        width=360,
        border_radius=8
    )

    weight_input = ft.TextField(
        label="Введите вес:",
        keyboard_type=ft.KeyboardType.NUMBER,
        text_align=ft.TextAlign.LEFT,
        width=360,
        border_radius=8
    )

    result_text = ft.Text(
        size=16,
        text_align=ft.TextAlign.CENTER
    )

    def add_calibration_point(e):
        try:
            pressure = float(pressure_input.value)
            weight = float(weight_input.value)
            calc.add_point(pressure, weight)
            result_text.value = "✅ Точка калибровки добавлена"
            result_text.color = ft.colors.GREEN
            pressure_input.value = ""
            weight_input.value = ""
            page.update()
        except ValueError:
            result_text.value = "❌ Ошибка: введите числовые значения"
            result_text.color = ft.colors.RED
            page.update()

    def calculate_result(e):
        try:
            pressure = float(pressure_input.value)
            result = calc.calculate_weight(pressure)
            if result is not None:
                result_text.value = f"Расчетный вес: {result:.2f}"
                result_text.color = ft.colors.BLACK
            else:
                result_text.value = "Необходимо минимум 2 точки калибровки"
                result_text.color = ft.colors.RED
            page.update()
        except ValueError:
            result_text.value = "❌ Ошибка: введите числовое значение давления"
            result_text.color = ft.colors.RED
            page.update()

    add_button = ft.ElevatedButton(
        text="Добавить точку калибровки",
        width=360,
        height=40,
        on_click=add_calibration_point,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    calc_button = ft.ElevatedButton(
        text="Рассчитать вес",
        width=360,
        height=40,
        on_click=calculate_result,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.GREEN,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    page.add(
        welcome_text,
        ft.Divider(height=20),
        calibration_title,
        pressure_input,
        weight_input,
        add_button,
        ft.Divider(height=20),
        calc_button,
        result_text
    )

if __name__ == '__main__':
    ft.app(target=main, view=ft.AppView.FLET_APP_HIDDEN, assets_dir="assets")
import flet as ft
import numpy as np
from scipy import interpolate
import sqlite3
import os
import sys
from typing import Optional, List, Tuple
import time
from flet.security import encrypt, decrypt

class WeightCalculator:
    def __init__(self):
        self.calibration_points = []
        self.db_path = "calibration.db"
        self.last_update = 0
        self.update_interval = 0.5  # Секунд между обновлениями
        self.init_db()
        self.load_points()

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS calibration_points
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     pressure REAL NOT NULL,
                     weight REAL NOT NULL,
                     UNIQUE(pressure))''')
        conn.commit()
        conn.close()

    def load_points(self) -> List[Tuple[int, float, float]]:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, pressure, weight FROM calibration_points ORDER BY pressure")
            self.calibration_points = c.fetchall()
            conn.close()
            return self.calibration_points
        except sqlite3.Error:
            return []

    def add_point(self, pressure: float, weight: float) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO calibration_points (pressure, weight) VALUES (?, ?)",
                     (pressure, weight))
            conn.commit()
            conn.close()
            self.load_points()
            return True
        except sqlite3.Error:
            return False

    def delete_point(self, point_id: int) -> bool:
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM calibration_points WHERE id = ?", (point_id,))
            conn.commit()
            conn.close()
            self.load_points()
            return True
        except sqlite3.Error:
            return False

    def calculate_weight(self, pressure: float) -> Optional[float]:
        if len(self.calibration_points) < 2:
            return None

        try:
            pressures = np.array([p[1] for p in self.calibration_points])
            weights = np.array([p[2] for p in self.calibration_points])

            if len(self.calibration_points) == 2:
                f = interpolate.interp1d(pressures, weights, kind='linear', fill_value='extrapolate')
            else:
                f = interpolate.interp1d(pressures, weights, kind='quadratic', fill_value='extrapolate')

            return float(f(pressure))
        except:
            return None

def main(page: ft.Page):
    page.title = "Прогноз веса"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10 if page.width < 600 else 20
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)

    calc = WeightCalculator()

    def get_size(default: int, mobile: int) -> int:
        return mobile if page.width < 600 else default

    # Компоненты интерфейса
    pressure_input = ft.TextField(
        label="Давление",
        width=get_size(400, page.width * 0.9),
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    weight_input = ft.TextField(
        label="Вес",
        width=get_size(400, page.width * 0.9),
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    result_text = ft.Text(
        size=get_size(16, 14),
        text_align=ft.TextAlign.CENTER,
        color=ft.colors.BLACK
    )

    # Оптимизированное создание графика с кэшированием
    last_chart_update = 0
    chart_cache = None

    def create_chart():
        nonlocal last_chart_update, chart_cache
        current_time = time.time()

        if chart_cache and current_time - last_chart_update < 0.5:
            return chart_cache

        if len(calc.calibration_points) < 2:
            chart_cache = ft.Text("Добавьте минимум 2 точки для отображения графика")
            return chart_cache

        try:
            pressures = [p[1] for p in calc.calibration_points]
            weights = [p[2] for p in calc.calibration_points]

            x_interp = np.linspace(min(pressures), max(pressures), 50)
            if len(calc.calibration_points) == 2:
                f = interpolate.interp1d(pressures, weights, kind='linear')
            else:
                f = interpolate.interp1d(pressures, weights, kind='quadratic')
            y_interp = f(x_interp)

            chart = ft.LineChart(
                tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.WHITE),
                expand=True,
                min_y=min(weights) * 0.9,
                max_y=max(weights) * 1.1,
                min_x=min(pressures) * 0.9,
                max_x=max(pressures) * 1.1,
                left_axis=ft.ChartAxis(title=ft.Text("Вес"), labels_size=50),
                bottom_axis=ft.ChartAxis(title=ft.Text("Давление"), labels_size=50),
            )

            # Линия интерполяции
            chart.data_series.append(
                ft.LineChartData(
                    color=ft.colors.RED,
                    stroke_width=2,
                    data_points=[ft.LineChartDataPoint(x, y) for x, y in zip(x_interp, y_interp)],
                )
            )

            # Точки калибровки
            chart.data_series.append(
                ft.LineChartData(
                    color=ft.colors.BLUE,
                    stroke_width=4,
                    data_points=[ft.LineChartDataPoint(p, w) for p, w in zip(pressures, weights)],
                )
            )

            chart_cache = chart
            last_chart_update = current_time
            return chart
        except:
            chart_cache = ft.Text("Ошибка при создании графика")
            return chart_cache

    # Таблица с оптимизированным обновлением
    last_table_update = 0
    table_cache = None

    def create_data_table():
        nonlocal last_table_update, table_cache
        current_time = time.time()

        if table_cache and current_time - last_table_update < 0.5:
            return table_cache

        points = calc.calibration_points

        if not points:
            table_cache = ft.Text("Нет калибровочных точек")
            return table_cache

        table = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("ID")),
                ft.DataColumn(ft.Text("Давление")),
                ft.DataColumn(ft.Text("Вес")),
                ft.DataColumn(ft.Text("Действия")),
            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(str(point[0]))),
                        ft.DataCell(ft.Text(f"{point[1]:.2f}")),
                        ft.DataCell(ft.Text(f"{point[2]:.2f}")),
                        ft.DataCell(
                            ft.IconButton(
                                ft.icons.DELETE,
                                icon_color=ft.colors.RED_400,
                                tooltip="Удалить точку",
                                data=point[0],
                                on_click=lambda e: delete_point(e.control.data)
                            )
                        ),
                    ],
                )
                for point in points
            ],
        )

        table_cache = table
        last_table_update = current_time
        return table

    # Контейнеры для графика и таблицы
    chart_container = ft.Container(
        content=create_chart(),
        height=get_size(400, 300),
        border=ft.border.all(1, ft.colors.GREY_400),
        border_radius=10,
        padding=10,
    )

    data_table_container = ft.Container(
        content=create_data_table(),
        padding=10,
    )

    def update_display():
        current_time = time.time()
        if current_time - calc.last_update < calc.update_interval:
            return

        try:
            chart_container.content = create_chart()
            data_table_container.content = create_data_table()
            calc.last_update = current_time
            page.update()
        except Exception as e:
            result_text.value = f"Ошибка обновления: {str(e)}"
            result_text.color = ft.colors.RED
            page.update()

    def add_calibration_point(e):
        try:
            pressure = float(pressure_input.value)
            weight = float(weight_input.value)

            if calc.add_point(pressure, weight):
                result_text.value = "✅ Точка калибровки добавлена"
                result_text.color = ft.colors.GREEN
                pressure_input.value = ""
                weight_input.value = ""
                update_display()
            else:
                result_text.value = "❌ Ошибка добавления точки"
                result_text.color = ft.colors.RED
                page.update()
        except ValueError:
            result_text.value = "❌ Ошибка: введите числовые значения"
            result_text.color = ft.colors.RED
            page.update()

    def delete_point(point_id):
        if calc.delete_point(point_id):
            update_display()
        else:
            result_text.value = "❌ Ошибка удаления точки"
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
        "Добавить точку калибровки",
        width=get_size(400, page.width * 0.9),
        on_click=add_calibration_point,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    calc_button = ft.ElevatedButton(
        "Рассчитать вес",
        width=get_size(400, page.width * 0.9),
        on_click=calculate_result,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.GREEN,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    def on_resize(e):
        pressure_input.width = get_size(400, page.width * 0.9)
        weight_input.width = get_size(400, page.width * 0.9)
        add_button.width = get_size(400, page.width * 0.9)
        calc_button.width = get_size(400, page.width * 0.9)
        chart_container.height = get_size(400, 300)
        page.update()

    page.on_resize = on_resize

    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        "Калькулятор веса на основе давления",
                        size=get_size(24, 20),
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Добавьте калибровочные точки (минимум 2) для расчета веса на основе давления.",
                        size=get_size(16, 14),
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Divider(height=20),
                    pressure_input,
                    weight_input,
                    add_button,
                    ft.Divider(height=20),
                    calc_button,
                    result_text,
                    ft.Divider(height=20),
                    ft.Text(
                        "График калибровочной кривой",
                        size=get_size(20, 16),
                        weight=ft.FontWeight.BOLD
                    ),
                    chart_container,
                    ft.Divider(height=20),
                    ft.Text(
                        "Таблица калибровочных точек",
                        size=get_size(20, 16),
                        weight=ft.FontWeight.BOLD
                    ),
                    data_table_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=10,
            border_radius=10,
        )
    )

if __name__ == '__main__':
    try:
        ft.app(
            target=main,
            view=ft.AppView.WEB_BROWSER,
            assets_dir="assets",
            port=8550,
            web_renderer="canvas"  
        )
    except Exception as e:
        print(f"Critical error: {str(e)}")
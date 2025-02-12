import flet as ft
import numpy as np
from scipy import interpolate
import sqlite3
import os
from pathlib import Path

class WeightCalculator:
    def __init__(self):
        self.calibration_points = []
        # Изменяем путь к базе данных на постоянное хранилище
        self.db_path = str(Path.home() / "calibration.db")
        self.init_db()
        self.load_points()

    def init_db(self):
        """Initialize database with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Создаем таблицу, если она не существует
            c.execute('''CREATE TABLE IF NOT EXISTS calibration_points
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         pressure REAL NOT NULL,
                         weight REAL NOT NULL)''')
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Ошибка инициализации БД: {str(e)}")

    def validate_values(self, pressure, weight):
        """Validate input values"""
        try:
            pressure = float(pressure)
            weight = float(weight)
            if pressure <= 0 or weight <= 0:
                return False
            return True
        except (ValueError, TypeError):
            return False

    def load_points(self):
        """Load calibration points from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, pressure, weight FROM calibration_points ORDER BY pressure")
            self.calibration_points = c.fetchall()
            conn.close()
            return self.calibration_points
        except sqlite3.Error as e:
            print(f"Ошибка загрузки точек: {str(e)}")
            return []

    def add_point(self, pressure, weight):
        """Add new calibration point"""
        try:
            if not self.validate_values(pressure, weight):
                return False

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO calibration_points (pressure, weight) VALUES (?, ?)",
                     (pressure, weight))
            conn.commit()
            conn.close()
            return self.load_points()
        except sqlite3.Error as e:
            print(f"Ошибка добавления точки: {str(e)}")
            return False

    def edit_point(self, point_id, pressure, weight):
        """Edit existing calibration point"""
        try:
            if not self.validate_values(pressure, weight):
                return False

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("UPDATE calibration_points SET pressure = ?, weight = ? WHERE id = ?",
                     (pressure, weight, point_id))
            conn.commit()
            conn.close()
            return self.load_points()
        except sqlite3.Error as e:
            print(f"Ошибка редактирования точки: {str(e)}")
            return False

    def delete_point(self, point_id):
        """Delete calibration point"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM calibration_points WHERE id = ?", (point_id,))
            conn.commit()
            conn.close()
            return self.load_points()
        except sqlite3.Error as e:
            print(f"Ошибка удаления точки: {str(e)}")
            return False

    def calculate_weight(self, pressure):
        """Calculate weight using interpolation"""
        if len(self.calibration_points) < 2:
            return None

        try:
            pressures = np.array([p[1] for p in self.calibration_points])
            weights = np.array([p[2] for p in self.calibration_points])

            # Линейная интерполяция для 2 точек, квадратичная для >2 точек
            if len(self.calibration_points) == 2:
                f = interpolate.interp1d(pressures, weights, kind='linear', fill_value='extrapolate')
            else:
                f = interpolate.interp1d(pressures, weights, kind='quadratic', fill_value='extrapolate')

            return float(f(pressure))
        except Exception as e:
            print(f"Ошибка расчета веса: {str(e)}")
            return None

def main(page: ft.Page):
    page.title = "Прогноз веса"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10 if page.width < 600 else 20
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)

    def get_size(default, mobile):
        return mobile if page.width < 600 else default

    # Диалог редактирования точки
    edit_dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Редактировать точку калибровки"),
        content=ft.Column(
            controls=[
                ft.TextField(label="Давление", keyboard_type=ft.KeyboardType.NUMBER),
                ft.TextField(label="Вес", keyboard_type=ft.KeyboardType.NUMBER),
            ],
            spacing=10,
        ),
    )

    def show_edit_dialog(point_id, pressure, weight):
        def save_changes(e):
            try:
                new_pressure = float(edit_dialog.content.controls[0].value)
                new_weight = float(edit_dialog.content.controls[1].value)

                if calc.edit_point(point_id, new_pressure, new_weight):
                    result_text.value = "✅ Точка калибровки обновлена"
                    result_text.color = ft.colors.GREEN
                    page.dialog = None
                    update_display()
                else:
                    result_text.value = "❌ Ошибка обновления точки"
                    result_text.color = ft.colors.RED
                page.update()
            except ValueError:
                result_text.value = "❌ Ошибка: введите числовые значения"
                result_text.color = ft.colors.RED
                page.update()

        edit_dialog.content.controls[0].value = str(pressure)
        edit_dialog.content.controls[1].value = str(weight)

        edit_dialog.actions = [
            ft.TextButton("Отмена", on_click=lambda e: setattr(page, 'dialog', None)),
            ft.TextButton("Сохранить", on_click=save_changes),
        ]
        page.dialog = edit_dialog
        page.update()

    calc = WeightCalculator()

    pressure_input = ft.TextField(
        label="Давление",
        width=get_size(400, page.width * 0.9),
        text_align=ft.TextAlign.LEFT,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    weight_input = ft.TextField(
        label="Вес",
        width=get_size(400, page.width * 0.9),
        text_align=ft.TextAlign.LEFT,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    result_text = ft.Text(
        size=get_size(16, 14),
        text_align=ft.TextAlign.CENTER,
        color=ft.colors.BLACK
    )

    def create_chart():
        if len(calc.calibration_points) < 2:
            return ft.Text("Добавьте минимум 2 точки для отображения графика")

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
                left_axis=ft.ChartAxis(
                    title=ft.Text("Вес"),
                    labels_size=50,
                ),
                bottom_axis=ft.ChartAxis(
                    title=ft.Text("Давление"),
                    labels_size=50,
                ),
            )

            # Добавляем только одну линию с соответствующей интерполяцией
            chart.data_series.append(
                ft.LineChartData(
                    color=ft.colors.RED,
                    stroke_width=2,
                    data_points=[
                        ft.LineChartDataPoint(x, y)
                        for x, y in zip(x_interp, y_interp)
                    ],
                )
            )

            return chart
        except Exception as e:
            print(f"Ошибка при создании графика: {str(e)}")
            return ft.Text("Ошибка при создании графика")

    def create_data_table():
        points = calc.load_points()

        if not points:
            return ft.Text("Нет калибровочных точек")

        return ft.DataTable(
            width=get_size(400, page.width * 0.9),
            border=ft.border.all(1, ft.colors.GREY_400),
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
                            ft.Container(
                                content=ft.Row(
                                    [
                                        ft.IconButton(
                                            icon=ft.icons.EDIT,
                                            icon_size=20,
                                            icon_color="blue",
                                            tooltip="Редактировать",
                                            on_click=lambda e, p=point: show_edit_dialog(p[0], p[1], p[2]),
                                        ),
                                        ft.IconButton(
                                            icon=ft.icons.DELETE,
                                            icon_size=20,
                                            icon_color="red",
                                            tooltip="Удалить",
                                            on_click=lambda e, pid=point[0]: delete_point(pid),
                                        ),
                                    ],
                                    spacing=5,
                                    alignment=ft.MainAxisAlignment.CENTER,
                                ),
                                padding=5,
                            )
                        ),
                    ],
                )
                for point in points
            ],
        )

    def update_display():
        try:
            chart_container.content = create_chart()
            data_table_container.content = create_data_table()
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
            result_text.value = "✅ Точка калибровки удалена"
            result_text.color = ft.colors.GREEN
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
    ft.app(target=main, view=ft.AppView.WEB_BROWSER, port=5000, host="0.0.0.0")
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
            # Обновляем список точек после удаления
            self.calibration_points = self.load_points()
            update_display()
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

    calc = WeightCalculator()
    editing_mode = False
    edited_values = {}

    def get_size(default, mobile):
        return mobile if page.width < 600 else default

    def toggle_edit_mode(e):
        nonlocal editing_mode
        editing_mode = not editing_mode
        if not editing_mode:  # Выход из режима редактирования без сохранения
            edited_values.clear()
        update_display()

    def save_changes(e):
        nonlocal editing_mode
        try:
            for point_id, new_values in edited_values.items():
                if not calc.edit_point(point_id, new_values['pressure'], new_values['weight']):
                    result_text.value = "❌ Ошибка сохранения изменений"
                    result_text.color = ft.colors.RED
                    page.update()
                    return

            result_text.value = "✅ Изменения сохранены"
            result_text.color = ft.colors.GREEN
            editing_mode = False
            edited_values.clear()
            update_display()
        except Exception as e:
            result_text.value = f"❌ Ошибка: {str(e)}"
            result_text.color = ft.colors.RED
            page.update()

    def on_value_change(e, point_id, field):
        try:
            value = float(e.control.value)
            if point_id not in edited_values:
                edited_values[point_id] = {
                    'pressure': next(p[1] for p in calc.calibration_points if p[0] == point_id),
                    'weight': next(p[2] for p in calc.calibration_points if p[0] == point_id)
                }
            edited_values[point_id][field] = value
        except ValueError:
            pass

    def delete_point(point_id):
        if calc.delete_point(point_id):
            result_text.value = "✅ Точка калибровки удалена"
            result_text.color = ft.colors.GREEN
            update_display()
        else:
            result_text.value = "❌ Ошибка удаления точки"
            result_text.color = ft.colors.RED
            page.update()

    def create_data_table():
        points = calc.load_points()
        if not points:
            return ft.Text("Нет калибровочных точек")

        # Таблица калибровочных точек
        table = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text("ID", width=50),
                            ft.Text("Давление", width=100),
                            ft.Text("Вес", width=100),
                            ft.Text("", width=30),  # Уменьшенная колонка для кнопки удаления
                        ],
                    ),
                    padding=10,
                    bgcolor=ft.colors.BLUE_50,
                )
            ],
            spacing=2,
        )

        # Строки данных
        for point in points:
            if editing_mode:
                row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"{point[0]}", width=50),
                            ft.TextField(
                                value=str(edited_values.get(point[0], {}).get('pressure', point[1])),
                                width=100,
                                height=40,
                                text_size=14,
                                on_change=lambda e, pid=point[0]: on_value_change(e, pid, 'pressure'),
                            ),
                            ft.TextField(
                                value=str(edited_values.get(point[0], {}).get('weight', point[2])),
                                width=100,
                                height=40,
                                text_size=14,
                                on_change=lambda e, pid=point[0]: on_value_change(e, pid, 'weight'),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=ft.colors.RED,
                                width=30,
                                icon_size=20,
                                on_click=lambda pid=point[0]: delete_point(pid),
                            ),
                        ],
                    ),
                    padding=5,
                )
            else:
                row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"{point[0]}", width=50),
                            ft.Text(f"{point[1]:.2f}", width=100),
                            ft.Text(f"{point[2]:.2f}", width=100),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_color=ft.colors.RED,
                                width=30,
                                icon_size=20,
                                on_click=lambda pid=point[0]: delete_point(pid),
                            ),
                        ],
                    ),
                    padding=5,
                )
            table.controls.append(row)

        buttons = ft.Row(
            [
                ft.ElevatedButton(
                    "Редактировать" if not editing_mode else "Отмена",
                    on_click=toggle_edit_mode,
                ),
                ft.ElevatedButton(
                    "Сохранить",
                    visible=editing_mode,
                    on_click=save_changes,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        return ft.Column([table, buttons], spacing=20)

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
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
        """Initialize database with proper schema"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Удаляем старую таблицу и создаем новую с полем id
        c.execute('DROP TABLE IF EXISTS calibration_points')
        c.execute('''CREATE TABLE calibration_points
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     pressure REAL NOT NULL,
                     weight REAL NOT NULL)''')
        conn.commit()
        conn.close()

    def validate_values(self, pressure, weight):
        """Validate input values"""
        if pressure < 0 or weight < 0:
            raise ValueError("Значения давления и веса должны быть положительными")
        return True

    def load_points(self):
        """Load calibration points from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT id, pressure, weight FROM calibration_points ORDER BY pressure")
            self.calibration_points = c.fetchall()
            conn.close()
            return self.calibration_points
        except sqlite3.Error:
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
        except (sqlite3.Error, ValueError) as e:
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
        except (sqlite3.Error, ValueError) as e:
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
        except sqlite3.Error:
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
        except:
            return None

def main(page: ft.Page):
    # Настройка страницы для мобильного интерфейса
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
        edit_dialog.content.controls[0].value = str(pressure)
        edit_dialog.content.controls[1].value = str(weight)

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
                result_text.value = "❌ Ошибка: введите корректные числовые значения"
                result_text.color = ft.colors.RED
                page.update()

        edit_dialog.actions = [
            ft.TextButton("Отмена", on_click=lambda e: setattr(page, 'dialog', None)),
            ft.TextButton("Сохранить", on_click=save_changes),
        ]
        page.dialog = edit_dialog
        page.update()

    calc = WeightCalculator()

    # Заголовок - адаптивный размер текста
    title = ft.Text(
        "Калькулятор веса на основе давления",
        size=get_size(24, 20),
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )

    description = ft.Text(
        "Добавьте калибровочные точки (минимум 2) для расчета веса на основе давления.",
        size=get_size(16, 14),
        text_align=ft.TextAlign.CENTER,
    )

    # Поля ввода - адаптивная ширина
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

    # График калибровки
    def create_chart():
        if len(calc.calibration_points) < 2:
            return ft.Text("Добавьте минимум 2 точки для отображения графика")

        try:
            pressures = [p[1] for p in calc.calibration_points]
            weights = [p[2] for p in calc.calibration_points]

            # Создаем точки для интерполированной кривой
            x_interp = np.linspace(min(pressures), max(pressures), 50)

            # Линейная интерполяция для 2 точек, квадратичная для >2 точек
            if len(calc.calibration_points) == 2:
                f = interpolate.interp1d(pressures, weights, kind='linear')
            else:
                f = interpolate.interp1d(pressures, weights, kind='quadratic')

            y_interp = f(x_interp)

            # График
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

            # Добавляем линию интерполяции
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

            # Добавляем точки калибровки
            chart.data_series.append(
                ft.LineChartData(
                    color=ft.colors.BLUE,
                    stroke_width=4,
                    data_points=[
                        ft.LineChartDataPoint(p, w)
                        for p, w in zip(pressures, weights)
                    ],
                )
            )

            return chart
        except:
            return ft.Text("Ошибка при создании графика")

    # Таблица калибровочных точек
    def create_data_table():
        points = calc.load_points()

        if not points:
            return ft.Text("Нет калибровочных точек")

        return ft.DataTable(
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
                            ft.Row(
                                controls=[
                                    ft.IconButton(
                                        ft.icons.EDIT,
                                        icon_color=ft.colors.BLUE,
                                        tooltip="Редактировать точку",
                                        data=point,
                                        on_click=lambda e: show_edit_dialog(
                                            e.control.data[0],
                                            e.control.data[1],
                                            e.control.data[2]
                                        )
                                    ),
                                    ft.IconButton(
                                        ft.icons.DELETE,
                                        icon_color=ft.colors.RED_400,
                                        tooltip="Удалить точку",
                                        data=point[0],
                                        on_click=lambda e: delete_point(e.control.data)
                                    ),
                                ]
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

    # Кнопки - адаптивная ширина
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

    # График - адаптивная высота
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

    # Обработка изменения размера окна
    def on_resize(e):
        pressure_input.width = get_size(400, page.width * 0.9)
        weight_input.width = get_size(400, page.width * 0.9)
        add_button.width = get_size(400, page.width * 0.9)
        calc_button.width = get_size(400, page.width * 0.9)
        chart_container.height = get_size(400, 300)
        page.update()

    page.on_resize = on_resize

    # Добавляем все элементы на страницу
    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    title,
                    description,
                    ft.Divider(height=20),
                    pressure_input,
                    weight_input,
                    add_button,
                    ft.Divider(height=20),
                    calc_button,
                    result_text,
                    ft.Divider(height=20),
                    ft.Text("График калибровочной кривой",
                           size=get_size(20, 16),
                           weight=ft.FontWeight.BOLD),
                    chart_container,
                    ft.Divider(height=20),
                    ft.Text("Таблица калибровочных точек",
                           size=get_size(20, 16),
                           weight=ft.FontWeight.BOLD),
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
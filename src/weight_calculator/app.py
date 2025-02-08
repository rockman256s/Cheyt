"""
Weight Calculator - BeeWare Android Application
"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from database import init_db, add_calibration_point, get_all_points
from interpolation import linear_interpolation, quadratic_interpolation

class WeightCalculator(toga.App):
    def startup(self):
        # Initialize database
        init_db()

        # Create main window
        self.main_window = toga.MainWindow(title=self.name)

        # Create input fields
        self.pressure_input = toga.TextInput(placeholder='Давление')
        self.weight_input = toga.TextInput(placeholder='Вес')
        self.calc_input = toga.TextInput(placeholder='Введите давление для расчета')
        self.result_label = toga.Label('Результат: ')

        # Create buttons
        add_button = toga.Button('Добавить точку', on_press=self.add_point)
        calc_button = toga.Button('Рассчитать', on_press=self.calculate_weight)

        # Create layouts
        input_box = toga.Box(
            children=[
                toga.Box(
                    children=[self.pressure_input, self.weight_input, add_button],
                    style=Pack(direction=ROW, padding=5)
                ),
                toga.Box(
                    children=[self.calc_input, calc_button, self.result_label],
                    style=Pack(direction=ROW, padding=5)
                )
            ],
            style=Pack(direction=COLUMN, padding=5)
        )

        # Main container
        main_box = toga.Box(
            children=[input_box],
            style=Pack(direction=COLUMN, padding=10)
        )

        # Add the content to the main window
        self.main_window.content = main_box
        self.main_window.show()

    def add_point(self, widget):
        try:
            pressure = float(self.pressure_input.value)
            weight = float(self.weight_input.value)
            if add_calibration_point(pressure, weight):
                self.main_window.info_dialog(
                    'Успех',
                    'Точка калибровки добавлена'
                )
                self.pressure_input.value = ''
                self.weight_input.value = ''
            else:
                self.main_window.error_dialog(
                    'Ошибка',
                    'Не удалось добавить точку'
                )
        except ValueError:
            self.main_window.error_dialog(
                'Ошибка',
                'Введите корректные числовые значения'
            )

    def calculate_weight(self, widget):
        try:
            pressure = float(self.calc_input.value)
            points = get_all_points()
            if len(points) >= 2:
                if len(points) == 2:
                    result = linear_interpolation(pressure, points)
                else:
                    result = quadratic_interpolation(pressure, points)
                self.result_label.text = f'Результат: {result:.2f}'
            else:
                self.main_window.error_dialog(
                    'Ошибка',
                    'Необходимо минимум 2 точки калибровки'
                )
        except ValueError:
            self.main_window.error_dialog(
                'Ошибка',
                'Введите корректное числовое значение'
            )

def main():
    return WeightCalculator('Калькулятор веса', 'org.weightcalc')

if __name__ == '__main__':
    app = main()
    app.main_loop()

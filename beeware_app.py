import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from interpolation import linear_interpolation, quadratic_interpolation
from database import init_db, add_calibration_point, get_all_points
from utils import validate_input, validate_points

class WeightCalculatorApp(toga.App):
    def startup(self):
        # Initialize database
        init_db()

        # Create main box with padding
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Title
        title_label = toga.Label(
            'Калькулятор веса',
            style=Pack(padding=(0, 0, 20, 0), font_size=18)
        )
        main_box.add(title_label)

        # Calibration section
        calibration_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # Pressure input
        pressure_label = toga.Label('Давление:', style=Pack(padding=(0, 5)))
        self.pressure_input = toga.NumberInput(style=Pack(flex=1))

        # Weight input
        weight_label = toga.Label('Вес:', style=Pack(padding=(0, 5)))
        self.weight_input = toga.NumberInput(style=Pack(flex=1))

        # Add point button
        add_button = toga.Button(
            'Добавить точку',
            on_press=self.add_point,
            style=Pack(padding=5)
        )

        # Add widgets to calibration box
        calibration_box.add(pressure_label)
        calibration_box.add(self.pressure_input)
        calibration_box.add(weight_label)
        calibration_box.add(self.weight_input)
        calibration_box.add(add_button)

        # Calculation section
        calculation_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        calc_label = toga.Label(
            'Расчет веса',
            style=Pack(padding=(10, 0))
        )

        # Calculation input
        calc_pressure_label = toga.Label('Введите давление для расчета:', style=Pack(padding=(0, 5)))
        self.calc_pressure_input = toga.NumberInput(style=Pack(flex=1))

        # Calculate button
        calc_button = toga.Button(
            'Рассчитать',
            on_press=self.calculate,
            style=Pack(padding=5)
        )

        # Result label
        self.result_label = toga.Label(
            '',
            style=Pack(padding=(10, 0))
        )

        # Add widgets to calculation box
        calculation_box.add(calc_label)
        calculation_box.add(calc_pressure_label)
        calculation_box.add(self.calc_pressure_input)
        calculation_box.add(calc_button)
        calculation_box.add(self.result_label)

        # Add all sections to main box
        main_box.add(calibration_box)
        main_box.add(calculation_box)

        # Create main window
        self.main_window = toga.MainWindow(title='Калькулятор веса')
        self.main_window.content = main_box
        self.main_window.show()

    def add_point(self, widget):
        try:
            pressure = float(self.pressure_input.value)
            weight = float(self.weight_input.value)

            is_valid, error_message = validate_input(str(pressure), str(weight))
            if is_valid:
                if add_calibration_point(pressure, weight):
                    self.pressure_input.value = None
                    self.weight_input.value = None
                    self.result_label.text = 'Точка добавлена успешно'
                else:
                    self.result_label.text = 'Ошибка при добавлении точки'
            else:
                self.result_label.text = error_message
        except (ValueError, TypeError):
            self.result_label.text = 'Введите корректные значения'

    def calculate(self, widget):
        try:
            pressure = float(self.calc_pressure_input.value)
            points = get_all_points()

            is_valid, error_message = validate_points(points)
            if not is_valid:
                self.result_label.text = error_message
                return

            min_pressure = min(p[0] for p in points)
            max_pressure = max(p[0] for p in points)

            if pressure < min_pressure or pressure > max_pressure:
                warning = f"Внимание: значение давления ({pressure}) вне диапазона калибровки ({min_pressure:.1f} - {max_pressure:.1f})"
                self.result_label.text = warning
                return

            if len(points) == 2:
                result = linear_interpolation(pressure, points)
                method = "линейная интерполяция"
            else:
                result = quadratic_interpolation(pressure, points)
                method = "квадратичная интерполяция"

            self.result_label.text = f"Расчетный вес: {result:.2f} ({method})"

        except (ValueError, TypeError):
            self.result_label.text = 'Введите корректное значение давления'

def main():
    return WeightCalculatorApp('Калькулятор веса', 'org.weightcalculator')

if __name__ == '__main__':
    app = main()
    app.main_loop()
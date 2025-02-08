from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window
import sqlite3
import os

class WeightCalculatorApp(App):
    def build(self):
        # Set window size for testing
        Window.size = (400, 600)

        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Title
        title = Label(
            text='Калькулятор веса',
            size_hint_y=None,
            height=dp(50)
        )
        layout.add_widget(title)

        # Calibration inputs
        cal_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        self.pressure_input = TextInput(
            hint_text='Давление',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        self.weight_input = TextInput(
            hint_text='Вес',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        add_button = Button(
            text='Добавить точку',
            size_hint_y=None,
            height=dp(40)
        )
        add_button.bind(on_press=self.add_point)

        cal_layout.add_widget(self.pressure_input)
        cal_layout.add_widget(self.weight_input)
        cal_layout.add_widget(add_button)


        # Weight calculation
        calc_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(120))
        self.calc_input = TextInput(
            hint_text='Введите давление для расчета',
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        calc_button = Button(
            text='Рассчитать',
            size_hint_y=None,
            height=dp(40)
        )
        calc_button.bind(on_press=self.calculate_weight)
        self.result_label = Label(
            text='',
            size_hint_y=None,
            height=dp(40)
        )

        calc_layout.add_widget(self.calc_input)
        calc_layout.add_widget(calc_button)
        calc_layout.add_widget(self.result_label)

        # Add all widgets to main layout
        layout.add_widget(cal_layout)
        layout.add_widget(calc_layout)

        return layout

    def add_point(self, instance):
        try:
            pressure = float(self.pressure_input.text)
            weight = float(self.weight_input.text)

            # Store in SQLite database
            conn = sqlite3.connect('calibration.db')
            c = conn.cursor()

            # Create table if not exists
            c.execute('''CREATE TABLE IF NOT EXISTS calibration_points
                        (pressure REAL, weight REAL)''')

            # Add point
            c.execute("INSERT INTO calibration_points VALUES (?, ?)", (pressure, weight))
            conn.commit()
            conn.close()

            self.pressure_input.text = ''
            self.weight_input.text = ''
            self.result_label.text = 'Точка добавлена'
        except ValueError:
            self.result_label.text = 'Ошибка: введите числовые значения'
        except sqlite3.Error:
            self.result_label.text = 'Ошибка базы данных'

    def calculate_weight(self, instance):
        try:
            pressure = float(self.calc_input.text)

            # Get calibration points from database
            conn = sqlite3.connect('calibration.db')
            c = conn.cursor()
            c.execute("SELECT * FROM calibration_points ORDER BY pressure")
            points = c.fetchall()
            conn.close()

            if len(points) < 2:
                self.result_label.text = 'Нужно минимум 2 точки калибровки'
                return

            # Simple linear interpolation
            for i in range(len(points) - 1):
                if points[i][0] <= pressure <= points[i + 1][0]:
                    p1, w1 = points[i]
                    p2, w2 = points[i + 1]
                    weight = w1 + (w2 - w1) * (pressure - p1) / (p2 - p1)
                    self.result_label.text = f'Расчетный вес: {weight:.2f}'
                    return

            self.result_label.text = 'Давление вне диапазона калибровки'

        except ValueError:
            self.result_label.text = 'Ошибка: введите числовое значение'
        except sqlite3.Error:
            self.result_label.text = 'Ошибка базы данных'

if __name__ == '__main__':
    if not os.path.exists('calibration.db'):
        conn = sqlite3.connect('calibration.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS calibration_points
                    (pressure REAL, weight REAL)''')
        conn.commit()
        conn.close()

    WeightCalculatorApp().run()
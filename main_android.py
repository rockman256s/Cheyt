"""
Weight Calculator Android Application
"""
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import platform
import sqlite3
import os

class WeightCalculatorApp(App):
    def build(self):
        # Настройка окна для Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_EXTERNAL_STORAGE
            ])

        # Set window size for testing (только для десктопа)
        if platform != 'android':
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
        cal_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(200))

        # Pressure input
        pressure_label = Label(
            text='Давление:',
            size_hint_y=None,
            height=dp(30)
        )
        self.pressure_input = TextInput(
            multiline=False,
            input_type='number',
            size_hint_y=None,
            height=dp(40)
        )

        # Weight input
        weight_label = Label(
            text='Вес:',
            size_hint_y=None,
            height=dp(30)
        )
        self.weight_input = TextInput(
            multiline=False,
            input_type='number',
            size_hint_y=None,
            height=dp(40)
        )

        add_button = Button(
            text='Добавить точку калибровки',
            size_hint_y=None,
            height=dp(40)
        )
        add_button.bind(on_press=self.add_point)

        cal_layout.add_widget(pressure_label)
        cal_layout.add_widget(self.pressure_input)
        cal_layout.add_widget(weight_label)
        cal_layout.add_widget(self.weight_input)
        cal_layout.add_widget(add_button)

        # Weight calculation
        calc_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(150))
        calc_label = Label(
            text='Введите давление для расчета:',
            size_hint_y=None,
            height=dp(30)
        )
        self.calc_input = TextInput(
            multiline=False,
            input_type='number',
            size_hint_y=None,
            height=dp(40)
        )
        calc_button = Button(
            text='Рассчитать вес',
            size_hint_y=None,
            height=dp(40)
        )
        calc_button.bind(on_press=self.calculate_weight)
        self.result_label = Label(
            text='',
            size_hint_y=None,
            height=dp(40)
        )

        calc_layout.add_widget(calc_label)
        calc_layout.add_widget(self.calc_input)
        calc_layout.add_widget(calc_button)
        calc_layout.add_widget(self.result_label)

        # Add all layouts to main layout
        layout.add_widget(cal_layout)
        layout.add_widget(calc_layout)

        return layout

    def get_application_path(self):
        """Get path for database file based on platform"""
        if platform == 'android':
            from android.storage import app_storage_path
            return app_storage_path()
        return os.path.dirname(os.path.abspath(__file__))

    def add_point(self, instance):
        try:
            pressure = float(self.pressure_input.text)
            weight = float(self.weight_input.text)

            # Store in SQLite database with platform-specific path
            db_path = os.path.join(self.get_application_path(), 'calibration.db')
            conn = sqlite3.connect(db_path)
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
            self.result_label.text = 'Точка калибровки добавлена'
        except ValueError:
            self.result_label.text = 'Ошибка: введите числовые значения'
        except sqlite3.Error as e:
            self.result_label.text = f'Ошибка базы данных: {str(e)}'
        except Exception as e:
            self.result_label.text = f'Ошибка: {str(e)}'

    def calculate_weight(self, instance):
        try:
            pressure = float(self.calc_input.text)

            # Get calibration points from database
            db_path = os.path.join(self.get_application_path(), 'calibration.db')
            conn = sqlite3.connect(db_path)
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
        except sqlite3.Error as e:
            self.result_label.text = f'Ошибка базы данных: {str(e)}'
        except Exception as e:
            self.result_label.text = f'Ошибка: {str(e)}'

if __name__ == '__main__':
    try:
        WeightCalculatorApp().run()
    except Exception as e:
        print(f"Critical error: {str(e)}")
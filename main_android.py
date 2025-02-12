"""
Weight Calculator Android Application
"""
import kivy
kivy.require('2.2.1')

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
from pathlib import Path
import numpy as np
from scipy import interpolate
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class WeightCalculatorApp(App):
    def build(self):
        # Set up Android permissions
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([
                    Permission.WRITE_EXTERNAL_STORAGE,
                    Permission.READ_EXTERNAL_STORAGE
                ])
            except Exception as e:
                logger.error(f"Error requesting permissions: {e}")

        # Set window size for desktop testing
        if platform != 'android':
            Window.size = (400, 600)

        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))

        # Title
        title = Label(
            text='Калькулятор веса',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(24)
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

        # Add calibration point button
        add_button = Button(
            text='Добавить точку калибровки',
            size_hint_y=None,
            height=dp(40),
            background_color=(0.2, 0.6, 1, 1)
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
            height=dp(40),
            background_color=(0.2, 0.6, 1, 1)
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

        # Initialize database
        self.init_db()

        return layout

    def get_db_path(self):
        """Get platform-specific database path"""
        if platform == 'android':
            try:
                from android.storage import app_storage_path
                db_dir = app_storage_path()
            except Exception as e:
                logger.error(f"Error getting Android storage path: {e}")
                db_dir = str(Path.home())
        else:
            db_dir = str(Path.home())

        return os.path.join(db_dir, 'calibration.db')

    def init_db(self):
        """Initialize database with proper schema"""
        try:
            logger.info("Initializing database...")
            conn = sqlite3.connect(self.get_db_path())
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS calibration_points
                        (pressure REAL NOT NULL,
                         weight REAL NOT NULL)''')

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Database initialization error: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during database initialization: {e}")

    def validate_input(self, value):
        """Validate numeric input"""
        try:
            val = float(value)
            return val > 0
        except (ValueError, TypeError):
            return False

    def add_point(self, instance):
        """Add new calibration point"""
        try:
            logger.info("Adding calibration point...")
            if not self.validate_input(self.pressure_input.text):
                self.result_label.text = 'Ошибка: введите корректное значение давления'
                return

            if not self.validate_input(self.weight_input.text):
                self.result_label.text = 'Ошибка: введите корректное значение веса'
                return

            pressure = float(self.pressure_input.text)
            weight = float(self.weight_input.text)

            conn = sqlite3.connect(self.get_db_path())
            c = conn.cursor()
            c.execute("INSERT INTO calibration_points VALUES (?, ?)", (pressure, weight))
            conn.commit()
            conn.close()

            self.pressure_input.text = ''
            self.weight_input.text = ''
            self.result_label.text = '✓ Точка калибровки добавлена'
            logger.info("Calibration point added successfully")
        except sqlite3.Error as e:
            logger.error(f"Database error while adding point: {e}")
            self.result_label.text = 'Ошибка сохранения данных'
        except Exception as e:
            logger.error(f"Unexpected error while adding point: {e}")
            self.result_label.text = f'Ошибка: {str(e)}'

    def calculate_weight(self, instance):
        """Calculate weight using interpolation"""
        try:
            logger.info("Calculating weight...")
            if not self.validate_input(self.calc_input.text):
                self.result_label.text = 'Ошибка: введите корректное значение давления'
                return

            pressure = float(self.calc_input.text)

            # Get calibration points
            conn = sqlite3.connect(self.get_db_path())
            c = conn.cursor()
            c.execute("SELECT pressure, weight FROM calibration_points ORDER BY pressure")
            points = c.fetchall()
            conn.close()

            if len(points) < 2:
                self.result_label.text = 'Необходимо минимум 2 точки калибровки'
                return

            # Prepare data for interpolation
            pressures = np.array([p[0] for p in points])
            weights = np.array([p[1] for p in points])

            # Choose interpolation method based on number of points
            if len(points) == 2:
                f = interpolate.interp1d(pressures, weights, kind='linear', fill_value='extrapolate')
            else:
                f = interpolate.interp1d(pressures, weights, kind='quadratic', fill_value='extrapolate')

            # Calculate weight
            calculated_weight = float(f(pressure))
            self.result_label.text = f'Расчетный вес: {calculated_weight:.2f}'
            logger.info(f"Weight calculated successfully: {calculated_weight:.2f}")
        except sqlite3.Error as e:
            logger.error(f"Database error while calculating weight: {e}")
            self.result_label.text = 'Ошибка чтения данных калибровки'
        except Exception as e:
            logger.error(f"Unexpected error while calculating weight: {e}")
            self.result_label.text = f'Ошибка расчета: {str(e)}'

if __name__ == '__main__':
    try:
        logger.info("Starting Weight Calculator App...")
        WeightCalculatorApp().run()
    except Exception as e:
        logger.error(f"Critical error in main: {e}")
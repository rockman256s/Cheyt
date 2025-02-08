from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.metrics import dp

from database import init_db, add_calibration_point, get_all_points
from interpolation import linear_interpolation, quadratic_interpolation
from utils import validate_input, validate_points

class WeightCalculatorLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = dp(20)  # Увеличенные отступы
        self.spacing = dp(20)  # Увеличенное расстояние между элементами

        # Initialize database
        init_db()

        # Create ScrollView
        scroll_layout = BoxLayout(orientation='vertical', spacing=dp(20), size_hint_y=None)
        scroll_layout.bind(minimum_height=scroll_layout.setter('height'))

        # Title with larger font and more space
        title_container = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(100))
        title = Label(
            text='Калькулятор веса',
            size_hint_y=None,
            height=dp(80),  # Увеличиваем высоту заголовка
            font_size=dp(24),
            color=(0, 0, 0, 1)  # Черный цвет текста
        )
        title_container.add_widget(title)
        scroll_layout.add_widget(title_container)

        # Добавляем разделитель после заголовка
        scroll_layout.add_widget(Label(size_hint_y=None, height=dp(20)))

        # Vertical input layout for calibration
        calibration_layout = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(180), spacing=dp(10))

        # Pressure input
        pressure_label = Label(text='Давление:', size_hint_y=None, height=dp(30), font_size=dp(18), color=(0, 0, 0, 1))
        self.pressure_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            padding=[dp(10), dp(10), dp(10), 0],  # Добавлены отступы внутри поля
            background_color=(1, 1, 1, 1),  # Белый фон для контраста
            foreground_color=(0, 0, 0, 1)  # Черный текст
        )

        # Weight input
        weight_label = Label(text='Вес:', size_hint_y=None, height=dp(30), font_size=dp(18), color=(0, 0, 0, 1))
        self.weight_input = TextInput(
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            padding=[dp(10), dp(10), dp(10), 0],  # Добавлены отступы внутри поля
            background_color=(1, 1, 1, 1),  # Белый фон для контраста
            foreground_color=(0, 0, 0, 1)  # Черный текст
        )

        # Add button with improved style
        add_button = Button(
            text='Добавить точку',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            background_color=(0.2, 0.6, 1, 1),  # Синий цвет кнопки
            background_normal=''  # Убираем стандартный фон кнопки
        )
        add_button.bind(on_press=self.add_point)

        # Add widgets to calibration layout
        calibration_layout.add_widget(pressure_label)
        calibration_layout.add_widget(self.pressure_input)
        calibration_layout.add_widget(weight_label)
        calibration_layout.add_widget(self.weight_input)
        calibration_layout.add_widget(add_button)

        scroll_layout.add_widget(calibration_layout)

        # Calculation section with separator
        scroll_layout.add_widget(Label(size_hint_y=None, height=dp(20)))  # Разделитель

        calc_label = Label(
            text='Расчет веса:',
            size_hint_y=None,
            height=dp(30),
            font_size=dp(18),
            color=(0, 0, 0, 1)
        )
        scroll_layout.add_widget(calc_label)

        # Calculation input
        self.calc_pressure = TextInput(
            hint_text='Введите давление для расчета',
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            padding=[dp(10), dp(10), dp(10), 0],  # Добавлены отступы внутри поля
            background_color=(1, 1, 1, 1),  # Белый фон для контраста
            foreground_color=(0, 0, 0, 1)  # Черный текст
        )
        scroll_layout.add_widget(self.calc_pressure)

        calc_button = Button(
            text='Рассчитать',
            size_hint_y=None,
            height=dp(50),
            font_size=dp(18),
            background_color=(0.2, 0.6, 1, 1),  # Синий цвет кнопки
            background_normal=''  # Убираем стандартный фон кнопки
        )
        calc_button.bind(on_press=self.calculate)
        scroll_layout.add_widget(calc_button)

        # Results label with larger font and multiline support
        self.result_label = Label(
            text='',
            size_hint_y=None,
            height=dp(120),
            font_size=dp(18),
            halign='left',
            valign='middle',
            color=(0, 0, 0, 1)  # Черный цвет текста
        )
        self.result_label.bind(
            width=lambda *x: self.result_label.setter('text_size')(self.result_label, (self.result_label.width - dp(20), None)),
            texture_size=lambda *x: self.result_label.setter('height')(self.result_label, self.result_label.texture_size[1])
        )
        scroll_layout.add_widget(self.result_label)

        # Add ScrollView to main layout
        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(scroll_layout)
        self.add_widget(scroll)

    def add_point(self, instance):
        pressure = self.pressure_input.text
        weight = self.weight_input.text

        is_valid, error_message = validate_input(pressure, weight)
        if is_valid:
            if add_calibration_point(float(pressure), float(weight)):
                self.pressure_input.text = ''
                self.weight_input.text = ''
                self.result_label.text = 'Точка добавлена успешно'
            else:
                self.result_label.text = 'Ошибка при добавлении точки'
        else:
            self.result_label.text = error_message

    def calculate(self, instance):
        try:
            pressure = float(self.calc_pressure.text)
            points = get_all_points()

            is_valid, error_message = validate_points(points)
            if not is_valid:
                self.result_label.text = error_message
                return

            min_pressure = min(p[0] for p in points)
            max_pressure = max(p[0] for p in points)

            warning = ""
            if pressure < min_pressure or pressure > max_pressure:
                warning = (f"Внимание: значение давления ({pressure}) вне диапазона "
                          f"калибровки ({min_pressure:.1f} - {max_pressure:.1f})\n")

            if len(points) == 2:
                result = linear_interpolation(pressure, points)
                method = "линейная интерполяция"
            else:
                result = quadratic_interpolation(pressure, points)
                method = "квадратичная интерполяция"

            self.result_label.text = f"{warning}Расчетный вес: {result:.2f}\n({method})"

        except ValueError:
            self.result_label.text = "Введите корректное значение давления"

class WeightCalculatorApp(App):
    def build(self):
        # Set window size to smaller width
        Window.size = (360, 800)  # Увеличиваем ширину окна на 5px
        return WeightCalculatorLayout()

if __name__ == '__main__':
    Window.clearcolor = (0.98, 0.98, 0.98, 1)  # Почти белый фон
    WeightCalculatorApp().run()
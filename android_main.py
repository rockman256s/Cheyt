from kivy.metrics import dp
from kivy.core.window import Window
from kivy_garden.graph import Graph, MeshLinePlot
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRectangleFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard

from database import init_db, add_calibration_point, get_all_points
from interpolation import linear_interpolation, quadratic_interpolation, get_interpolation_curve
from utils import validate_input, validate_points

class WeightCalculatorScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize database
        init_db()

        # Main layout
        main_layout = MDBoxLayout(
            orientation='vertical',
            spacing=dp(16),
            padding=dp(16),
            md_bg_color=[0.92, 0.92, 0.92, 1]  # Light gray background
        )

        # Title with better contrast
        title = MDLabel(
            text="Калькулятор веса",
            font_style="H4",
            halign="center",
            theme_text_color="Primary",
            size_hint_y=None,
            height=dp(60)
        )
        main_layout.add_widget(title)

        # Input Section Card
        input_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(320),
            padding=dp(16),
            spacing=dp(10),
            radius=[dp(10)],
            elevation=2,
            md_bg_color=[1, 1, 1, 1]  # White background
        )

        # Input fields with better styling
        self.pressure_input = MDTextField(
            hint_text="Введите давление",
            helper_text="Обязательное поле",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(48),
            mode="rectangle",
            line_color_focus=[0.2, 0.6, 1, 1]  # Blue focus color
        )

        self.weight_input = MDTextField(
            hint_text="Введите вес",
            helper_text="Обязательное поле",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(48),
            mode="rectangle",
            line_color_focus=[0.2, 0.6, 1, 1]  # Blue focus color
        )

        # Add button with improved style
        add_button = MDRectangleFlatButton(
            text="Добавить точку",
            on_release=self.add_point,
            size_hint_x=1,
            height=dp(50),
            text_color=[0.2, 0.6, 1, 1]  # Blue text
        )

        # Add widgets to input card
        input_card.add_widget(MDLabel(text="Калибровка", font_style="H5", size_hint_y=None, height=dp(40)))
        input_card.add_widget(self.pressure_input)
        input_card.add_widget(self.weight_input)
        input_card.add_widget(add_button)

        main_layout.add_widget(input_card)

        # Graph Card with improved styling
        graph_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(300),
            padding=dp(16),
            spacing=dp(10),
            radius=[dp(10)],
            elevation=2,
            md_bg_color=[1, 1, 1, 1]
        )

        # Graph with better visuals
        self.graph = Graph(
            xlabel='Давление',
            ylabel='Вес',
            x_ticks_minor=5,
            x_ticks_major=1,
            y_ticks_minor=5,
            y_ticks_major=1,
            y_grid_label=True,
            x_grid_label=True,
            padding=5,
            x_grid=True,
            y_grid=True,
            xmin=0,
            xmax=10,
            ymin=0,
            ymax=10
        )

        graph_card.add_widget(MDLabel(text="График калибровки", font_style="H5", size_hint_y=None, height=dp(40)))
        graph_card.add_widget(self.graph)
        main_layout.add_widget(graph_card)

        # Calculation Card
        calc_card = MDCard(
            orientation='vertical',
            size_hint_y=None,
            height=dp(200),
            padding=dp(16),
            spacing=dp(10),
            radius=[dp(10)],
            elevation=2,
            md_bg_color=[1, 1, 1, 1]
        )

        # Calculation input with consistent styling
        self.calc_pressure = MDTextField(
            hint_text="Введите давление для расчета",
            helper_text="Обязательное поле",
            helper_text_mode="on_error",
            size_hint_y=None,
            height=dp(48),
            mode="rectangle",
            line_color_focus=[0.2, 0.6, 1, 1]  # Blue focus color
        )

        # Calculate button with consistent styling
        calc_button = MDRectangleFlatButton(
            text="Рассчитать",
            on_release=self.calculate,
            size_hint_x=1,
            height=dp(50),
            text_color=[0.2, 0.6, 1, 1]  # Blue text
        )

        # Result label
        self.result_label = MDLabel(
            text="",
            size_hint_y=None,
            height=dp(48),
            halign="center"
        )

        calc_card.add_widget(MDLabel(text="Расчет веса", font_style="H5", size_hint_y=None, height=dp(40)))
        calc_card.add_widget(self.calc_pressure)
        calc_card.add_widget(calc_button)
        calc_card.add_widget(self.result_label)

        main_layout.add_widget(calc_card)
        self.add_widget(main_layout)

    def add_point(self, instance):
        pressure = self.pressure_input.text
        weight = self.weight_input.text

        is_valid, error_message = validate_input(pressure, weight)
        if is_valid:
            if add_calibration_point(float(pressure), float(weight)):
                self.pressure_input.text = ''
                self.weight_input.text = ''
                self.update_graph()
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

            if len(points) == 2:
                result = linear_interpolation(pressure, points)
                method = "линейная интерполяция"
            else:
                result = quadratic_interpolation(pressure, points)
                method = "квадратичная интерполяция"

            self.result_label.text = f"Расчетный вес: {result:.2f} ({method})"

        except ValueError:
            self.result_label.text = "Введите корректное значение давления"

    def update_graph(self):
        self.graph.clear_plots()
        points = get_all_points()

        if points:
            # Update graph range
            pressures = [p[0] for p in points]
            weights = [p[1] for p in points]

            padding = 0.1
            p_range = max(pressures) - min(pressures) if len(pressures) > 1 else 1
            w_range = max(weights) - min(weights) if len(weights) > 1 else 1

            self.graph.xmin = max(0, min(pressures) - p_range * padding)
            self.graph.xmax = max(pressures) + p_range * padding
            self.graph.ymin = max(0, min(weights) - w_range * padding)
            self.graph.ymax = max(weights) + w_range * padding

            # Plot points with blue color
            plot = MeshLinePlot(color=[0.2, 0.6, 1, 1])  # Blue points
            plot.points = [(p[0], p[1]) for p in points]
            self.graph.add_plot(plot)

            # Plot interpolation curve with green color
            if len(points) >= 2:
                x_curve, y_curve = get_interpolation_curve(points)
                curve_plot = MeshLinePlot(color=[0.4, 0.8, 0.4, 1])  # Softer green
                curve_plot.points = list(zip(x_curve, y_curve))
                self.graph.add_plot(curve_plot)

class WeightCalculatorApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"
        return WeightCalculatorScreen()

if __name__ == '__main__':
    Window.size = (400, 800)
    WeightCalculatorApp().run()
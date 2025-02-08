from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.garden.graph import Graph, MeshLinePlot
from database import init_db, add_calibration_point, get_all_points
from interpolation import linear_interpolation, quadratic_interpolation, get_interpolation_curve
import numpy as np

class WeightCalculatorApp(App):
    def build(self):
        # Initialize database
        init_db()
        
        # Create main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Calibration inputs
        cal_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        self.pressure_input = TextInput(hint_text='Давление', multiline=False)
        self.weight_input = TextInput(hint_text='Вес', multiline=False)
        add_button = Button(text='Добавить точку')
        add_button.bind(on_press=self.add_point)
        
        cal_layout.add_widget(self.pressure_input)
        cal_layout.add_widget(self.weight_input)
        cal_layout.add_widget(add_button)
        
        # Graph
        self.graph = Graph(xlabel='Давление', ylabel='Вес',
                          x_ticks_minor=5, x_ticks_major=10,
                          y_ticks_minor=5, y_ticks_major=10,
                          y_grid_label=True, x_grid_label=True,
                          padding=5, size_hint_y=0.6)
        
        # Weight calculation
        calc_layout = BoxLayout(orientation='horizontal', size_hint_y=0.2)
        self.calc_input = TextInput(hint_text='Введите давление для расчета')
        calc_button = Button(text='Рассчитать')
        calc_button.bind(on_press=self.calculate_weight)
        self.result_label = Label(text='')
        
        calc_layout.add_widget(self.calc_input)
        calc_layout.add_widget(calc_button)
        calc_layout.add_widget(self.result_label)
        
        # Add all widgets to main layout
        layout.add_widget(cal_layout)
        layout.add_widget(self.graph)
        layout.add_widget(calc_layout)
        
        self.update_graph()
        return layout
    
    def add_point(self, instance):
        try:
            pressure = float(self.pressure_input.text)
            weight = float(self.weight_input.text)
            if add_calibration_point(pressure, weight):
                self.pressure_input.text = ''
                self.weight_input.text = ''
                self.update_graph()
        except ValueError:
            pass
    
    def update_graph(self):
        self.graph.remove_plot()
        points = get_all_points()
        if len(points) >= 2:
            x_curve, y_curve = get_interpolation_curve(points)
            plot = MeshLinePlot(color=[0, 1, 0, 1])
            plot.points = [(x, y) for x, y in zip(x_curve, y_curve)]
            self.graph.add_plot(plot)
            
            # Update graph range
            x_min = min(p[0] for p in points)
            x_max = max(p[0] for p in points)
            y_min = min(p[1] for p in points)
            y_max = max(p[1] for p in points)
            
            margin = 0.1
            x_range = x_max - x_min
            y_range = y_max - y_min
            
            self.graph.xmin = x_min - margin * x_range
            self.graph.xmax = x_max + margin * x_range
            self.graph.ymin = y_min - margin * y_range
            self.graph.ymax = y_max + margin * y_range
    
    def calculate_weight(self, instance):
        try:
            pressure = float(self.calc_input.text)
            points = get_all_points()
            if len(points) >= 2:
                if len(points) == 2:
                    result = linear_interpolation(pressure, points)
                else:
                    result = quadratic_interpolation(pressure, points)
                self.result_label.text = f'Вес: {result:.2f}'
            else:
                self.result_label.text = 'Недостаточно точек'
        except ValueError:
            self.result_label.text = 'Ошибка ввода'

if __name__ == '__main__':
    WeightCalculatorApp().run()

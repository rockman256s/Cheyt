import flet as ft
import numpy as np
from scipy import interpolate
import sqlite3
import os
from pathlib import Path
from datetime import datetime
import requests
from functools import lru_cache
import json

# Add Spanish translations to the TRANSLATIONS dictionary
TRANSLATIONS = {
    "en": {
        "app_title": "Weight Calculator",
        "title": "Weight Calculator Based on Pressure",
        "pressure": "Pressure",
        "weight": "Weight",
        "location": "Location",
        "date": "Date",
        "calculate": "Calculate Weight",
        "add_point": "Add Calibration Point",
        "calculation_history": "Calculation History",
        "calibration_curve": "Calibration Curve Graph",
        "calibration_points": "Calibration Points Table",
        "add_new_point": "Add New Calibration Point:",
        "edit": "Edit",
        "save": "Save",
        "cancel": "Cancel",
        "clear_history": "Clear History",
        "min_points_msg": "Add calibration points (minimum 2) to calculate weight based on pressure.",
        "error_numeric": "Error: enter numeric values",
        "point_added": "✅ Calibration point added",
        "point_error": "❌ Error adding point",
        "changes_saved": "✅ Changes saved",
        "changes_error": "❌ Error saving changes",
        "unknown": "Unknown",
        "navigation": "Navigation",
        "page": "Page",
        "of": "of",
        "next": "Next",
        "previous": "Previous"
    },
    "es": {
        "app_title": "Calculadora de peso",
        "title": "Calculadora de peso basada en presión",
        "pressure": "Presión",
        "weight": "Peso",
        "location": "Ubicación",
        "date": "Fecha",
        "calculate": "Calcular peso",
        "add_point": "Añadir punto de calibración",
        "calculation_history": "Historial de cálculos",
        "calibration_curve": "Gráfico de curva de calibración",
        "calibration_points": "Tabla de puntos de calibración",
        "add_new_point": "Añadir nuevo punto de calibración:",
        "edit": "Editar",
        "save": "Guardar",
        "cancel": "Cancelar",
        "clear_history": "Borrar historial",
        "min_points_msg": "Agregue puntos de calibración (mínimo 2) para calcular el peso según la presión.",
        "error_numeric": "Error: ingrese valores numéricos",
        "point_added": "✅ Punto de calibración añadido",
        "point_error": "❌ Error al añadir punto",
        "changes_saved": "✅ Cambios guardados",
        "changes_error": "❌ Error al guardar cambios",
        "unknown": "Desconocido",
        "navigation": "Navegación",
        "page": "Página",
        "of": "de",
        "next": "Siguiente",
        "previous": "Anterior"
    },
    "ru": {
        "app_title": "Калькулятор веса",
        "pressure": "Давление",
        "weight": "Вес",
        "location": "Местоположение",
        "date": "Дата",
        "calculate": "Рассчитать вес",
        "add_point": "Добавить точку калибровки",
        "calculation_history": "История расчетов",
        "calibration_curve": "График калибровочной кривой",
        "calibration_points": "Таблица калибровочных точек",
        "add_new_point": "Добавить новую точку калибровки:",
        "edit": "Редактировать",
        "save": "Сохранить",
        "cancel": "Отмена",
        "clear_history": "Очистить историю",
        "min_points_msg": "Добавьте калибровочные точки (минимум 2) для расчета веса на основе давления.",
        "error_numeric": "Ошибка: введите числовые значения",
        "point_added": "✅ Точка калибровки добавлена",
        "point_error": "❌ Ошибка добавления точки",
        "changes_saved": "✅ Изменения сохранены",
        "changes_error": "❌ Ошибка сохранения изменений",
        "unknown": "Неизвестно"
    },
    "uk": {
        "app_title": "Калькулятор ваги",
        "pressure": "Тиск",
        "weight": "Вага",
        "location": "Місцезнаходження",
        "date": "Дата",
        "calculate": "Розрахувати вагу",
        "add_point": "Додати точку калібрування",
        "calculation_history": "Історія розрахунків",
        "calibration_curve": "Графік калібрувальної кривої",
        "calibration_points": "Таблиця точок калібрування",
        "add_new_point": "Додати нову точку калібрування:",
        "edit": "Редагувати",
        "save": "Зберегти",
        "cancel": "Відміна",
        "clear_history": "Очистити історію",
        "min_points_msg": "Додайте точки калібрування (мінімум 2) для розрахунку ваги на основі тиску.",
        "error_numeric": "Помилка: введіть числові значення",
        "point_added": "✅ Точку калібрування додано",
        "point_error": "❌ Помилка додавання точки",
        "changes_saved": "✅ Зміни збережено",
        "changes_error": "❌ Помилка збереження змін",
        "unknown": "Невідомо"
    },
    "hi": {
        "app_title": "वजन कैलकुलेटर",
        "pressure": "दबाव",
        "weight": "वजन",
        "location": "स्थान",
        "date": "दिनांक",
        "calculate": "वजन की गणना करें",
        "add_point": "कैलिब्रेशन बिंदु जोड़ें",
        "calculation_history": "गणना इतिहास",
        "calibration_curve": "कैलिब्रेशन वक्र ग्राफ",
        "calibration_points": "कैलिब्रेशन बिंदु तालिका",
        "add_new_point": "नया कैलिब्रेशन बिंदु जोड़ें:",
        "edit": "संपादित करें",
        "save": "सहेजें",
        "cancel": "रद्द करें",
        "clear_history": "इतिहास साफ़ करें",
        "min_points_msg": "दबाव के आधार पर वजन की गणना के लिए कैलिब्रेशन बिंदु जोड़ें (न्यूनतम 2)।",
        "error_numeric": "त्रुटि: संख्यात्मक मान दर्ज करें",
        "point_added": "✅ कैलिब्रेशन बिंदु जोड़ा गया",
        "point_error": "❌ बिंदु जोड़ने में त्रुटि",
        "changes_saved": "✅ परिवर्तन सहेजे गए",
        "changes_error": "❌ परिवर्तन सहेजने में त्रुटि",
        "unknown": "अज्ञात"
    },
    "mo": {
        "app_title": "Calculator de greutate",
        "pressure": "Presiune",
        "weight": "Greutate",
        "location": "Locație",
        "date": "Data",
        "calculate": "Calculează greutatea",
        "add_point": "Adaugă punct de calibrare",
        "calculation_history": "Istoricul calculelor",
        "calibration_curve": "Graficul curbei de calibrare",
        "calibration_points": "Tabelul punctelor de calibrare",
        "add_new_point": "Adaugă punct nou de calibrare:",
        "edit": "Editează",
        "save": "Salvează",
        "cancel": "Anulează",
        "clear_history": "Șterge istoricul",
        "min_points_msg": "Adaugă puncte de calibrare (minim 2) pentru a calcula greutatea în baza presiunii.",
        "error_numeric": "Eroare: introduceți valori numerice",
        "point_added": "✅ Punct de calibrare adăugat",
        "point_error": "❌ Eroare la adăugarea punctului",
        "changes_saved": "✅ Modificări salvate",
        "changes_error": "❌ Eroare la salvarea modificărilor",
        "unknown": "Necunoscut"
    },
    "ky": {
        "app_title": "Салмак калькулятору",
        "pressure": "Басым",
        "weight": "Салмак",
        "location": "Жайгашуу",
        "date": "Күнү",
        "calculate": "Салмакты эсептөө",
        "add_point": "Калибрлөө чекитин кошуу",
        "calculation_history": "Эсептөөлөр тарыхы",
        "calibration_curve": "Калибрлөө ийри сызыгынын графиги",
        "calibration_points": "Калибрлөө чекиттеринин таблицасы",
        "add_new_point": "Жаңы калибрлөө чекитин кошуу:",
        "edit": "Түзөтүү",
        "save": "Сактоо",
        "cancel": "Жокко чыгаруу",
        "clear_history": "Тарыхты тазалоо",
        "min_points_msg": "Басымдын негизинде салмакты эсептөө үчүн калибрлөө чекиттерин кошуңуз (минимум 2).",
        "error_numeric": "Ката: сандык маанилерди киргизиңиз",
        "point_added": "✅ Калибрлөө чекити кошулду",
        "point_error": "❌ Чекитти кошууда ката кетти",
        "changes_saved": "✅ Өзгөртүүлөр сакталды",
        "changes_error": "❌ Өзгөртүүлөрдү сактоодо ката кетти",
        "unknown": "Белгисиз"
    },
    "uz": {
        "app_title": "Vazn kalkulyatori",
        "pressure": "Bosim",
        "weight": "Vazn",
        "location": "Joylashuv",
        "date": "Sana",
        "calculate": "Vaznni hisoblash",
        "add_point": "Kalibrlash nuqtasini qo'shish",
        "calculation_history": "Hisob-kitoblar tarixi",
        "calibration_curve": "Kalibrlash egri chizig'i grafigi",
        "calibration_points": "Kalibrlash nuqtalari jadvali",
        "add_new_point": "Yangi kalibrlash nuqtasini qo'shish:",
        "edit": "Tahrirlash",
        "save": "Saqlash",
        "cancel": "Bekor qilish",
        "clear_history": "Tarixni tozalash",
        "min_points_msg": "Bosim asosida vaznni hisoblash uchun kalibrlash nuqtalarini qo'shing (minimum 2).",
        "error_numeric": "Xato: raqamli qiymatlarni kiriting",
        "point_added": "✅ Kalibrlash nuqtasi qo'shildi",
        "point_error": "❌ Nuqta qo'shishda xato",
        "changes_saved": "✅ O'zgarishlar saqlandi",
        "changes_error": "❌ O'zgarishlarni saqlashda xato",
        "unknown": "Noma'lum"
    }
}

class WeightCalculator:
    def __init__(self, page: ft.Page):
        self.calibration_points = []
        self.db_path = str(Path.home() / "calibration.db")
        self.client_ip = get_client_ip(page)
        self.current_location = get_location_fallback(self.client_ip)
        self.current_page = 1
        self.items_per_page = 30
        self.current_language = "en"  # Default language
        self.init_db()
        self.load_points()

    def init_db(self):
        """Initialize database with proper schema"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            c.execute('''CREATE TABLE IF NOT EXISTS calibration_points
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         pressure REAL NOT NULL,
                         weight REAL NOT NULL)''')

            c.execute('''CREATE TABLE IF NOT EXISTS weight_history
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         date TEXT NOT NULL,
                         pressure REAL NOT NULL,
                         weight REAL NOT NULL,
                         location TEXT)''')

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
            self.calibration_points = self.load_points()
            return True
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

            if len(self.calibration_points) == 2:
                f = interpolate.interp1d(pressures, weights, kind='linear', fill_value='extrapolate')
            else:
                f = interpolate.interp1d(pressures, weights, kind='quadratic', fill_value='extrapolate')

            return float(f(pressure))
        except Exception as e:
            print(f"Ошибка расчета веса: {str(e)}")
            return None

    def save_calculation(self, pressure, weight):
        """Save calculation to history"""
        try:
            location = self.current_location

            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""INSERT INTO weight_history (date, pressure, weight, location)
                        VALUES (?, ?, ?, ?)""",
                     (datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                      pressure, weight, location))
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка сохранения расчета: {str(e)}")
            return False

    def get_calculation_history(self, page=1):
        """Get calculation history with pagination"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()

            # Получаем общее количество записей
            c.execute("SELECT COUNT(*) FROM weight_history")
            total_records = c.fetchone()[0]

            # Вычисляем смещение для текущей страницы
            offset = (page - 1) * self.items_per_page

            c.execute("""SELECT date, pressure, weight, location 
                        FROM weight_history 
                        ORDER BY date DESC 
                        LIMIT ? OFFSET ?""",
                     (self.items_per_page, offset))
            history = c.fetchall()
            conn.close()
            return history, total_records
        except sqlite3.Error as e:
            print(f"Ошибка получения истории: {str(e)}")
            return [], 0

    def clear_history(self):
        """Clear calculation history"""
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("DELETE FROM weight_history")
            conn.commit()
            conn.close()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка очистки истории: {str(e)}")
            return False


def get_client_ip(page: ft.Page) -> str:
    """Get client IP address from Flet page"""
    try:
        return page.client_ip if page.client_ip else None
    except Exception as e:
        print(f"Ошибка получения IP клиента: {str(e)}")
        return None

@lru_cache(maxsize=1)
def get_location_fallback(client_ip=None):
    """Get location based on client IP"""
    try:
        # Используем несколько сервисов с приоритетом точности
        services = [
            {
                'url': f'https://ipapi.co/{client_ip}/json/' if client_ip else 'https://ipapi.co/json/',
                'priority': 1,
                'fields': {'city': 'city', 'region': 'region', 'country': 'country_name'}
            },
            {
                'url': f'https://ipwho.is/{client_ip}' if client_ip else 'https://ipwho.is/',
                'priority': 2,
                'fields': {'city': 'city', 'region': 'region', 'country': 'country'}
            },
            {
                'url': f'https://ip-api.com/json/{client_ip}' if client_ip else 'https://ip-api.com/json/',
                'priority': 3,
                'fields': {'city': 'city', 'region': 'regionName', 'country': 'country'}
            }
        ]

        print(f"Определение местоположения для IP: {client_ip}")

        for service in services:
            try:
                response = requests.get(
                    service['url'],
                    timeout=5,
                    headers={
                        'User-Agent': 'Mozilla/5.0',
                        'Accept': 'application/json'
                    }
                )

                if response.status_code == 200:
                    data = response.json()
                    print(f"Ответ от {service['url']}: {data}")
                    location_parts = []
                    fields = service['fields']

                    # Получаем и проверяем каждую часть адреса
                    city = data.get(fields['city'])
                    region = data.get(fields['region'])
                    country = data.get(fields['country'])

                    # Валидация данных
                    if city and len(city) > 1 and not city.isdigit():
                        location_parts.append(city)
                    if region and len(region) > 1 and not region.isdigit():
                        location_parts.append(region)
                    if country and len(country) > 1 and not country.isdigit():
                        location_parts.append(country)

                    if location_parts:
                        result = ', '.join(location_parts)
                        print(f"Определено местоположение: {result}")
                        return result

            except Exception as e:
                print(f"Ошибка сервиса {service['url']}: {str(e)}")
                continue

    except Exception as e:
        print(f"Общая ошибка определения местоположения: {str(e)}")
    return "Неизвестно"

def main(page: ft.Page):
    page.title = "Weight Calculator"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10 if page.width < 600 else 20
    page.theme = ft.Theme(color_scheme_seed=ft.colors.BLUE)

    calc = WeightCalculator(page)
    current_language = "en"  # Default language

    def get_text(key):
        return TRANSLATIONS.get(current_language, TRANSLATIONS["en"]).get(key, key)

    def change_language(e):
        nonlocal current_language
        current_language = e.control.value
        update_texts()
        update_display()

    # Update the language dropdown options to include Spanish
    language_dropdown = ft.Dropdown(
        width=200,
        options=[
            ft.dropdown.Option("en", "English"),
            ft.dropdown.Option("es", "Español"),
            ft.dropdown.Option("ru", "Русский"),
            ft.dropdown.Option("uk", "Українська"),
            ft.dropdown.Option("hi", "हिंदी"),
            ft.dropdown.Option("mo", "Română"),
            ft.dropdown.Option("ky", "Кыргызча"),
            ft.dropdown.Option("uz", "O'zbek"),
        ],
        value=current_language,
        on_change=change_language,
    )

    def update_texts():
        page.title = get_text("app_title")
        pressure_input.label = get_text("pressure")
        weight_input.label = get_text("weight")
        result_text.value = ""
        add_button.text = get_text("add_point")
        add_calibration_point_text.value = get_text("add_new_point")
        calculation_history_text.value = get_text("calculation_history")
        calibration_curve_text.value = get_text("calibration_curve")
        calibration_points_text.value = get_text("calibration_points")
        edit_button.text = get_text("edit")
        save_button.text = get_text("save")
        clear_history_button.text = get_text("clear_history")
        min_points_msg.value = get_text("min_points_msg")
        page.update()


    editing_mode = False
    edited_values = {}

    def get_size(default, mobile):
        return mobile if page.width < 600 else default

    def toggle_edit_mode(e):
        nonlocal editing_mode
        editing_mode = not editing_mode
        if not editing_mode:
            edited_values.clear()
        update_display()

    def save_changes(e):
        nonlocal editing_mode
        try:
            for point_id, new_values in edited_values.items():
                if not calc.edit_point(point_id, new_values['pressure'], new_values['weight']):
                    result_text.value = get_text("changes_error")
                    result_text.color = ft.colors.RED
                    page.update()
                    return

            result_text.value = get_text("changes_saved")
            result_text.color = ft.colors.GREEN
            editing_mode = False
            edited_values.clear()
            update_display()
        except Exception as e:
            result_text.value = f"❌ Error: {str(e)}"
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
            result_text.value = get_text("point_added")
            result_text.color = ft.colors.GREEN
            update_display()
        else:
            result_text.value = get_text("point_error")
            result_text.color = ft.colors.RED
            page.update()

    def create_data_table():
        points = calc.load_points()
        if not points:
            return ft.Text(get_text("point_error"))

        table = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(get_text("edit"), width=50, size=14),
                            ft.Text(get_text("pressure"), width=100, size=14),
                            ft.Text(get_text("weight"), width=100, size=14),
                            ft.Text("", width=30),
                        ],
                        spacing=0,
                    ),
                    padding=10,
                    bgcolor=ft.colors.BLUE_50,
                ),
            ],
            spacing=2,
        )

        for point in points:
            if editing_mode:
                row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"{point[0]}", width=50, size=14),
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
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.icons.DELETE_FOREVER,
                                    icon_color=ft.colors.RED_500,
                                    width=30,
                                    icon_size=24,
                                    tooltip=get_text("clear_history"),
                                    on_click=lambda e, pid=point[0]: delete_point(pid),
                                ),
                                margin=ft.margin.only(left=-12),
                            ),
                        ],
                        spacing=0,
                    ),
                    padding=5,
                )
            else:
                row = ft.Container(
                    content=ft.Row(
                        [
                            ft.Text(f"{point[0]}", width=50, size=14),
                            ft.Text(f"{point[1]:.2f}", width=100, size=14),
                            ft.Text(f"{point[2]:.2f}", width=100, size=14),
                            ft.Container(
                                content=ft.IconButton(
                                    icon=ft.icons.DELETE_FOREVER,
                                    icon_color=ft.colors.RED_500,
                                    width=30,
                                    icon_size=24,
                                    tooltip=get_text("clear_history"),
                                    on_click=lambda e, pid=point[0]: delete_point(pid),
                                ),
                                margin=ft.margin.only(left=-12),
                            ),

                        ],
                        spacing=0,
                    ),
                    padding=5,
                )
            table.controls.append(row)

        buttons = ft.Row(
            [
                ft.ElevatedButton(
                    get_text("edit") if not editing_mode else get_text("cancel"),
                    on_click=toggle_edit_mode,
                ),
                ft.ElevatedButton(
                    get_text("save"),
                    visible=editing_mode,
                    on_click=save_changes,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10,
        )

        return ft.Column([table, buttons], spacing=20)

    pressure_input = ft.TextField(
        label=get_text("pressure"),
        width=get_size(400, page.width * 0.9),
        text_align=ft.TextAlign.LEFT,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    calibration_pressure_input = ft.TextField(
        label=get_text("pressure"),
        width=get_size(400, page.width * 0.9),
        text_align=ft.TextAlign.LEFT,
        keyboard_type=ft.KeyboardType.NUMBER,
    )

    weight_input = ft.TextField(
        label=get_text("weight"),
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
            return ft.Text(get_text("min_points_msg"))

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
                    title=ft.Text(get_text("weight")),
                    labels_size=50,
                ),
                bottom_axis=ft.ChartAxis(
                    title=ft.Text(get_text("pressure")),
                    labels_size=50,
                ),
            )

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
            pressure = float(calibration_pressure_input.value)
            weight = float(weight_input.value)

            if calc.add_point(pressure, weight):
                result_text.value = get_text("point_added")
                result_text.color = ft.colors.GREEN
                calibration_pressure_input.value = ""
                weight_input.value = ""
                update_display()
            else:
                result_text.value = get_text("point_error")
                result_text.color = ft.colors.RED
            page.update()
        except ValueError:
            result_text.value = get_text("error_numeric")
            result_text.color = ft.colors.RED
            page.update()

    def calculate_result(e):
        try:
            pressure = float(pressure_input.value)
            result = calc.calculate_weight(pressure)

            if result is not None:
                calc.save_calculation(pressure, result)
                result_text.value = f"Расчетный вес: {result:.2f}"
                result_text.color = ft.colors.BLACK
                history_container.content = create_history_table()
            else:
                result_text.value = get_text("min_points_msg")
                result_text.color = ft.colors.RED
            page.update()
        except ValueError:
            result_text.value = get_text("error_numeric")
            result_text.color = ft.colors.RED
            page.update()

    def create_history_table():
        history, total_records = calc.get_calculation_history(calc.current_page)
        if not history:
            return ft.Column([
                ft.Text(get_text("calculation_history")),
                ft.ElevatedButton(
                    get_text("clear_history"),
                    on_click=clear_history,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.RED_400,
                    ),
                ),
            ])

        # Update navigation text
        navigation_row = ft.Row(
            [
                ft.IconButton(
                    icon=ft.icons.ARROW_BACK,
                    on_click=lambda e: change_page(-1),
                    disabled=calc.current_page == 1,
                ),
                ft.Text(
                    f"{get_text('page')} {calc.current_page} {get_text('of')} {(total_records - 1) // calc.items_per_page + 1}"
                ),
                ft.IconButton(
                    icon=ft.icons.ARROW_FORWARD,
                    on_click=lambda e: change_page(1),
                    disabled=calc.current_page * calc.items_per_page >= total_records,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        return ft.Column(
            [
                ft.Text(
                    get_text("title"),
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    text_align=ft.TextAlign.CENTER,
                ),
                create_data_table(),
                navigation_row,
                ft.ElevatedButton(
                    get_text("clear_history"),
                    on_click=clear_history,
                    style=ft.ButtonStyle(
                        color=ft.colors.WHITE,
                        bgcolor=ft.colors.RED_400,
                    ),
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20,
        )

    def change_page(delta):
        calc.current_page += delta
        history_container.content = create_history_table()
        page.update()

    def clear_history(e):
        if calc.clear_history():
            result_text.value = get_text("changes_saved")
            result_text.color = ft.colors.GREEN
            calc.current_page = 1
            history_container.content = create_history_table()
        else:
            result_text.value = get_text("changes_error")
            result_text.color = ft.colors.RED
        page.update()

    add_button = ft.ElevatedButton(
        get_text("add_point"),
        width=get_size(400, page.width * 0.9),
        on_click=add_calibration_point,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
            shape=ft.RoundedRectangleBorder(radius=8),
        )
    )

    calculate_button = ft.ElevatedButton(
        content=ft.Row(
            [
                ft.Icon(name=ft.icons.CALCULATE, color=ft.colors.WHITE),
                ft.Text(get_text("calculate"), color=ft.colors.WHITE, size=16),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        width=get_size(400, page.width * 0.9),
        on_click=calculate_result,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE,
        ),
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

    history_container = ft.Container(
        content=create_history_table(),
        padding=10,
        border=ft.border.all(1, ft.colors.GREY_400),
        border_radius=10,
        margin=ft.margin.only(top=20, bottom=20),
    )

    def on_resize(e):
        pressure_input.width = get_size(400, page.width * 0.9)
        weight_input.width = get_size(400, page.width * 0.9)
        add_button.width = get_size(400, page.width * 0.9)
        calculate_button.width = get_size(400, page.width * 0.9)
        chart_container.height = get_size(400, 300)
        page.update()

    page.on_resize = on_resize

    def on_view_pop(view):
        try:
            calc.current_location = get_location_fallback(calc.client_ip)
            page.update()
        except Exception as e:
            print(f"Ошибка обработки местоположения: {str(e)}")
            calc.current_location = get_location_fallback(calc.client_ip)
            page.update()

    page.on_view_pop = on_view_pop


    add_calibration_point_text = ft.Text(
        get_text("add_new_point"),
        size=16,
        weight=ft.FontWeight.BOLD
    )
    calculation_history_text = ft.Text(
        get_text("calculation_history"),
        size=get_size(20, 16),
        weight=ft.FontWeight.BOLD
    )
    calibration_curve_text = ft.Text(
        get_text("calibration_curve"),
        size=get_size(20, 16),
        weight=ft.FontWeight.BOLD
    )
    calibration_points_text = ft.Text(
        get_text("calibration_points"),
        size=get_size(20, 16),
        weight=ft.FontWeight.BOLD
    )
    min_points_msg = ft.Text(
        get_text("min_points_msg"),
        size=get_size(16, 14),
        text_align=ft.TextAlign.CENTER,
    )
    edit_button = ft.ElevatedButton(
        get_text("edit"),
        on_click=toggle_edit_mode
    )
    save_button = ft.ElevatedButton(
        get_text("save"),
        visible=editing_mode,
        on_click=save_changes
    )
    clear_history_button = ft.ElevatedButton(
        get_text("clear_history"),
        on_click=clear_history
    )

    page.add(
        ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(
                        get_text("app_title"),
                        size=get_size(24, 20),
                        weight=ft.FontWeight.BOLD,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(get_text("title"), size=get_size(18, 16)), # Added title
                    min_points_msg,
                    ft.Divider(height=20),
                    pressure_input,
                    calculate_button,
                    result_text,
                    ft.Divider(height=20),
                    calculation_history_text,
                    history_container,
                    ft.Divider(height=20),
                    calibration_curve_text,
                    chart_container,
                    ft.Divider(height=20),
                    calibration_points_text,
                    ft.Container(
                        content=ft.Column([
                            add_calibration_point_text,
                            calibration_pressure_input,
                            weight_input,
                            add_button,
                        ]),
                        padding=10,
                        border=ft.border.all(1, ft.colors.GREY_400),
                        border_radius=10,
                        margin=ft.margin.only(bottom=20),
                    ),
                    data_table_container,
                    language_dropdown,
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
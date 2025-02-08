import streamlit as st
import pandas as pd
import numpy as np
from database import init_db, add_calibration_point, get_all_points, clear_all_points
from interpolation import linear_interpolation, quadratic_interpolation, get_interpolation_curve

def main():
    st.title("Калькулятор веса")

    # Инициализация базы данных
    init_db()

    # Добавление новой точки калибровки
    st.header("Калибровка")
    col1, col2 = st.columns(2)

    with col1:
        pressure = st.number_input("Давление:", min_value=0.0, format="%.2f")
    with col2:
        weight = st.number_input("Вес:", min_value=0.0, format="%.2f")

    if st.button("Добавить точку"):
        if add_calibration_point(pressure, weight):
            st.success("Точка калибровки добавлена")
        else:
            st.error("Ошибка при добавлении точки")

    # Получаем точки калибровки
    points = get_all_points()

    if points:
        # Таблица данных
        st.header("Данные калибровки")
        df = pd.DataFrame(points, columns=['Давление', 'Вес'])
        st.dataframe(
            df.style.format({
                'Давление': '{:.2f}',
                'Вес': '{:.2f}'
            }),
            hide_index=True,
            height=min(len(points) * 35 + 38, 250)
        )

        # График калибровки
        if len(points) >= 2:
            st.header("График калибровки")
            try:
                # Получаем точки для кривой
                x_curve, y_curve = get_interpolation_curve(points, num_points=200)

                # Создаем единый DataFrame для графика
                curve_data = pd.DataFrame({
                    'Давление': x_curve,
                    'Вес': y_curve,
                    'Тип': ['Кривая'] * len(x_curve)
                })

                points_data = pd.DataFrame({
                    'Давление': [p[0] for p in points],
                    'Вес': [p[1] for p in points],
                    'Тип': ['Точка'] * len(points)
                })

                # Объединяем данные
                plot_data = pd.concat([curve_data, points_data])

                # Отображаем один график с кривой и точками
                st.scatter_chart(
                    data=plot_data,
                    x='Давление',
                    y='Вес',
                    color='Тип',
                    size=[0.1 if t == 'Кривая' else 1 for t in plot_data['Тип']]
                )

                # Расчет веса
                st.header("Расчет веса")
                input_pressure = st.number_input(
                    "Введите давление для расчета:",
                    min_value=0.0,
                    format="%.2f"
                )

                if st.button("Рассчитать"):
                    try:
                        if len(points) == 2:
                            result = linear_interpolation(input_pressure, points)
                        else:
                            result = quadratic_interpolation(input_pressure, points)
                        st.success(f"Расчетный вес: {result:.2f}")
                    except Exception as e:
                        st.error(f"Ошибка при расчете: {str(e)}")
            except Exception as e:
                st.error(f"Ошибка при построении графика: {str(e)}")
        else:
            st.info("Добавьте еще точки для построения графика")
    else:
        st.info("Добавьте точки калибровки для начала работы")

    # Кнопка очистки данных
    if st.button("Очистить все точки"):
        if clear_all_points():
            st.success("Все точки калибровки удалены")
        else:
            st.error("Ошибка при удалении точек")

if __name__ == '__main__':
    main()
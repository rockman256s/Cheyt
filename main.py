import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
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
                x_curve, y_curve = get_interpolation_curve(points, num_points=500)

                # Создаем DataFrame для кривой
                curve_df = pd.DataFrame({
                    'Давление': x_curve,
                    'Вес': y_curve
                })

                # Создаем график с кривой
                chart = alt.Chart(curve_df).mark_line(
                    color='blue',
                    strokeWidth=2
                ).encode(
                    x=alt.X('Давление', title='Давление'),
                    y=alt.Y('Вес', title='Вес')
                )

                # Добавляем точки калибровки
                points_df = pd.DataFrame(points, columns=['Давление', 'Вес'])
                points_chart = alt.Chart(points_df).mark_circle(
                    color='red',
                    size=100
                ).encode(
                    x='Давление',
                    y='Вес'
                )

                # Комбинируем кривую и точки
                final_chart = (chart + points_chart).interactive()
                st.altair_chart(final_chart, use_container_width=True)

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
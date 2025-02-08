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

    # Отображение графика калибровки и таблицы данных
    points = get_all_points()
    if len(points) > 0:
        st.header("Данные калибровки")

        # Создаем DataFrame для точек калибровки
        points_df = pd.DataFrame(points, columns=['Давление', 'Вес'])

        # Отображаем таблицу данных
        st.dataframe(
            points_df,
            column_config={
                "Давление": st.column_config.NumberColumn(format="%.2f"),
                "Вес": st.column_config.NumberColumn(format="%.2f")
            },
            hide_index=True
        )

        st.header("График калибровки")
        if len(points) >= 2:
            # Получаем точки для линии интерполяции
            x_curve, y_curve = get_interpolation_curve(points)

            # Создаем единый DataFrame для графика
            chart_df = pd.DataFrame({
                'Давление': np.concatenate([x_curve, [p[0] for p in points]]),
                'Вес': np.concatenate([y_curve, [p[1] for p in points]]),
                'Тип': ['Линия'] * len(x_curve) + ['Точка'] * len(points)
            })

            # Отображаем единый график
            st.scatter_chart(
                data=chart_df,
                x='Давление',
                y='Вес',
                color='Тип',
                size='Тип'
            )

            # Расчет веса
            st.header("Расчет веса")
            input_pressure = st.number_input(
                "Введите давление для расчета:", 
                min_value=0.0,
                format="%.2f"
            )

            if st.button("Рассчитать"):
                if len(points) == 2:
                    result = linear_interpolation(input_pressure, points)
                else:
                    result = quadratic_interpolation(input_pressure, points)
                st.success(f"Расчетный вес: {result:.2f}")
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
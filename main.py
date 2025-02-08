import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from scipy import interpolate

def get_interpolation_curve(df):
    if len(df) >= 2:
        # Sort points by pressure
        df_sorted = df.sort_values('pressure')

        # Create interpolation function
        if len(df) == 2:
            # Linear interpolation for 2 points
            f = interpolate.interp1d(df_sorted['pressure'], df_sorted['weight'], 
                                   kind='linear', fill_value='extrapolate')
        else:
            # Quadratic interpolation for 3+ points
            f = interpolate.interp1d(df_sorted['pressure'], df_sorted['weight'], 
                                   kind='quadratic', fill_value='extrapolate')

        # Generate points for smooth curve
        x_new = np.linspace(df_sorted['pressure'].min(), df_sorted['pressure'].max(), 100)
        y_new = f(x_new)

        return pd.DataFrame({'pressure': x_new, 'weight': y_new})
    return pd.DataFrame(columns=['pressure', 'weight'])

def main():
    st.set_page_config(page_title="Калькулятор веса", layout="centered")

    # Основной заголовок
    st.title("Калькулятор веса на основе давления")

    # Описание функциональности
    st.write("Добавьте калибровочные точки (минимум 2) для расчета веса на основе давления. При "
             "наличии двух точек используется линейная интерполяция, при большем количестве - "
             "квадратичная.")

    # Initialize session state for storing calibration points
    if 'calibration_points' not in st.session_state:
        st.session_state.calibration_points = pd.DataFrame(columns=['pressure', 'weight'])

    # Calibration section
    st.header("Калибровочные данные")

    # Create a form for calibration inputs
    with st.form("calibration_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            pressure = st.number_input("Давление:", 
                                     min_value=0.0, 
                                     step=0.1,
                                     format="%.2f")
        with col2:
            weight = st.number_input("Вес:", 
                                   min_value=0.0,
                                   step=0.1,
                                   format="%.2f")

        submitted = st.form_submit_button("Добавить точку калибровки")

        if submitted:
            new_point = pd.DataFrame({'pressure': [pressure], 'weight': [weight]})
            st.session_state.calibration_points = pd.concat(
                [st.session_state.calibration_points, new_point], 
                ignore_index=True
            )
            st.success("✅ Точка калибровки добавлена")

    # Display calibration points and graph
    if not st.session_state.calibration_points.empty:
        st.subheader("График калибровочной кривой")

        # Create base scatter plot for calibration points
        points_chart = alt.Chart(st.session_state.calibration_points).mark_circle(
            size=100,
            color='#1f77b4'
        ).encode(
            x=alt.X('pressure:Q', title='Давление'),
            y=alt.Y('weight:Q', title='Вес'),
            tooltip=['pressure:Q', 'weight:Q']
        ).properties(
            width=600,
            height=400
        )

        # Add interpolation curve if we have enough points
        if len(st.session_state.calibration_points) >= 2:
            curve_data = get_interpolation_curve(st.session_state.calibration_points)
            curve_chart = alt.Chart(curve_data).mark_line(
                color='red'
            ).encode(
                x='pressure:Q',
                y='weight:Q'
            )
            # Combine points and curve
            chart = (points_chart + curve_chart)
        else:
            chart = points_chart

        st.altair_chart(chart, use_container_width=True)

        # Display calibration points in a table
        st.subheader("Текущие точки калибровки")
        st.dataframe(
            st.session_state.calibration_points.style.format({
                'pressure': '{:.2f}',
                'weight': '{:.2f}'
            })
        )

        # Add calculation section if we have enough points
        if len(st.session_state.calibration_points) >= 2:
            st.header("Расчет веса")
            pressure_to_calc = st.number_input(
                "Введите давление для расчета:",
                min_value=0.0,
                step=0.1,
                format="%.2f"
            )

            if st.button("Рассчитать вес"):
                curve_data = get_interpolation_curve(st.session_state.calibration_points)
                f = interpolate.interp1d(
                    curve_data['pressure'],
                    curve_data['weight'],
                    kind='linear',
                    fill_value='extrapolate'
                )
                calculated_weight = float(f(pressure_to_calc))
                st.success(f"Расчетный вес: {calculated_weight:.2f}")

if __name__ == "__main__":
    main()
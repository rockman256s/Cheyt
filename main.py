import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from scipy import interpolate
import sys
from pathlib import Path

# Add src directory to Python path.  This might be unnecessary without the database and interpolation functions.
sys.path.append(str(Path(__file__).parent / 'src'))
#from weight_calculator.database import init_db, add_calibration_point, get_all_points, clear_all_points
#from weight_calculator.interpolation import linear_interpolation, quadratic_interpolation, get_interpolation_curve


def main():
    st.title("Прогноз веса")
    st.write("Добро пожаловать в приложение для прогнозирования веса!")

    # Initialize session state for storing calibration points
    if 'calibration_points' not in st.session_state:
        st.session_state.calibration_points = pd.DataFrame(columns=['pressure', 'weight'])

    # Calibration section
    st.header("Калибровка")
    with st.form("calibration_form"):
        pressure = st.number_input("Введите давление:", min_value=0.0, format="%.2f")
        weight = st.number_input("Введите вес:", min_value=0.0, format="%.2f")
        submitted = st.form_submit_button("Добавить точку калибровки")

        if submitted:
            new_point = pd.DataFrame({'pressure': [pressure], 'weight': [weight]})
            st.session_state.calibration_points = pd.concat([st.session_state.calibration_points, new_point], ignore_index=True)
            st.success("Точка калибровки добавлена")

    # Display calibration points
    if not st.session_state.calibration_points.empty:
        st.subheader("Текущие точки калибровки")
        st.dataframe(st.session_state.calibration_points)

        # Create visualization
        chart = alt.Chart(st.session_state.calibration_points).mark_circle().encode(
            x='pressure:Q',
            y='weight:Q',
            tooltip=['pressure', 'weight']
        ).properties(
            width=600,
            height=400,
            title='График калибровки'
        )
        st.altair_chart(chart)

if __name__ == "__main__":
    main()
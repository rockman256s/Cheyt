import streamlit as st
import plotly.graph_objects as go
import pandas as pd

from interpolation import linear_interpolation, quadratic_interpolation, get_interpolation_curve
from utils import validate_input, validate_points
from database import init_db, add_calibration_point, get_all_points, clear_all_points

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="Калькулятор веса",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for mobile optimization
st.markdown("""
    <style>
        .stButton > button {
            width: 100%;
            height: 3rem;
            margin-top: 1rem;
        }
        .stNumberInput > div > div > input {
            height: 3rem;
        }
        @media (max-width: 640px) {
            .main > div {
                padding-left: 0.5rem;
                padding-right: 0.5rem;
            }
        }
    </style>
""", unsafe_allow_html=True)

st.title("Калькулятор веса")

# Calibration section in a card-like container
with st.container():
    st.markdown("""
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem;'>
            <h3>Калибровка</h3>
        </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        pressure = st.number_input("Давление:", 
                                 min_value=0.0, 
                                 format="%.2f",
                                 help="Введите значение давления")
    with col2:
        weight = st.number_input("Вес:", 
                               min_value=0.0, 
                               format="%.2f",
                               help="Введите значение веса")

    if st.button("Добавить точку", use_container_width=True):
        is_valid, error_message = validate_input(str(pressure), str(weight))
        if is_valid:
            if add_calibration_point(pressure, weight):
                st.success("✅ Точка добавлена успешно")
            else:
                st.error("❌ Ошибка при добавлении точки")
        else:
            st.error(error_message)

# Display current calibration points
points = get_all_points()
if points:
    st.markdown("""
        <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;'>
            <h3>Текущие точки калибровки</h3>
        </div>
    """, unsafe_allow_html=True)

    df = pd.DataFrame(points, columns=["Давление", "Вес"])
    st.dataframe(df, use_container_width=True)

    # Plot calibration curve with mobile-optimized layout
    x_curve, y_curve = get_interpolation_curve(points)
    fig = go.Figure()

    # Add calibration points
    fig.add_trace(go.Scatter(
        x=[p[0] for p in points],
        y=[p[1] for p in points],
        mode='markers',
        name='Точки калибровки',
        marker=dict(size=10)
    ))

    # Add interpolation curve
    fig.add_trace(go.Scatter(
        x=x_curve,
        y=y_curve,
        mode='lines',
        name='Кривая интерполяции',
        line=dict(width=2)
    ))

    fig.update_layout(
        title="График калибровки",
        xaxis_title="Давление",
        yaxis_title="Вес",
        height=300,  # Уменьшенная высота для мобильных устройств
        margin=dict(l=10, r=10, t=40, b=10),  # Уменьшенные отступы
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        showlegend=True
    )
    st.plotly_chart(fig, use_container_width=True)

# Weight calculation section
st.markdown("""
    <div style='background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-top: 1rem;'>
        <h3>Расчет веса</h3>
    </div>
""", unsafe_allow_html=True)

calc_pressure = st.number_input("Введите давление для расчета:", 
                              format="%.2f",
                              help="Введите значение давления для расчета веса")

if st.button("Рассчитать", use_container_width=True):
    if points:
        is_valid, error_message = validate_points(points)
        if is_valid:
            if len(points) == 2:
                result = linear_interpolation(calc_pressure, points)
                method = "линейная интерполяция"
            else:
                result = quadratic_interpolation(calc_pressure, points)
                method = "квадратичная интерполяция"

            st.success(f"💫 Расчетный вес: {result:.2f} ({method})")

            # Check if extrapolating
            min_pressure = min(p[0] for p in points)
            max_pressure = max(p[0] for p in points)
            if calc_pressure < min_pressure or calc_pressure > max_pressure:
                st.warning(f"⚠️ Внимание: значение давления ({calc_pressure}) вне диапазона калибровки ({min_pressure:.1f} - {max_pressure:.1f})")
        else:
            st.error(error_message)
    else:
        st.error("❌ Добавьте точки калибровки")

# Clear calibration with confirmation dialog
if st.button("Очистить калибровку", use_container_width=True):
    if st.button("⚠️ Подтвердить очистку", use_container_width=True):
        if clear_all_points():
            st.success("🗑️ Калибровка очищена")
        else:
            st.error("❌ Ошибка при очистке калибровки")
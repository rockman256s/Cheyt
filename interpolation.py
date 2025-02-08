import numpy as np
from typing import List, Tuple

def linear_interpolation(x: float, points: List[Tuple[float, float]]) -> float:
    """
    Perform linear interpolation/extrapolation for given pressure value

    Args:
        x: pressure value to interpolate
        points: list of (pressure, weight) calibration points

    Returns:
        Interpolated/extrapolated weight value
    """
    x_values = np.array([p[0] for p in points])
    y_values = np.array([p[1] for p in points])

    # Linear extrapolation using first and last points
    coefficients = np.polyfit(x_values, y_values, 1)
    return np.polyval(coefficients, x)

def quadratic_interpolation(x: float, points: List[Tuple[float, float]]) -> float:
    """
    Perform quadratic interpolation/extrapolation for given pressure value

    Args:
        x: pressure value to interpolate
        points: list of (pressure, weight) calibration points

    Returns:
        Interpolated/extrapolated weight value
    """
    x_values = np.array([p[0] for p in points])
    y_values = np.array([p[1] for p in points])

    coefficients = np.polyfit(x_values, y_values, 2)
    return np.polyval(coefficients, x)

def get_interpolation_curve(points: List[Tuple[float, float]], num_points: int = 100, extend_factor: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate points for plotting interpolation curve with extended range

    Args:
        points: list of (pressure, weight) calibration points
        num_points: number of points to generate for the curve
        extend_factor: factor to extend the range beyond calibration points

    Returns:
        Tuple of (x_values, y_values) for plotting
    """
    x_min = min(p[0] for p in points)
    x_max = max(p[0] for p in points)

    # Extend range by extend_factor
    range_x = x_max - x_min
    x_min = x_min - range_x * extend_factor
    x_max = x_max + range_x * extend_factor

    x_values = np.linspace(x_min, x_max, num_points)

    if len(points) == 2:
        y_values = np.array([linear_interpolation(x, points) for x in x_values])
    else:
        y_values = np.array([quadratic_interpolation(x, points) for x in x_values])

    return x_values, y_values
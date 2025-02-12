import numpy as np
from scipy.interpolate import interp1d
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

    coefficients = np.polyfit(x_values, y_values, min(len(points)-1, 3))
    return np.polyval(coefficients, x)

def get_interpolation_curve(points: List[Tuple[float, float]], num_points: int = 100, extend_factor: float = 0.2) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate points for plotting interpolation curve with extended range using cubic spline

    Args:
        points: list of (pressure, weight) calibration points
        num_points: number of points to generate for the curve
        extend_factor: factor to extend the range beyond calibration points

    Returns:
        Tuple of (x_values, y_values) for plotting
    """
    if len(points) < 2:
        return np.array([]), np.array([])

    x_values = np.array([p[0] for p in points])
    y_values = np.array([p[1] for p in points])

    x_min = min(x_values)
    x_max = max(x_values)

    # Extend range by extend_factor
    range_x = x_max - x_min
    x_extended_min = x_min - range_x * extend_factor
    x_extended_max = x_max + range_x * extend_factor

    # Create extended x values for smooth curve
    x_curve = np.linspace(x_extended_min, x_extended_max, num_points)

    if len(points) == 2:
        # Use linear interpolation for 2 points
        coefficients = np.polyfit(x_values, y_values, 1)
        y_curve = np.polyval(coefficients, x_curve)
    else:
        # Use cubic spline interpolation for more than 2 points
        # k=2 for quadratic spline, k=3 for cubic spline
        spline = interp1d(x_values, y_values, kind='quadratic', bounds_error=False, fill_value='extrapolate')
        y_curve = spline(x_curve)

    return x_curve, y_curve
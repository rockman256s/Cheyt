from typing import List, Tuple

def validate_input(pressure: str, weight: str) -> Tuple[bool, str]:
    """
    Validate pressure and weight input values
    
    Args:
        pressure: pressure value as string
        weight: weight value as string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        p = float(pressure)
        w = float(weight)
        
        if p <= 0 or w <= 0:
            return False, "Значения должны быть положительными"
        
        return True, ""
    except ValueError:
        return False, "Введите корректные числовые значения"

def validate_points(points: List[Tuple[float, float]]) -> Tuple[bool, str]:
    """
    Validate calibration points
    
    Args:
        points: list of (pressure, weight) calibration points
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(points) < 2:
        return False, "Необходимо минимум 2 точки для калибровки"
    
    pressures = [p[0] for p in points]
    if len(set(pressures)) != len(pressures):
        return False, "Значения давления должны быть уникальными"
    
    return True, ""

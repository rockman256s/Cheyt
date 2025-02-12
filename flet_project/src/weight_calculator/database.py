import sqlite3
from typing import List, Tuple
from contextlib import contextmanager

DATABASE_NAME = "calibration.db"

@contextmanager
def get_db_connection():
    """Create database connection context manager"""
    conn = sqlite3.connect(DATABASE_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database and create necessary tables"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS calibration_points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pressure REAL NOT NULL,
            weight REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        conn.commit()

def add_calibration_point(pressure: float, weight: float) -> bool:
    """Add new calibration point to database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO calibration_points (pressure, weight) VALUES (?, ?)",
                (pressure, weight)
            )
            conn.commit()
            return True
    except sqlite3.Error:
        return False

def get_all_points() -> List[Tuple[float, float]]:
    """Get all calibration points from database"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT pressure, weight FROM calibration_points ORDER BY pressure"
        )
        return cursor.fetchall()

def clear_all_points() -> bool:
    """Remove all calibration points from database"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM calibration_points")
            conn.commit()
            return True
    except sqlite3.Error:
        return False

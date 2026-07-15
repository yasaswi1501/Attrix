from pathlib import Path

# Base directory mapping
BASE_DIR = Path(__file__).resolve().parent.parent

# Centralized Path Resolutions
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "Palo Alto Networks.csv"

# Color Palette Definitions (Apple-inspired Light Theme)
COLOR_BACKGROUND_TRANSPARENT = "rgba(0,0,0,0)"
COLOR_PRIMARY_TEXT = "#1D1D1F"
COLOR_SECONDARY_TEXT = "#6E6E73"
COLOR_MUTED_TEXT = "#86868B"
COLOR_BORDER = "rgba(0, 0, 0, 0.06)"
COLOR_GRID = "rgba(0, 0, 0, 0.04)"

# Domain Colors
COLOR_RETENTION = "#2E7D5B"       # Safe Green
COLOR_ATTENTION = "#C9792B"       # Alert Orange
COLOR_ELEVATED_RISK = "#B54747"   # Critical Red
COLOR_ACCENT_BLUE = "#0071E3"     # Accent Blue
COLOR_NEUTRAL_GREY = "#8E8E93"    # Neutral Grey

FONT_STACK = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif'

# Global Default Configurations
DEFAULT_EARLY_TENURE_THRESHOLD = 2

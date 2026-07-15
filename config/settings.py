from pathlib import Path

# Base directory mapping
BASE_DIR = Path(__file__).resolve().parent.parent

# Centralized Path Resolutions
DATA_DIR = BASE_DIR / "data"
RAW_DATA_PATH = DATA_DIR / "raw" / "Palo Alto Networks.csv"

# Color Palette Definitions (Apple-inspired Dark Theme)
COLOR_BACKGROUND_TRANSPARENT = "rgba(0,0,0,0)"
COLOR_PRIMARY_TEXT = "#F4F4F5"      # Zinc 100
COLOR_SECONDARY_TEXT = "#A1A1AA"    # Zinc 400
COLOR_MUTED_TEXT = "#71717A"        # Zinc 500
COLOR_BORDER = "rgba(255, 255, 255, 0.08)"
COLOR_GRID = "rgba(255, 255, 255, 0.04)"

# Domain Colors (Muted Dark Mode equivalents)
COLOR_RETENTION = "#10B981"       # Safe Emerald
COLOR_ATTENTION = "#F59E0B"       # Alert Amber
COLOR_ELEVATED_RISK = "#EF4444"   # Critical Red
COLOR_ACCENT_BLUE = "#3B82F6"     # Accent Blue
COLOR_NEUTRAL_GREY = "#4B5563"    # Gray 600

FONT_STACK = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif'

# Global Default Configurations
DEFAULT_EARLY_TENURE_THRESHOLD = 2

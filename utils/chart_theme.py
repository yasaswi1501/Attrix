import plotly.io as pio
import plotly.graph_objects as go

# Color Palette Definitions (Apple-inspired Light Theme)
COLOR_BACKGROUND_TRANSPARENT = "rgba(0,0,0,0)"
COLOR_PRIMARY_TEXT = "#1D1D1F"
COLOR_SECONDARY_TEXT = "#6E6E73"
COLOR_MUTED_TEXT = "#86868B"
COLOR_BORDER = "rgba(0, 0, 0, 0.08)"
COLOR_GRID = "rgba(0, 0, 0, 0.04)"

# Domain Colors
COLOR_RETENTION = "#2E7D5B"       # Safe Green
COLOR_ATTENTION = "#C9792B"       # Alert Orange
COLOR_ELEVATED_RISK = "#B54747"   # Critical Red
COLOR_ACCENT_BLUE = "#0071E3"     # Accent Blue
COLOR_NEUTRAL_GREY = "#8E8E93"    # Neutral Grey

FONT_STACK = '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Segoe UI", sans-serif'

def get_chart_theme_layout() -> dict:
    """
    Returns the standard layout options to be merged into Plotly charts.
    """
    return {
        "paper_bgcolor": COLOR_BACKGROUND_TRANSPARENT,
        "plot_bgcolor": COLOR_BACKGROUND_TRANSPARENT,
        "font": {
            "family": FONT_STACK,
            "color": COLOR_PRIMARY_TEXT,
            "size": 13
        },
        "margin": {"t": 60, "b": 50, "l": 50, "r": 30},
        "title": {
            "font": {
                "size": 16,
                "color": COLOR_PRIMARY_TEXT,
                "weight": "bold"
            },
            "x": 0.0,
            "xanchor": "left"
        },
        "legend": {
            "font": {
                "size": 12,
                "color": COLOR_SECONDARY_TEXT
            },
            "bgcolor": COLOR_BACKGROUND_TRANSPARENT,
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.2,
            "xanchor": "center",
            "x": 0.5
        },
        "xaxis": {
            "gridcolor": COLOR_GRID,
            "linecolor": COLOR_BORDER,
            "tickfont": {"color": COLOR_SECONDARY_TEXT, "size": 11},
            "titlefont": {"color": COLOR_PRIMARY_TEXT, "size": 12},
            "zeroline": False,
            "showgrid": True
        },
        "yaxis": {
            "gridcolor": COLOR_GRID,
            "linecolor": COLOR_BORDER,
            "tickfont": {"color": COLOR_SECONDARY_TEXT, "size": 11},
            "titlefont": {"color": COLOR_PRIMARY_TEXT, "size": 12},
            "zeroline": False,
            "showgrid": True
        },
        "hoverlabel": {
            "bgcolor": "#FFFFFF",
            "font": {
                "family": FONT_STACK,
                "color": COLOR_PRIMARY_TEXT,
                "size": 12
            },
            "bordercolor": COLOR_BORDER
        }
    }

def apply_apple_theme(fig: go.Figure, title: str = "", xaxis_title: str = "", yaxis_title: str = "", height: int = 380, show_legend: bool = False) -> go.Figure:
    """
    Applies the custom Apple theme to an existing Plotly figure object.
    """
    theme = get_chart_theme_layout()
    theme["title"]["text"] = title
    
    fig.update_layout(
        paper_bgcolor=theme["paper_bgcolor"],
        plot_bgcolor=theme["plot_bgcolor"],
        font=theme["font"],
        margin=theme["margin"],
        title=theme["title"],
        showlegend=show_legend,
        height=height
    )
    
    if show_legend:
        fig.update_layout(legend=theme["legend"])
        
    fig.update_xaxes(
        gridcolor=theme["xaxis"]["gridcolor"],
        linecolor=theme["xaxis"]["linecolor"],
        tickfont=theme["xaxis"]["tickfont"],
        title_font=theme["xaxis"]["titlefont"],
        zeroline=theme["xaxis"]["zeroline"],
        showgrid=theme["xaxis"]["showgrid"],
        title_text=xaxis_title
    )
    
    fig.update_yaxes(
        gridcolor=theme["yaxis"]["gridcolor"],
        linecolor=theme["yaxis"]["linecolor"],
        tickfont=theme["yaxis"]["tickfont"],
        title_font=theme["yaxis"]["titlefont"],
        zeroline=theme["yaxis"]["zeroline"],
        showgrid=theme["yaxis"]["showgrid"],
        title_text=yaxis_title
    )
    
    return fig

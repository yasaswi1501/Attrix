import plotly.io as pio
import plotly.graph_objects as go

from config.settings import (
    COLOR_BACKGROUND_TRANSPARENT,
    COLOR_PRIMARY_TEXT,
    COLOR_SECONDARY_TEXT,
    COLOR_MUTED_TEXT,
    COLOR_BORDER,
    COLOR_GRID,
    COLOR_RETENTION,
    COLOR_ATTENTION,
    COLOR_ELEVATED_RISK,
    COLOR_ACCENT_BLUE,
    COLOR_NEUTRAL_GREY,
    FONT_STACK
)

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
            "size": 12.5
        },
        "margin": {"t": 45, "b": 35, "l": 45, "r": 20, "pad": 4},
        "title": {
            "font": {
                "size": 14,
                "color": COLOR_PRIMARY_TEXT,
                "weight": "bold"
            },
            "x": 0.0,
            "xanchor": "left"
        },
        "legend": {
            "font": {
                "size": 11,
                "color": COLOR_SECONDARY_TEXT
            },
            "bgcolor": COLOR_BACKGROUND_TRANSPARENT,
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.22,
            "xanchor": "center",
            "x": 0.5
        },
        "xaxis": {
            "gridcolor": COLOR_GRID,
            "linecolor": COLOR_BORDER,
            "tickfont": {"color": COLOR_SECONDARY_TEXT, "size": 10.5},
            "titlefont": {"color": COLOR_PRIMARY_TEXT, "size": 11.5},
            "zeroline": False,
            "showgrid": False
        },
        "yaxis": {
            "gridcolor": COLOR_GRID,
            "linecolor": COLOR_BORDER,
            "tickfont": {"color": COLOR_SECONDARY_TEXT, "size": 10.5},
            "titlefont": {"color": COLOR_PRIMARY_TEXT, "size": 11.5},
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
        },
        "modebar": {
            "activecolor": COLOR_ACCENT_BLUE,
            "bgcolor": COLOR_BACKGROUND_TRANSPARENT,
            "color": COLOR_NEUTRAL_GREY,
            "remove": ["zoom", "pan", "select", "lasso2d", "zoomIn", "zoomOut", "autoScale", "hoverClosestCartesian", "hoverCompareCartesian", "toggleSpikelines"]
        }
    }

def apply_apple_theme(
    fig: go.Figure, 
    title: str = "", 
    xaxis_title: str = "", 
    yaxis_title: str = "", 
    height: int = 320, 
    show_legend: bool = False
) -> go.Figure:
    """
    Applies the custom Apple/Stripe-inspired theme to an existing Plotly figure object.
    Automatically handles gridlines based on horizontal/vertical trace orientation.
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
        height=height,
        modebar=theme["modebar"]
    )
    
    if show_legend:
        fig.update_layout(legend=theme["legend"])
        
    # Check trace orientation to toggle horizontal/vertical gridline states
    is_horizontal = False
    for trace in fig.data:
        if hasattr(trace, 'orientation') and trace.orientation == 'h':
            is_horizontal = True
            break

    if is_horizontal:
        # Horizontal bars need vertical grids
        fig.update_xaxes(
            gridcolor=theme["xaxis"]["gridcolor"],
            linecolor=theme["xaxis"]["linecolor"],
            tickfont=theme["xaxis"]["tickfont"],
            title_font=theme["xaxis"]["titlefont"],
            zeroline=False,
            showgrid=True,
            title_text=xaxis_title
        )
        fig.update_yaxes(
            gridcolor=theme["yaxis"]["gridcolor"],
            linecolor=theme["yaxis"]["linecolor"],
            tickfont=theme["yaxis"]["tickfont"],
            title_font=theme["yaxis"]["titlefont"],
            zeroline=False,
            showgrid=False,
            title_text=yaxis_title
        )
    else:
        # Vertical bars / lines / scatters need horizontal grids
        fig.update_xaxes(
            gridcolor=theme["xaxis"]["gridcolor"],
            linecolor=theme["xaxis"]["linecolor"],
            tickfont=theme["xaxis"]["tickfont"],
            title_font=theme["xaxis"]["titlefont"],
            zeroline=False,
            showgrid=False,
            title_text=xaxis_title
        )
        fig.update_yaxes(
            gridcolor=theme["yaxis"]["gridcolor"],
            linecolor=theme["yaxis"]["linecolor"],
            tickfont=theme["yaxis"]["tickfont"],
            title_font=theme["yaxis"]["titlefont"],
            zeroline=False,
            showgrid=True,
            title_text=yaxis_title
        )
    
    return fig

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
    Returns the standard layout options to be merged into Plotly charts,
    relying on Streamlit's native theme engine to format axis text and gridlines.
    """
    return {
        "paper_bgcolor": "rgba(0,0,0,0)",
        "plot_bgcolor": "rgba(0,0,0,0)",
        "font": {
            "family": FONT_STACK,
            "size": 12.5
        },
        "margin": {"t": 45, "b": 35, "l": 45, "r": 20, "pad": 4},
        "title": {
            "font": {
                "size": 14,
                "weight": "bold"
            },
            "x": 0.0,
            "xanchor": "left"
        },
        "legend": {
            "font": {
                "size": 11
            },
            "bgcolor": "rgba(0,0,0,0)",
            "orientation": "h",
            "yanchor": "bottom",
            "y": -0.22,
            "xanchor": "center",
            "x": 0.5
        },
        "xaxis": {
            "zeroline": False,
            "showgrid": False
        },
        "yaxis": {
            "zeroline": False,
            "showgrid": True
        },
        "hoverlabel": {
            "bgcolor": "#18181B",
            "font": {
                "family": FONT_STACK,
                "size": 12
            }
        },
        "modebar": {
            "activecolor": COLOR_ACCENT_BLUE,
            "bgcolor": "rgba(0,0,0,0)",
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
            zeroline=False,
            showgrid=True,
            title_text=xaxis_title
        )
        fig.update_yaxes(
            zeroline=False,
            showgrid=False,
            title_text=yaxis_title
        )
    else:
        # Vertical bars / lines / scatters need horizontal grids
        fig.update_xaxes(
            zeroline=False,
            showgrid=False,
            title_text=xaxis_title
        )
        fig.update_yaxes(
            zeroline=False,
            showgrid=True,
            title_text=yaxis_title
        )
    
    return fig

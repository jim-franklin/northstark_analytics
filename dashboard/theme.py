"""
Single source of truth for all colors, fonts, and layout constants.
"""

# Brand Colors
INDIGO_700 = "#3730a3"
INDIGO_600 = "#4f46e5"  # primary brand
INDIGO_500 = "#6366f1"
INDIGO_400 = "#818cf8"
INDIGO_300 = "#a5b4fc"
INDIGO_200 = "#c7d2fe"
INDIGO_100 = "#e0e7ff"
INDIGO_50 = "#eef2ff"

SLATE_900 = "#0f172a"
SLATE_700 = "#334155"
SLATE_500 = "#64748b"
SLATE_300 = "#cbd5e1"
SLATE_100 = "#f1f5f9"
SLATE_50 = "#f8fafc"

WHITE = "#ffffff"
GRID_COLOR = "#e5e7eb"

# Chart Palette (ordered)
PALETTE = [INDIGO_600, INDIGO_400, INDIGO_300, INDIGO_200, INDIGO_500, INDIGO_700]

# Typography
FONT_FAMILY = "Inter, Segoe UI, system-ui, sans-serif"
FONT_SIZE = 12

#  Plotly Layout Defaults
# Apply with: fig.update_layout(**CHART_LAYOUT)
CHART_LAYOUT = dict(
    paper_bgcolor=WHITE,
    plot_bgcolor=SLATE_50,
    font=dict(family=FONT_FAMILY, size=FONT_SIZE, color=SLATE_700),
    margin=dict(t=48, b=48, l=48, r=20),
    height=300,
    hoverlabel=dict(bgcolor=WHITE, font_size=12, font_family=FONT_FAMILY),
    xaxis=dict(gridcolor=GRID_COLOR, linecolor=SLATE_300, tickfont=dict(size=11)),
    yaxis=dict(gridcolor=GRID_COLOR, linecolor=SLATE_300, tickfont=dict(size=11)),
)

#  Sidebar Styles
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "230px",
    "padding": "28px 16px",
    "backgroundColor": INDIGO_700,
    "overflowY": "auto",
    "zIndex": 100,
}

CONTENT_STYLE = {
    "marginLeft": "230px",
    "padding": "28px 32px",
    "backgroundColor": SLATE_100,
    "minHeight": "100vh",
}

# Component Styles
CARD_STYLE = {
    "backgroundColor": WHITE,
    "borderRadius": "10px",
    "padding": "16px 20px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
    "marginBottom": "20px",
}

KPI_CARD_STYLE = {
    **CARD_STYLE,
    "textAlign": "center",
    "padding": "20px 16px",
}

LABEL_STYLE = {
    "fontSize": "11px",
    "color": INDIGO_200,
    "marginBottom": "5px",
    "fontFamily": FONT_FAMILY,
    "letterSpacing": "0.3px",
    "textTransform": "uppercase",
}

DROPDOWN_STYLE = {
    "backgroundColor": INDIGO_600,
    "color": WHITE,
    "border": "none",
    "borderRadius": "6px",
    "fontSize": "13px",
    "marginBottom": "18px",
}

"""
components/sidebar.py

Left sidebar with filter controls and a data mode toggle at the bottom.
The toggle switches between Cleaned Data (silver) and Raw Data (data/raw).
"""

from dash import html, dcc
import sys
import os
from theme import INDIGO_200, INDIGO_600, INDIGO_700, INDIGO_100, WHITE, FONT_FAMILY
from data_loader import PLANS, DATE_MIN, DATE_MAX, INDUSTRIES

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "260px",
    "padding": "20px 16px",
    "backgroundColor": INDIGO_700,
    "overflowY": "auto",
    "zIndex": 100,
    "display": "flex",
    "flexDirection": "column",
}

label_style = {
    "color": INDIGO_200,
    "fontSize": "11px",
    "fontFamily": FONT_FAMILY,
    "fontWeight": "600",
    "letterSpacing": "0.4px",
    "textTransform": "uppercase",
    "marginBottom": "4px",
    "display": "block",
}

selection_text_style = {
    "fontSize": "10px",
    "color": INDIGO_200,
    "fontFamily": FONT_FAMILY,
    "marginTop": "-10px",
    "marginBottom": "16px",
    "lineHeight": "1.5",
    "wordBreak": "break-word",
}

dropdown_style = {
    "marginBottom": "4px",
    "fontSize": "13px",
}


def build_sidebar():
    return html.Div(
        style=SIDEBAR_STYLE,
        children=[
            # Title
            html.H5(
                "NorthStark Inc.",
                style={
                    "color": WHITE,
                    "fontFamily": FONT_FAMILY,
                    "fontWeight": "700",
                    "marginBottom": "20px",
                    "fontSize": "15px",
                },
            ),
            html.Hr(style={"borderColor": INDIGO_600, "marginBottom": "20px"}),
            # Plan filter
            html.Label("Plan Type", style=label_style),
            dcc.Dropdown(
                id="filter-plan",
                options=[{"label": p, "value": p} for p in PLANS],
                value=PLANS,
                multi=True,
                searchable=False,
                clearable=False,
                style=dropdown_style,
            ),
            html.P(id="selected-plans", style=selection_text_style),
            # Date range filter
            html.Label("Date Range", style=label_style),
            dcc.DatePickerRange(
                id="filter-date",
                min_date_allowed=DATE_MIN,
                max_date_allowed=DATE_MAX,
                start_date=DATE_MIN,
                end_date=DATE_MAX,
                display_format="MMM YYYY",
                style={"marginBottom": "16px", "width": "100%"},
            ),
            # Industry filter
            html.Label("Industry", style={**label_style, "marginTop": "8px"}),
            dcc.Dropdown(
                id="filter-industry",
                options=[{"label": i, "value": i} for i in INDUSTRIES],
                value=INDUSTRIES,
                multi=True,
                searchable=False,
                clearable=False,
                style=dropdown_style,
            ),
            html.P(id="selected-industries", style=selection_text_style),
            # Customer status filter
            html.Label("Customer Status", style=label_style),
            dcc.Dropdown(
                id="filter-status",
                options=[
                    {"label": "All Customers", "value": "all"},
                    {"label": "Active Only", "value": "active"},
                    {"label": "Churned Only", "value": "churned"},
                ],
                value="all",
                searchable=False,
                clearable=False,
                style=dropdown_style,
            ),
            html.P(id="selected-status", style=selection_text_style),
            # Spacer pushes toggle to the bottom
            html.Div(style={"flex": "1"}),
            # Data mode toggle at the bottom
            html.Hr(style={"borderColor": INDIGO_600, "marginBottom": "14px"}),
            html.Label("Data Mode", style=label_style),
            dcc.RadioItems(
                id="toggle-data-mode",
                options=[
                    {"label": " Cleaned Data", "value": "clean"},
                    {"label": " Messy Data", "value": "raw"},
                ],
                value="raw",
                labelStyle={
                    "display": "flex",
                    "alignItems": "center",
                    "gap": "8px",
                    "color": WHITE,
                    "fontSize": "13px",
                    "fontFamily": FONT_FAMILY,
                    "marginBottom": "8px",
                    "cursor": "pointer",
                },
                inputStyle={
                    "accentColor": INDIGO_100,
                    "cursor": "pointer",
                },
            ),
            # Banner shown when raw mode is active
            html.Div(
                id="raw-mode-banner",
                style={"display": "none"},
                children=[
                    html.P(
                        "Viewing unprocessed data. Refunds, duplicates, and inconsistent values are included.",
                        style={
                            "fontSize": "10px",
                            "color": "#fde68a",
                            "fontFamily": FONT_FAMILY,
                            "lineHeight": "1.5",
                            "margin": "8px 0 0 0",
                            "backgroundColor": "rgba(251,191,36,0.15)",
                            "padding": "8px",
                            "borderRadius": "6px",
                            "border": "1px solid rgba(251,191,36,0.3)",
                        },
                    )
                ],
            ),
        ],
    )

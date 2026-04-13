"""
layout/main_layout.py

Uses dash-bootstrap-components for a flexible, responsive grid.
The sidebar is a fixed-width Col and the content area takes the remaining space.
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
import sys
import os
from theme import FONT_FAMILY, SLATE_500, SLATE_100, WHITE
from components.sidebar import build_sidebar
from components.kpi_cards import build_kpi_cards

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

CHART_CARD = {
    "backgroundColor": WHITE,
    "borderRadius": "10px",
    "padding": "16px 20px",
    "boxShadow": "0 1px 4px rgba(0,0,0,0.06)",
    "height": "100%",
}

NOTE_STYLE = {
    "fontSize": "12px",
    "color": SLATE_500,
    "margin": "4px 0 0 0",
    "fontFamily": FONT_FAMILY,
}


def build_layout():
    return dbc.Container(
        fluid=True,
        style={"fontFamily": FONT_FAMILY, "padding": "0", "margin": "0"},
        children=[
            dbc.Row(
                style={"margin": "0"},
                children=[
                    # Sidebar column — fixed width, full height
                    dbc.Col(
                        build_sidebar(),
                        width="auto",
                        style={"padding": "0"},
                    ),
                    # Main content column — fills remaining space
                    dbc.Col(
                        style={
                            "backgroundColor": SLATE_100,
                            "minHeight": "100vh",
                            "padding": "28px 32px",
                        },
                        children=[
                            html.H1(
                                "Sales & Customer Performance",
                                style={
                                    "fontSize": "22px",
                                    "fontWeight": "700",
                                    "color": "#1e1b4b",
                                    "margin": "0 0 8px 0",
                                    "fontFamily": FONT_FAMILY,
                                },
                            ),
                            html.Div(
                                id="data-mode-label", style={"marginBottom": "20px"}
                            ),
                            build_kpi_cards(),
                            # Charts row 1
                            dbc.Row(
                                style={"marginBottom": "16px"},
                                children=[
                                    dbc.Col(
                                        html.Div(
                                            style=CHART_CARD,
                                            children=[
                                                dcc.Graph(
                                                    id="chart-revenue-line",
                                                    config={"displayModeBar": False},
                                                ),
                                                html.P(
                                                    "Sum of paid transactions excluding refunds per month.",
                                                    style=NOTE_STYLE,
                                                ),
                                            ],
                                        ),
                                        md=6,
                                        style={"paddingRight": "8px"},
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            style=CHART_CARD,
                                            children=[
                                                dcc.Graph(
                                                    id="chart-revenue-bar",
                                                    config={"displayModeBar": False},
                                                ),
                                                html.P(
                                                    "Revenue grouped by subscription plan tier.",
                                                    style=NOTE_STYLE,
                                                ),
                                            ],
                                        ),
                                        md=6,
                                        style={"paddingLeft": "8px"},
                                    ),
                                ],
                            ),
                            # Charts row 2
                            dbc.Row(
                                children=[
                                    dbc.Col(
                                        html.Div(
                                            style=CHART_CARD,
                                            children=[
                                                dcc.Graph(
                                                    id="chart-pipeline-pie",
                                                    config={"displayModeBar": False},
                                                ),
                                                html.P(
                                                    "Pipeline stages. Raw mode shows unnormalized CRM values.",
                                                    style=NOTE_STYLE,
                                                ),
                                            ],
                                        ),
                                        md=6,
                                        style={"paddingRight": "8px"},
                                    ),
                                    dbc.Col(
                                        html.Div(
                                            style=CHART_CARD,
                                            children=[
                                                dcc.Graph(
                                                    id="chart-new-customers",
                                                    config={"displayModeBar": False},
                                                ),
                                                html.P(
                                                    "New customers = first paid transaction date per customer per month.",
                                                    style=NOTE_STYLE,
                                                ),
                                            ],
                                        ),
                                        md=6,
                                        style={"paddingLeft": "8px"},
                                    ),
                                ]
                            ),
                        ],
                    ),
                ],
            )
        ],
    )

from dash import html
import sys
import os


from theme import (
    KPI_CARD_STYLE,
    FONT_FAMILY,
    INDIGO_600,
    SLATE_500,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _single_card(card_id, label, tooltip_text):
    return html.Div(
        style={**KPI_CARD_STYLE, "flex": "1"},
        children=[
            html.P(
                label,
                style={
                    "fontSize": "11px",
                    "color": SLATE_500,
                    "marginBottom": "4px",
                    "fontFamily": FONT_FAMILY,
                    "textTransform": "uppercase",
                    "letterSpacing": "0.4px",
                },
            ),
            html.H2(
                id=card_id,
                style={
                    "fontSize": "30px",
                    "fontWeight": "700",
                    "color": INDIGO_600,
                    "margin": "0 0 6px 0",
                    "fontFamily": FONT_FAMILY,
                },
            ),
            html.P(
                tooltip_text,
                style={
                    "fontSize": "11px",
                    "color": SLATE_500,
                    "margin": "0",
                    "fontFamily": FONT_FAMILY,
                    "lineHeight": "1.5",
                },
            ),
        ],
    )


def build_kpi_cards():
    return html.Div(
        style={"display": "flex", "gap": "16px", "marginBottom": "20px"},
        children=[
            _single_card(
                "kpi-revenue",
                "Total Revenue",
                "Sum of paid transactions excluding refunds and duplicates",
            ),
            _single_card(
                "kpi-active",
                "Active Customers",
                "Unique customers with at least one paid transaction who have not churned",
            ),
            _single_card(
                "kpi-churn",
                "Churn Rate",
                "Churned customers divided by total unique customers",
            ),
        ],
    )

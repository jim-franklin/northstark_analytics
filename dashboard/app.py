import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import dash
import dash_bootstrap_components as dbc
from layout.main_layout import build_layout
from callbacks.filters import register_callbacks

app = dash.Dash(
    __name__,
    title="NorthStack Inc. Dashboard",
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)

app.layout = build_layout()
register_callbacks(app)

if __name__ == "__main__":
    app.run(debug=True, port=8050)

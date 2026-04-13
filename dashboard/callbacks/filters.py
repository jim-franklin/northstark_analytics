import sys
import os
from dash import Input, Output
import pandas as pd
import plotly.graph_objects as go

from data_loader import (
    customers as silver_customers,
    transactions as silver_transactions,
    churn as silver_churn,
    PLANS,
    INDUSTRIES,
)
from raw_data_loader import billing_raw, crm_raw, churn_raw
from theme import (
    CHART_LAYOUT,
    PALETTE,
    INDIGO_600,
    GRID_COLOR,
    SLATE_300,
    WHITE,
    FONT_FAMILY,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _axis(title, prefix="", angle=0):
    return dict(
        title=title,
        gridcolor=GRID_COLOR,
        linecolor=SLATE_300,
        tickprefix=prefix,
        tickangle=angle,
        showgrid=True,
        zeroline=False,
    )


def _empty_fig(title):
    fig = go.Figure()
    fig.update_layout(
        **CHART_LAYOUT,
        title=dict(text=title, font=dict(size=14)),
        annotations=[
            dict(
                text="No data for selected filters",
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=13, color="#94a3b8"),
            )
        ],
    )
    return fig


def register_callbacks(app):

    @app.callback(
        Output("raw-mode-banner", "style"),
        Input("toggle-data-mode", "value"),
    )
    def toggle_banner(mode):
        if mode == "raw":
            return {"display": "block"}
        return {"display": "none"}

    @app.callback(
        Output("kpi-revenue", "children"),
        Output("kpi-active", "children"),
        Output("kpi-churn", "children"),
        Output("chart-revenue-line", "figure"),
        Output("chart-revenue-bar", "figure"),
        Output("chart-pipeline-pie", "figure"),
        Output("chart-new-customers", "figure"),
        Output("selected-plans", "children"),
        Output("selected-industries", "children"),
        Output("selected-status", "children"),
        Input("toggle-data-mode", "value"),
        Input("filter-plan", "value"),
        Input("filter-date", "start_date"),
        Input("filter-date", "end_date"),
        Input("filter-industry", "value"),
        Input("filter-status", "value"),
    )
    def update_all(mode, plans, start_date, end_date, industries, status):

        active_plans = plans if plans is not None else PLANS
        active_industries = industries if industries is not None else INDUSTRIES

        if mode == "raw":
            tx = billing_raw.copy()
            churn_ref = churn_raw.copy()

            # Plan filter works on raw billing directly
            tx = tx[tx["plan"].isin(active_plans)] if active_plans else tx.iloc[0:0]

            # Date filter
            if start_date:
                tx = tx[tx["transaction_date"] >= pd.to_datetime(start_date)]
            if end_date:
                tx = tx[tx["transaction_date"] <= pd.to_datetime(end_date)]

            # Industry filter is skipped in raw mode because CRM IDs (CUST-001) and
            # billing IDs (C001) use different formats and cannot be joined without cleaning.
            # This is intentional — it demonstrates the ID mismatch issue.

            # Status filter uses churn IDs which are in CUST-001 format.
            # Billing uses C001 so this join also fails in raw mode — also intentional.
            churned_ids = set(churn_ref["customer_id"].unique())
            if status == "active":
                tx = tx[~tx["customer_id"].isin(churned_ids)]
            elif status == "churned":
                tx = tx[tx["customer_id"].isin(churned_ids)]

            # Pipeline from raw CRM — shows inconsistent stage values
            pipeline_source = crm_raw.copy()
            pipeline_col = "pipeline_stage"

        else:
            tx = silver_transactions.copy()
            churn_ref = silver_churn.copy()

            tx = tx[tx["plan"].isin(active_plans)] if active_plans else tx.iloc[0:0]

            if start_date:
                tx = tx[tx["transaction_date"] >= pd.to_datetime(start_date)]
            if end_date:
                tx = tx[tx["transaction_date"] <= pd.to_datetime(end_date)]

            if active_industries:
                ind_custs = silver_customers[
                    silver_customers["industry"].isin(active_industries)
                    | (silver_customers["billing_only_flag"] == True)
                ]["customer_id"].unique()
                tx = tx[tx["customer_id"].isin(ind_custs)]
            else:
                tx = tx.iloc[0:0]

            churned_ids = set(churn_ref["customer_id"].unique())
            if status == "active":
                tx = tx[~tx["customer_id"].isin(churned_ids)]
            elif status == "churned":
                tx = tx[tx["customer_id"].isin(churned_ids)]

            pipeline_source = silver_customers[
                silver_customers["customer_id"].isin(tx["customer_id"].unique())
            ].copy()
            pipeline_col = "pipeline_stage"

        # KPI values
        total_revenue = tx["amount"].sum()
        total_unique = tx["customer_id"].nunique()
        churned_ids_set = set(churn_ref["customer_id"].unique())
        active_count = tx[~tx["customer_id"].isin(churned_ids_set)][
            "customer_id"
        ].nunique()
        churned_in_view = len(
            churned_ids_set.intersection(set(tx["customer_id"].unique()))
        )
        churn_rate = (
            round(churned_in_view / total_unique * 100, 1) if total_unique > 0 else 0.0
        )

        kpi_revenue = f"${total_revenue:,.0f}"
        kpi_active = f"{active_count:,}"
        kpi_churn = f"{churn_rate}%"

        label_plans = label_industries = label_status = ""

        # Chart 1: Monthly revenue line
        if tx.empty:
            fig_line = _empty_fig("Monthly Revenue")
        else:
            rev_by_month = (
                tx.groupby("month")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"amount": "revenue"})
                .sort_values("month")
            )
            fig_line = go.Figure()
            fig_line.add_trace(
                go.Scatter(
                    x=rev_by_month["month"],
                    y=rev_by_month["revenue"],
                    mode="lines+markers",
                    line=dict(color=INDIGO_600, width=2.5),
                    marker=dict(size=6, color=INDIGO_600),
                    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
                )
            )
            fig_line.update_layout(
                **CHART_LAYOUT, title=dict(text="Monthly Revenue", font=dict(size=14))
            )
            fig_line.update_xaxes(**_axis("Month", angle=-45))
            fig_line.update_yaxes(**_axis("Revenue (CAD)", prefix="$"))

        # Chart 2: Revenue by plan bar
        if tx.empty:
            fig_bar = _empty_fig("Revenue by Plan")
        else:
            rev_by_plan = (
                tx.groupby("plan")["amount"]
                .sum()
                .reset_index()
                .rename(columns={"amount": "revenue"})
                .sort_values("revenue", ascending=False)
            )
            fig_bar = go.Figure()
            fig_bar.add_trace(
                go.Bar(
                    x=rev_by_plan["plan"],
                    y=rev_by_plan["revenue"],
                    marker=dict(color=PALETTE[: len(rev_by_plan)], line=dict(width=0)),
                    hovertemplate="<b>%{x}</b><br>Revenue: $%{y:,.0f}<extra></extra>",
                )
            )
            fig_bar.update_layout(
                **CHART_LAYOUT,
                title=dict(text="Revenue by Plan", font=dict(size=14)),
                bargap=0.4,
            )
            fig_bar.update_xaxes(**_axis("Plan"))
            fig_bar.update_yaxes(**_axis("Revenue (CAD)", prefix="$"))

        # Chart 3: Pipeline stage pie — Plotly default colors
        if pipeline_source.empty or pipeline_col not in pipeline_source.columns:
            fig_pie = _empty_fig("Pipeline Stage Distribution")
        else:
            pipeline = pipeline_source[pipeline_col].value_counts().reset_index()
            pipeline.columns = ["stage", "count"]
            fig_pie = go.Figure(
                go.Pie(
                    labels=pipeline["stage"],
                    values=pipeline["count"],
                    hole=0.4,
                    hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Share: %{percent}<extra></extra>",
                )
            )
            fig_pie.update_layout(
                paper_bgcolor=WHITE,
                font=dict(family=FONT_FAMILY, size=12),
                height=300,
                margin=dict(t=48, b=20, l=20, r=20),
                title=dict(text="Pipeline Stage Distribution", font=dict(size=14)),
                legend=dict(orientation="v", x=1.0, y=0.5),
            )

        # Chart 4: New customers per month area
        if tx.empty:
            fig_area = _empty_fig("New Customers Per Month")
        else:
            first_tx = tx.groupby("customer_id")["transaction_date"].min().reset_index()
            first_tx["month"] = (
                first_tx["transaction_date"].dt.to_period("M").astype(str)
            )
            new_cust = (
                first_tx.groupby("month")
                .size()
                .reset_index(name="new_customers")
                .sort_values("month")
            )
            fig_area = go.Figure()
            fig_area.add_trace(
                go.Scatter(
                    x=new_cust["month"],
                    y=new_cust["new_customers"],
                    mode="lines",
                    fill="tozeroy",
                    fillcolor="rgba(79, 70, 229, 0.12)",
                    line=dict(color=INDIGO_600, width=2.5),
                    hovertemplate="<b>%{x}</b><br>New Customers: %{y}<extra></extra>",
                )
            )
            fig_area.update_layout(
                **CHART_LAYOUT,
                title=dict(text="New Customers Per Month", font=dict(size=14)),
            )
            fig_area.update_xaxes(**_axis("Month", angle=-45))
            fig_area.update_yaxes(**_axis("New Customers"))

        return (
            kpi_revenue,
            kpi_active,
            kpi_churn,
            fig_line,
            fig_bar,
            fig_pie,
            fig_area,
            label_plans,
            label_industries,
            label_status,
        )

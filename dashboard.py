import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
import numpy as np
import pandas as pd
from scipy.stats import norm, beta
import plotly.graph_objs as go

# ------------------------------
# 📦 模拟数据（A/B 每日数据）
# ------------------------------
np.random.seed(42)
days = pd.date_range("2024-01-01", periods=14)
data = pd.DataFrame({
    "date": np.repeat(days, 2),
    "group": ["A", "B"] * len(days),
    "conversions": np.random.binomial(n=500, p=[0.10, 0.12] * len(days)),
    "visitors": 500
})
pivot = data.pivot(index="date", columns="group", values="conversions")

# 汇总
conv_a_total = data[data.group == 'A']["conversions"].sum()
conv_b_total = data[data.group == 'B']["conversions"].sum()
n_a = n_b = 500 * len(days)
cr_a = conv_a_total / n_a
cr_b = conv_b_total / n_b
uplift = (cr_b - cr_a) / cr_a

# ------------------------------
# 📊 Frequentist 分析
# ------------------------------
se = np.sqrt(cr_a * (1 - cr_a) / n_a + cr_b * (1 - cr_b) / n_b)
z = (cr_b - cr_a) / se
p_value = 1 - norm.cdf(abs(z))
ci_low, ci_high = (cr_b - cr_a) - 1.96 * se, (cr_b - cr_a) + 1.96 * se

# ------------------------------
# 🔁 Bootstrap Uplift CI
# ------------------------------
bootstrap_diff = []
for _ in range(5000):
    bs_a = np.random.binomial(1, cr_a, n_a)
    bs_b = np.random.binomial(1, cr_b, n_b)
    uplift_bs = (np.mean(bs_b) - np.mean(bs_a))
    bootstrap_diff.append(uplift_bs)
boot_low, boot_high = np.percentile(bootstrap_diff, [2.5, 97.5])

# ------------------------------
# 🧠 Bayesian 后验分布
# ------------------------------
posterior_a = beta(conv_a_total + 1, n_a - conv_a_total + 1)
posterior_b = beta(conv_b_total + 1, n_b - conv_b_total + 1)
x = np.linspace(0.05, 0.2, 500)
posterior_trace = go.Figure()
posterior_trace.add_trace(go.Scatter(x=x, y=posterior_a.pdf(x), name="Group A Posterior"))
posterior_trace.add_trace(go.Scatter(x=x, y=posterior_b.pdf(x), name="Group B Posterior"))
posterior_trace.update_layout(title="🧠 Bayesian Posterior Distributions", height=400)

# ------------------------------
# 📈 时间趋势图
# ------------------------------
trend_fig = go.Figure()
trend_fig.add_trace(go.Scatter(x=days, y=pivot["A"] / 500, name="Group A", mode="lines+markers"))
trend_fig.add_trace(go.Scatter(x=days, y=pivot["B"] / 500, name="Group B", mode="lines+markers"))
trend_fig.update_layout(title="📆 Daily Conversion Trend", height=400)

# ------------------------------
# 🚀 App Layout
# ------------------------------
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])

app.layout = dbc.Container([
    html.H2("📊 A/B Test Pro Dashboard", className="text-center text-info my-4"),

    dbc.Row([
        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Group A", className="text-info"),
                html.P(f"CR: {cr_a:.2%}"),
                html.P(f"Conversions: {conv_a_total} / {n_a}")
            ])
        ], color="dark", inverse=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Group B", className="text-danger"),
                html.P(f"CR: {cr_b:.2%}"),
                html.P(f"Conversions: {conv_b_total} / {n_b}")
            ])
        ], color="dark", inverse=True), width=4),

        dbc.Col(dbc.Card([
            dbc.CardBody([
                html.H4("Results", className="text-warning"),
                html.P(f"Uplift: {uplift:.2%}"),
                html.P(f"Z-score: {z:.2f}"),
                html.P(f"P-value: {p_value:.4f}"),
                html.P(f"95% CI: [{ci_low:.2%}, {ci_high:.2%}]"),
                html.P(f"Bootstrap CI: [{boot_low:.2%}, {boot_high:.2%}]"),
            ])
        ], color="secondary", inverse=True), width=4)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(figure=trend_fig), width=6),
        dbc.Col(dcc.Graph(figure=posterior_trace), width=6)
    ]),

    dbc.Row([
        dbc.Col(dbc.Alert("✨ 数据使用模拟生成，仅作展示。可扩展上传 CSV 或接入数据库。", color="info"), width=12)
    ])
], fluid=True)

if __name__ == '__main__':
    app.run_server(debug=True)

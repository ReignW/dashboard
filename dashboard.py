
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy.stats import beta, ttest_ind, norm

# ---------------------
# Simulate multi-group data
# ---------------------
np.random.seed(42)
groups = ['A', 'B', 'C', 'D']
days = pd.date_range("2024-01-01", periods=30)
data = []

for group in groups:
    base_cr = 0.10 + 0.02 * groups.index(group)  # Slightly increasing CR
    base_arpu = 5 + 2 * groups.index(group)
    for date in days:
        visitors = np.random.randint(450, 550)
        conversions = np.random.binomial(visitors, base_cr)
        revenue = conversions * np.random.normal(base_arpu, 1)
        retained = np.random.binomial(conversions, 0.3 + 0.05 * groups.index(group))
        data.append([date, group, visitors, conversions, revenue, retained])

df = pd.DataFrame(data, columns=["date", "group", "visitors", "conversions", "revenue", "retained"])
df["cr"] = df["conversions"] / df["visitors"]
df["arpu"] = df["revenue"] / df["visitors"]
df["retention_rate"] = df["retained"] / df["conversions"].replace(0, np.nan)

# ---------------------
# Page config
# ---------------------
st.set_page_config(layout="wide", page_title="Pro A/B/n Test Dashboard")
st.title("📊 Pro-Level A/B/n Test Analysis Dashboard")
st.caption("Simulated data comparing Groups A, B, C, and D over 30 days. Includes CR, ARPU, Retention, Bayesian, Bootstrap, and more.")

# ---------------------
# Summary cards
# ---------------------
st.subheader("🧮 Summary Metrics")
summary = df.groupby("group").agg(
    total_visitors=("visitors", "sum"),
    total_conversions=("conversions", "sum"),
    total_revenue=("revenue", "sum"),
    total_retained=("retained", "sum")
)
summary["CR"] = summary["total_conversions"] / summary["total_visitors"]
summary["ARPU"] = summary["total_revenue"] / summary["total_visitors"]
summary["Retention"] = summary["total_retained"] / summary["total_conversions"]

st.dataframe(summary.style.format("{:.2%}", subset=["CR", "Retention"]).format("${:.2f}", subset=["ARPU"]))

# ---------------------
# Conversion Rate Over Time
# ---------------------
st.subheader("📈 Daily Conversion Rate by Group")
fig_cr = px.line(df, x="date", y="cr", color="group", markers=True)
st.plotly_chart(fig_cr, use_container_width=True)

# ---------------------
# ARPU Over Time
# ---------------------
st.subheader("💰 Daily ARPU by Group")
fig_arpu = px.line(df, x="date", y="arpu", color="group", markers=True)
st.plotly_chart(fig_arpu, use_container_width=True)

# ---------------------
# Retention Over Time
# ---------------------
st.subheader("🔁 Daily Retention Rate by Group")
fig_ret = px.line(df, x="date", y="retention_rate", color="group", markers=True)
st.plotly_chart(fig_ret, use_container_width=True)

# ---------------------
# Boxplots
# ---------------------
st.subheader("📦 Conversion Rate Distribution")
fig_box = px.box(df, x="group", y="cr")
st.plotly_chart(fig_box, use_container_width=True)

# ---------------------
# Bayesian Posterior (Group A vs others)
# ---------------------
st.subheader("🧠 Bayesian Posterior: Group A vs Others")
posterior_x = np.linspace(0.05, 0.25, 500)
fig_bayes = go.Figure()
a_conv = df[df.group == 'A']["conversions"].sum()
a_total = df[df.group == 'A']["visitors"].sum()
posterior_a = beta(a_conv + 1, a_total - a_conv + 1)
fig_bayes.add_trace(go.Scatter(x=posterior_x, y=posterior_a.pdf(posterior_x), name="A"))

for group in ['B', 'C', 'D']:
    g_conv = df[df.group == group]["conversions"].sum()
    g_total = df[df.group == group]["visitors"].sum()
    posterior = beta(g_conv + 1, g_total - g_conv + 1)
    fig_bayes.add_trace(go.Scatter(x=posterior_x, y=posterior.pdf(posterior_x), name=group))

st.plotly_chart(fig_bayes, use_container_width=True)

# ---------------------
# Bootstrap uplift A vs B
# ---------------------
st.subheader("🎲 Bootstrap Uplift: A vs B")
a_cr = df[df.group == "A"]["cr"]
b_cr = df[df.group == "B"]["cr"]
boot_diffs = [np.mean(np.random.choice(b_cr, size=len(b_cr), replace=True)) -
              np.mean(np.random.choice(a_cr, size=len(a_cr), replace=True))
              for _ in range(3000)]
ci = np.percentile(boot_diffs, [2.5, 97.5])
fig_boot = px.histogram(boot_diffs, nbins=50, title="Bootstrap Uplift Distribution (B - A)")
fig_boot.add_vline(x=ci[0], line=dict(color="red", dash="dash"))
fig_boot.add_vline(x=ci[1], line=dict(color="green", dash="dash"))
st.plotly_chart(fig_boot, use_container_width=True)

# ---------------------
# Welch’s t-test A vs B
# ---------------------
st.subheader("🧪 Welch’s T-Test (A vs B)")
t_stat, p_val = ttest_ind(a_cr, b_cr, equal_var=False)
st.write(f"**T-Statistic:** {t_stat:.3f}")
st.write(f"**P-Value:** {p_val:.5f}")
if p_val < 0.05:
    st.success("Result: Statistically significant difference.")
else:
    st.warning("Result: No significant difference.")

# ---------------------
# Auto Summary
# ---------------------
st.subheader("📄 Automated Summary")
best_group = summary["CR"].idxmax()
best_arpu = summary["ARPU"].idxmax()
st.markdown(f"- **Highest Conversion Rate:** Group {best_group} ({summary.loc[best_group, 'CR']:.2%})")
st.markdown(f"- **Highest ARPU:** Group {best_arpu} (${summary.loc[best_arpu, 'ARPU']:.2f})")
st.markdown(f"- **Lowest Retention:** Group {summary['Retention'].idxmin()} ({summary['Retention'].min():.2%})")

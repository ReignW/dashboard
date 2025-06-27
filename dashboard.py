
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm, beta, ttest_ind

# Simulate A/B test data
np.random.seed(42)
days = pd.date_range("2024-01-01", periods=14)
df = pd.DataFrame({
    "date": np.tile(days, 2),
    "group": ["A"] * 14 + ["B"] * 14,
    "visitors": 500,
    "conversions": np.concatenate([
        np.random.binomial(500, 0.10, 14),
        np.random.binomial(500, 0.12, 14)
    ])
})
df["conversion_rate"] = df["conversions"] / df["visitors"]

# Summary statistics
summary = df.groupby("group").agg(
    total_conversions=("conversions", "sum"),
    total_visitors=("visitors", "sum")
)
summary["conversion_rate"] = summary["total_conversions"] / summary["total_visitors"]

# Frequentist confidence interval
cr_diff = summary.loc["B", "conversion_rate"] - summary.loc["A", "conversion_rate"]
p_a = summary.loc["A", "conversion_rate"]
p_b = summary.loc["B", "conversion_rate"]
n = summary["total_visitors"].iloc[0]
se = np.sqrt(p_a * (1 - p_a) / n + p_b * (1 - p_b) / n)
z_score = cr_diff / se
p_value = 1 - norm.cdf(abs(z_score))
ci_low, ci_high = cr_diff - 1.96 * se, cr_diff + 1.96 * se

# Bootstrap uplift distribution
def bootstrap_diff(a, b, n=5000):
    return [np.mean(np.random.choice(b, size=len(b), replace=True)) -
            np.mean(np.random.choice(a, size=len(a), replace=True))
            for _ in range(n)]

boot_diffs = bootstrap_diff(df[df.group == "A"]["conversion_rate"],
                            df[df.group == "B"]["conversion_rate"])
boot_ci = np.percentile(boot_diffs, [2.5, 97.5])

# Bayesian inference
a_conv = summary.loc["A", "total_conversions"]
a_total = summary.loc["A", "total_visitors"]
b_conv = summary.loc["B", "total_conversions"]
b_total = summary.loc["B", "total_visitors"]
posterior_a = beta(a_conv + 1, a_total - a_conv + 1)
posterior_b = beta(b_conv + 1, b_total - b_conv + 1)
x = np.linspace(0.05, 0.2, 500)

# Layout
st.set_page_config(layout="wide", page_title="Advanced A/B Test Dashboard")

st.title("🔬 Advanced A/B Test Analysis Dashboard")
st.markdown("This dashboard visualizes A/B testing results using frequentist, bootstrap, and Bayesian methods.")

# Summary
col1, col2, col3 = st.columns(3)
col1.metric("Group A CR", f"{p_a:.2%}")
col2.metric("Group B CR", f"{p_b:.2%}", delta=f"{cr_diff:.2%}")
col3.metric("p-value (Z test)", f"{p_value:.5f}")

st.markdown("#### Null Hypothesis (H₀): CR_A = CR_B")
st.markdown("#### Alternative Hypothesis (H₁): CR_A ≠ CR_B")

# Chart 1 - Daily CR trend
st.subheader("1. Daily Conversion Rate Trend")
fig1 = px.line(df, x="date", y="conversion_rate", color="group", markers=True)
st.plotly_chart(fig1, use_container_width=True)

# Chart 2 - Overall CR bar
st.subheader("2. Overall Conversion Rate Comparison")
fig2 = px.bar(summary.reset_index(), x="group", y="conversion_rate", text_auto=True)
st.plotly_chart(fig2, use_container_width=True)

# Chart 3 - Bayesian Posterior
st.subheader("3. Bayesian Posterior Distributions")
fig3 = go.Figure()
fig3.add_trace(go.Scatter(x=x, y=posterior_a.pdf(x), name="Posterior A"))
fig3.add_trace(go.Scatter(x=x, y=posterior_b.pdf(x), name="Posterior B"))
fig3.update_layout(title="Beta Posterior Distributions")
st.plotly_chart(fig3, use_container_width=True)

# Chart 4 - Bootstrap Uplift Histogram
st.subheader("4. Bootstrap Uplift Distribution")
fig4 = px.histogram(boot_diffs, nbins=50)
fig4.add_vline(x=boot_ci[0], line=dict(color="red", dash="dash"))
fig4.add_vline(x=boot_ci[1], line=dict(color="green", dash="dash"))
st.plotly_chart(fig4, use_container_width=True)

# Chart 5 - Boxplot of CR
st.subheader("5. Conversion Rate Distribution by Group")
fig5 = px.box(df, x="group", y="conversion_rate")
st.plotly_chart(fig5, use_container_width=True)

# Chart 6 - Rolling Average
st.subheader("6. 3-Day Rolling Conversion Rate")
df["rolling_cr"] = df.groupby("group")["conversion_rate"].transform(lambda x: x.rolling(3, 1).mean())
fig6 = px.line(df, x="date", y="rolling_cr", color="group")
st.plotly_chart(fig6, use_container_width=True)

# Chart 7 - Scatter by Conversions
st.subheader("7. CR Scatter Sized by Conversion Volume")
fig7 = px.scatter(df, x="date", y="conversion_rate", color="group", size="conversions")
st.plotly_chart(fig7, use_container_width=True)

# Chart 8 - Cumulative CR
st.subheader("8. Cumulative Conversion Rate Over Time")
df["cumulative_conv"] = df.groupby("group")["conversions"].cumsum()
df["cumulative_vis"] = df.groupby("group")["visitors"].cumsum()
df["cumulative_cr"] = df["cumulative_conv"] / df["cumulative_vis"]
fig8 = px.line(df, x="date", y="cumulative_cr", color="group")
st.plotly_chart(fig8, use_container_width=True)

# Chart 9 - Error bars
st.subheader("9. Mean CR with Standard Deviation")
means = df.groupby("group")["conversion_rate"].mean()
stds = df.groupby("group")["conversion_rate"].std()
fig9 = go.Figure(data=[go.Bar(x=["A", "B"], y=means, error_y=dict(type='data', array=stds))])
st.plotly_chart(fig9, use_container_width=True)

# Chart 10 - Welch's t-test
st.subheader("10. Welch's t-test")
t_stat, pval = ttest_ind(df[df.group=="A"]["conversion_rate"], df[df.group=="B"]["conversion_rate"], equal_var=False)
st.metric("t-test p-value", f"{pval:.5f}")
if pval < 0.05:
    st.success("Statistically significant difference detected.")
else:
    st.warning("No statistically significant difference.")

st.markdown("---")
st.caption("All data shown here is simulated.")

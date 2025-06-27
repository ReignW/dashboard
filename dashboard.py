import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm, beta

# --------------------------
# 🧪 模拟 A/B 数据
# --------------------------
np.random.seed(42)
days = pd.date_range("2024-01-01", periods=14)
data = pd.DataFrame({
    "date": np.repeat(days, 2),
    "group": ["A", "B"] * len(days),
    "conversions": np.random.binomial(n=500, p=[0.10, 0.12] * len(days)),
    "visitors": 500
})
pivot = data.pivot(index="date", columns="group", values="conversions")

# 汇总指标
conv_a_total = data[data.group == 'A']["conversions"].sum()
conv_b_total = data[data.group == 'B']["conversions"].sum()
n_a = n_b = 500 * len(days)
cr_a = conv_a_total / n_a
cr_b = conv_b_total / n_b
uplift = (cr_b - cr_a) / cr_a

# --------------------------
# 📊 Frequentist 检验
# --------------------------
se = np.sqrt(cr_a * (1 - cr_a) / n_a + cr_b * (1 - cr_b) / n_b)
z = (cr_b - cr_a) / se
p_value = 1 - norm.cdf(abs(z))
ci_low, ci_high = (cr_b - cr_a) - 1.96 * se, (cr_b - cr_a) + 1.96 * se

# --------------------------
# 🔁 Bootstrap 置信区间
# --------------------------
bootstrap_diff = []
for _ in range(3000):
    bs_a = np.random.binomial(1, cr_a, n_a)
    bs_b = np.random.binomial(1, cr_b, n_b)
    uplift_bs = np.mean(bs_b) - np.mean(bs_a)
    bootstrap_diff.append(uplift_bs)
boot_low, boot_high = np.percentile(bootstrap_diff, [2.5, 97.5])

# --------------------------
# 🧠 Bayesian 后验分布
# --------------------------
posterior_a = beta(conv_a_total + 1, n_a - conv_a_total + 1)
posterior_b = beta(conv_b_total + 1, n_b - conv_b_total + 1)
x = np.linspace(0.05, 0.2, 500)

# --------------------------
# 📈 可视化图表
# --------------------------
def plot_conversion_trend():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=days, y=pivot["A"] / 500, name="Group A", mode="lines+markers"))
    fig.add_trace(go.Scatter(x=days, y=pivot["B"] / 500, name="Group B", mode="lines+markers"))
    fig.update_layout(title="📆 每日转化率趋势", height=400)
    return fig

def plot_posterior():
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=posterior_a.pdf(x), name="Group A Posterior"))
    fig.add_trace(go.Scatter(x=x, y=posterior_b.pdf(x), name="Group B Posterior"))
    fig.update_layout(title="🧠 贝叶斯后验分布", height=400)
    return fig

def plot_bootstrap():
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=bootstrap_diff, nbinsx=50, name="Bootstrap Uplift"))
    fig.add_vline(x=boot_low, line=dict(color="red", dash="dash"))
    fig.add_vline(x=boot_high, line=dict(color="green", dash="dash"))
    fig.update_layout(title="🔁 Bootstrap Uplift 分布", height=400)
    return fig

# --------------------------
# 🎨 Streamlit 布局
# --------------------------
st.set_page_config(layout="wide", page_title="A/B Test Dashboard")
st.title("📊 A/B Test 专业分析看板")
st.caption("✨ 使用模拟数据，展示 Frequentist / Bootstrap / Bayesian 分析方法")

# --------------------------
# 📦 指标卡片
# --------------------------
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Group A 转化率", f"{cr_a:.2%}", delta=None)
    st.text(f"Conversions: {conv_a_total} / {n_a}")
with col2:
    st.metric("Group B 转化率", f"{cr_b:.2%}", delta=f"{uplift:.2%}")
    st.text(f"Conversions: {conv_b_total} / {n_b}")
with col3:
    st.metric("P-Value", f"{p_value:.4f}")
    st.text(f"Z-score: {z:.2f}")
    st.text(f"95% CI: {ci_low:.2%} ~ {ci_high:.2%}")
    st.text(f"Bootstrap CI: {boot_low:.2%} ~ {boot_high:.2%}")

st.divider()

# --------------------------
# 📈 图表展示
# --------------------------
col4, col5 = st.columns(2)
with col4:
    st.plotly_chart(plot_conversion_trend(), use_container_width=True)
with col5:
    st.plotly_chart(plot_posterior(), use_container_width=True)

st.plotly_chart(plot_bootstrap(), use_container_width=True)

st.info("你可以上传 CSV 文件、调整转化逻辑、添加多指标分析，进一步扩

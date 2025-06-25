
import streamlit as st
import pandas as pd
import altair as alt

st.title("渠道销售分析数据看板")

# 假设读取CSV或数据库数据
df = pd.read_csv("channel_daily_data.csv", parse_dates=['date'])

# 筛选时间范围
start_date = st.date_input("开始日期", df['date'].min())
end_date = st.date_input("结束日期", df['date'].max())
df_filtered = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

# 聚合渠道指标（含SKU维度）
channel_sku_summary = df_filtered.groupby(['channel', 'product_id', 'product_name']).agg({
    'uv': 'sum', 'pv': 'sum', 'gmv': 'sum', 'cost': 'sum',
    'orders': 'sum', 'clicks': 'sum', 'impressions': 'sum'
}).reset_index()
channel_sku_summary['转化率(CVR)'] = channel_sku_summary['orders'] / channel_sku_summary['clicks']
channel_sku_summary['ROI'] = channel_sku_summary['gmv'] / channel_sku_summary['cost']

st.subheader("各渠道-SKU维度汇总指标")
st.dataframe(channel_sku_summary)

# 趋势图：每日UV、GMV、ROI per 渠道
st.subheader("每日趋势")
selected_channel = st.selectbox("选择渠道查看趋势", df['channel'].unique())
df_daily = df_filtered[df_filtered['channel'] == selected_channel].groupby('date').agg({
    'uv': 'sum', 'gmv': 'sum', 'cost': 'sum'
}).reset_index()
df_daily['ROI'] = df_daily['gmv'] / df_daily['cost']

df_melted = df_daily.melt(id_vars='date', value_vars=['uv', 'gmv', 'ROI'], var_name='指标', value_name='值')
chart = alt.Chart(df_melted).mark_line().encode(
    x='date:T', y='值:Q', color='指标:N', tooltip=['date:T', '指标:N', '值:Q']
).properties(title=f"每日趋势 - {selected_channel}", width=700)
st.altair_chart(chart, use_container_width=True)

# ROI 边际效应分析（ROI 随费用变化）
st.subheader("边际ROI分析")
channel_cost_roi = df_filtered.groupby(['channel', 'date']).agg({'cost': 'sum', 'gmv': 'sum'}).reset_index()
channel_cost_roi['ROI'] = channel_cost_roi['gmv'] / channel_cost_roi['cost']
selected_marginal_channel = st.selectbox("选择渠道分析ROI边际变化", df['channel'].unique())
marginal_df = channel_cost_roi[channel_cost_roi['channel'] == selected_marginal_channel]

marginal_chart = alt.Chart(marginal_df).mark_circle(size=80).encode(
    x='cost:Q', y='ROI:Q', tooltip=['date:T', 'cost:Q', 'ROI:Q']
).properties(title=f"{selected_marginal_channel} 渠道 ROI vs 成本 (边际效应)", width=700)
st.altair_chart(marginal_chart, use_container_width=True)

# Top10 ROI 产品
st.subheader("Top10 ROI产品")
product_roi = df_filtered.groupby(['product_id', 'product_name']).agg({
    'gmv': 'sum', 'cost': 'sum'
}).reset_index()
product_roi['ROI'] = product_roi['gmv'] / product_roi['cost']
top10 = product_roi.sort_values(by='ROI', ascending=False).head(10)
st.dataframe(top10)

# 渠道 GMV 占比
st.subheader("渠道GMV占比")
channel_summary = df_filtered.groupby('channel').agg({
    'uv': 'sum', 'pv': 'sum', 'gmv': 'sum', 'cost': 'sum',
    'orders': 'sum', 'clicks': 'sum', 'impressions': 'sum'
}).reset_index()
channel_summary['转化率(CVR)'] = channel_summary['orders'] / channel_summary['clicks']
channel_summary['ROI'] = channel_summary['gmv'] / channel_summary['cost']
channel_summary['全段ROI'] = channel_summary['gmv'] / (channel_summary['cost'] + df_filtered['gross_profit'].sum())
channel_summary['GMV占比'] = channel_summary['gmv'] / channel_summary['gmv'].sum()

pie_chart = alt.Chart(channel_summary).mark_arc().encode(
    theta='GMV占比:Q', color='channel:N', tooltip=['channel', 'GMV占比']
)
st.altair_chart(pie_chart, use_container_width=True)

# 首推渠道选择器
st.subheader("首推渠道设定")
primary_channel = st.selectbox("请选择要主推的渠道：", channel_summary['channel'].unique())
st.success(f"当前主推渠道设定为：{primary_channel}")

# 渠道+品类组合分析
df_filtered['category'] = df_filtered['product_name'].apply(lambda x: x.split("_")[0] if '_' in x else 'Unknown')
combo = df_filtered.groupby(['channel', 'category']).agg({'gmv': 'sum', 'cost': 'sum'}).reset_index()
combo['ROI'] = combo['gmv'] / combo['cost']
st.subheader("渠道+品类组合 ROI 分析")
st.dataframe(combo.sort_values(by='ROI', ascending=False))

# 费用异常归因与建议
st.subheader("费用异常归因与优化建议")
channel_cost_alert = df_filtered.groupby(['date', 'channel'])['cost'].sum().reset_index()
cost_mean = channel_cost_alert.groupby('channel')['cost'].mean().reset_index(name='mean_cost')
cost_merged = channel_cost_alert.merge(cost_mean, on='channel')
cost_merged['异常程度'] = cost_merged['cost'] / cost_merged['mean_cost']
cost_alerts = cost_merged.sort_values(by='异常程度', ascending=False).head(5)

# 添加归因和建议
cost_alerts['归因分析'] = "可能因高频投放、无效点击或预算外推"
cost_alerts['优化建议'] = "建议复查投放时间、屏蔽低质受众、压缩预算"

st.dataframe(cost_alerts)

st.caption("数据来源：营销数据平台 | 开发：数据团队")

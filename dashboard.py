
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("渠道销售分析数据看板")

# 假设读取CSV或数据库数据
df = pd.read_csv("channel_daily_data.csv", parse_dates=['date'])

# 筛选时间范围
start_date = st.date_input("开始日期", df['date'].min())
end_date = st.date_input("结束日期", df['date'].max())
df_filtered = df[(df['date'] >= pd.to_datetime(start_date)) & (df['date'] <= pd.to_datetime(end_date))]

# 聚合渠道指标
channel_summary = df_filtered.groupby('channel').agg({
    'uv': 'sum',
    'pv': 'sum',
    'gmv': 'sum',
    'cost': 'sum',
    'gross_profit': 'sum',
    'orders': 'sum',
    'clicks': 'sum',
    'impressions': 'sum'
}).reset_index()

channel_summary['转化率(CVR)'] = channel_summary['orders'] / channel_summary['clicks']
channel_summary['ROI'] = channel_summary['gmv'] / channel_summary['cost']
channel_summary['全段ROI'] = channel_summary['gmv'] / (channel_summary['cost'] + channel_summary['gross_profit'])
channel_summary['GMV占比'] = channel_summary['gmv'] / channel_summary['gmv'].sum()

# 展示渠道数据表格
st.subheader("各渠道汇总指标")
st.dataframe(channel_summary)

# 趋势图：每日UV、GMV、ROI
st.subheader("每日趋势")
selected_channel = st.selectbox("选择渠道查看趋势", df['channel'].unique())
df_daily = df_filtered[df_filtered['channel'] == selected_channel].groupby('date').agg({
    'uv': 'sum',
    'gmv': 'sum',
    'cost': 'sum'
}).reset_index()
df_daily['ROI'] = df_daily['gmv'] / df_daily['cost']

fig, ax = plt.subplots()
ax.plot(df_daily['date'], df_daily['uv'], label='UV')
ax.plot(df_daily['date'], df_daily['gmv'], label='GMV')
ax.plot(df_daily['date'], df_daily['ROI'], label='ROI')
ax.legend()
st.pyplot(fig)

# Top10 ROI 产品
st.subheader("Top10 ROI产品")
product_roi = df_filtered.groupby(['product_id', 'product_name']).agg({
    'gmv': 'sum',
    'cost': 'sum'
}).reset_index()
product_roi['ROI'] = product_roi['gmv'] / product_roi['cost']
top10 = product_roi.sort_values(by='ROI', ascending=False).head(10)
st.dataframe(top10)

# GMV 占比图
st.subheader("渠道GMV占比")
fig2, ax2 = plt.subplots()
ax2.pie(channel_summary['GMV占比'], labels=channel_summary['channel'], autopct='%1.1f%%')
st.pyplot(fig2)

# 拓展功能：渠道+品类组合分析
df_filtered['category'] = df_filtered['product_name'].apply(lambda x: x.split("_")[0] if '_' in x else 'Unknown')
combo = df_filtered.groupby(['channel', 'category']).agg({'gmv': 'sum', 'cost': 'sum'}).reset_index()
combo['ROI'] = combo['gmv'] / combo['cost']
st.subheader("渠道+品类组合 ROI 分析")
st.dataframe(combo.sort_values(by='ROI', ascending=False))

# 拓展功能：费用异常预警
st.subheader("费用异常预警（Top5成本异常天）")
channel_cost_alert = df_filtered.groupby(['date', 'channel'])['cost'].sum().reset_index()
cost_mean = channel_cost_alert.groupby('channel')['cost'].mean().reset_index(name='mean_cost')
cost_merged = channel_cost_alert.merge(cost_mean, on='channel')
cost_merged['异常程度'] = cost_merged['cost'] / cost_merged['mean_cost']
cost_alerts = cost_merged.sort_values(by='异常程度', ascending=False).head(5)
st.dataframe(cost_alerts)

st.caption("数据来源：营销数据平台 | 开发：数据团队")

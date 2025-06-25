# 渠道销售数据看板（Streamlit）

## 项目说明
本项目用于可视化展示各个渠道对销售的贡献，包括每日UV、GMV、ROI趋势、转化率、渠道GMV占比、Top10 ROI商品等。

## 使用方式（无需本地Python）
1. 注册并登录 [Streamlit Cloud](https://streamlit.io/cloud)
2. Fork 本项目或上传本文件夹至你的 GitHub 仓库
3. 在 Streamlit Cloud 点击 “New app”
   - 选择仓库
   - 指定主文件为：`dashboard.py`
4. 启动后即可获得链接访问数据看板

## 数据说明
数据文件：`channel_daily_data.csv`
字段说明：
- `date`: 日期
- `channel`: 渠道名（如 Google、Douyin）
- `product_name`: 商品名（用下划线区分品类）
- `uv`, `pv`, `gmv`, `cost`, `orders` 等为分析指标

# 渠道销售数据看板（Streamlit）

## 部署方式（推荐使用 Streamlit Cloud）

1. 注册登录：https://streamlit.io/cloud
2. 新建一个 GitHub 仓库，上传本文件夹下的所有文件（含 dashboard.py 和 CSV）
3. 在 Streamlit Cloud 创建新 app：
   - 选择你的 GitHub 仓库
   - 指定入口文件为 `dashboard.py`
   - 点击部署即可生成访问链接

## 数据字段说明

- `date`: 日期
- `channel`: 渠道名称（如 Google、Facebook）
- `product_name`: 商品名，前缀视为品类（如 beauty_mask001）
- 其他字段：UV、PV、GMV、Cost、订单数、点击数、毛利等

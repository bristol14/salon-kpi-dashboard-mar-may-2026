import pandas as pd
import streamlit as st
import plotly.express as px
import os
import sqlite3

st.write(os.path.abspath(__file__))
df = pd.read_excel("salon_3months_data.xlsx")

st.write(df["合計売上"].dtype)  # ← ここ
# ======================
# データ読み込み & 日付修正（ここ重要）
# ======================


df["日付"] = pd.to_datetime(df["日付"])
df["日付"] = df["日付"].dt.strftime("%Y-%m-%d")

stylist = st.selectbox("スタイリストを選択",["全員"] + list(df["スタイリスト"].unique()))

if stylist != "全員":
    df = df[df["スタイリスト"] == stylist]



st.subheader("KPI")

total_sales = df["合計売上"].sum()
total_customers = df["客数"].sum()
average_price = total_sales / total_customers
working_days = df["日付"].nunique()
working_hours = working_days * 8
Productivity = total_sales / working_hours 

col1,col2 = st.columns(2)
col3,col4 = st.columns(2)
with col1:
    st.metric("総売上",f"{total_sales:,.0f}円")

with col2:
    st.metric("総客数",f"{total_customers}人")

with col3:
    st.metric("平均客単価",f"{average_price:,.0f}円")

with col4:
    st.metric("1時間あたりの生産性",f"{Productivity:,.0f}円")

    










# ======================
# DB接続
# ======================
conn = sqlite3.connect("sales.DB")
df.to_sql("sales", conn, if_exists="replace", index=False)


# ======================
# 月別売上
# ======================
result = pd.read_sql("""
SELECT 
 スタイリスト,
 sum(指名客数) * 1.0/sum(客数) AS 指名率,
 substr(日付,1,7) AS 月                    

FROM sales
GROUP BY スタイリスト,月
""", conn)

st.subheader("(各スタイリスト)指名率")

fig7 = px.bar(
    result,
    x = "月",
    y = "指名率",
    color = "スタイリスト"
    )
st.plotly_chart(fig7)

# ======================
# 月別スタイリスト売上
# ======================
result1 = pd.read_sql("""
SELECT
 substr(日付,1,7) AS 月,
 スタイリスト,
 sum(合計売上) AS 売上
FROM sales
GROUP BY 月, スタイリスト
ORDER BY 月, スタイリスト
""", conn)

st.subheader("(月別スタイリスト) 技術+店販 総売上")

result1["月"] = pd.to_datetime(result1["月"])
result1 = result1.sort_values(["月","スタイリスト"])
result1["月"] = result1["月"].dt.strftime("%Y年%-m月")
result1["売上"] = pd.to_numeric(result1["売上"])

fig = px.bar(
    result1,
    x="月",
    y="売上",
    color="スタイリスト",
    barmode="group"
)

fig.update_layout(
    yaxis=dict(tickformat=",.0f")
)

st.plotly_chart(fig)

# ======================
# 技術売上
# ======================
result3 = pd.read_sql("""
SELECT
 substr(日付,1,7) AS 月,
 スタイリスト,
 sum(技術売上) AS 技売
FROM sales
GROUP BY 月, スタイリスト
ORDER BY 月, スタイリスト
""", conn)

result3["月"] = pd.to_datetime(result3["月"])
result3 = result3.sort_values(["月","スタイリスト"])
result3["月"] = result3["月"].dt.strftime("%Y年%-m月")
result3["技売"] = pd.to_numeric(result3["技売"])

fig1 = px.bar(
    result3,
    x="月",
    y="技売",
    labels={"技売":"技術売上(円)"},
    color="スタイリスト",
    barmode="group"
)

fig1.update_layout(
    yaxis=dict(tickformat=",.0f")
)

st.plotly_chart(fig1)

# ======================
# 曜日別売上（ここが今回の修正ポイント）
# ======================
result4 = pd.read_sql("""
SELECT
 CASE strftime('%w', date(日付)) 
  WHEN '0' THEN '日'
  WHEN '1' THEN '月'
  WHEN '2' THEN '火'
  WHEN '3' THEN '水'
  WHEN '4' THEN '木'
  WHEN '5' THEN '金'
  WHEN '6' THEN '土'  
 END AS 曜日,                   
 スタイリスト,
 sum(合計売上) AS 売上
FROM sales
GROUP BY strftime('%w', date(日付)), スタイリスト
ORDER BY strftime('%w', date(日付)), スタイリスト
""", conn)

st.subheader("(曜日別)スタイリスト売上合計")

# 曜日順を固定（重要）
order = ["月","火","水","木","金","土","日"]
result4["曜日"] = pd.Categorical(result4["曜日"], categories=order, ordered=True)
result4 = result4.sort_values("曜日")

fig2 = px.bar(
    result4,
    x="曜日",
    y="売上",
    color="スタイリスト"
)

st.plotly_chart(fig2)


fig2 = px.bar(
    result4,
    x="曜日",
    y="売上",
    color="スタイリスト",
    facet_col="スタイリスト",  # スタイリスト毎に表示する
    facet_col_wrap=2,
    title = "客数と客単価の関係" # ←2列表示
)

st.plotly_chart(fig2)
st.subheader("スタイリスト別の売上構造分析")

fig3 = px.scatter( #合計売上が客数に起因してるのかどうかを調べる
    df,
    x = "客数",
    y = "合計売上",
    color = "スタイリスト",
    facet_col = "スタイリスト",
    facet_col_wrap = 2,
    trendline = "ols",
    title="客数と売上の関係"
    )
st.plotly_chart(fig3)


df["客単価"] = df["合計売上"] / df["客数"]
df["指名率"] = df["指名客数"] / df["客数"]

fig5 = px.scatter(
    df,
    x = "客数",
    y = "客単価",
    size = "合計売上",
    color = "スタイリスト",
    title = "客数・客単価・売上の関係"
    )

st.plotly_chart(fig5)

fig6 = px.scatter(
    df,
    x = "指名率",
    y = "客単価",
    color = "スタイリスト",
    size = "合計売上",
    title = "指名率・客単価・売上の関係"
    )

st.plotly_chart(fig6)



# ======================
# DB閉じる
# ======================
conn.close()

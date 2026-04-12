import pandas as pd
import streamlit as st




df = pd.read_excel("サロンファイル")#pandasでエクセルファイルを読み込んで、それをdfとする

conn = sqlite3.connect("sql用のフォルダ")

df.to_sql("サロンファイル",conn,if_exist = "replace",)

SELECT
 
 substr(日付,1,7) AS 月,
 sum(合計売上) AS 売上

FROM
 sales.DB

GROUP BY 月


 



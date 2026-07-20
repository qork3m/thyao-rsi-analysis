import pandas as pd
from dotenv import load_dotenv
import os
from functions import get_evds_series, get_stock_data, calculate_rsi
import sqlite3

load_dotenv()
api_key = os.getenv('EVDS_API_KEY')

folder_name = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(folder_name, "thyao_bist.db")
connection = sqlite3.connect(db_path)

df_THYAO = get_stock_data("THYAO.IS", start='2022-01-01', end='2026-07-02')

df_THYAO = df_THYAO["Close"].squeeze().reset_index()

df_THYAO["RSI"] = calculate_rsi(df_THYAO["THYAO.IS"])

df_THYAO.to_sql("thyao_df", connection, if_exists="replace", index=False)

df_interest_rates = get_evds_series(
    api_key, ['TP.BISPOLFAIZ.TUR'], '01-01-2022', '02-07-2026')

df_interest_rates = df_interest_rates.squeeze().reset_index()

df_interest_rates.to_sql("interest_df", connection,
                         if_exists="replace", index=False)

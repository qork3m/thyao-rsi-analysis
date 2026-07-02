import pandas as pd
import matplotlib.pyplot as plt
import evds
import yfinance as yf
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('EVDS_API_KEY')


def get_evds_series(api_key, series_codes, startdate, enddate, frequency=5):
    tcmb = evds.evdsAPI(api_key)
    df = tcmb.get_data(series_codes, startdate=startdate,
                       enddate=enddate, frequency=frequency)
    df["Tarih"] = pd.to_datetime(df["Tarih"])
    df.set_index("Tarih", inplace=True)
    return df


def get_stock_data(ticker, start, end):
    df = yf.download(ticker, start=start, end=end)
    return df


def calculate_rsi(series, span=14):
    diff = series.diff()
    gains = diff.where(diff > 0, 0)
    losses = diff.where(diff < 0, 0)
    avg_gains = gains.ewm(span=14, adjust=False).mean()
    avg_losses = - losses.ewm(span=span, adjust=False).mean()
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    return rsi


df_THYAO = get_stock_data("THYAO.IS", start='2022-01-01', end='2026-07-02')
df_THYAO["RSI"] = calculate_rsi(df_THYAO["Close"])

df_interest_rates = get_evds_series(
    api_key, ['TP.BISPOLFAIZ.TUR'], '01-01-2022', '02-07-2026')

# "diff" değişkenine bir önceki döneme göre politika faiz kararında bir değişiklik var mı onu atıyoruz.
diff = df_interest_rates['TP_BISPOLFAIZ_TUR'].diff()

# Yukarıdaki diff değişkenine atadıklarımızı "NaN" içermeyecek ve "diff" 0 olmayacak şekilde atıyoruz.
df_interest_rate_change_pos = df_interest_rates[(diff > 0) & (diff.notna())]
df_interest_rate_change_neg = df_interest_rates[(diff < 0) & (diff.notna())]

# çıkan verilerin tarihlerini farklı bir DF'e atıyoruz.
df_interest_rate_change_pos_dates = df_interest_rate_change_pos.index
df_interest_rate_change_neg_dates = df_interest_rate_change_neg.index

# 2 Satır, 1 Sütundan oluşan altlı üstlü iki pencere açıyoruz.
# gridspec_kw ile üst pencereyi (fiyat) daha büyük, alt pencereyi (RSI) daha dar yapıyoruz.
fig, (ax1, ax2) = plt.subplots(nrows=2, ncols=1, figsize=(
    14, 8), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

ax1.plot(df_THYAO.index, df_THYAO['Close'], color='black', label='THYAO')

for tarih in df_interest_rate_change_pos_dates:
    ax1.axvline(x=tarih, color='green',
                linestyle='--', linewidth=1, alpha=0.5)

for tarih in df_interest_rate_change_neg_dates:
    ax1.axvline(x=tarih, color='red',
                linestyle='--', linewidth=1, alpha=0.5)

ax1.set_title("THYAO Price & RSI vs. CBRT Interest Rate Decisions (2022-2026)",
              fontsize=14, fontweight='bold')
ax1.legend(loc='upper left')

ax1.text(0.99, 0.98, "Sources: TCMB, Yfinance",
         transform=ax1.transAxes,
         ha='right', va='top',
         fontsize=9, color='gray', fontstyle='italic')

# RSI
ax2.plot(df_THYAO.index, df_THYAO['RSI'], color='purple', label='RSI (14)')

# RSI'ın 70 ve 30 bariyerlerini çiziyoruz
ax2.axhline(70, color='red', linestyle='--', alpha=0.5)
ax2.axhline(30, color='green', linestyle='--', alpha=0.5)

# Her bir endeks için tarihleri döndürüp dikey çizgi ekliyoruz o tarihlere.
for tarih in df_interest_rate_change_pos_dates:
    ax2.axvline(x=tarih, color='green',
                linestyle='--', linewidth=1, alpha=0.5)

for tarih in df_interest_rate_change_neg_dates:
    ax2.axvline(x=tarih, color='red',
                linestyle='--', linewidth=1, alpha=0.5)

ax2.set_ylabel("RSI")
ax2.legend(loc='upper left')

plt.tight_layout()
plt.show()

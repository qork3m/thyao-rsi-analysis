import yfinance as yf
import pandas as pd
import evds


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

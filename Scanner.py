import yfinance as yf
import pandas as pd


def calculate_score(df):

    if df is None or len(df) < 35:
        return None

    try:

        # แก้ MultiIndex ของ yfinance
        if hasattr(df.columns, "nlevels") and df.columns.nlevels > 1:
            df.columns = df.columns.get_level_values(0)

        close = df["Close"].astype(float)
        high = df["High"].astype(float)
        low = df["Low"].astype(float)

        # ======================
        # RSI 14
        # ======================

        delta = close.diff()

        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)

        avg_gain = gain.rolling(14).mean()
        avg_loss = loss.rolling(14).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        rsi_val = float(rsi.iloc[-1])

        # ======================
        # STOCH 14
        # ======================

        lowest_low = low.rolling(14).min()
        highest_high = high.rolling(14).max()

        stoch = (
            (close - lowest_low)
            / (highest_high - lowest_low)
        ) * 100

        sto_val = float(stoch.iloc[-1])

        # ======================
        # SMA10
        # ======================

        sma10 = close.rolling(10).mean()

        sma_val = float(sma10.iloc[-1])

        price = float(close.iloc[-1])

        # ======================
        # MACD
        # ======================

        ema12 = close.ewm(span=12, adjust=False).mean()
        ema26 = close.ewm(span=26, adjust=False).mean()

        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()

        hist = macd - signal

        hist_now = float(hist.iloc[-1])
        hist_prev = float(hist.iloc[-2])

        # ======================
        # RSI Score
        # ======================

        if rsi_val < 30:
            rsiScore = 50
        elif rsi_val < 40:
            rsiScore = 40
        elif rsi_val < 50:
            rsiScore = 25
        elif rsi_val < 60:
            rsiScore = 10
        else:
            rsiScore = 0

        # ======================
        # STO Score
        # ======================

        if sto_val < 20:
            stoScore = 30
        elif sto_val < 40:
            stoScore = 20
        elif sto_val < 60:
            stoScore = 10
        else:
            stoScore = 0

        # ======================
        # SMA Score
        # ======================

        smaScore = 20 if price < sma_val else 0

        score = rsiScore + stoScore + smaScore

        # ======================
        # STATUS
        # ======================

        if score >= 80:
            status = "STRONG DCA"
        elif score >= 60:
            status = "DCA"
        elif score >= 40:
            status = "WATCH"
        else:
            status = "AVOID"

        # ======================
        # MOMENTUM
        # ======================

        if hist_now < 0 and hist_now > hist_prev:
            momentum = "WEAK BEAR"

        elif hist_now < 0 and hist_now < hist_prev:
            momentum = "STRONG BEAR"

        elif hist_now > 0 and hist_now < hist_prev:
            momentum = "WEAK BULL"

        else:
            momentum = "STRONG BULL"

        return {
            "status": status,
            "score": int(score),

            "price": round(price, 2),

            "rsi": round(rsi_val, 1),
            "sto": round(sto_val, 1),
            "sma": round(sma_val, 2),

            "rsiScore": int(rsiScore),
            "stoScore": int(stoScore),
            "smaScore": int(smaScore),

            "momentum": momentum
        }

    except Exception as e:

        print("calculate_score error:", e)
        return None

def analyze_symbol(symbol):
    
    try:

        day_df = yf.download(
            symbol,
            period="1y",
            interval="1d",
            progress=False,
            auto_adjust=True
        )

        week_df = yf.download(
            symbol,
            period="5y",
            interval="1wk",
            progress=False,
            auto_adjust=True
        )

        return {
            "symbol": symbol,
            "day": calculate_score(day_df),
            "week": calculate_score(week_df)
        }

    except Exception as e:

        print(symbol, e)
        return None
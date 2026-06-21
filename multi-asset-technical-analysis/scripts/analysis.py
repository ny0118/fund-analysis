#!/usr/bin/env python3
"""
多品种多周期技术分析脚本
分析6个核心品种（BTC, ETH, GOLD, SPX, OIL, NDX）的5个周期技术指标
输出 result.json 供 HTML 报告使用
"""

import json
import time
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ============================================================
# 品种定义
# ============================================================
ASSETS = [
    {"key": "BTC", "name": "比特币", "source": "binance", "symbol": "BTCUSDT", "category": "加密货币"},
    {"key": "ETH", "name": "以太坊", "source": "binance", "symbol": "ETHUSDT", "category": "加密货币"},
    {"key": "GOLD", "name": "黄金(XAU)", "source": "binance", "symbol": "XAUTUSDT", "category": "大宗商品"},
    {"key": "SPX", "name": "标普500", "source": "akshare", "symbol": "SPY", "category": "股票指数"},
    {"key": "OIL", "name": "原油(WTI)", "source": "akshare", "symbol": "USO", "category": "大宗商品"},
    {"key": "NDX", "name": "纳斯达克100", "source": "akshare", "symbol": "QQQ", "category": "股票指数"},
]

PERIODS = ["daily", "weekly", "monthly", "quarterly", "yearly"]
PERIOD_CN = {
    "daily": "日线", "weekly": "周线", "monthly": "月线",
    "quarterly": "季线", "yearly": "年线"
}

# ============================================================
# 数据获取
# ============================================================

def fetch_binance_klines(symbol, interval="1d", limit=730):
    """从 Binance API 获取K线数据"""
    url = "http://data-api.binance.vision/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    records = []
    for item in data:
        records.append({
            "date": datetime.fromtimestamp(item[0] / 1000).strftime("%Y-%m-%d"),
            "open": float(item[1]),
            "high": float(item[2]),
            "low": float(item[3]),
            "close": float(item[4]),
            "volume": float(item[5]),
            "quote_volume": float(item[7]),  # USDT 交易额
        })
    df = pd.DataFrame(records)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    return df


def fetch_akshare_daily(symbol):
    """从 akshare 获取美股ETF日线数据"""
    import akshare as ak
    df = ak.stock_us_daily(symbol=symbol, adjust="qfq")
    # akshare 返回的列名可能是中文
    df = df.rename(columns={
        "date": "date", "open": "open", "high": "high",
        "low": "low", "close": "close", "volume": "volume"
    })
    # 确保列名正确
    col_map = {}
    for c in df.columns:
        cl = c.lower()
        if cl in ["date", "open", "high", "low", "close", "volume"]:
            col_map[c] = cl
    df = df.rename(columns=col_map)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date").reset_index(drop=True)
    # 确保数值列是 float
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def get_daily_data(asset):
    """根据品种获取日线数据"""
    if asset["source"] == "binance":
        return fetch_binance_klines(asset["symbol"])
    else:
        return fetch_akshare_daily(asset["symbol"])


# ============================================================
# 数据重采样
# ============================================================

def resample_to_periods(daily_df):
    """将日线数据重采样为周线/月线/季线/年线"""
    df = daily_df.set_index("date").copy()
    result = {}

    # 日线
    result["daily"] = df.reset_index()

    # 周线 - 按ISO周，取每周最后一个交易日的数据
    weekly = df.resample("W-FRI").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna(subset=["close"])
    result["weekly"] = weekly.reset_index().rename(columns={"date": "date"})

    # 月线
    monthly = df.resample("ME").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna(subset=["close"])
    result["monthly"] = monthly.reset_index().rename(columns={"date": "date"})

    # 季线
    quarterly = df.resample("QE").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna(subset=["close"])
    result["quarterly"] = quarterly.reset_index().rename(columns={"date": "date"})

    # 年线
    yearly = df.resample("YE").agg({
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }).dropna(subset=["close"])
    result["yearly"] = yearly.reset_index().rename(columns={"date": "date"})

    return result


# ============================================================
# 技术指标计算
# ============================================================

def calc_ema(series, period):
    """计算EMA"""
    return series.ewm(span=period, adjust=False).mean()


def calc_ema_signal(df):
    """EMA(12,52) 交叉信号"""
    close = df["close"]
    ema12 = calc_ema(close, 12)
    ema52 = calc_ema(close, 52)

    if len(close) < 53:
        return 0, "数据不足，无法计算EMA(12,52)"

    # 当前状态
    curr_above = ema12.iloc[-1] > ema52.iloc[-1]
    prev_above = ema12.iloc[-2] > ema52.iloc[-2]

    if curr_above and not prev_above:
        return 1, "EMA12上穿EMA52"
    elif not curr_above and prev_above:
        return -1, "EMA12下穿EMA52"
    else:
        if curr_above:
            return 0, "EMA12位于EMA52上方，未发生交叉"
        else:
            return 0, "EMA12位于EMA52下方，未发生交叉"


def calc_macd_signal(df):
    """MACD(12,26,9) 信号"""
    close = df["close"]
    ema12 = calc_ema(close, 12)
    ema26 = calc_ema(close, 26)
    dif = ema12 - ema26
    dea = calc_ema(dif, 9)
    histogram = 2 * (dif - dea)

    if len(close) < 27:
        return 0, "数据不足，无法计算MACD"

    curr_hist = histogram.iloc[-1]
    prev_hist = histogram.iloc[-2]
    curr_dif = dif.iloc[-1]

    # 柱状线由负转正 或 DIF上穿零轴
    hist_cross_up = (curr_hist > 0 and prev_hist <= 0)
    dif_cross_up = (curr_dif > 0 and dif.iloc[-2] <= 0)
    hist_cross_down = (curr_hist < 0 and prev_hist >= 0)
    dif_cross_down = (curr_dif < 0 and dif.iloc[-2] >= 0)

    if hist_cross_up or dif_cross_up:
        return 1, "MACD柱状线由负转正/DIF上穿零轴"
    elif hist_cross_down or dif_cross_down:
        return -1, "MACD柱状线由正转负/DIF下穿零轴"
    else:
        if curr_hist > 0:
            return 0, "MACD柱状线为正，未发生转换"
        elif curr_hist < 0:
            return 0, "MACD柱状线为负，未发生转换"
        else:
            return 0, "MACD柱状线为零，未发生转换"


def calc_rsi(close, period=14):
    """RSI 使用 Wilder 平滑法"""
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = (-delta).where(delta < 0, 0.0)

    # Wilder 平滑: 使用 EMA (alpha = 1/period)
    avg_gain = gain.ewm(alpha=1.0/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1.0/period, min_periods=period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi


def calc_rsi_signal(df):
    """RSI(14) 信号"""
    close = df["close"]
    rsi = calc_rsi(close, 14)

    if len(close) < 16:
        return 0, "数据不足，无法计算RSI"

    curr_rsi = rsi.iloc[-1]
    prev_rsi = rsi.iloc[-2]

    # RSI从30以下向上突破
    if prev_rsi < 30 and curr_rsi >= 30:
        return 1, f"RSI从超卖区回升（{prev_rsi:.1f}→{curr_rsi:.1f}）"
    # RSI从70以上向下跌破
    elif prev_rsi > 70 and curr_rsi <= 70:
        return -1, f"RSI从超买区回落（{prev_rsi:.1f}→{curr_rsi:.1f}）"
    else:
        if curr_rsi < 30:
            return 0, f"RSI处于超卖区（{curr_rsi:.1f}），未突破30"
        elif curr_rsi > 70:
            return 0, f"RSI处于超买区（{curr_rsi:.1f}），未跌破70"
        else:
            return 0, f"RSI中性（{curr_rsi:.1f}），未突破阈值"


def calc_kdj(df, n=9, m1=3, m2=3):
    """KDJ 指标"""
    low_list = df["low"].rolling(window=n, min_periods=n).min()
    high_list = df["high"].rolling(window=n, min_periods=n).max()

    rsv = (df["close"] - low_list) / (high_list - low_list) * 100
    rsv = rsv.fillna(50)  # 没有足够数据时设为50

    # 使用 Wilder 平滑法
    k = rsv.ewm(alpha=1.0/m1, adjust=False).mean()
    d = k.ewm(alpha=1.0/m2, adjust=False).mean()
    j = 3 * k - 2 * d

    return k, d, j


def calc_kdj_signal(df):
    """KDJ(9,3,3) 信号"""
    if len(df) < 10:
        return 0, "数据不足，无法计算KDJ"

    k, d, j = calc_kdj(df)
    curr_j = j.iloc[-1]

    if curr_j < 0:
        return 1, f"J值极端超卖（{curr_j:.1f}）"
    elif curr_j > 100:
        return -1, f"J值极端超买（{curr_j:.1f}）"
    else:
        return 0, f"J值中性（{curr_j:.1f}），未进入极端区间"


def calc_boll_signal(df, period=20, std_mult=2):
    """BOLL(20,2) 信号"""
    close = df["close"]
    if len(close) < period:
        return 0, "数据不足，无法计算BOLL"

    mid = close.rolling(window=period).mean()
    std = close.rolling(window=period).std()
    upper = mid + std_mult * std
    lower = mid - std_mult * std

    curr_close = close.iloc[-1]
    curr_upper = upper.iloc[-1]
    curr_lower = lower.iloc[-1]
    prev_close = close.iloc[-2]
    prev_upper = upper.iloc[-2]
    prev_lower = lower.iloc[-2]

    # 价格突破上轨（超买逃顶）记-1
    if prev_close <= prev_upper and curr_close > curr_upper:
        return -1, f"价格突破BOLL上轨（超买逃顶）"
    # 价格跌破下轨（超卖抄底）记+1
    elif prev_close >= prev_lower and curr_close < curr_lower:
        return 1, f"价格跌破BOLL下轨（超卖抄底）"
    else:
        if curr_close > curr_upper:
            return 0, f"价格在上轨上方运行"
        elif curr_close < curr_lower:
            return 0, f"价格在下轨下方运行"
        else:
            return 0, f"价格在BOLL轨道内运行"


# ============================================================
# 单品种全周期分析
# ============================================================

def analyze_asset(asset):
    """分析单个品种的所有周期"""
    print(f"  正在获取 {asset['key']} ({asset['name']}) 数据...")
    try:
        daily_df = get_daily_data(asset)
    except Exception as e:
        print(f"  [错误] 获取 {asset['key']} 数据失败: {e}")
        return None

    if daily_df is None or len(daily_df) < 60:
        print(f"  [错误] {asset['key']} 数据量不足: {len(daily_df) if daily_df is not None else 0} 条")
        return None

    print(f"  获取到 {len(daily_df)} 条日线数据")

    # 重采样
    period_dfs = resample_to_periods(daily_df)

    # 当前价格和日期
    current_price = float(daily_df["close"].iloc[-1])
    current_date = daily_df["date"].iloc[-1].strftime("%Y-%m-%d")

    # 日均交易额
    if "quote_volume" in daily_df.columns:
        avg_daily_volume_usd = float(daily_df["quote_volume"].tail(365).mean())
    else:
        daily_df["notional"] = daily_df["close"] * daily_df["volume"]
        avg_daily_volume_usd = float(daily_df["notional"].tail(365).mean())

    # 各周期分析
    analysis = {}
    total_right_pos = 0
    total_right_neg = 0
    total_left_pos = 0
    total_left_neg = 0

    # 各周期所需的最小数据量
    min_data_map = {
        "daily": 30,
        "weekly": 15,
        "monthly": 10,
        "quarterly": 6,
        "yearly": 3,
    }

    for period in PERIODS:
        pdf = period_dfs[period]
        min_data = min_data_map[period]
        if len(pdf) < min_data:
            analysis[period] = {
                "last_close": None,
                "last_date": None,
                "ema": {"score": 0, "detail": "数据不足"},
                "macd": {"score": 0, "detail": "数据不足"},
                "rsi": {"score": 0, "detail": "数据不足"},
                "kdj": {"score": 0, "detail": "数据不足"},
                "boll": {"score": 0, "detail": "数据不足"},
                "right_positive": 0, "right_negative": 0,
                "left_positive": 0, "left_negative": 0,
            }
            continue

        last_close = float(pdf["close"].iloc[-1])
        last_date = pdf["date"].iloc[-1].strftime("%Y-%m-%d") if hasattr(pdf["date"].iloc[-1], "strftime") else str(pdf["date"].iloc[-1])

        # 计算各指标
        ema_score, ema_detail = calc_ema_signal(pdf)
        macd_score, macd_detail = calc_macd_signal(pdf)
        rsi_score, rsi_detail = calc_rsi_signal(pdf)
        kdj_score, kdj_detail = calc_kdj_signal(pdf)
        boll_score, boll_detail = calc_boll_signal(pdf)

        # 右侧正负分
        rp = sum(1 for s in [ema_score, macd_score] if s > 0)
        rn = sum(1 for s in [ema_score, macd_score] if s < 0)
        # 左侧正负分
        lp = sum(1 for s in [rsi_score, kdj_score, boll_score] if s > 0)
        ln = sum(1 for s in [rsi_score, kdj_score, boll_score] if s < 0)

        total_right_pos += rp
        total_right_neg += rn
        total_left_pos += lp
        total_left_neg += ln

        analysis[period] = {
            "last_close": round(last_close, 4),
            "last_date": last_date,
            "ema": {"score": ema_score, "detail": ema_detail},
            "macd": {"score": macd_score, "detail": macd_detail},
            "rsi": {"score": rsi_score, "detail": rsi_detail},
            "kdj": {"score": kdj_score, "detail": kdj_detail},
            "boll": {"score": boll_score, "detail": boll_detail},
            "right_positive": rp,
            "right_negative": rn,
            "left_positive": lp,
            "left_negative": ln,
        }

    # 综合信号
    has_pos = (total_right_pos + total_left_pos) > 0
    has_neg = (total_right_neg + total_left_neg) > 0
    if has_pos and not has_neg:
        composite = "偏多"
    elif has_neg and not has_pos:
        composite = "偏空"
    elif has_pos and has_neg:
        composite = "分化"
    else:
        composite = "中性"

    result = {
        "name": asset["name"],
        "symbol": asset["symbol"],
        "category": asset["category"],
        "current_price": round(current_price, 4),
        "current_date": current_date,
        "avg_daily_volume_usd": round(avg_daily_volume_usd, 2),
        "composite_signal": composite,
        "composite_scores": {
            "right_positive": total_right_pos,
            "right_negative": total_right_neg,
            "left_positive": total_left_pos,
            "left_negative": total_left_neg,
        },
        "analysis": analysis,
    }

    print(f"  {asset['key']} 分析完成: {composite} (右侧+{total_right_pos}/-{total_right_neg}, 左侧+{total_left_pos}/-{total_left_neg})")
    return result


# ============================================================
# 主函数
# ============================================================

def main():
    print("=" * 60)
    print(f"多品种多周期技术分析 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {}

    for i, asset in enumerate(ASSETS):
        print(f"\n[{i+1}/{len(ASSETS)}] 分析 {asset['key']} ({asset['name']})")
        try:
            result = analyze_asset(asset)
            if result is not None:
                results[asset["key"]] = result
        except Exception as e:
            print(f"  [错误] 分析 {asset['key']} 时发生异常: {e}")
            import traceback
            traceback.print_exc()

        # 请求间延迟
        if i < len(ASSETS) - 1:
            time.sleep(0.4)

    # 输出结果
    output_path = "/workspace/multi-asset-technical-analysis/scripts/result.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"分析完成! 共 {len(results)} 个品种")
    print(f"结果已保存到: {output_path}")
    print("=" * 60)


if __name__ == "__main__":
    main()

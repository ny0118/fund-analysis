#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多品类右侧交易技术分析脚本（扩展品种）
数据源：Binance API, Gate.io API, akshare
技术指标：EMA(12,52) + MACD(12,26,9)
分析周期：日线/周线/月线/季线/年线

适配 GitHub Actions 自动化部署：
- 输出路径使用相对路径（相对于项目根目录）
- 每个 HTTP 请求之间加 1 秒延迟防止限流
- 单个品种失败时跳过继续处理其他品种
"""

import json
import time
import requests
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import warnings
import sys
import os

warnings.filterwarnings('ignore')

# ============================================================
# 品种定义
# ============================================================

CATEGORIES = {
    "外汇": [
        {"symbol": "FXE", "name": "欧元/美元", "source": "akshare", "ticker": "FXE"},
        {"symbol": "FXY", "name": "美元/日元", "source": "akshare", "ticker": "FXY"},
        {"symbol": "FXB", "name": "英镑/美元", "source": "akshare", "ticker": "FXB"},
        {"symbol": "FXA", "name": "澳元/美元", "source": "akshare", "ticker": "FXA"},
        {"symbol": "FXC", "name": "加元/美元", "source": "akshare", "ticker": "FXC"},
        {"symbol": "FXS", "name": "美元/瑞郎", "source": "akshare", "ticker": "FXS"},
        {"symbol": "FXF", "name": "美元/瑞典克朗", "source": "akshare", "ticker": "FXF"},
    ],
    "债券/利率": [
        {"symbol": "TLT", "name": "20+年美国国债", "source": "akshare", "ticker": "TLT"},
        {"symbol": "SHY", "name": "1-3年美国国债", "source": "akshare", "ticker": "SHY"},
        {"symbol": "IEF", "name": "7-10年美国国债", "source": "akshare", "ticker": "IEF"},
        {"symbol": "LQD", "name": "投资级企业债", "source": "akshare", "ticker": "LQD"},
        {"symbol": "HYG", "name": "高收益企业债", "source": "akshare", "ticker": "HYG"},
        {"symbol": "EMB", "name": "新兴市场美元债", "source": "akshare", "ticker": "EMB"},
        {"symbol": "AGG", "name": "美国综合债券", "source": "akshare", "ticker": "AGG"},
    ],
    "大宗商品": [
        {"symbol": "SLV", "name": "白银", "source": "akshare", "ticker": "SLV"},
        {"symbol": "DBA", "name": "农产品综合", "source": "akshare", "ticker": "DBA"},
        {"symbol": "DBB", "name": "基础金属综合", "source": "akshare", "ticker": "DBB"},
        {"symbol": "DBE", "name": "能源综合", "source": "akshare", "ticker": "DBE"},
        {"symbol": "PALL", "name": "钯金", "source": "akshare", "ticker": "PALL"},
        {"symbol": "CPER", "name": "铜", "source": "akshare", "ticker": "CPER"},
        {"symbol": "JJC", "name": "铜期货", "source": "akshare", "ticker": "JJC"},
        {"symbol": "URA", "name": "铀/核能", "source": "akshare", "ticker": "URA"},
        {"symbol": "LIT", "name": "锂", "source": "akshare", "ticker": "LIT"},
        {"symbol": "REMX", "name": "稀土", "source": "akshare", "ticker": "REMX"},
        {"symbol": "GDX", "name": "金矿股", "source": "akshare", "ticker": "GDX"},
        {"symbol": "SIL", "name": "银矿股", "source": "akshare", "ticker": "SIL"},
        {"symbol": "COPX", "name": "铜矿股", "source": "akshare", "ticker": "COPX"},
        {"symbol": "XOP", "name": "油气勘探", "source": "akshare", "ticker": "XOP"},
        {"symbol": "OIH", "name": "油气服务", "source": "akshare", "ticker": "OIH"},
    ],
    "股票指数": [
        {"symbol": "IWM", "name": "罗素2000", "source": "akshare", "ticker": "IWM"},
        {"symbol": "EFA", "name": "发达市场", "source": "akshare", "ticker": "EFA"},
        {"symbol": "EEM", "name": "新兴市场", "source": "akshare", "ticker": "EEM"},
        {"symbol": "VGK", "name": "欧洲", "source": "akshare", "ticker": "VGK"},
        {"symbol": "EWJ", "name": "日本", "source": "akshare", "ticker": "EWJ"},
        {"symbol": "EWZ", "name": "巴西", "source": "akshare", "ticker": "EWZ"},
        {"symbol": "FXI", "name": "中国", "source": "akshare", "ticker": "FXI"},
        {"symbol": "INDA", "name": "印度", "source": "akshare", "ticker": "INDA"},
        {"symbol": "XLF", "name": "金融", "source": "akshare", "ticker": "XLF"},
        {"symbol": "XLK", "name": "科技", "source": "akshare", "ticker": "XLK"},
        {"symbol": "XLE", "name": "能源", "source": "akshare", "ticker": "XLE"},
        {"symbol": "XLI", "name": "工业", "source": "akshare", "ticker": "XLI"},
        {"symbol": "XLP", "name": "必需消费", "source": "akshare", "ticker": "XLP"},
        {"symbol": "XLU", "name": "公用事业", "source": "akshare", "ticker": "XLU"},
        {"symbol": "XLV", "name": "医疗", "source": "akshare", "ticker": "XLV"},
        {"symbol": "XLB", "name": "原材料", "source": "akshare", "ticker": "XLB"},
        {"symbol": "VNQ", "name": "房地产", "source": "akshare", "ticker": "VNQ"},
        {"symbol": "SMH", "name": "半导体", "source": "akshare", "ticker": "SMH"},
        {"symbol": "IBB", "name": "生物科技", "source": "akshare", "ticker": "IBB"},
        {"symbol": "XBI", "name": "生物科技小盘", "source": "akshare", "ticker": "XBI"},
        {"symbol": "KRE", "name": "地区银行", "source": "akshare", "ticker": "KRE"},
        {"symbol": "XRT", "name": "零售", "source": "akshare", "ticker": "XRT"},
        {"symbol": "XHB", "name": "住宅建筑", "source": "akshare", "ticker": "XHB"},
    ],
    "货币": [
        {"symbol": "UUP", "name": "美元指数", "source": "akshare", "ticker": "UUP"},
    ],
    "加密货币": [
        {"symbol": "BNB", "name": "BNB", "source": "binance", "pair": "BNBUSDT"},
        {"symbol": "SOL", "name": "SOL", "source": "binance", "pair": "SOLUSDT"},
        {"symbol": "XRP", "name": "XRP", "source": "binance", "pair": "XRPUSDT"},
        {"symbol": "ADA", "name": "ADA", "source": "binance", "pair": "ADAUSDT"},
        {"symbol": "DOT", "name": "DOT", "source": "binance", "pair": "DOTUSDT"},
        {"symbol": "LINK", "name": "LINK", "source": "binance", "pair": "LINKUSDT"},
        {"symbol": "AVAX", "name": "AVAX", "source": "binance", "pair": "AVAXUSDT"},
        {"symbol": "DOGE", "name": "DOGE", "source": "binance", "pair": "DOGEUSDT"},
        {"symbol": "LTC", "name": "LTC", "source": "binance", "pair": "LTCUSDT"},
        {"symbol": "TRX", "name": "TRX", "source": "binance", "pair": "TRXUSDT"},
        {"symbol": "OKB", "name": "OKB", "source": "gateio", "pair": "OKB_USDT"},
        {"symbol": "GT", "name": "GT", "source": "gateio", "pair": "GT_USDT"},
        {"symbol": "HYPE", "name": "HYPE", "source": "gateio", "pair": "HYPE_USDT"},
        {"symbol": "MNT", "name": "MNT", "source": "gateio", "pair": "MNT_USDT"},
    ],
}


# ============================================================
# 数据获取函数
# ============================================================

def get_binance_klines(pair, interval='1d', limit=1000):
    """从Binance API获取K线数据"""
    url = "http://data-api.binance.vision/api/v3/klines"
    params = {
        'symbol': pair,
        'interval': interval,
        'limit': limit
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        df = pd.DataFrame(data, columns=[
            'timestamp', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_volume', 'trades', 'taker_buy_base',
            'taker_buy_quote', 'ignore'
        ])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        for col in ['open', 'high', 'low', 'close', 'volume', 'quote_volume']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  [ERROR] Binance {pair} 获取失败: {e}")
        return None


def get_gateio_klines(pair, interval='1d', limit=1000):
    """从Gate.io API获取K线数据
    返回格式: [timestamp, volume, open, high, low, close, amount, is_closed]
    注意: 最新在前，需要反转
    """
    url = "https://api.gateio.ws/api/v4/spot/candlesticks"
    params = {
        'currency_pair': pair,
        'interval': interval,
        'limit': limit
    }
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None
        # Gate.io返回最新在前，需要反转
        data = data[::-1]
        df = pd.DataFrame(data, columns=[
            'timestamp', 'volume', 'open', 'high', 'low', 'close', 'amount', 'is_closed'
        ])
        df['date'] = pd.to_datetime(df['timestamp'], unit='s')
        for col in ['volume', 'open', 'high', 'low', 'close', 'amount']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        # Gate.io的quote_volume需要用 amount 字段（USDT成交额）
        df['quote_volume'] = df['amount']
        df = df.sort_values('date').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  [ERROR] Gate.io {pair} 获取失败: {e}")
        return None


def get_akshare_data(ticker, period='daily'):
    """从akshare获取美股ETF数据"""
    try:
        import akshare as ak
        # 尝试获取数据
        df = ak.stock_us_daily(symbol=ticker, adjust="qfq")
        if df is None or df.empty:
            print(f"  [WARN] akshare {ticker} 返回空数据")
            return None

        # akshare返回的列名可能是中文
        df.columns = df.columns.str.lower()
        # 标准化列名
        col_map = {}
        for col in df.columns:
            if 'date' in col:
                col_map[col] = 'date'
            elif 'open' in col:
                col_map[col] = 'open'
            elif 'high' in col:
                col_map[col] = 'high'
            elif 'low' in col:
                col_map[col] = 'low'
            elif 'close' in col:
                col_map[col] = 'close'
            elif 'volume' in col:
                col_map[col] = 'volume'
        df = df.rename(columns=col_map)

        df['date'] = pd.to_datetime(df['date'])
        for col in ['open', 'high', 'low', 'close', 'volume']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # 估算美元交易额 = volume * (high + low) / 2
        if 'volume' in df.columns:
            avg_price = (df['high'] + df['low']) / 2
            df['quote_volume'] = df['volume'] * avg_price
        else:
            df['quote_volume'] = 0

        df = df.sort_values('date').reset_index(drop=True)
        return df
    except Exception as e:
        print(f"  [ERROR] akshare {ticker} 获取失败: {e}")
        return None


# ============================================================
# 数据重采样函数
# ============================================================

def resample_ohlcv(df_daily, period):
    """将日线数据重采样为指定周期"""
    if df_daily is None or len(df_daily) < 10:
        return None

    df = df_daily.copy()
    df = df.set_index('date')

    rule_map = {
        'daily': 'D',
        'weekly': 'W',
        'monthly': 'ME',
        'quarterly': 'QE',
        'yearly': 'YE'
    }
    rule = rule_map.get(period, 'D')

    resampled = df.resample(rule).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum',
        'quote_volume': 'sum'
    }).dropna(subset=['close'])

    # 过滤掉close为0的数据
    resampled = resampled[resampled['close'] > 0]

    return resampled.reset_index()


# ============================================================
# 技术指标计算
# ============================================================

def calc_ema_signal(df, fast=12, slow=52):
    """计算EMA交叉信号
    EMA12上穿EMA52: +1
    EMA12下穿EMA52: -1
    否则: 0
    """
    if df is None or len(df) < slow + 5:
        return 0

    close = df['close'].values
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)

    if ema_fast is None or ema_slow is None:
        return 0

    # 检查最近两个周期的交叉情况
    if len(ema_fast) < 2 or len(ema_slow) < 2:
        return 0

    curr_fast, prev_fast = ema_fast[-1], ema_fast[-2]
    curr_slow, prev_slow = ema_slow[-1], ema_slow[-2]

    if prev_fast <= prev_slow and curr_fast > curr_slow:
        return 1  # 上穿
    elif prev_fast >= prev_slow and curr_fast < curr_slow:
        return -1  # 下穿
    else:
        return 0


def calc_ema(data, period):
    """计算EMA"""
    if len(data) < period:
        return None
    ema = np.zeros(len(data))
    # 初始SMA
    ema[period - 1] = np.mean(data[:period])
    multiplier = 2.0 / (period + 1)
    for i in range(period, len(data)):
        ema[i] = (data[i] - ema[i - 1]) * multiplier + ema[i - 1]
    return ema[period - 1:]


def calc_macd_signal(df, fast=12, slow=26, signal=9):
    """计算MACD信号
    柱状线由负转正 或 DIF上穿零轴: +1
    反向: -1
    否则: 0
    """
    if df is None or len(df) < slow + signal + 5:
        return 0

    close = df['close'].values
    ema_fast = calc_ema(close, fast)
    ema_slow = calc_ema(close, slow)

    if ema_fast is None or ema_slow is None:
        return 0

    # DIF = EMA_fast - EMA_slow
    min_len = min(len(ema_fast), len(ema_slow))
    dif = ema_fast[:min_len] - ema_slow[:min_len]

    if len(dif) < signal + 2:
        return 0

    # DEA = EMA(DIF, signal)
    dea = calc_ema(dif, signal)
    if dea is None or len(dea) < 2:
        return 0

    # MACD柱 = 2 * (DIF - DEA)
    min_len2 = min(len(dif), len(dea))
    histogram = 2 * (dif[:min_len2] - dea[:min_len2])

    if len(histogram) < 2:
        return 0

    curr_hist = histogram[-1]
    prev_hist = histogram[-2]
    curr_dif = dif[min_len2 - 1]
    prev_dif = dif[min_len2 - 2]

    # 柱状线由负转正
    hist_positive = (prev_hist <= 0 and curr_hist > 0)
    hist_negative = (prev_hist >= 0 and curr_hist < 0)

    # DIF上穿/下穿零轴
    dif_positive = (prev_dif <= 0 and curr_dif > 0)
    dif_negative = (prev_dif >= 0 and curr_dif < 0)

    if hist_positive or dif_positive:
        return 1
    elif hist_negative or dif_negative:
        return -1
    else:
        return 0


# ============================================================
# 综合信号判断
# ============================================================

def get_composite_signal(positive_score, negative_score):
    """判断综合信号
    全正=偏多, 全负=偏空, 有正有负=分化, 全零=中性
    """
    if positive_score > 0 and negative_score == 0:
        return "偏多"
    elif negative_score > 0 and positive_score == 0:
        return "偏空"
    elif positive_score > 0 and negative_score > 0:
        return "分化"
    else:
        return "中性"


def get_signal_sort_order(signal):
    """获取信号排序权重"""
    order = {"偏多": 0, "分化": 1, "中性": 2, "偏空": 3}
    return order.get(signal, 4)


# ============================================================
# 主分析流程
# ============================================================

def analyze_asset(asset_info):
    """分析单个品种"""
    symbol = asset_info['symbol']
    name = asset_info['name']
    source = asset_info['source']

    print(f"  分析 {symbol} ({name}) [{source}]...")

    # 获取日线数据
    df_daily = None
    if source == 'binance':
        df_daily = get_binance_klines(asset_info['pair'], '1d', 1000)
    elif source == 'gateio':
        df_daily = get_gateio_klines(asset_info['pair'], '1d', 1000)
    elif source == 'akshare':
        df_daily = get_akshare_data(asset_info['ticker'])

    if df_daily is None or len(df_daily) < 60:
        print(f"    [SKIP] {symbol} 数据不足")
        return None

    # 检查价格是否有效（跳过价格为0的品种如FXS）
    if (df_daily['close'] == 0).any():
        print(f"    [SKIP] {symbol} 存在零价格数据")
        return None

    # 计算日均交易额（最近30天）
    recent_30 = df_daily.tail(30)
    if 'quote_volume' in recent_30.columns:
        avg_daily_volume_usd = recent_30['quote_volume'].mean()
    else:
        avg_daily_volume_usd = 0

    # 获取当前价格
    current_price = df_daily['close'].iloc[-1]

    # 各周期分析
    periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
    period_names = {
        'daily': '日线',
        'weekly': '周线',
        'monthly': '月线',
        'quarterly': '季线',
        'yearly': '年线'
    }

    total_positive = 0
    total_negative = 0
    period_details = []

    for period in periods:
        df_period = resample_ohlcv(df_daily, period)
        if df_period is None or len(df_period) < 60:
            period_details.append({
                "period": period_names[period],
                "ema_signal": 0,
                "macd_signal": 0,
                "score": "0"
            })
            continue

        ema_sig = calc_ema_signal(df_period)
        macd_sig = calc_macd_signal(df_period)

        positive = 0
        negative = 0
        if ema_sig > 0:
            positive += 1
        elif ema_sig < 0:
            negative += 1
        if macd_sig > 0:
            positive += 1
        elif macd_sig < 0:
            negative += 1

        total_positive += positive
        total_negative += negative

        score_str = f"+{positive}" if positive > 0 else str(-negative) if negative > 0 else "0"

        period_details.append({
            "period": period_names[period],
            "ema_signal": ema_sig,
            "macd_signal": macd_sig,
            "score": score_str
        })

    composite_signal = get_composite_signal(total_positive, total_negative)

    result = {
        "symbol": symbol,
        "name": name,
        "current_price": round(float(current_price), 6),
        "avg_daily_volume_usd": round(float(avg_daily_volume_usd), 2),
        "positive_score": total_positive,
        "negative_score": total_negative,
        "composite_signal": composite_signal,
        "details": period_details
    }

    print(f"    {composite_signal} (正:{total_positive} 负:{total_negative}) 价格:{current_price}")
    return result


def main():
    print("=" * 60)
    print("多品类右侧交易技术分析（扩展品种）")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    all_results = []
    category_order = ["外汇", "债券/利率", "大宗商品", "股票指数", "货币", "加密货币"]

    for category in category_order:
        if category not in CATEGORIES:
            continue
        assets = CATEGORIES[category]
        print(f"\n[{category}] ({len(assets)}个品种)")
        print("-" * 40)

        category_results = []
        for asset_info in assets:
            try:
                result = analyze_asset(asset_info)
                if result is not None:
                    result["category"] = category
                    category_results.append(result)
            except Exception as e:
                print(f"    [ERROR] {asset_info['symbol']} 分析异常: {e}")
                import traceback
                traceback.print_exc()

            # 延迟 1 秒避免限流（GitHub Actions 环境）
            time.sleep(1)

        # 品类内按综合信号排序
        category_results.sort(key=lambda x: get_signal_sort_order(x['composite_signal']))
        all_results.extend(category_results)

    # 构建最终输出
    output = {
        "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "total_assets": len(all_results),
        "category_order": category_order,
        "assets": all_results
    }

    # 输出JSON（使用相对路径，适配 GitHub Actions 工作目录）
    output_path = "./new-assets-right-side/scripts/result.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print(f"分析完成! 共 {len(all_results)} 个品种")
    print(f"结果保存到: {output_path}")
    print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 统计概览
    signal_counts = {}
    for r in all_results:
        sig = r['composite_signal']
        signal_counts[sig] = signal_counts.get(sig, 0) + 1
    print("\n信号分布:")
    for sig in ["偏多", "分化", "中性", "偏空"]:
        print(f"  {sig}: {signal_counts.get(sig, 0)}")


if __name__ == '__main__':
    main()

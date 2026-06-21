#!/usr/bin/env python3
"""
HTML 报告生成脚本（核心品种）
读取 result.json，生成自包含的深色主题 HTML 技术分析报告

适配 GitHub Actions 自动化部署：
- 读取路径使用相对路径（相对于项目根目录）
- 输出路径使用相对路径
- ECharts 引用路径改为 _shared/js/echarts.min.js（相对于HTML文件）
"""

import json
import os
from datetime import datetime

# ============================================================
# 配置
# ============================================================
RESULT_FILE = "./multi-asset-technical-analysis/scripts/result.json"
OUTPUT_FILE = "./multi-asset-technical-analysis/multi-asset-technical-analysis.html"

PERIODS = ["daily", "weekly", "monthly", "quarterly", "yearly"]
PERIOD_CN = {
    "daily": "日线", "weekly": "周线", "monthly": "月线",
    "quarterly": "季线", "yearly": "年线"
}
INDICATORS = ["ema", "macd", "rsi", "kdj", "boll"]
INDICATOR_CN = {
    "ema": "EMA(12,52)", "macd": "MACD(12,26,9)",
    "rsi": "RSI(14)", "kdj": "KDJ(9,3,3)", "boll": "BOLL(20,2)"
}
RIGHT_INDICATORS = ["ema", "macd"]
LEFT_INDICATORS = ["rsi", "kdj", "boll"]

# 颜色
COLORS = {
    "bg": "#0f172a",
    "card": "#1e293b",
    "card_hover": "#263548",
    "accent": "#3b82f6",
    "positive": "#22c55e",
    "negative": "#ef4444",
    "muted": "#8896ab",
    "text": "#e2e8f0",
    "text_secondary": "#94a3b8",
    "border": "#334155",
    "header_bg": "#1a2332",
}

ASSET_COLORS = ["#3b82f6", "#a855f7", "#f59e0b", "#22c55e", "#ef4444", "#06b6d4"]


def load_data():
    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def format_volume(v):
    """格式化交易额"""
    if v is None:
        return "N/A"
    if v >= 1e12:
        return f"${v/1e12:.2f}T"
    elif v >= 1e9:
        return f"${v/1e9:.2f}B"
    elif v >= 1e6:
        return f"${v/1e6:.2f}M"
    else:
        return f"${v:,.0f}"


def format_price(p):
    if p is None:
        return "N/A"
    if p >= 10000:
        return f"{p:,.2f}"
    elif p >= 1:
        return f"{p:,.4f}"
    else:
        return f"{p:.6f}"


def signal_color(signal):
    if signal == "偏多":
        return COLORS["positive"]
    elif signal == "偏空":
        return COLORS["negative"]
    elif signal == "分化":
        return "#f59e0b"
    else:
        return COLORS["muted"]


def score_badge(score):
    if score > 0:
        return f'<span style="color:{COLORS["positive"]};font-weight:700;">+{score}</span>'
    elif score < 0:
        return f'<span style="color:{COLORS["negative"]};font-weight:700;">{score}</span>'
    else:
        return f'<span style="color:{COLORS["muted"]};">0</span>'


def generate_html(data):
    asset_keys = list(data.keys())
    asset_names = [data[k]["name"] for k in asset_keys]
    asset_categories = [data[k]["category"] for k in asset_keys]
    today = datetime.now().strftime("%Y-%m-%d")

    # ============================================================
    # 构建嵌入的 JavaScript 数据
    # ============================================================
    js_data = json.dumps(data, ensure_ascii=False)

    # ============================================================
    # HTML 模板
    # ============================================================
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>多品种多周期技术分析报告</title>
<script src="_shared/js/echarts.min.js"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    background: {COLORS["bg"]};
    color: {COLORS["text"]};
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    line-height: 1.6;
    padding: 20px;
}}
.container {{
    max-width: 1400px;
    margin: 0 auto;
}}
h1 {{
    text-align: center;
    font-size: 28px;
    margin-bottom: 8px;
    color: {COLORS["text"]};
}}
h1 .accent {{ color: {COLORS["accent"]}; }}
.subtitle {{
    text-align: center;
    color: {COLORS["text_secondary"]};
    font-size: 14px;
    margin-bottom: 30px;
}}
.section-title {{
    font-size: 20px;
    font-weight: 700;
    margin: 30px 0 15px;
    padding-left: 12px;
    border-left: 4px solid {COLORS["accent"]};
    color: {COLORS["text"]};
}}
.card {{
    background: {COLORS["card"]};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid {COLORS["border"]};
}}
.card:hover {{
    background: {COLORS["card_hover"]};
}}
/* 评分规则说明 */
.rules-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}}
.rule-box {{
    background: rgba(255,255,255,0.03);
    border-radius: 8px;
    padding: 16px;
}}
.rule-box h3 {{
    font-size: 16px;
    margin-bottom: 10px;
}}
.rule-box.right h3 {{ color: {COLORS["accent"]}; }}
.rule-box.left h3 {{ color: #f59e0b; }}
.rule-box ul {{
    list-style: none;
    padding: 0;
}}
.rule-box li {{
    font-size: 13px;
    color: {COLORS["text_secondary"]};
    padding: 3px 0;
}}
.rule-box li::before {{
    content: "\\2022";
    margin-right: 6px;
    color: {COLORS["muted"]};
}}
/* 概览表 */
.overview-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}}
.overview-table th {{
    background: {COLORS["header_bg"]};
    padding: 12px 10px;
    text-align: center;
    font-weight: 600;
    color: {COLORS["text_secondary"]};
    border-bottom: 2px solid {COLORS["border"]};
    white-space: nowrap;
}}
.overview-table td {{
    padding: 10px;
    text-align: center;
    border-bottom: 1px solid {COLORS["border"]};
    white-space: nowrap;
}}
.overview-table tr:hover td {{
    background: rgba(255,255,255,0.03);
}}
.signal-badge {{
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 700;
    color: #fff;
}}
/* 信号卡片网格 */
.signal-cards {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}}
.signal-card {{
    background: {COLORS["card"]};
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    border: 1px solid {COLORS["border"]};
    transition: transform 0.2s;
}}
.signal-card:hover {{
    transform: translateY(-2px);
}}
.signal-card .asset-name {{
    font-size: 16px;
    font-weight: 700;
    margin-bottom: 4px;
}}
.signal-card .asset-category {{
    font-size: 12px;
    color: {COLORS["text_secondary"]};
    margin-bottom: 10px;
}}
.signal-card .signal-text {{
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 8px;
}}
.signal-card .score-detail {{
    font-size: 12px;
    color: {COLORS["text_secondary"]};
    line-height: 1.8;
}}
/* 图表容器 */
.chart-container {{
    width: 100%;
    height: 400px;
}}
.chart-container-tall {{
    width: 100%;
    height: 500px;
}}
/* 品种详情卡片 */
.asset-detail {{
    background: {COLORS["card"]};
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 20px;
    border: 1px solid {COLORS["border"]};
}}
.asset-detail .header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 16px;
    flex-wrap: wrap;
    gap: 10px;
}}
.asset-detail .header h3 {{
    font-size: 20px;
    font-weight: 700;
}}
.asset-detail .header .price-info {{
    text-align: right;
    font-size: 14px;
    color: {COLORS["text_secondary"]};
}}
.asset-detail .header .price-info .price {{
    font-size: 24px;
    font-weight: 700;
    color: {COLORS["text"]};
}}
.period-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}}
.period-table th {{
    background: {COLORS["header_bg"]};
    padding: 10px 8px;
    text-align: center;
    font-weight: 600;
    color: {COLORS["text_secondary"]};
    border-bottom: 2px solid {COLORS["border"]};
    white-space: nowrap;
}}
.period-table td {{
    padding: 8px;
    text-align: center;
    border-bottom: 1px solid {COLORS["border"]};
    font-size: 12px;
}}
.period-table tr:hover td {{
    background: rgba(255,255,255,0.03);
}}
.period-table .indicator-name {{
    font-weight: 600;
    color: {COLORS["text"]};
}}
.period-table .detail-text {{
    color: {COLORS["text_secondary"]};
    max-width: 200px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}}
.period-table .right-section {{
    border-left: 2px solid {COLORS["accent"]};
}}
.period-table .left-section {{
    border-left: 2px solid #f59e0b;
}}
@media (max-width: 768px) {{
    .rules-grid {{ grid-template-columns: 1fr; }}
    body {{ padding: 10px; }}
    .overview-table {{ font-size: 12px; }}
    .period-table {{ font-size: 11px; }}
}}
</style>
</head>
<body>
<div class="container">

<h1>多品种多周期<span class="accent">技术分析</span>报告</h1>
<p class="subtitle">报告日期：<span id="report-date">{today}</span> | 分析品种：<span id="asset-count">{len(asset_keys)}</span> 个 | 覆盖周期：日线 / 周线 / 月线 / 季线 / 年线</p>

<!-- 评分规则说明 -->
<div class="section-title">评分规则说明</div>
<div class="card">
<div class="rules-grid">
    <div class="rule-box right">
        <h3>右侧交易指标（趋势跟踪）</h3>
        <ul>
            <li><strong>EMA(12,52)</strong>：EMA12上穿EMA52记 +1（看多），下穿记 -1（看空），否则 0</li>
            <li><strong>MACD(12,26,9)</strong>：柱状线由负转正或DIF上穿零轴记 +1，反向记 -1，否则 0</li>
        </ul>
        <p style="margin-top:8px;font-size:12px;color:{COLORS["muted"]};">右侧指标：顺势而为，确认趋势后入场</p>
    </div>
    <div class="rule-box left">
        <h3>左侧交易指标（逆势抄底/逃顶）</h3>
        <ul>
            <li><strong>RSI(14)</strong>：RSI从30以下向上突破记 +1（超卖回升），从70以上向下跌破记 -1（超买回落），否则 0</li>
            <li><strong>KDJ(9,3,3)</strong>：J值&lt;0 记 +1（极端超卖），J值&gt;100 记 -1（极端超买），否则 0</li>
            <li><strong>BOLL(20,2)</strong>：价格跌破下轨记 +1（超卖抄底），突破上轨记 -1（超买逃顶），否则 0</li>
        </ul>
        <p style="margin-top:8px;font-size:12px;color:{COLORS["muted"]};">左侧指标：逆势操作，在极端位置寻找反转机会</p>
    </div>
</div>
<div style="margin-top:12px;font-size:13px;color:{COLORS["text_secondary"]};">
    <strong>评分规则</strong>：每个指标在每个周期独立打分 +1/-1/0；左侧和右侧分别统计正分和负分，正负分不抵消分别累加；综合信号：仅正分=偏多，仅负分=偏空，有正有负=分化，全零=中性。
</div>
</div>

<!-- 综合概览表 -->
<div class="section-title">综合概览</div>
<div class="card" style="overflow-x:auto;">
<table class="overview-table">
<thead>
<tr>
    <th>品种</th>
    <th>类别</th>
    <th>最新价格</th>
    <th>日期</th>
    <th>日均交易额</th>
    <th>右侧正分</th>
    <th>右侧负分</th>
    <th>左侧正分</th>
    <th>左侧负分</th>
    <th>综合信号</th>
</tr>
</thead>
<tbody id="overview-tbody">
</tbody>
</table>
</div>

<!-- 综合信号得分卡片 -->
<div class="section-title">综合信号</div>
<div class="signal-cards" id="signal-cards">
</div>

<!-- 左右信号分布堆叠柱状图 -->
<div class="section-title">左右侧信号分布</div>
<div class="card">
<div class="chart-container" id="chart-signal-dist"></div>
</div>

<!-- 各品种五周期正负分对比图 -->
<div class="section-title">各品种五周期正负分对比</div>
<div class="card">
<div class="chart-container-tall" id="chart-period-compare"></div>
</div>

<!-- 热力图 -->
<div class="section-title">技术指标信号热力图</div>
<div class="card">
<div class="chart-container-tall" id="chart-heatmap"></div>
</div>

<!-- 各品种详细分析 -->
<div class="section-title">各品种详细分析</div>
<div id="asset-details">
</div>

</div>

<script>
// ============================================================
// 嵌入数据
// ============================================================
var DATA = {js_data};
var PERIODS = {json.dumps(PERIODS)};
var PERIOD_CN = {json.dumps(PERIOD_CN)};
var INDICATORS = {json.dumps(INDICATORS)};
var INDICATOR_CN = {json.dumps(INDICATOR_CN)};
var RIGHT_INDICATORS = {json.dumps(RIGHT_INDICATORS)};
var LEFT_INDICATORS = {json.dumps(LEFT_INDICATORS)};
var ASSET_COLORS = {json.dumps(ASSET_COLORS)};
var assetKeys = {json.dumps(asset_keys)};

// ============================================================
// 工具函数
// ============================================================
function formatVolume(v) {{
    if (v == null) return "N/A";
    if (v >= 1e12) return "$" + (v/1e12).toFixed(2) + "T";
    if (v >= 1e9) return "$" + (v/1e9).toFixed(2) + "B";
    if (v >= 1e6) return "$" + (v/1e6).toFixed(2) + "M";
    return "$" + v.toLocaleString();
}}
function formatPrice(p) {{
    if (p == null) return "N/A";
    if (p >= 10000) return p.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:2}});
    if (p >= 1) return p.toLocaleString(undefined, {{minimumFractionDigits:2, maximumFractionDigits:4}});
    return p.toFixed(6);
}}
function signalColor(sig) {{
    if (sig === "偏多") return "{COLORS["positive"]}";
    if (sig === "偏空") return "{COLORS["negative"]}";
    if (sig === "分化") return "#f59e0b";
    return "{COLORS["muted"]}";
}}
function scoreBadge(s) {{
    if (s > 0) return '<span style="color:{COLORS["positive"]};font-weight:700;">+' + s + '</span>';
    if (s < 0) return '<span style="color:{COLORS["negative"]};font-weight:700;">' + s + '</span>';
    return '<span style="color:{COLORS["muted"]};">0</span>';
}}

// ============================================================
// 渲染概览表
// ============================================================
(function() {{
    var tbody = document.getElementById("overview-tbody");
    var html = "";
    assetKeys.forEach(function(key) {{
        var d = DATA[key];
        var cs = d.composite_scores;
        html += '<tr>';
        html += '<td style="font-weight:700;">' + d.name + '</td>';
        html += '<td>' + d.category + '</td>';
        html += '<td style="font-weight:600;">' + formatPrice(d.current_price) + '</td>';
        html += '<td>' + d.current_date + '</td>';
        html += '<td>' + formatVolume(d.avg_daily_volume_usd) + '</td>';
        html += '<td>' + scoreBadge(cs.right_positive) + '</td>';
        html += '<td>' + scoreBadge(cs.right_negative) + '</td>';
        html += '<td>' + scoreBadge(cs.left_positive) + '</td>';
        html += '<td>' + scoreBadge(cs.left_negative) + '</td>';
        html += '<td><span class="signal-badge" style="background:' + signalColor(d.composite_signal) + ';">' + d.composite_signal + '</span></td>';
        html += '</tr>';
    }});
    tbody.innerHTML = html;
}})();

// ============================================================
// 渲染信号卡片
// ============================================================
(function() {{
    var container = document.getElementById("signal-cards");
    var html = "";
    assetKeys.forEach(function(key, i) {{
        var d = DATA[key];
        var cs = d.composite_scores;
        html += '<div class="signal-card">';
        html += '<div class="asset-name">' + d.name + '</div>';
        html += '<div class="asset-category">' + d.category + '</div>';
        html += '<div class="signal-text" style="color:' + signalColor(d.composite_signal) + ';">' + d.composite_signal + '</div>';
        html += '<div class="score-detail">';
        html += '右侧 +' + cs.right_positive + ' / -' + cs.right_negative + '<br>';
        html += '左侧 +' + cs.left_positive + ' / -' + cs.left_negative;
        html += '</div>';
        html += '</div>';
    }});
    container.innerHTML = html;
}})();

// ============================================================
// 图表1: 左右侧信号分布堆叠柱状图
// ============================================================
(function() {{
    var chart = echarts.init(document.getElementById("chart-signal-dist"));
    var names = assetKeys.map(function(k) {{ return DATA[k].name; }});
    var rightPos = assetKeys.map(function(k) {{ return DATA[k].composite_scores.right_positive; }});
    var rightNeg = assetKeys.map(function(k) {{ return -DATA[k].composite_scores.right_negative; }});
    var leftPos = assetKeys.map(function(k) {{ return DATA[k].composite_scores.left_positive; }});
    var leftNeg = assetKeys.map(function(k) {{ return -DATA[k].composite_scores.left_negative; }});

    var option = {{
        tooltip: {{ trigger: "axis" }},
        legend: {{
            data: ["右侧正分", "右侧负分", "左侧正分", "左侧负分"],
            textStyle: {{ color: "{COLORS["text_secondary"]}" }},
            top: 0
        }},
        grid: {{ left: 60, right: 30, top: 40, bottom: 40 }},
        xAxis: {{
            type: "category",
            data: names,
            axisLabel: {{ color: "{COLORS["text_secondary"]}", fontSize: 12 }},
            axisLine: {{ lineStyle: {{ color: "{COLORS["border"]}" }} }}
        }},
        yAxis: {{
            type: "value",
            axisLabel: {{ color: "{COLORS["text_secondary"]}" }},
            splitLine: {{ lineStyle: {{ color: "{COLORS["border"]}", type: "dashed" }} }}
        }},
        series: [
            {{ name: "右侧正分", type: "bar", stack: "right", data: rightPos, itemStyle: {{ color: "{COLORS["accent"]}" }}, barWidth: "30%" }},
            {{ name: "右侧负分", type: "bar", stack: "right", data: rightNeg, itemStyle: {{ color: "{COLORS["accent"]}", opacity: 0.4 }} }},
            {{ name: "左侧正分", type: "bar", stack: "left", data: leftPos, itemStyle: {{ color: "#f59e0b" }}, barWidth: "30%" }},
            {{ name: "左侧负分", type: "bar", stack: "left", data: leftNeg, itemStyle: {{ color: "#f59e0b", opacity: 0.4 }} }}
        ]
    }};
    chart.setOption(option);
    window.addEventListener("resize", function() {{ chart.resize(); }});
}})();

// ============================================================
// 图表2: 各品种五周期正负分对比图
// ============================================================
(function() {{
    var chart = echarts.init(document.getElementById("chart-period-compare"));
    var periods = PERIODS.map(function(p) {{ return PERIOD_CN[p]; }});
    var series = [];

    assetKeys.forEach(function(key, idx) {{
        var d = DATA[key];
        var posData = PERIODS.map(function(p) {{
            var a = d.analysis[p];
            return (a.right_positive + a.left_positive) - (a.right_negative + a.left_negative);
        }});
        series.push({{
            name: d.name,
            type: "bar",
            data: posData,
            itemStyle: {{
                color: function(params) {{
                    var val = params.value;
                    if (val > 0) return "{COLORS["positive"]}";
                    if (val < 0) return "{COLORS["negative"]}";
                    return "{COLORS["muted"]}";
                }}
            }}
        }});
    }});

    var option = {{
        tooltip: {{ trigger: "axis" }},
        legend: {{
            data: assetKeys.map(function(k) {{ return DATA[k].name; }}),
            textStyle: {{ color: "{COLORS["text_secondary"]}" }},
            top: 0
        }},
        grid: {{ left: 50, right: 30, top: 50, bottom: 40 }},
        xAxis: {{
            type: "category",
            data: periods,
            axisLabel: {{ color: "{COLORS["text_secondary"]}" }},
            axisLine: {{ lineStyle: {{ color: "{COLORS["border"]}" }} }}
        }},
        yAxis: {{
            type: "value",
            axisLabel: {{ color: "{COLORS["text_secondary"]}" }},
            splitLine: {{ lineStyle: {{ color: "{COLORS["border"]}", type: "dashed" }} }}
        }},
        series: series
    }};
    chart.setOption(option);
    window.addEventListener("resize", function() {{ chart.resize(); }});
}})();

// ============================================================
// 图表3: 热力图 (5指标 x 5周期 x 6品种)
// ============================================================
(function() {{
    var chart = echarts.init(document.getElementById("chart-heatmap"));

    // 构建热力图数据: [x(周期), y(品种-指标), value]
    var yData = [];
    var xData = PERIODS.map(function(p) {{ return PERIOD_CN[p]; }});
    var heatData = [];

    assetKeys.forEach(function(key) {{
        var d = DATA[key];
        INDICATORS.forEach(function(ind) {{
            var label = d.name + " " + INDICATOR_CN[ind];
            yData.push(label);
            PERIODS.forEach(function(p, pi) {{
                var score = d.analysis[p][ind].score;
                heatData.push([pi, yData.length - 1, score]);
            }});
        }});
    }});

    var option = {{
        tooltip: {{
            position: "top",
            formatter: function(params) {{
                var val = params.value;
                var yLabel = yData[val[1]];
                var xLabel = xData[val[0]];
                var score = val[2];
                var scoreText = score > 0 ? "+" + score : "" + score;
                var scoreColor = score > 0 ? "{COLORS["positive"]}" : (score < 0 ? "{COLORS["negative"]}" : "{COLORS["muted"]}");
                return yLabel + "<br/>" + xLabel + ": <span style=\\"color:" + scoreColor + ";font-weight:700;\\">" + scoreText + "</span>";
            }}
        }},
        grid: {{ left: 140, right: 80, top: 10, bottom: 40 }},
        xAxis: {{
            type: "category",
            data: xData,
            axisLabel: {{ color: "{COLORS["text_secondary"]}" }},
            axisLine: {{ lineStyle: {{ color: "{COLORS["border"]}" }} }},
            splitArea: {{ show: true, areaStyle: {{ color: ["{COLORS["bg"]}", "rgba(255,255,255,0.02)"] }} }}
        }},
        yAxis: {{
            type: "category",
            data: yData,
            axisLabel: {{ color: "{COLORS["text_secondary"]}", fontSize: 11 }},
            axisLine: {{ lineStyle: {{ color: "{COLORS["border"]}" }} }},
            splitArea: {{ show: false }}
        }},
        visualMap: {{
            min: -1, max: 1,
            calculable: false,
            orient: "vertical",
            right: 10,
            top: "center",
            inRange: {{
                color: ["{COLORS["negative"]}", "{COLORS["card"]}", "{COLORS["positive"]}"]
            }},
            textStyle: {{ color: "{COLORS["text_secondary"]}" }},
            text: ["+1 看多", "-1 看空"]
        }},
        series: [{{
            type: "heatmap",
            data: heatData,
            label: {{
                show: true,
                formatter: function(p) {{
                    var v = p.value[2];
                    return v > 0 ? "+" + v : "" + v;
                }},
                fontSize: 11,
                fontWeight: 700
            }},
            itemStyle: {{
                borderColor: "{COLORS["bg"]}",
                borderWidth: 2,
                borderRadius: 3
            }}
        }}]
    }};
    chart.setOption(option);
    window.addEventListener("resize", function() {{ chart.resize(); }});
}})();

// ============================================================
// 各品种详细分析卡片
// ============================================================
(function() {{
    var container = document.getElementById("asset-details");
    var html = "";

    assetKeys.forEach(function(key) {{
        var d = DATA[key];
        html += '<div class="asset-detail">';
        html += '<div class="header">';
        html += '<div><h3>' + d.name + ' (' + d.symbol + ')</h3>';
        html += '<span style="font-size:13px;color:{COLORS["text_secondary"]};">' + d.category + '</span></div>';
        html += '<div class="price-info">';
        html += '<div class="price">' + formatPrice(d.current_price) + '</div>';
        html += '<div>' + d.current_date + ' | ' + formatVolume(d.avg_daily_volume_usd) + '/日</div>';
        html += '<div><span class="signal-badge" style="background:' + signalColor(d.composite_signal) + ';font-size:14px;padding:4px 16px;">' + d.composite_signal + '</span></div>';
        html += '</div></div>';

        // 各周期表格
        PERIODS.forEach(function(p) {{
            var a = d.analysis[p];
            if (!a || a.last_close == null) return;
            html += '<div style="margin-top:16px;">';
            html += '<div style="font-size:15px;font-weight:600;margin-bottom:8px;color:{COLORS["accent"]};">';
            html += PERIOD_CN[p] + ' <span style="font-size:12px;color:{COLORS["text_secondary"]};font-weight:400;">(' + a.last_date + ' 收盘: ' + formatPrice(a.last_close) + ')</span>';
            html += '</div>';
            html += '<table class="period-table"><thead><tr>';
            html += '<th>指标</th><th>信号</th><th>说明</th>';
            html += '<th style="color:{COLORS["accent"]};">右侧</th>';
            html += '<th style="color:#f59e0b;">左侧</th>';
            html += '</tr></thead><tbody>';

            // 右侧指标
            RIGHT_INDICATORS.forEach(function(ind) {{
                var info = a[ind];
                html += '<tr class="right-section">';
                html += '<td class="indicator-name">' + INDICATOR_CN[ind] + '</td>';
                html += '<td>' + scoreBadge(info.score) + '</td>';
                html += '<td class="detail-text" title="' + info.detail + '">' + info.detail + '</td>';
                html += '<td>' + (ind === "ema" ? (a.right_positive > 0 || a.right_negative > 0 ? "R+" + a.right_positive + "/-" + a.right_negative : "") : "") + '</td>';
                html += '<td></td>';
                html += '</tr>';
            }});

            // 左侧指标
            LEFT_INDICATORS.forEach(function(ind) {{
                var info = a[ind];
                html += '<tr class="left-section">';
                html += '<td class="indicator-name">' + INDICATOR_CN[ind] + '</td>';
                html += '<td>' + scoreBadge(info.score) + '</td>';
                html += '<td class="detail-text" title="' + info.detail + '">' + info.detail + '</td>';
                html += '<td></td>';
                html += '<td>' + (ind === "rsi" ? (a.left_positive > 0 || a.left_negative > 0 ? "L+" + a.left_positive + "/-" + a.left_negative : "") : "") + '</td>';
                html += '</tr>';
            }});

            // 合计行
            html += '<tr style="background:rgba(255,255,255,0.03);font-weight:600;">';
            html += '<td colspan="3" style="text-align:right;">周期合计</td>';
            html += '<td style="color:{COLORS["accent"]};">+' + a.right_positive + ' / -' + a.right_negative + '</td>';
            html += '<td style="color:#f59e0b;">+' + a.left_positive + ' / -' + a.left_negative + '</td>';
            html += '</tr>';

            html += '</tbody></table></div>';
        }});

        html += '</div>';
    }});

    container.innerHTML = html;
}})();

</script>
</body>
</html>"""

    return html


def main():
    print("加载分析数据...")
    data = load_data()

    if not data:
        print("错误: result.json 为空或不存在")
        return

    print(f"共 {len(data)} 个品种: {list(data.keys())}")

    print("生成 HTML 报告...")
    html_content = generate_html(data)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"HTML 报告已保存到: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

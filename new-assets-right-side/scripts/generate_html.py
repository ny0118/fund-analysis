#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTML报告生成脚本
读取result.json，生成自包含的深色主题HTML报告
"""

import json
import os
import sys

def format_volume(volume):
    """格式化交易额"""
    if volume is None or volume == 0:
        return "N/A"
    if volume >= 1e12:
        return f"${volume/1e12:.2f}万亿"
    elif volume >= 1e8:
        return f"${volume/1e8:.2f}亿"
    elif volume >= 1e4:
        return f"${volume/1e4:.2f}万"
    else:
        return f"${volume:.2f}"


def format_price(price):
    """格式化价格"""
    if price is None:
        return "N/A"
    if price >= 1000:
        return f"{price:,.2f}"
    elif price >= 1:
        return f"{price:.4f}"
    elif price >= 0.001:
        return f"{price:.6f}"
    else:
        return f"{price:.8f}"


def get_signal_color(signal):
    """获取信号颜色"""
    colors = {
        "偏多": "#34d399",
        "偏空": "#fb7185",
        "分化": "#fbbf24",
        "中性": "#94a3b8"
    }
    return colors.get(signal, "#94a3b8")


def get_signal_bg(signal):
    """获取信号背景色"""
    bgs = {
        "偏多": "rgba(52,211,153,0.15)",
        "偏空": "rgba(251,113,133,0.15)",
        "分化": "rgba(251,191,36,0.15)",
        "中性": "rgba(148,163,184,0.15)"
    }
    return bgs.get(signal, "rgba(148,163,184,0.15)")


def generate_html(data):
    """生成HTML报告"""

    assets = data['assets']
    total = data['total_assets']
    generated_at = data['generated_at']
    category_order = data.get('category_order', ["外汇", "债券/利率", "大宗商品", "股票指数", "货币", "加密货币"])

    # 按品类分组
    categories_data = {}
    for cat in category_order:
        categories_data[cat] = [a for a in assets if a['category'] == cat]

    # 信号统计
    signal_stats = {"偏多": 0, "偏空": 0, "分化": 0, "中性": 0}
    for a in assets:
        sig = a['composite_signal']
        if sig in signal_stats:
            signal_stats[sig] += 1

    # 品类信号统计
    category_signal_stats = {}
    for cat in category_order:
        cat_assets = categories_data.get(cat, [])
        cat_stats = {"偏多": 0, "偏空": 0, "分化": 0, "中性": 0}
        for a in cat_assets:
            sig = a['composite_signal']
            if sig in cat_stats:
                cat_stats[sig] += 1
        category_signal_stats[cat] = cat_stats

    # 构建品种数据JS
    assets_js = json.dumps(assets, ensure_ascii=False, indent=2)

    # 构建概览表行
    overview_rows = ""
    for a in assets:
        sig_color = get_signal_color(a['composite_signal'])
        sig_bg = get_signal_bg(a['composite_signal'])
        vol_str = format_volume(a['avg_daily_volume_usd'])
        price_str = format_price(a['current_price'])
        overview_rows += f"""
        <tr>
            <td>{a['category']}</td>
            <td><strong>{a['symbol']}</strong></td>
            <td>{a['name']}</td>
            <td>{price_str}</td>
            <td>{vol_str}</td>
            <td style="text-align:center">{a['positive_score']}</td>
            <td style="text-align:center">{a['negative_score']}</td>
            <td style="text-align:center"><span class="signal-badge" style="color:{sig_color};background:{sig_bg};border:1px solid {sig_color}">{a['composite_signal']}</span></td>
        </tr>"""

    # 构建品种详情卡片
    detail_cards = ""
    for cat in category_order:
        cat_assets = categories_data.get(cat, [])
        if not cat_assets:
            continue

        detail_cards += f"""
    <div class="category-section" id="cat-{cat}">
        <h2 class="category-title">{cat} <span class="category-count">({len(cat_assets)})</span></h2>
        <div class="cards-grid">"""

        for a in cat_assets:
            sig_color = get_signal_color(a['composite_signal'])
            sig_bg = get_signal_bg(a['composite_signal'])
            vol_str = format_volume(a['avg_daily_volume_usd'])
            price_str = format_price(a['current_price'])

            # 详情表格行
            detail_rows = ""
            for d in a['details']:
                ema_str = "+" if d['ema_signal'] > 0 else ("-" if d['ema_signal'] < 0 else "0")
                macd_str = "+" if d['macd_signal'] > 0 else ("-" if d['macd_signal'] < 0 else "0")
                ema_color = "#34d399" if d['ema_signal'] > 0 else ("#fb7185" if d['ema_signal'] < 0 else "#94a3b8")
                macd_color = "#34d399" if d['macd_signal'] > 0 else ("#fb7185" if d['macd_signal'] < 0 else "#94a3b8")
                score_str = str(d['score'])
                score_color = "#34d399" if score_str.startswith('+') else ("#fb7185" if score_str.startswith('-') else "#94a3b8")

                detail_rows += f"""
                <tr>
                    <td>{d['period']}</td>
                    <td style="color:{ema_color};font-weight:bold;text-align:center">{ema_str}</td>
                    <td style="color:{macd_color};font-weight:bold;text-align:center">{macd_str}</td>
                    <td style="color:{score_color};font-weight:bold;text-align:center">{score_str}</td>
                </tr>"""

            detail_cards += f"""
        <div class="asset-card" data-category="{a['category']}" data-signal="{a['composite_signal']}">
            <div class="card-header">
                <div class="card-title-row">
                    <span class="card-symbol">{a['symbol']}</span>
                    <span class="card-name">{a['name']}</span>
                </div>
                <div class="card-signal" style="color:{sig_color};background:{sig_bg};border:1px solid {sig_color}">{a['composite_signal']}</div>
            </div>
            <div class="card-body">
                <div class="card-info">
                    <div class="info-item">
                        <span class="info-label">当前价格</span>
                        <span class="info-value">{price_str}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">日均交易额</span>
                        <span class="info-value">{vol_str}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">正分/负分</span>
                        <span class="info-value"><span style="color:#34d399">+{a['positive_score']}</span> / <span style="color:#fb7185">{a['negative_score']}</span></span>
                    </div>
                </div>
                <table class="detail-table">
                    <thead>
                        <tr>
                            <th>周期</th>
                            <th>EMA</th>
                            <th>MACD</th>
                            <th>得分</th>
                        </tr>
                    </thead>
                    <tbody>
                        {detail_rows}
                    </tbody>
                </table>
            </div>
        </div>"""

        detail_cards += """
        </div>
    </div>"""

    # 品类筛选按钮
    filter_buttons = '<button class="filter-btn active" data-filter="all">全部</button>'
    for cat in category_order:
        count = len(categories_data.get(cat, []))
        filter_buttons += f'<button class="filter-btn" data-filter="{cat}">{cat} ({count})</button>'

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>多品类右侧交易技术分析报告</title>
    <script src="./_shared/js/echarts.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            text-align: center;
            padding: 40px 0 30px;
            border-bottom: 1px solid #1e293b;
            margin-bottom: 30px;
        }}
        .header h1 {{
            font-size: 2.2em;
            color: #38bdf8;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        .header .subtitle {{
            color: #94a3b8;
            font-size: 1em;
        }}
        .header .date-info {{
            color: #64748b;
            font-size: 0.9em;
            margin-top: 8px;
        }}

        /* 评分规则说明 */
        .rules-section {{
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
            border: 1px solid #334155;
        }}
        .rules-section h2 {{
            color: #38bdf8;
            font-size: 1.2em;
            margin-bottom: 16px;
        }}
        .rules-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 16px;
        }}
        .rule-item {{
            background: #0f172a;
            border-radius: 8px;
            padding: 16px;
            border: 1px solid #334155;
        }}
        .rule-item h3 {{
            color: #38bdf8;
            font-size: 0.95em;
            margin-bottom: 8px;
        }}
        .rule-item p {{
            color: #94a3b8;
            font-size: 0.85em;
            line-height: 1.5;
        }}
        .rule-item .rule-formula {{
            color: #e2e8f0;
            font-family: 'Courier New', monospace;
            background: #1e293b;
            padding: 8px 12px;
            border-radius: 4px;
            margin-top: 8px;
            font-size: 0.85em;
        }}

        /* 信号卡片 */
        .signal-cards {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 30px;
        }}
        .signal-card {{
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
            text-align: center;
            border: 1px solid #334155;
            transition: transform 0.2s;
        }}
        .signal-card:hover {{
            transform: translateY(-2px);
        }}
        .signal-card .count {{
            font-size: 2.5em;
            font-weight: 700;
            margin-bottom: 8px;
        }}
        .signal-card .label {{
            font-size: 1em;
            color: #94a3b8;
        }}
        .signal-card .pct {{
            font-size: 0.85em;
            color: #64748b;
            margin-top: 4px;
        }}

        /* 筛选按钮 */
        .filter-bar {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 24px;
            justify-content: center;
        }}
        .filter-btn {{
            background: #1e293b;
            color: #94a3b8;
            border: 1px solid #334155;
            padding: 8px 18px;
            border-radius: 20px;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }}
        .filter-btn:hover {{
            background: #334155;
            color: #e2e8f0;
        }}
        .filter-btn.active {{
            background: #38bdf8;
            color: #0f172a;
            border-color: #38bdf8;
            font-weight: 600;
        }}

        /* 图表区域 */
        .chart-section {{
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
            border: 1px solid #334155;
        }}
        .chart-section h2 {{
            color: #38bdf8;
            font-size: 1.1em;
            margin-bottom: 16px;
        }}
        .chart-container {{
            width: 100%;
            height: 500px;
        }}
        .chart-container-tall {{
            width: 100%;
            height: 700px;
        }}

        /* 概览表 */
        .overview-section {{
            background: #1e293b;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
            border: 1px solid #334155;
            overflow-x: auto;
        }}
        .overview-section h2 {{
            color: #38bdf8;
            font-size: 1.1em;
            margin-bottom: 16px;
        }}
        .overview-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
        }}
        .overview-table th {{
            background: #0f172a;
            color: #38bdf8;
            padding: 12px 10px;
            text-align: left;
            position: sticky;
            top: 0;
            border-bottom: 2px solid #334155;
            white-space: nowrap;
        }}
        .overview-table td {{
            padding: 10px;
            border-bottom: 1px solid #1e293b;
            white-space: nowrap;
        }}
        .overview-table tr:hover {{
            background: rgba(56,189,248,0.05);
        }}
        .signal-badge {{
            display: inline-block;
            padding: 3px 10px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        /* 品类分区 */
        .category-section {{
            margin-bottom: 40px;
        }}
        .category-title {{
            color: #38bdf8;
            font-size: 1.3em;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #334155;
        }}
        .category-count {{
            color: #64748b;
            font-size: 0.8em;
            font-weight: 400;
        }}

        /* 品种卡片 */
        .cards-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
            gap: 16px;
        }}
        .asset-card {{
            background: #1e293b;
            border-radius: 12px;
            border: 1px solid #334155;
            overflow: hidden;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .asset-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }}
        .card-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: #0f172a;
            border-bottom: 1px solid #334155;
        }}
        .card-title-row {{
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .card-symbol {{
            font-size: 1.2em;
            font-weight: 700;
            color: #38bdf8;
        }}
        .card-name {{
            color: #94a3b8;
            font-size: 0.9em;
        }}
        .card-signal {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .card-body {{
            padding: 16px 20px;
        }}
        .card-info {{
            display: flex;
            justify-content: space-between;
            margin-bottom: 16px;
            gap: 8px;
        }}
        .info-item {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .info-label {{
            color: #64748b;
            font-size: 0.75em;
        }}
        .info-value {{
            color: #e2e8f0;
            font-size: 0.9em;
            font-weight: 600;
        }}
        .detail-table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85em;
        }}
        .detail-table th {{
            background: #0f172a;
            color: #64748b;
            padding: 8px 10px;
            text-align: left;
            font-weight: 500;
            font-size: 0.8em;
        }}
        .detail-table td {{
            padding: 8px 10px;
            border-bottom: 1px solid #1e293b;
        }}
        .detail-table tr:hover {{
            background: rgba(56,189,248,0.03);
        }}

        .footer {{
            text-align: center;
            padding: 30px 0;
            color: #475569;
            font-size: 0.85em;
            border-top: 1px solid #1e293b;
            margin-top: 40px;
        }}

        @media (max-width: 768px) {{
            .signal-cards {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .cards-grid {{
                grid-template-columns: 1fr;
            }}
            .header h1 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>多品类右侧交易技术分析报告</h1>
            <div class="subtitle">EMA(12,52) + MACD(12,26,9) | 日线/周线/月线/季线/年线</div>
            <div class="date-info">报告生成时间：<span id="report-date">{generated_at}</span> | 分析品种：<span id="total-count">{total}</span>个</div>
        </div>

        <!-- 评分规则说明 -->
        <div class="rules-section">
            <h2>评分规则说明</h2>
            <div class="rules-grid">
                <div class="rule-item">
                    <h3>EMA交叉信号</h3>
                    <p>快线EMA(12)与慢线EMA(52)的交叉判断趋势方向</p>
                    <div class="rule-formula">
                        EMA12 上穿 EMA52 → +1<br>
                        EMA12 下穿 EMA52 → -1<br>
                        无交叉 → 0
                    </div>
                </div>
                <div class="rule-item">
                    <h3>MACD信号</h3>
                    <p>基于DIF/DEA的柱状线和零轴判断动量变化</p>
                    <div class="rule-formula">
                        柱状线由负转正 或 DIF上穿零轴 → +1<br>
                        柱状线由正转负 或 DIF下穿零轴 → -1<br>
                        无变化 → 0
                    </div>
                </div>
                <div class="rule-item">
                    <h3>综合评分</h3>
                    <p>五个周期(日/周/月/季/年)的EMA+MACD信号分别计分</p>
                    <div class="rule-formula">
                        正分和负分分别累加，不抵消<br>
                        全正 → 偏多 | 全负 → 偏空<br>
                        有正有负 → 分化 | 全零 → 中性
                    </div>
                </div>
                <div class="rule-item">
                    <h3>分析周期</h3>
                    <p>覆盖五个时间维度，捕捉不同级别的趋势信号</p>
                    <div class="rule-formula">
                        日线 → 短期趋势<br>
                        周线 → 中短期趋势<br>
                        月线 → 中期趋势<br>
                        季线 → 中长期趋势<br>
                        年线 → 长期趋势
                    </div>
                </div>
            </div>
        </div>

        <!-- 综合信号得分卡片 -->
        <div class="signal-cards">
            <div class="signal-card">
                <div class="count" style="color:#34d399">{signal_stats['偏多']}</div>
                <div class="label">偏多</div>
                <div class="pct">{signal_stats['偏多']/total*100:.1f}%</div>
            </div>
            <div class="signal-card">
                <div class="count" style="color:#fbbf24">{signal_stats['分化']}</div>
                <div class="label">分化</div>
                <div class="pct">{signal_stats['分化']/total*100:.1f}%</div>
            </div>
            <div class="signal-card">
                <div class="count" style="color:#94a3b8">{signal_stats['中性']}</div>
                <div class="label">中性</div>
                <div class="pct">{signal_stats['中性']/total*100:.1f}%</div>
            </div>
            <div class="signal-card">
                <div class="count" style="color:#fb7185">{signal_stats['偏空']}</div>
                <div class="label">偏空</div>
                <div class="pct">{signal_stats['偏空']/total*100:.1f}%</div>
            </div>
        </div>

        <!-- 品类筛选按钮 -->
        <div class="filter-bar">
            {filter_buttons}
        </div>

        <!-- 品类信号分布堆叠柱状图 -->
        <div class="chart-section">
            <h2>品类信号分布</h2>
            <div class="chart-container" id="chart-category-distribution"></div>
        </div>

        <!-- 各品种正负分对比图 -->
        <div class="chart-section">
            <h2>各品种正负分对比</h2>
            <div class="chart-container-tall" id="chart-score-comparison"></div>
        </div>

        <!-- 热力图 -->
        <div class="chart-section">
            <h2>信号热力图</h2>
            <div class="chart-container-tall" id="chart-heatmap"></div>
        </div>

        <!-- 综合概览表 -->
        <div class="overview-section">
            <h2>综合概览表</h2>
            <table class="overview-table">
                <thead>
                    <tr>
                        <th>品类</th>
                        <th>代码</th>
                        <th>名称</th>
                        <th>当前价格</th>
                        <th>日均交易额</th>
                        <th>正分</th>
                        <th>负分</th>
                        <th>综合信号</th>
                    </tr>
                </thead>
                <tbody>
                    {overview_rows}
                </tbody>
            </table>
        </div>

        <!-- 各品种详细分析卡片 -->
        {detail_cards}

        <!-- 页脚 -->
        <div class="footer">
            <p>本报告基于EMA+MACD右侧交易指标自动生成，仅供参考，不构成投资建议</p>
            <p>数据来源：Binance API / Gate.io API / akshare | 生成时间：<span id="footer-date">{generated_at}</span></p>
        </div>
    </div>

    <script>
        // 嵌入数据
        var assetsData = {assets_js};

        // 品类信号分布堆叠柱状图
        (function() {{
            var categories = {json.dumps(category_order, ensure_ascii=False)};
            var categoryStats = {json.dumps(category_signal_stats, ensure_ascii=False)};

            var bullishData = [], bearishData = [], divergentData = [], neutralData = [];
            categories.forEach(function(cat) {{
                var stats = categoryStats[cat] || {{}};
                bullishData.push(stats['偏多'] || 0);
                bearishData.push(stats['偏空'] || 0);
                divergentData.push(stats['分化'] || 0);
                neutralData.push(stats['中性'] || 0);
            }});

            var chart = echarts.init(document.getElementById('chart-category-distribution'));
            var option = {{
                tooltip: {{
                    trigger: 'axis',
                    axisPointer: {{ type: 'shadow' }},
                    backgroundColor: '#1e293b',
                    borderColor: '#334155',
                    textStyle: {{ color: '#e2e8f0' }}
                }},
                legend: {{
                    data: ['偏多', '偏空', '分化', '中性'],
                    textStyle: {{ color: '#94a3b8' }},
                    top: 0
                }},
                grid: {{
                    left: '3%', right: '4%', bottom: '3%', top: '40px',
                    containLabel: true
                }},
                xAxis: {{
                    type: 'category',
                    data: categories,
                    axisLabel: {{ color: '#94a3b8', rotate: 0 }},
                    axisLine: {{ lineStyle: {{ color: '#334155' }} }}
                }},
                yAxis: {{
                    type: 'value',
                    axisLabel: {{ color: '#94a3b8' }},
                    axisLine: {{ lineStyle: {{ color: '#334155' }} }},
                    splitLine: {{ lineStyle: {{ color: '#1e293b' }} }}
                }},
                series: [
                    {{
                        name: '偏多', type: 'bar', stack: 'total',
                        data: bullishData,
                        itemStyle: {{ color: '#34d399' }}
                    }},
                    {{
                        name: '偏空', type: 'bar', stack: 'total',
                        data: bearishData,
                        itemStyle: {{ color: '#fb7185' }}
                    }},
                    {{
                        name: '分化', type: 'bar', stack: 'total',
                        data: divergentData,
                        itemStyle: {{ color: '#fbbf24' }}
                    }},
                    {{
                        name: '中性', type: 'bar', stack: 'total',
                        data: neutralData,
                        itemStyle: {{ color: '#94a3b8' }}
                    }}
                ]
            }};
            chart.setOption(option);
            window.addEventListener('resize', function() {{ chart.resize(); }});
        }})();

        // 各品种正负分对比图
        (function() {{
            var symbols = assetsData.map(function(a) {{ return a.symbol; }});
            var positiveScores = assetsData.map(function(a) {{ return a.positive_score; }});
            var negativeScores = assetsData.map(function(a) {{ return -a.negative_score; }});

            var chart = echarts.init(document.getElementById('chart-score-comparison'));
            var option = {{
                tooltip: {{
                    trigger: 'axis',
                    axisPointer: {{ type: 'shadow' }},
                    backgroundColor: '#1e293b',
                    borderColor: '#334155',
                    textStyle: {{ color: '#e2e8f0' }},
                    formatter: function(params) {{
                        var tip = params[0].name + '<br/>';
                        params.forEach(function(p) {{
                            tip += p.marker + p.seriesName + ': ' + (p.value > 0 ? '+' : '') + p.value + '<br/>';
                        }});
                        return tip;
                    }}
                }},
                legend: {{
                    data: ['正分', '负分'],
                    textStyle: {{ color: '#94a3b8' }},
                    top: 0
                }},
                grid: {{
                    left: '3%', right: '4%', bottom: '15%', top: '40px',
                    containLabel: true
                }},
                xAxis: {{
                    type: 'category',
                    data: symbols,
                    axisLabel: {{
                        color: '#94a3b8',
                        rotate: 45,
                        fontSize: 10
                    }},
                    axisLine: {{ lineStyle: {{ color: '#334155' }} }}
                }},
                yAxis: {{
                    type: 'value',
                    axisLabel: {{ color: '#94a3b8' }},
                    axisLine: {{ lineStyle: {{ color: '#334155' }} }},
                    splitLine: {{ lineStyle: {{ color: '#1e293b' }} }}
                }},
                series: [
                    {{
                        name: '正分', type: 'bar',
                        data: positiveScores,
                        itemStyle: {{ color: '#34d399' }}
                    }},
                    {{
                        name: '负分', type: 'bar',
                        data: negativeScores,
                        itemStyle: {{ color: '#fb7185' }}
                    }}
                ]
            }};
            chart.setOption(option);
            window.addEventListener('resize', function() {{ chart.resize(); }});
        }})();

        // 热力图
        (function() {{
            var periods = ['日线', '周线', '月线', '季线', '年线'];
            var symbols = assetsData.map(function(a) {{ return a.symbol; }});

            var heatData = [];
            var maxScore = 2;
            assetsData.forEach(function(asset, i) {{
                asset.details.forEach(function(d, j) {{
                    var score = 0;
                    if (d.score.startsWith('+')) score = parseInt(d.score.substring(1));
                    else if (d.score.startsWith('-')) score = parseInt(d.score);
                    heatData.push([j, i, score]);
                }});
            }});

            var chart = echarts.init(document.getElementById('chart-heatmap'));
            var option = {{
                tooltip: {{
                    position: 'top',
                    backgroundColor: '#1e293b',
                    borderColor: '#334155',
                    textStyle: {{ color: '#e2e8f0' }},
                    formatter: function(params) {{
                        return symbols[params.value[1]] + ' - ' + periods[params.value[0]] + '<br/>得分: ' + (params.value[2] > 0 ? '+' : '') + params.value[2];
                    }}
                }},
                grid: {{
                    left: '3%', right: '12%', bottom: '15%', top: '10px',
                    containLabel: true
                }},
                xAxis: {{
                    type: 'category',
                    data: periods,
                    splitArea: {{ show: true }},
                    axisLabel: {{ color: '#94a3b8' }},
                    axisLine: {{ lineStyle: {{ color: '#334155' }} }}
                }},
                yAxis: {{
                    type: 'category',
                    data: symbols,
                    splitArea: {{ show: true }},
                    axisLabel: {{
                        color: '#94a3b8',
                        fontSize: 10
                    }},
                    axisLine: {{ lineStyle: {{ color: '#334155' }} }}
                }},
                visualMap: {{
                    min: -2,
                    max: 2,
                    calculable: true,
                    orient: 'vertical',
                    right: '2%',
                    top: 'center',
                    inRange: {{
                        color: ['#fb7185', '#1e293b', '#34d399']
                    }},
                    textStyle: {{ color: '#94a3b8' }},
                    text: ['正', '负']
                }},
                series: [{{
                    type: 'heatmap',
                    data: heatData,
                    label: {{
                        show: true,
                        color: '#e2e8f0',
                        fontSize: 9,
                        formatter: function(p) {{
                            var v = p.value[2];
                            return v > 0 ? '+' + v : '' + v;
                        }}
                    }},
                    emphasis: {{
                        itemStyle: {{
                            shadowBlur: 10,
                            shadowColor: 'rgba(56,189,248,0.5)'
                        }}
                    }}
                }}]
            }};
            chart.setOption(option);
            window.addEventListener('resize', function() {{ chart.resize(); }});
        }})();

        // 品类筛选功能
        (function() {{
            var filterBtns = document.querySelectorAll('.filter-btn');
            var categorySections = document.querySelectorAll('.category-section');
            var overviewRows = document.querySelectorAll('.overview-table tbody tr');

            filterBtns.forEach(function(btn) {{
                btn.addEventListener('click', function() {{
                    var filter = this.getAttribute('data-filter');

                    filterBtns.forEach(function(b) {{ b.classList.remove('active'); }});
                    this.classList.add('active');

                    // 筛选品类区块
                    categorySections.forEach(function(section) {{
                        if (filter === 'all' || section.id === 'cat-' + filter) {{
                            section.style.display = 'block';
                        }} else {{
                            section.style.display = 'none';
                        }}
                    }});

                    // 筛选概览表行
                    overviewRows.forEach(function(row) {{
                        var catCell = row.querySelector('td');
                        if (!catCell) return;
                        if (filter === 'all' || catCell.textContent === filter) {{
                            row.style.display = '';
                        }} else {{
                            row.style.display = 'none';
                        }}
                    }});
                }});
            }});
        }})();

        // 动态日期
        (function() {{
            var now = new Date();
            var dateStr = now.getFullYear() + '-' +
                String(now.getMonth() + 1).padStart(2, '0') + '-' +
                String(now.getDate()).padStart(2, '0') + ' ' +
                String(now.getHours()).padStart(2, '0') + ':' +
                String(now.getMinutes()).padStart(2, '0') + ':' +
                String(now.getSeconds()).padStart(2, '0');
            var reportDateEl = document.getElementById('report-date');
            if (reportDateEl) reportDateEl.textContent = dateStr;
        }})();
    </script>
</body>
</html>"""

    return html


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    result_path = os.path.join(script_dir, 'result.json')

    # 读取result.json
    print(f"读取数据文件: {result_path}")
    with open(result_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"共 {data['total_assets']} 个品种")

    # 生成HTML
    html_content = generate_html(data)

    # 输出HTML文件
    output_path = os.path.join(os.path.dirname(script_dir), 'new-assets-right-side.html')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"HTML报告已生成: {output_path}")
    print(f"文件大小: {os.path.getsize(output_path) / 1024:.1f} KB")


if __name__ == '__main__':
    main()

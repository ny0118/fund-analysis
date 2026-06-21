(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var accent2 = style.getPropertyValue('--accent2').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var positive = style.getPropertyValue('--positive').trim();
  var negative = style.getPropertyValue('--negative').trim();

  // ============================================
  // DATA: Real analysis results with yearly & volume
  // ============================================
  var assets = {
    'BTC': {
      name: '比特币', symbol: 'BTCUSDT', price: 63260.30, date: '2026-06-20',
      volume: 1686272542,
      composite: { signal: '中性', rightPos: 0, rightNeg: 0, leftPos: 0, leftNeg: 0, totalPos: 0, totalNeg: 0 },
      periods: {
        daily:   { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=36.69', kdjDetail: 'J值=14.05', bollDetail: '价格在布林带区间内' },
        weekly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=35.45', kdjDetail: 'J值=4.88', bollDetail: '价格在布林带区间内' },
        monthly: { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: 'RSI=45.11', kdjDetail: 'J值=0.59', bollDetail: '价格在布林带区间内' },
        quarterly:{ ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: 'J值=13.6', bollDetail: '数据不足' },
        yearly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: '数据不足', bollDetail: '数据不足' }
      }
    },
    'ETH': {
      name: '以太坊', symbol: 'ETHUSDT', price: 1709.68, date: '2026-06-20',
      volume: 1455796653,
      composite: { signal: '偏多', rightPos: 0, rightNeg: 0, leftPos: 1, leftNeg: 0, totalPos: 1, totalNeg: 0 },
      periods: {
        daily:   { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=38.51', kdjDetail: 'J值=27.01', bollDetail: '价格在布林带区间内' },
        weekly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=32.66', kdjDetail: 'J值=9.91', bollDetail: '价格在布林带区间内' },
        monthly: { ema: 0, macd: 0, rsi: 0, kdj: 1, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: 'RSI=37.77', kdjDetail: 'J值=-5.26<0，左侧超卖', bollDetail: '价格在布林带区间内' },
        quarterly:{ ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: 'J值=9.1', bollDetail: '数据不足' },
        yearly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: '数据不足', bollDetail: '数据不足' }
      }
    },
    'GOLD': {
      name: '黄金', symbol: 'GLD', price: 387.12, date: '2026-06-18',
      volume: 4558496799,
      composite: { signal: '偏空', rightPos: 0, rightNeg: -1, leftPos: 0, leftNeg: 0, totalPos: 0, totalNeg: -1 },
      periods: {
        daily:   { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=38.16', kdjDetail: 'J值=62.63', bollDetail: '价格在布林带区间内' },
        weekly:  { ema: 0, macd: -1, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'DIF下穿零轴', rsiDetail: 'RSI=40.88', kdjDetail: 'J值=12.87', bollDetail: '价格在布林带区间内' },
        monthly: { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=62.39', kdjDetail: 'J值=19.03', bollDetail: '价格在布林带区间内' },
        quarterly:{ ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: 'J值=65.09', bollDetail: '数据不足' },
        yearly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: '数据不足', bollDetail: '数据不足' }
      }
    },
    'SPX': {
      name: '标普500', symbol: 'SPY', price: 746.74, date: '2026-06-18',
      volume: 46703712363,
      composite: { signal: '偏空', rightPos: 0, rightNeg: 0, leftPos: 0, leftNeg: -1, totalPos: 0, totalNeg: -1 },
      periods: {
        daily:   { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=54.11', kdjDetail: 'J值=75.37', bollDetail: '价格在布林带区间内' },
        weekly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=66.2', kdjDetail: 'J值=77.28', bollDetail: '价格在布林带区间内' },
        monthly: { ema: 0, macd: 0, rsi: -1, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=72.94>70，左侧超买', kdjDetail: 'J值=91.53', bollDetail: '价格在布林带区间内' },
        quarterly:{ ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: 'J值=94.47', bollDetail: '数据不足' },
        yearly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: '数据不足', bollDetail: '数据不足' }
      }
    },
    'OIL': {
      name: '原油(WTI)', symbol: 'USO', price: 114.87, date: '2026-06-18',
      volume: 1066643401,
      composite: { signal: '中性', rightPos: 0, rightNeg: 0, leftPos: 0, leftNeg: 0, totalPos: 0, totalNeg: 0 },
      periods: {
        daily:   { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=33.16', kdjDetail: 'J值=4.02', bollDetail: '价格在布林带区间内' },
        weekly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=51.28', kdjDetail: 'J值=2.97', bollDetail: '价格在布林带区间内' },
        monthly: { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=61.47', kdjDetail: 'J值=68.35', bollDetail: '价格在布林带区间内' },
        quarterly:{ ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: 'J值=68.73', bollDetail: '数据不足' },
        yearly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: '数据不足', bollDetail: '数据不足' }
      }
    },
    'NDX': {
      name: '纳斯达克100', symbol: 'QQQ', price: 740.62, date: '2026-06-18',
      volume: 29546567893,
      composite: { signal: '偏空', rightPos: 0, rightNeg: 0, leftPos: 0, leftNeg: -3, totalPos: 0, totalNeg: -3 },
      periods: {
        daily:   { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=59.09', kdjDetail: 'J值=94.04', bollDetail: '价格在布林带区间内' },
        weekly:  { ema: 0, macd: 0, rsi: -1, kdj: 0, boll: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=70.69>70，左侧超买', kdjDetail: 'J值=89.61', bollDetail: '价格在布林带区间内' },
        monthly: { ema: 0, macd: 0, rsi: -1, kdj: 0, boll: -1, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换', rsiDetail: 'RSI=78.15>70，左侧超买', kdjDetail: 'J值=97.25', bollDetail: '价格在上轨上方，左侧超买' },
        quarterly:{ ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: 'J值=95.31', bollDetail: '数据不足' },
        yearly:  { ema: 0, macd: 0, rsi: 0, kdj: 0, boll: 0, emaDetail: '数据不足', macdDetail: '数据不足', rsiDetail: '数据不足', kdjDetail: '数据不足', bollDetail: '数据不足' }
      }
    }
  };

  var periodNames = { daily: '日线', weekly: '周线', monthly: '月线', quarterly: '季线', yearly: '年线' };
  var indicatorNames = { ema: 'EMA', macd: 'MACD', rsi: 'RSI', kdj: 'KDJ', boll: 'BOLL' };

  // Helper: compute right-side (EMA+MACD) and left-side (RSI+KDJ+BOLL) scores per period
  function computeScores(pd) {
    var rightPos = (pd.ema > 0 ? 1 : 0) + (pd.macd > 0 ? 1 : 0);
    var rightNeg = (pd.ema < 0 ? -1 : 0) + (pd.macd < 0 ? -1 : 0);
    var leftPos = (pd.rsi > 0 ? 1 : 0) + (pd.kdj > 0 ? 1 : 0) + (pd.boll > 0 ? 1 : 0);
    var leftNeg = (pd.rsi < 0 ? -1 : 0) + (pd.kdj < 0 ? -1 : 0) + (pd.boll < 0 ? -1 : 0);
    return { rightPos: rightPos, rightNeg: rightNeg, leftPos: leftPos, leftNeg: leftNeg };
  }

  function formatVolume(v) {
    if (v >= 1e9) return '$' + (v / 1e9).toFixed(2) + 'B';
    if (v >= 1e6) return '$' + (v / 1e6).toFixed(1) + 'M';
    return '$' + v.toFixed(0);
  }

  function badgeHtml(pos, neg) {
    if (pos > 0) return '<span class="badge badge-positive">+' + pos + '</span>';
    if (neg < 0) return '<span class="badge badge-negative">' + neg + '</span>';
    return '<span class="badge badge-neutral">0</span>';
  }

  // ============================================
  // Build overview table (right/left separated, 5 periods)
  // ============================================
  var overviewBody = document.getElementById('overview-body');
  var assetKeys = Object.keys(assets);

  assetKeys.forEach(function(key) {
    var a = assets[key];
    var row = document.createElement('tr');
    var periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'];
    var html = '<td class="asset-col">' + a.name + '<br><span class="asset-symbol">' + a.symbol + '</span></td>';
    html += '<td>$' + a.price.toFixed(2) + '</td>';
    html += '<td>' + formatVolume(a.volume) + '</td>';

    // Right-side columns
    periods.forEach(function(p) {
      var sc = computeScores(a.periods[p]);
      html += '<td>' + badgeHtml(sc.rightPos, sc.rightNeg) + '</td>';
    });
    // Left-side columns
    periods.forEach(function(p) {
      var sc = computeScores(a.periods[p]);
      html += '<td>' + badgeHtml(sc.leftPos, sc.leftNeg) + '</td>';
    });

    // Composite signal
    var comp = a.composite;
    var signalBadge = comp.totalPos > 0 && comp.totalNeg === 0 ? 'badge-positive' :
                      comp.totalNeg < 0 && comp.totalPos === 0 ? 'badge-negative' :
                      comp.totalPos > 0 && comp.totalNeg < 0 ? 'badge-neutral' : 'badge-neutral';
    html += '<td><span class="badge ' + signalBadge + '">' + comp.signal + '</span></td>';
    row.innerHTML = html;
    overviewBody.appendChild(row);
  });

  // ============================================
  // Build composite scores section
  // ============================================
  var compositeContainer = document.getElementById('composite-scores');
  assetKeys.forEach(function(key) {
    var a = assets[key];
    var comp = a.composite;
    var card = document.createElement('div');
    card.style.cssText = 'background:var(--bg2);border:1px solid var(--rule);border-radius:10px;padding:1rem;';

    var signalColor = comp.signal === '偏多' ? positive : (comp.signal === '偏空' ? negative : muted);

    card.innerHTML =
      '<div style="font-weight:700;font-size:1rem;color:var(--ink);margin-bottom:0.5rem;">' + a.name + '</div>' +
      '<div style="font-size:1.5rem;font-weight:700;color:' + signalColor + ';margin-bottom:0.5rem;">' + comp.signal + '</div>' +
      '<div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem;font-size:0.8rem;">' +
        '<div style="color:var(--accent);">右侧: +' + comp.rightPos + ' / ' + comp.rightNeg + '</div>' +
        '<div style="color:var(--accent2);">左侧: +' + comp.leftPos + ' / ' + comp.leftNeg + '</div>' +
        '<div style="color:var(--positive);">总正分: +' + comp.totalPos + '</div>' +
        '<div style="color:var(--negative);">总负分: ' + comp.totalNeg + '</div>' +
      '</div>';
    compositeContainer.appendChild(card);
  });

  // ============================================
  // Build detail cards
  // ============================================
  var detailContainer = document.getElementById('assets-detail');

  assetKeys.forEach(function(key) {
    var a = assets[key];
    var card = document.createElement('div');
    card.className = 'asset-card';

    var comp = a.composite;
    var signalColor = comp.signal === '偏多' ? positive : (comp.signal === '偏空' ? negative : muted);

    var headerHtml = '<div class="asset-header">' +
      '<div><span class="asset-name">' + a.name + '</span> <span class="asset-symbol">' + a.symbol + '</span></div>' +
      '<div style="text-align:right;">' +
        '<div class="asset-price">$' + a.price.toFixed(2) + ' <span style="font-size:0.8rem;color:var(--muted)">' + a.date + '</span></div>' +
        '<div style="font-size:0.85rem;color:' + signalColor + ';font-weight:700;">' + comp.signal + '</div>' +
      '</div>' +
      '</div>';

    var gridHtml = '<div class="score-grid">';
    var periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'];

    periods.forEach(function(p) {
      var pd = a.periods[p];
      var sc = computeScores(pd);
      gridHtml += '<div class="period-card">';
      gridHtml += '<div class="period-name">' + periodNames[p] + '</div>';

      ['ema', 'macd', 'rsi', 'kdj', 'boll'].forEach(function(ind) {
        var score = pd[ind];
        var valClass = score > 0 ? 'positive' : (score < 0 ? 'negative' : 'neutral');
        var valText = score > 0 ? '+1' : (score < 0 ? '-1' : '0');
        var sideLabel = (ind === 'ema' || ind === 'macd') ? ' [右]' : ' [左]';
        gridHtml += '<div class="indicator-row">' +
          '<span class="indicator-label">' + indicatorNames[ind] + sideLabel + '</span>' +
          '<span class="indicator-value ' + valClass + '">' + valText + '</span>' +
          '</div>';
      });

      gridHtml += '<div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid var(--rule);font-size:0.75rem;">';
      gridHtml += '<span style="color:var(--accent);">右侧: ' + (sc.rightPos > 0 ? '+' + sc.rightPos : sc.rightNeg < 0 ? sc.rightNeg : '0') + '</span> | ';
      gridHtml += '<span style="color:var(--accent2);">左侧: ' + (sc.leftPos > 0 ? '+' + sc.leftPos : sc.leftNeg < 0 ? sc.leftNeg : '0') + '</span>';
      gridHtml += '</div>';

      gridHtml += '</div>';
    });

    gridHtml += '</div>';
    card.innerHTML = headerHtml + gridHtml;
    detailContainer.appendChild(card);
  });

  // ============================================
  // Chart 1: Right-side Score Comparison
  // ============================================
  var chart1 = echarts.init(document.getElementById('chart-right-comparison'), null, { renderer: 'svg' });

  var assetNames = assetKeys.map(function(k) { return assets[k].name; });
  var rightPosData = assetKeys.map(function(k) { return assets[k].composite.rightPos; });
  var rightNegData = assetKeys.map(function(k) { return Math.abs(assets[k].composite.rightNeg); });

  chart1.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['正分', '负分'], textStyle: { color: muted }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
    xAxis: {
      type: 'category',
      data: assetNames,
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: ink }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: rule } },
      splitLine: { lineStyle: { color: rule, opacity: 0.3 } },
      axisLabel: { color: muted }
    },
    series: [
      {
        name: '正分',
        type: 'bar',
        data: rightPosData,
        itemStyle: { color: positive, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      },
      {
        name: '负分',
        type: 'bar',
        data: rightNegData,
        itemStyle: { color: negative, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      }
    ]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // ============================================
  // Chart 2: Left-side Score Comparison
  // ============================================
  var chart2 = echarts.init(document.getElementById('chart-left-comparison'), null, { renderer: 'svg' });

  var leftPosData = assetKeys.map(function(k) { return assets[k].composite.leftPos; });
  var leftNegData = assetKeys.map(function(k) { return Math.abs(assets[k].composite.leftNeg); });

  chart2.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['正分', '负分'], textStyle: { color: muted }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
    xAxis: {
      type: 'category',
      data: assetNames,
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: ink }
    },
    yAxis: {
      type: 'value',
      axisLine: { lineStyle: { color: rule } },
      splitLine: { lineStyle: { color: rule, opacity: 0.3 } },
      axisLabel: { color: muted }
    },
    series: [
      {
        name: '正分',
        type: 'bar',
        data: leftPosData,
        itemStyle: { color: positive, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      },
      {
        name: '负分',
        type: 'bar',
        data: leftNegData,
        itemStyle: { color: negative, borderRadius: [4, 4, 0, 0] },
        barWidth: '30%'
      }
    ]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

  // ============================================
  // Chart 3: Heatmap (Asset x Period x Indicator)
  // ============================================
  var chart3 = echarts.init(document.getElementById('chart-heatmap'), null, { renderer: 'svg' });

  var yData = [];
  var xData = ['日线EMA', '日线MACD', '日线RSI', '日线KDJ', '日线BOLL',
               '周线EMA', '周线MACD', '周线RSI', '周线KDJ', '周线BOLL',
               '月线EMA', '月线MACD', '月线RSI', '月线KDJ', '月线BOLL',
               '季线EMA', '季线MACD', '季线RSI', '季线KDJ', '季线BOLL',
               '年线EMA', '年线MACD', '年线RSI', '年线KDJ', '年线BOLL'];

  var heatData = [];

  assetKeys.forEach(function(key, yi) {
    var a = assets[key];
    yData.push(a.name);
    var periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'];
    periods.forEach(function(p, pi) {
      var pd = a.periods[p];
      var indicators = ['ema', 'macd', 'rsi', 'kdj', 'boll'];
      indicators.forEach(function(ind, ii) {
        var score = pd[ind];
        var xi = pi * 5 + ii;
        heatData.push([xi, yi, score]);
      });
    });
  });

  chart3.setOption({
    animation: false,
    tooltip: {
      position: 'top',
      appendToBody: true,
      formatter: function(p) {
        var val = p.value[2];
        var label = val > 0 ? '+1 (看多)' : (val < 0 ? '-1 (看空)' : '0 (中性)');
        return yData[p.value[1]] + '<br>' + xData[p.value[0]] + ': <strong>' + label + '</strong>';
      }
    },
    grid: { left: '12%', right: '5%', top: '5%', bottom: '12%' },
    xAxis: {
      type: 'category',
      data: xData,
      splitArea: { show: false },
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: muted, fontSize: 10, rotate: 45 }
    },
    yAxis: {
      type: 'category',
      data: yData,
      splitArea: { show: false },
      axisLine: { lineStyle: { color: rule } },
      axisLabel: { color: ink }
    },
    visualMap: {
      min: -1,
      max: 1,
      calculable: false,
      orient: 'horizontal',
      left: 'center',
      bottom: '0%',
      itemWidth: 20,
      itemHeight: 12,
      textStyle: { color: muted },
      inRange: {
        color: [negative + 'cc', bg2, positive + 'cc']
      },
      outOfRange: { color: 'transparent' },
      pieces: [
        { min: -1, max: -1, label: '-1', color: negative + 'cc' },
        { min: 0, max: 0, label: '0', color: bg2 },
        { min: 1, max: 1, label: '+1', color: positive + 'cc' }
      ]
    },
    series: [{
      name: '指标得分',
      type: 'heatmap',
      data: heatData,
      label: {
        show: true,
        formatter: function(p) {
          var v = p.value[2];
          return v > 0 ? '+1' : (v < 0 ? '-1' : '0');
        },
        color: ink,
        fontSize: 11,
        fontWeight: 'bold'
      }
    }]
  });
  window.addEventListener('resize', function() { chart3.resize(); });

})();

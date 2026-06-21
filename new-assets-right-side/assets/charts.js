(function() {
  var style = getComputedStyle(document.documentElement);
  var accent = style.getPropertyValue('--accent').trim();
  var ink = style.getPropertyValue('--ink').trim();
  var muted = style.getPropertyValue('--muted').trim();
  var rule = style.getPropertyValue('--rule').trim();
  var bg2 = style.getPropertyValue('--bg2').trim();
  var positive = style.getPropertyValue('--positive').trim();
  var negative = style.getPropertyValue('--negative').trim();

  var assets = {
    'SLV': {
      name: '白银', symbol: 'SLV', price: 43.40, date: '2026-06-18',
      volume: 2224267787,
      composite: { signal: '偏空', totalPos: 0, totalNeg: -2 },
      periods: {
        daily:   { ema: 0, macd: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        weekly:  { ema: 0, macd: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        monthly: { ema: 0, macd: -1, emaDetail: '数据不足', macdDetail: 'DIF下穿零轴' },
        quarterly:{ ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        yearly:  { ema: 0, macd: -1, emaDetail: '数据不足', macdDetail: 'MACD由正转负' }
      }
    },
    'TLT': {
      name: '美国国债', symbol: 'TLT', price: 92.90, date: '2026-06-18',
      volume: 2344840639,
      composite: { signal: '偏多', totalPos: 1, totalNeg: 0 },
      periods: {
        daily:   { ema: 0, macd: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        weekly:  { ema: 0, macd: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        monthly: { ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        quarterly:{ ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        yearly:  { ema: 0, macd: 1, emaDetail: '数据不足', macdDetail: 'MACD由负转正' }
      }
    },
    'IWM': {
      name: '罗素2000', symbol: 'IWM', price: 228.29, date: '2026-06-18',
      volume: 8914699605,
      composite: { signal: '偏多', totalPos: 1, totalNeg: 0 },
      periods: {
        daily:   { ema: 0, macd: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        weekly:  { ema: 0, macd: 0, emaDetail: 'EMA12高于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        monthly: { ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        quarterly:{ ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        yearly:  { ema: 1, macd: 0, emaDetail: 'EMA12上穿EMA52', macdDetail: 'MACD未发生正负转换' }
      }
    },
    'UUP': {
      name: '美元指数', symbol: 'UUP', price: 28.27, date: '2026-06-18',
      volume: 64168807,
      composite: { signal: '偏空', totalPos: 0, totalNeg: -1 },
      periods: {
        daily:   { ema: 0, macd: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        weekly:  { ema: 0, macd: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        monthly: { ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        quarterly:{ ema: 0, macd: -1, emaDetail: '数据不足', macdDetail: 'DIF下穿零轴' },
        yearly:  { ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' }
      }
    },
    'SOL': {
      name: 'Solana', symbol: 'SOLUSDT', price: 146.19, date: '2026-06-20',
      volume: 268996536,
      composite: { signal: '中性', totalPos: 0, totalNeg: 0 },
      periods: {
        daily:   { ema: 0, macd: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        weekly:  { ema: 0, macd: 0, emaDetail: 'EMA12低于EMA52但无交叉', macdDetail: 'MACD未发生正负转换' },
        monthly: { ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        quarterly:{ ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' },
        yearly:  { ema: 0, macd: 0, emaDetail: '数据不足', macdDetail: 'MACD未发生正负转换' }
      }
    }
  };

  var periodNames = { daily: '日线', weekly: '周线', monthly: '月线', quarterly: '季线', yearly: '年线' };
  var indicatorNames = { ema: 'EMA', macd: 'MACD' };

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

  var assetKeys = Object.keys(assets);

  // Overview table
  var overviewBody = document.getElementById('overview-body');
  assetKeys.forEach(function(key) {
    var a = assets[key];
    var row = document.createElement('tr');
    var periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'];
    var html = '<td class="asset-col">' + a.name + '<br><span class="asset-symbol">' + a.symbol + '</span></td>';
    html += '<td>$' + a.price.toFixed(2) + '</td>';
    html += '<td>' + formatVolume(a.volume) + '</td>';

    periods.forEach(function(p) {
      var pd = a.periods[p];
      var pos = (pd.ema > 0 ? 1 : 0) + (pd.macd > 0 ? 1 : 0);
      var neg = (pd.ema < 0 ? -1 : 0) + (pd.macd < 0 ? -1 : 0);
      html += '<td>' + badgeHtml(pos, neg) + '</td>';
    });

    var comp = a.composite;
    var signalBadge = comp.totalPos > 0 && comp.totalNeg === 0 ? 'badge-positive' :
                      comp.totalNeg < 0 && comp.totalPos === 0 ? 'badge-negative' : 'badge-neutral';
    html += '<td><span class="badge ' + signalBadge + '">' + comp.signal + '</span></td>';
    row.innerHTML = html;
    overviewBody.appendChild(row);
  });

  // Composite scores
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
        '<div style="color:var(--positive);">总正分: +' + comp.totalPos + '</div>' +
        '<div style="color:var(--negative);">总负分: ' + comp.totalNeg + '</div>' +
      '</div>';
    compositeContainer.appendChild(card);
  });

  // Detail cards
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
      var pos = (pd.ema > 0 ? 1 : 0) + (pd.macd > 0 ? 1 : 0);
      var neg = (pd.ema < 0 ? -1 : 0) + (pd.macd < 0 ? -1 : 0);
      gridHtml += '<div class="period-card">';
      gridHtml += '<div class="period-name">' + periodNames[p] + '</div>';
      ['ema', 'macd'].forEach(function(ind) {
        var score = pd[ind];
        var valClass = score > 0 ? 'positive' : (score < 0 ? 'negative' : 'neutral');
        var valText = score > 0 ? '+1' : (score < 0 ? '-1' : '0');
        gridHtml += '<div class="indicator-row">' +
          '<span class="indicator-label">' + indicatorNames[ind] + '</span>' +
          '<span class="indicator-value ' + valClass + '">' + valText + '</span>' +
          '</div>';
      });
      gridHtml += '<div style="margin-top:0.5rem;padding-top:0.5rem;border-top:1px solid var(--rule);font-size:0.75rem;text-align:center;">';
      gridHtml += '<span style="color:var(--accent);">得分: ' + (pos > 0 ? '+' + pos : neg < 0 ? neg : '0') + '</span>';
      gridHtml += '</div>';
      gridHtml += '</div>';
    });
    gridHtml += '</div>';
    card.innerHTML = headerHtml + gridHtml;
    detailContainer.appendChild(card);
  });

  // Chart 1: Right-side Score Comparison
  var chart1 = echarts.init(document.getElementById('chart-right-comparison'), null, { renderer: 'svg' });
  var assetNames = assetKeys.map(function(k) { return assets[k].name; });
  var posData = assetKeys.map(function(k) { return assets[k].composite.totalPos; });
  var negData = assetKeys.map(function(k) { return Math.abs(assets[k].composite.totalNeg); });

  chart1.setOption({
    animation: false,
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' }, appendToBody: true },
    legend: { data: ['正分', '负分'], textStyle: { color: muted }, top: 0 },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '40px', containLabel: true },
    xAxis: { type: 'category', data: assetNames, axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink } },
    yAxis: { type: 'value', axisLine: { lineStyle: { color: rule } }, splitLine: { lineStyle: { color: rule, opacity: 0.3 } }, axisLabel: { color: muted } },
    series: [
      { name: '正分', type: 'bar', data: posData, itemStyle: { color: positive, borderRadius: [4, 4, 0, 0] }, barWidth: '30%' },
      { name: '负分', type: 'bar', data: negData, itemStyle: { color: negative, borderRadius: [4, 4, 0, 0] }, barWidth: '30%' }
    ]
  });
  window.addEventListener('resize', function() { chart1.resize(); });

  // Chart 2: Heatmap
  var chart2 = echarts.init(document.getElementById('chart-heatmap'), null, { renderer: 'svg' });
  var yData = [];
  var xData = ['日线EMA', '日线MACD', '周线EMA', '周线MACD', '月线EMA', '月线MACD',
               '季线EMA', '季线MACD', '年线EMA', '年线MACD'];
  var heatData = [];

  assetKeys.forEach(function(key, yi) {
    var a = assets[key];
    yData.push(a.name);
    var periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly'];
    periods.forEach(function(p, pi) {
      var pd = a.periods[p];
      heatData.push([pi * 2, yi, pd.ema]);
      heatData.push([pi * 2 + 1, yi, pd.macd]);
    });
  });

  chart2.setOption({
    animation: false,
    tooltip: { position: 'top', appendToBody: true, formatter: function(p) {
      var val = p.value[2];
      var label = val > 0 ? '+1 (看多)' : (val < 0 ? '-1 (看空)' : '0 (中性)');
      return yData[p.value[1]] + '<br>' + xData[p.value[0]] + ': <strong>' + label + '</strong>';
    }},
    grid: { left: '12%', right: '5%', top: '5%', bottom: '12%' },
    xAxis: { type: 'category', data: xData, splitArea: { show: false }, axisLine: { lineStyle: { color: rule } }, axisLabel: { color: muted, fontSize: 10, rotate: 45 } },
    yAxis: { type: 'category', data: yData, splitArea: { show: false }, axisLine: { lineStyle: { color: rule } }, axisLabel: { color: ink } },
    visualMap: {
      min: -1, max: 1, calculable: false, orient: 'horizontal', left: 'center', bottom: '0%',
      itemWidth: 20, itemHeight: 12, textStyle: { color: muted },
      inRange: { color: [negative + 'cc', bg2, positive + 'cc'] },
      outOfRange: { color: 'transparent' },
      pieces: [
        { min: -1, max: -1, label: '-1', color: negative + 'cc' },
        { min: 0, max: 0, label: '0', color: bg2 },
        { min: 1, max: 1, label: '+1', color: positive + 'cc' }
      ]
    },
    series: [{ name: '指标得分', type: 'heatmap', data: heatData,
      label: { show: true, formatter: function(p) { var v = p.value[2]; return v > 0 ? '+1' : (v < 0 ? '-1' : '0'); }, color: ink, fontSize: 11, fontWeight: 'bold' }
    }]
  });
  window.addEventListener('resize', function() { chart2.resize(); });

})();

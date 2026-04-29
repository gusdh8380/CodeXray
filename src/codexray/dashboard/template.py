from __future__ import annotations

from string import Template

HTML_TEMPLATE = Template(
    """<!DOCTYPE html>
<!-- codexray-dashboard-v1 -->
<html lang="en">
<head>
<meta charset="utf-8">
<title>CodeXray Dashboard — $path</title>
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; height: 100%; font-family: -apple-system, system-ui, sans-serif; color: #111827; background: #f9fafb; }
  header { padding: 12px 18px; background: #111827; color: #f9fafb; display: flex; align-items: baseline; gap: 16px; flex-wrap: wrap; }
  header h1 { margin: 0; font-size: 18px; }
  header .meta { font-size: 13px; opacity: 0.85; display: flex; gap: 14px; flex-wrap: wrap; }
  header .grade strong { font-size: 15px; padding: 1px 8px; border-radius: 4px; background: #dc2626; color: white; }
  header .grade.A strong { background: #16a34a; }
  header .grade.B strong { background: #65a30d; }
  header .grade.C strong { background: #ca8a04; }
  header .grade.D strong { background: #ea580c; }
  header .grade.F strong { background: #dc2626; }
  header .grade.NA strong { background: #6b7280; }
  .layout { display: flex; height: calc(100vh - 50px); }
  .sidebar { width: 320px; padding: 14px; border-right: 1px solid #e5e7eb; overflow-y: auto; background: #ffffff; }
  .sidebar input[type=search] { width: 100%; padding: 6px 10px; font-size: 13px; border: 1px solid #d1d5db; border-radius: 4px; margin-bottom: 12px; }
  .legend { font-size: 12px; display: flex; flex-direction: column; gap: 4px; margin-bottom: 14px; }
  .legend .row { display: flex; align-items: center; gap: 6px; }
  .legend .dot { width: 11px; height: 11px; border-radius: 50%; }
  .dot.hotspot { background: #dc2626; }
  .dot.active_stable { background: #f59e0b; }
  .dot.neglected_complex { background: #eab308; }
  .dot.stable { background: #9ca3af; }
  .detail { font-size: 13px; line-height: 1.5; }
  .detail h3 { margin: 0 0 6px; font-size: 14px; word-break: break-all; }
  .detail .badge { display: inline-block; padding: 1px 7px; border-radius: 3px; color: white; font-size: 11px; }
  .detail dl { display: grid; grid-template-columns: max-content 1fr; gap: 4px 12px; margin: 8px 0; }
  .detail dt { color: #6b7280; }
  .detail dd { margin: 0; }
  .detail .empty { color: #9ca3af; font-style: italic; }
  .graph { flex: 1; position: relative; overflow: hidden; }
  svg { width: 100%; height: 100%; display: block; background: #f9fafb; }
  .node { stroke: #ffffff; stroke-width: 1.5px; cursor: pointer; }
  .node.hotspot { fill: #dc2626; }
  .node.active_stable { fill: #f59e0b; }
  .node.neglected_complex { fill: #eab308; }
  .node.stable { fill: #9ca3af; }
  .node.selected { stroke: #111827; stroke-width: 3px; }
  .node.high-coupling { stroke: #f59e0b; stroke-width: 3px; }
  .node.dim { opacity: 0.15; }
  .edge { stroke: #cbd5e1; stroke-width: 1.2px; opacity: 0.6; }
  .edge.dim { opacity: 0.05; }
  .label { font-size: 10px; fill: #374151; pointer-events: none; }
  .label.dim { opacity: 0.15; }
  .empty-state { padding: 24px; color: #6b7280; font-size: 14px; }
  .hint { color: #9ca3af; font-size: 11px; margin: 6px 0 14px; }
  .zoom-controls { position: absolute; right: 14px; bottom: 14px; display: flex; gap: 4px; flex-direction: column; z-index: 5; }
  .zoom-controls button { width: 32px; height: 32px; border: 1px solid #d1d5db; border-radius: 6px; background: #ffffff; color: #111827; cursor: pointer; font-size: 16px; box-shadow: 0 1px 2px rgba(0,0,0,.06); }
  .zoom-controls button:hover { background: #f3f4f6; }
  svg { cursor: grab; }
  svg:active { cursor: grabbing; }
</style>
</head>
<body>
<header>
  <h1>CodeXray</h1>
  <div class="meta">
    <span class="path">$path</span>
    <span class="date">$date</span>
    <span class="grade $grade_class">Grade: <strong>$grade</strong> ($score)</span>
  </div>
</header>
<div class="layout">
  <aside class="sidebar">
    <input type="search" id="search" placeholder="filter by path..." autocomplete="off" />
    <div class="legend">
      <div class="row"><span class="dot hotspot"></span> Hotspot (자주 변경 × 결합도 높음)</div>
      <div class="row"><span class="dot active_stable"></span> 활발 안정</div>
      <div class="row"><span class="dot neglected_complex"></span> 방치 복잡</div>
      <div class="row"><span class="dot stable"></span> 안정</div>
    </div>
    <p class="hint">스크롤로 확대/축소, 드래그로 이동, 더블클릭은 비활성화</p>
    <div class="detail" id="detail">
      <p class="empty">노드를 클릭하면 상세가 여기에 표시됩니다.</p>
    </div>
  </aside>
  <div class="graph">
    <svg id="viz"></svg>
    <div class="zoom-controls">
      <button type="button" id="zoom-in" aria-label="확대">+</button>
      <button type="button" id="zoom-out" aria-label="축소">−</button>
      <button type="button" id="zoom-reset" aria-label="원래 크기">⟳</button>
    </div>
    <div id="empty" class="empty-state" style="display:none">분석 대상 노드가 없습니다.</div>
  </div>
</div>

<script type="application/json" id="codexray-data-inventory">$data_inventory</script>
<script type="application/json" id="codexray-data-graph">$data_graph</script>
<script type="application/json" id="codexray-data-metrics">$data_metrics</script>
<script type="application/json" id="codexray-data-entrypoints">$data_entrypoints</script>
<script type="application/json" id="codexray-data-quality">$data_quality</script>
<script type="application/json" id="codexray-data-hotspots">$data_hotspots</script>

<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<script>
(function () {
  function readJSON(id) {
    var el = document.getElementById(id);
    return el ? JSON.parse(el.textContent) : null;
  }
  var graphData = readJSON('codexray-data-graph') || {nodes: [], edges: []};
  var metricsData = readJSON('codexray-data-metrics') || {nodes: []};
  var hotspotsData = readJSON('codexray-data-hotspots') || {files: []};
  var entrypointsData = readJSON('codexray-data-entrypoints') || {entrypoints: []};

  var couplingByPath = {};
  (metricsData.nodes || []).forEach(function (n) {
    couplingByPath[n.path] = n;
  });
  var hotspotByPath = {};
  (hotspotsData.files || []).forEach(function (h) {
    hotspotByPath[h.path] = h;
  });
  var entrypointKindsByPath = {};
  (entrypointsData.entrypoints || []).forEach(function (e) {
    if (!entrypointKindsByPath[e.path]) entrypointKindsByPath[e.path] = [];
    entrypointKindsByPath[e.path].push(e.kind);
  });

  var nodes = (graphData.nodes || []).map(function (n) {
    var m = couplingByPath[n.path] || {fan_in: 0, fan_out: 0, external_fan_out: 0};
    var h = hotspotByPath[n.path] || {category: 'stable', change_count: 0, coupling: 0};
    var coupling = (m.fan_in || 0) + (m.fan_out || 0) + (m.external_fan_out || 0);
    return {
      id: n.path,
      language: n.language,
      fan_in: m.fan_in || 0,
      fan_out: m.fan_out || 0,
      external_fan_out: m.external_fan_out || 0,
      coupling: coupling,
      category: h.category || 'stable',
      change_count: h.change_count || 0,
      entrypoint_kinds: entrypointKindsByPath[n.path] || []
    };
  });
  var sortedCouplings = nodes.map(function(d) { return d.coupling; }).slice().sort(function(a,b){return a-b;});
  var p90Coupling = sortedCouplings.length > 1 ? sortedCouplings[Math.floor(sortedCouplings.length * 0.9)] : 0;
  nodes.forEach(function(d) {
    var base = Math.log(d.coupling + 1) * 4 + 4;
    d.highlight = d.coupling >= p90Coupling && p90Coupling > 0;
    d.r = d.highlight ? base * 1.5 : base;
  });
  var nodeById = {};
  nodes.forEach(function (n) { nodeById[n.id] = n; });
  var edges = (graphData.edges || [])
    .filter(function (e) { return e.kind === 'internal' && nodeById[e.from] && nodeById[e.to]; })
    .map(function (e) { return {source: e.from, target: e.to}; });

  var svg = d3.select('#viz');
  var emptyState = document.getElementById('empty');
  if (nodes.length === 0) {
    emptyState.style.display = 'block';
    return;
  }
  var width = svg.node().clientWidth || 800;
  var height = svg.node().clientHeight || 600;

  svg.append('defs').append('marker')
    .attr('id', 'arrow')
    .attr('viewBox', '0 -5 10 10')
    .attr('refX', 14).attr('refY', 0)
    .attr('markerWidth', 6).attr('markerHeight', 6)
    .attr('orient', 'auto')
    .append('path').attr('d', 'M0,-5L10,0L0,5').attr('fill', '#9ca3af');

  var zoomLayer = svg.append('g').attr('class', 'zoom-layer');

  var zoom = d3.zoom()
    .scaleExtent([0.2, 4])
    .on('zoom', function (event) {
      zoomLayer.attr('transform', event.transform);
    });
  svg.call(zoom).on('dblclick.zoom', null);

  function zoomBy(factor) {
    svg.transition().duration(180).call(zoom.scaleBy, factor);
  }
  function zoomReset() {
    svg.transition().duration(220).call(zoom.transform, d3.zoomIdentity);
  }
  document.getElementById('zoom-in').addEventListener('click', function () { zoomBy(1.4); });
  document.getElementById('zoom-out').addEventListener('click', function () { zoomBy(1 / 1.4); });
  document.getElementById('zoom-reset').addEventListener('click', zoomReset);

  var link = zoomLayer.append('g').selectAll('line')
    .data(edges)
    .enter().append('line')
    .attr('class', 'edge')
    .attr('marker-end', 'url(#arrow)');

  var node = zoomLayer.append('g').selectAll('circle')
    .data(nodes)
    .enter().append('circle')
    .attr('class', function (d) { return 'node ' + d.category + (d.highlight ? ' high-coupling' : ''); })
    .attr('r', function (d) { return d.r; })
    .on('click', function (event, d) { selectNode(d); event.stopPropagation(); })
    .call(d3.drag()
      .on('start', function (event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
      })
      .on('drag', function (event, d) { d.fx = event.x; d.fy = event.y; })
      .on('end', function (event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
      }));

  node.append('title').text(function (d) { return d.id + '\\nfan_in=' + d.fan_in + ' fan_out=' + d.fan_out; });

  var simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(edges).id(function (d) { return d.id; }).distance(50))
    .force('charge', d3.forceManyBody().strength(-160))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('x', d3.forceX(width / 2).strength(0.08))
    .force('y', d3.forceY(height / 2).strength(0.08))
    .force('collide', d3.forceCollide().radius(function (d) { return d.r + 2; }))
    .on('tick', tick);

  function tick() {
    link
      .attr('x1', function (d) { return d.source.x; })
      .attr('y1', function (d) { return d.source.y; })
      .attr('x2', function (d) { return d.target.x; })
      .attr('y2', function (d) { return d.target.y; });
    node
      .attr('cx', function (d) { return d.x; })
      .attr('cy', function (d) { return d.y; });
  }

  var detail = document.getElementById('detail');
  function selectNode(d) {
    node.classed('selected', function (n) { return n === d; });
    var html = '<h3>' + escapeHtml(d.id) + '</h3>';
    html += '<span class="badge dot-' + d.category + '" style="background:' + categoryColor(d.category) + '">' + d.category + '</span>';
    html += '<dl>';
    html += '<dt>language</dt><dd>' + escapeHtml(d.language) + '</dd>';
    html += '<dt>fan_in</dt><dd>' + d.fan_in + '</dd>';
    html += '<dt>fan_out</dt><dd>' + d.fan_out + '</dd>';
    html += '<dt>external_fan_out</dt><dd>' + d.external_fan_out + '</dd>';
    html += '<dt>change_count</dt><dd>' + d.change_count + '</dd>';
    if (d.entrypoint_kinds.length) {
      html += '<dt>entrypoint</dt><dd>' + d.entrypoint_kinds.map(escapeHtml).join(', ') + '</dd>';
    }
    html += '</dl>';
    detail.innerHTML = html;
  }
  function categoryColor(cat) {
    return ({hotspot: '#dc2626', active_stable: '#f59e0b', neglected_complex: '#eab308', stable: '#9ca3af'})[cat] || '#9ca3af';
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c];
    });
  }

  var search = document.getElementById('search');
  search.addEventListener('input', function () {
    var q = search.value.trim().toLowerCase();
    if (q === '') {
      node.classed('dim', false);
      link.classed('dim', false);
      return;
    }
    node.classed('dim', function (n) { return n.id.toLowerCase().indexOf(q) === -1; });
    link.classed('dim', function (e) {
      return e.source.id.toLowerCase().indexOf(q) === -1
          && e.target.id.toLowerCase().indexOf(q) === -1;
    });
  });

  window.addEventListener('resize', function () {
    width = svg.node().clientWidth;
    height = svg.node().clientHeight;
    simulation.force('center', d3.forceCenter(width / 2, height / 2));
    simulation.alpha(0.3).restart();
  });
})();
</script>
</body>
</html>
"""
)

/* Renders the chart specs benchmarks/publish.py writes into each page. */
(function () {
  const params = new URLSearchParams(location.search);
  const forced = params.get('theme');
  if (forced === 'light' || forced === 'dark') {
    document.documentElement.setAttribute('data-theme', forced);
  }

  const css = name =>
    getComputedStyle(document.documentElement).getPropertyValue(name).trim();

  const charts = [];

  function axis(spec, extra) {
    const log = spec && spec.type === 'log';
    return Object.assign(
      {
        title: {text: (spec && spec.title) || '', font: {size: 12, color: css('--ink-2')}},
        type: (spec && spec.type) || 'linear',
        rangemode: (spec && spec.rangemode) || 'normal',
        gridcolor: css('--grid'),
        linecolor: css('--axis'),
        zeroline: false,
        tickfont: {size: 11, color: css('--muted')},
        automargin: true,
        // Log axes: label the decades only (1, 10, 100, ...).
        dtick: log ? 1 : undefined
      },
      extra || {}
    );
  }

  function baseLayout(spec) {
    return {
      paper_bgcolor: 'rgba(0,0,0,0)',
      plot_bgcolor: 'rgba(0,0,0,0)',
      font: {family: 'system-ui, -apple-system, "Segoe UI", sans-serif', color: css('--ink')},
      margin: {l: 8, r: 16, t: 8, b: 8},
      hoverlabel: {
        bgcolor: css('--surface'),
        bordercolor: css('--border'),
        font: {color: css('--ink'), size: 12}
      },
      xaxis: axis(spec.xaxis),
      yaxis: axis(spec.yaxis),
      showlegend: false
    };
  }

  function lines(spec) {
    const traces = spec.traces.map(t => ({
      type: 'scatter',
      mode: 'lines+markers',
      name: t.name,
      x: t.x,
      y: t.y,
      line: {color: css('--series-' + t.hue), width: 2, dash: t.dash},
      marker: {size: 8, color: css('--series-' + t.hue), line: {width: 2, color: css('--surface')}},
      hovertemplate: `%{x:,} browsers<br>%{y:,.1f} ${t.unit}<extra>${t.name}</extra>`
    }));
    const layout = baseLayout(spec);
    // Label the x axis at the measured counts rather than log minor ticks.
    const xs = [...new Set(spec.traces.flatMap(t => t.x))].sort((a, b) => a - b);
    if (xs.length) {
      layout.xaxis.tickvals = xs;
      layout.xaxis.ticktext = xs.map(x => x.toLocaleString('en-US'));
      layout.xaxis.dtick = undefined;
    }
    layout.showlegend = true;
    layout.legend = {
      orientation: 'h', x: 0, y: 1.02, xanchor: 'left', yanchor: 'bottom',
      font: {size: 12, color: css('--ink-2')}
    };
    layout.hovermode = 'closest';
    if (spec.threshold) {
      layout.shapes = [{
        type: 'line', xref: 'paper', x0: 0, x1: 1, y0: spec.threshold, y1: spec.threshold,
        line: {color: css('--muted'), width: 1}
      }];
      layout.annotations = [{
        xref: 'paper', x: 0, y: Math.log10(spec.threshold), yref: 'y', xanchor: 'left',
        yanchor: 'bottom', showarrow: false, text: `${spec.threshold} ms`,
        font: {size: 11, color: css('--muted')}
      }];
    }
    return {traces, layout};
  }

  const wrap = label => label.replace(', ', ',<br>').replace(' (', '<br>(');

  function hbar(spec, el) {
    const bars = spec.bars;
    // Wrap long labels on narrow screens so they don't clip.
    const label = b => (el.clientWidth < 600 ? wrap(b.label) : b.label);
    const names = {};
    (spec.legend || []).forEach(l => { names[l.hue] = l.label; });
    // One trace per colour, so a legend can name them; overlaid, each bar
    // keeps its full width on its own row.
    const hues = [...new Set(bars.map(b => b.hue || 1))].sort((a, b) => a - b);
    const traces = hues.map(hue => {
      const group = bars.filter(b => (b.hue || 1) === hue);
      return {
        type: 'bar',
        orientation: 'h',
        name: names[hue] || '',
        y: group.map(label),
        x: group.map(b => b.value),
        text: group.map(b => b.text),
        textposition: 'outside',
        cliponaxis: false,
        textfont: {size: 12, color: css('--ink-2')},
        marker: {color: css('--series-' + hue)},
        hovertext: group.map(b => b.hover || `${b.label}: ${b.text}`),
        hoverinfo: 'text'
      };
    });
    const layout = baseLayout(spec);
    layout.bargap = 0.35;
    layout.barmode = 'overlay';
    layout.yaxis = axis({type: 'category'}, {
      gridcolor: 'rgba(0,0,0,0)',
      tickfont: {size: 12, color: css('--ink-2')},
      categoryorder: 'array',
      categoryarray: bars.map(label)
    });
    layout.margin.r = 64;
    if (spec.legend) {
      layout.showlegend = true;
      layout.legend = {
        orientation: 'h', x: 0, y: 1.02, xanchor: 'left', yanchor: 'bottom',
        font: {size: 12, color: css('--ink-2')}
      };
    }
    return {traces, layout};
  }

  function picker(spec, el, state) {
    const names = Object.keys(spec.series);
    if (!state.select) {
      const select = document.createElement('select');
      select.className = 'picker';
      select.setAttribute('aria-label', 'Scenario');
      names.forEach(n => select.add(new Option(n, n)));
      select.addEventListener('change', () => draw(el, spec, state));
      el.parentNode.insertBefore(select, el);
      state.select = select;
    }
    const s = spec.series[state.select.value || names[0]] || {x: [], y: [], commit: []};
    const traces = [{
      type: 'scatter',
      mode: 'lines+markers',
      x: s.x,
      y: s.y,
      customdata: s.commit,
      line: {color: css('--series-1'), width: 2},
      marker: {size: 8, color: css('--series-1'), line: {width: 2, color: css('--surface')}},
      hovertemplate: '%{x|%Y-%m-%d}<br>%{y:,.1f} ms<br>commit %{customdata}<extra></extra>'
    }];
    const layout = baseLayout(spec);
    layout.xaxis.type = 'date';
    layout.xaxis.tickformat = '%b %d';
    if (s.x.length === 1) {
      // One run so far: show a week around it, not a millisecond.
      const t = new Date(s.x[0]).getTime();
      const day = 86400000;
      layout.xaxis.range = [new Date(t - 3 * day), new Date(t + 3 * day)];
    }
    return {traces, layout};
  }

  function draw(el, spec, state) {
    const kind = {lines, hbar, picker}[spec.kind];
    const {traces, layout} = kind(spec, el, state);
    Plotly.react(el, traces, layout, {displayModeBar: false, responsive: true});
  }

  window.renderChart = function (el, spec) {
    const state = {};
    charts.push(() => draw(el, spec, state));
    draw(el, spec, state);
  };

  const redraw = () => charts.forEach(fn => fn());
  let resizeTimer;
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(redraw, 150);
  });
  if (window.matchMedia) {
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', redraw);
  }
})();

/**
 * Performance & Efficiency HTML5 Canvas Charts
 */

const PerformanceCharts = (function () {
  let latencyHistory = [32, 28, 44, 38, 25, 42, 35, 29, 31, 28];

  function drawLatencyChart(canvasId, p50 = 28, p95 = 42, p99 = 48) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Draw background grid lines
    ctx.strokeStyle = "rgba(255, 255, 255, 0.05)";
    ctx.lineWidth = 1;
    for (let y = 30; y < height; y += 40) {
      ctx.beginPath();
      ctx.moveTo(40, y);
      ctx.lineTo(width - 20, y);
      ctx.stroke();
    }

    // Keep history bounded
    if (latencyHistory.length > 20) latencyHistory.shift();

    // Plot line
    const maxVal = Math.max(...latencyHistory, p99, 80);
    const stepX = (width - 70) / (latencyHistory.length - 1);

    ctx.beginPath();
    latencyHistory.forEach((val, i) => {
      const x = 50 + i * stepX;
      const y = height - 30 - (val / maxVal) * (height - 60);
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });

    // Gradient fill under curve
    const gradient = ctx.createLinearGradient(0, 0, 0, height);
    gradient.addColorStop(0, "rgba(0, 242, 254, 0.35)");
    gradient.addColorStop(1, "rgba(0, 242, 254, 0.0)");

    ctx.strokeStyle = "#00f2fe";
    ctx.lineWidth = 2.5;
    ctx.stroke();

    ctx.lineTo(50 + (latencyHistory.length - 1) * stepX, height - 30);
    ctx.lineTo(50, height - 30);
    ctx.closePath();
    ctx.fillStyle = gradient;
    ctx.fill();

    // Draw percentile marker dots
    latencyHistory.forEach((val, i) => {
      const x = 50 + i * stepX;
      const y = height - 30 - (val / maxVal) * (height - 60);
      ctx.fillStyle = "#fff";
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
    });

    // Labels
    ctx.fillStyle = "#94a3b8";
    ctx.font = "11px JetBrains Mono";
    ctx.fillText(`P50: ${p50}ms`, 60, 25);
    ctx.fillText(`P95: ${p95}ms`, 180, 25);
    ctx.fillText(`P99: ${p99}ms`, 300, 25);
  }

  function drawCacheChart(canvasId, hitRate = 82, totalTokensSaved = 12450) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;

    ctx.clearRect(0, 0, width, height);

    // Donut chart
    const centerX = width * 0.35;
    const centerY = height * 0.5;
    const radius = 65;
    const innerRadius = 45;

    const hitAngle = (hitRate / 100) * (Math.PI * 2);

    // Background track (Misses)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
    ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
    ctx.lineWidth = radius - innerRadius;
    ctx.stroke();

    // Foreground track (Hits)
    ctx.beginPath();
    ctx.arc(centerX, centerY, radius, -Math.PI / 2, -Math.PI / 2 + hitAngle);
    ctx.strokeStyle = "#8a2be2";
    ctx.lineWidth = radius - innerRadius;
    ctx.stroke();

    // Center text
    ctx.fillStyle = "#fff";
    ctx.font = "bold 18px Outfit";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";
    ctx.fillText(`${Math.round(hitRate)}%`, centerX, centerY - 4);
    ctx.font = "10px Plus Jakarta Sans";
    ctx.fillStyle = "#94a3b8";
    ctx.fillText("Hit Rate", centerX, centerY + 14);

    // Legend on the right
    ctx.textAlign = "left";
    ctx.font = "12px Plus Jakarta Sans";
    ctx.fillStyle = "#c084fc";
    ctx.fillText(`• Cache Hits (${hitRate}%)`, width * 0.62, centerY - 25);
    ctx.fillStyle = "#64748b";
    ctx.fillText(`• Cache Misses (${100 - Math.round(hitRate)}%)`, width * 0.62, centerY);
    ctx.fillStyle = "#00f5a0";
    ctx.fillText(`• Tokens Saved: ${totalTokensSaved.toLocaleString()}`, width * 0.62, centerY + 25);
  }

  function addLatencyPoint(val) {
    latencyHistory.push(val);
  }

  return {
    renderLatency: drawLatencyChart,
    renderCache: drawCacheChart,
    pushLatency: addLatencyPoint
  };
})();

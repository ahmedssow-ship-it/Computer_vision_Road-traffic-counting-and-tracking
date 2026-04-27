
// ── Gestion de l'index ────────────────────────────────────────────────────────
let uploadedPath = null;

const radioButtons = document.querySelectorAll('input[name="source"]');
radioButtons?.forEach(rb => {
  rb.addEventListener("change", () => {
    document.getElementById("video-file").disabled = rb.value !== "upload";
    document.getElementById("video-url").disabled  = rb.value !== "url";
  });
});

// Upload vidéo
document.getElementById("video-file")?.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("video", file);

  document.getElementById("upload-status").textContent = "Upload en cours...";
  const res  = await fetch("/upload", { method: "POST", body: formData });
  const data = await res.json();

  if (data.success) {
    uploadedPath = data.path;
    document.getElementById("upload-status").textContent = `✅ ${data.filename}`;
  }
});

// Démarrer la détection
document.getElementById("start-btn")?.addEventListener("click", async () => {
  const source = document.querySelector('input[name="source"]:checked').value;
  const videoSource = source === "upload"
    ? uploadedPath
    : document.getElementById("video-url").value;

  if (!videoSource) {
    alert("Veuillez fournir une source vidéo.");
    return;
  }

  const selectedClasses = [...document.querySelectorAll('input[name="class"]:checked')]
    .map(cb => cb.value);

  const sceneId = document.getElementById("scene-id").value || "scene_01";

  await fetch("/start", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      video_source: videoSource,
      classes: selectedClasses,
      scene_id: sceneId
    })
  });

  window.location.href = "/live";
});

// ── Gestion du live ───────────────────────────────────────────────────────────
let liveChart = null;
const chartData = { labels: [], datasets: [] };

function initChart() {
  const ctx = document.getElementById("live-chart")?.getContext("2d");
  if (!ctx) return;

  liveChart = new Chart(ctx, {
    type: "line",
    data: chartData,
    options: {
      animation: false,
      scales: {
        y: { beginAtZero: true, title: { display: true, text: "Nb objets" } },
        x: { title: { display: true, text: "Frame" } }
      }
    }
  });
}

function updateStats() {
  fetch("/stats")
    .then(r => r.json())
    .then(data => {
      // Aucun objet
      const banner = document.getElementById("no-object-banner");
      if (banner) {
        banner.classList.toggle("hidden", !data.no_object);
      }

      // Compteurs actifs
      const activeDiv = document.getElementById("active-counts");
      if (activeDiv) {
        activeDiv.innerHTML = Object.entries(data.active)
          .map(([cls, n]) => `<div class="count-item"><span>${cls}</span><span class="count">${n}</span></div>`)
          .join("") || "<p>Aucun objet</p>";
      }

      // Totaux
      const totalDiv = document.getElementById("total-counts");
      if (totalDiv) {
        totalDiv.innerHTML = Object.entries(data.totals)
          .map(([cls, n]) => `<div class="count-item"><span>${cls}</span><span class="count total">${n}</span></div>`)
          .join("") || "<p>—</p>";
      }

      // Frame count
      const fc = document.getElementById("frame-count");
      if (fc) fc.textContent = data.frame_count;

      // Chart
      if (liveChart && data.frame_count % 10 === 0) {
        chartData.labels.push(data.frame_count);
        Object.entries(data.active).forEach(([cls, n]) => {
          let ds = chartData.datasets.find(d => d.label === cls);
          if (!ds) {
            ds = { label: cls, data: [], borderWidth: 2, fill: false };
            chartData.datasets.push(ds);
          }
          ds.data.push(n);
        });
        liveChart.update();
      }
    });
}

// Arrêter la détection
document.getElementById("stop-btn")?.addEventListener("click", async () => {
  const res  = await fetch("/stop", { method: "POST" });
  const data = await res.json();
  alert(`Détection arrêtée.
Total : ${JSON.stringify(data.stats)}`);
  window.location.href = "/dashboard";
});

// Initialiser et lancer le polling
initChart();
if (document.getElementById("video-stream")) {
  setInterval(updateStats, 1000);
}

const form = document.querySelector("#scan-form");
const statusEl = document.querySelector("#status");
const resultsEl = document.querySelector("#results");
const summaryGrid = document.querySelector("#summary-grid");
const entitiesEl = document.querySelector("#entities");
const metricsEl = document.querySelector("#metrics");
const relationshipsEl = document.querySelector("#relationships");
const assetsEl = document.querySelector("#assets");
const scanButton = document.querySelector("#scan-button");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(form);
  const payload = {
    root_path: formData.get("root_path"),
    artifact_root: formData.get("artifact_root"),
    context_root: formData.get("context_root"),
    max_files: Number(formData.get("max_files") || 500),
    extensions: String(formData.get("extensions") || "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean),
  };

  scanButton.disabled = true;
  statusEl.textContent = "Scanning local files and synthesizing semantic outputs...";

  try {
    const response = await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Scan failed.");
    }
    renderResults(data);
    statusEl.textContent = `Scan complete for ${data.scan_root}.`;
  } catch (error) {
    statusEl.textContent = error.message;
  } finally {
    scanButton.disabled = false;
  }
});

function renderResults(data) {
  resultsEl.classList.remove("hidden");
  summaryGrid.innerHTML = "";
  entitiesEl.innerHTML = "";
  metricsEl.innerHTML = "";
  relationshipsEl.innerHTML = "";
  assetsEl.innerHTML = "";

  const summaryItems = [
    ["Assets", data.summary.asset_count],
    ["Entities", data.summary.entity_count],
    ["Metrics", data.summary.metric_count],
    ["Relationships", data.summary.relationship_count],
    ["Drift Events", data.summary.drift_event_count],
  ];
  for (const [label, value] of summaryItems) {
    const card = document.createElement("div");
    card.className = "summary-card";
    card.innerHTML = `<div class="label">${label}</div><div class="value">${value}</div>`;
    summaryGrid.appendChild(card);
  }

  entitiesEl.appendChild(renderCardList(data.entities, renderEntityCard, "No entities synthesized."));
  metricsEl.appendChild(renderCardList(data.metrics, renderMetricCard, "No metric candidates found."));
  relationshipsEl.appendChild(
    renderCardList(data.relationships, renderRelationshipCard, "No cross-asset relationships inferred.")
  );
  assetsEl.appendChild(renderCardList(data.assets, renderAssetCard, "No supported assets discovered."));
}

function renderCardList(items, renderItem, emptyMessage) {
  const container = document.createElement("div");
  container.className = "card-list";
  if (!items.length) {
    const empty = document.createElement("p");
    empty.textContent = emptyMessage;
    container.appendChild(empty);
    return container;
  }
  items.forEach((item) => container.appendChild(renderItem(item)));
  return container;
}

function renderEntityCard(entity) {
  const card = document.createElement("article");
  card.className = "data-card";
  card.innerHTML = `
    <h3>${entity.name}</h3>
    <p>${entity.description || "Entity synthesized from discovered assets."}</p>
    <p>Confidence: ${formatConfidence(entity.confidence)}</p>
  `;
  card.appendChild(renderPills(entity.synonyms || []));
  return card;
}

function renderMetricCard(metric) {
  const card = document.createElement("article");
  card.className = "data-card";
  card.innerHTML = `
    <h3>${metric.name}</h3>
    <p>${metric.description || "Metric candidate inferred from field names."}</p>
    <p>Confidence: ${formatConfidence(metric.confidence)}</p>
  `;
  card.appendChild(renderPills(metric.policy_tags || []));
  return card;
}

function renderRelationshipCard(relationship) {
  const card = document.createElement("article");
  card.className = "data-card";
  card.innerHTML = `
    <h3>${relationship.relationship_kind}</h3>
    <p>${relationship.left_asset.qualified_name} → ${relationship.right_asset.qualified_name}</p>
    <p>${relationship.evidence || "Relationship inferred from metadata patterns."}</p>
  `;
  return card;
}

function renderAssetCard(asset) {
  const card = document.createElement("article");
  card.className = "data-card";
  const fieldList = document.createElement("div");
  fieldList.className = "field-list";
  (asset.fields || []).slice(0, 8).forEach((field) => {
    const item = document.createElement("div");
    item.className = "field-item";
    item.textContent = `${field.name} · ${field.field_type}`;
    fieldList.appendChild(item);
  });

  card.innerHTML = `
    <h3>${asset.qualified_name}</h3>
    <p>${asset.description || ""}</p>
    <p>Sensitivity: ${asset.sensitivity}</p>
  `;
  card.appendChild(renderPills(asset.policy_tags || []));
  if ((asset.fields || []).length) {
    card.appendChild(fieldList);
  }
  return card;
}

function renderPills(values) {
  const wrapper = document.createElement("div");
  wrapper.className = "pill-row";
  values.slice(0, 8).forEach((value) => {
    const pill = document.createElement("span");
    pill.className = "pill";
    pill.textContent = value;
    wrapper.appendChild(pill);
  });
  return wrapper;
}

function formatConfidence(value) {
  return typeof value === "number" ? value.toFixed(2) : "n/a";
}

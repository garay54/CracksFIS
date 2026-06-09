"use strict";

const CONFIG = {
  W: {
    label: "W",
    title: "Anchura W (mm)",
    min: 0,
    max: 30,
    step: 0.1,
    sets: {
      pequena: { label: "pequena", type: "trap", p: [0, 0, 1, 3], color: "#2563eb" },
      media: { label: "media", type: "tri", p: [2, 6, 19], color: "#b45309" },
      grande: { label: "grande", type: "trap", p: [16, 22, 30, 30], color: "#b91c1c" }
    }
  },
  L: {
    label: "L",
    title: "Longitud L (mm)",
    min: 0,
    max: 2000,
    step: 10,
    sets: {
      corta: { label: "corta", type: "trap", p: [0, 0, 200, 500], color: "#2563eb" },
      media: { label: "media", type: "tri", p: [400, 800, 1200], color: "#b45309" },
      larga: { label: "larga", type: "trap", p: [1000, 1500, 2000, 2000], color: "#b91c1c" }
    }
  },
  D: {
    label: "D",
    title: "Densidad D",
    min: 0,
    max: 1,
    step: 0.005,
    sets: {
      baja: { label: "baja", type: "trap", p: [0, 0, 0.08, 0.22], color: "#2563eb" },
      media: { label: "media", type: "tri", p: [0.12, 0.32, 0.55], color: "#b45309" },
      alta: { label: "alta", type: "trap", p: [0.42, 0.68, 1, 1], color: "#b91c1c" }
    }
  },
  C: {
    label: "C",
    title: "Completitud C",
    min: 0,
    max: 1,
    step: 0.01,
    sets: {
      truncada: { label: "truncada", type: "trap", p: [0, 0, 0.25, 0.55], color: "#b91c1c" },
      parcial: { label: "parcial", type: "tri", p: [0.25, 0.55, 0.85], color: "#b45309" },
      completa: { label: "completa", type: "trap", p: [0.55, 0.8, 1, 1], color: "#15803d" }
    }
  },
  SD: {
    label: "SD",
    title: "Severidad dimensional SD",
    min: 0,
    max: 100,
    step: 0.5,
    sets: severitySets()
  },
  SE: {
    label: "SE",
    title: "Severidad de extension SE",
    min: 0,
    max: 100,
    step: 0.5,
    sets: severitySets()
  },
  SF: {
    label: "SF",
    title: "Severidad final SF",
    min: 0,
    max: 100,
    step: 0.5,
    sets: {
      leve: { label: "leve", type: "trap", p: [0, 0, 20, 40], color: "#15803d" },
      moderada: { label: "moderada", type: "tri", p: [25, 50, 75], color: "#b45309" },
      critica: { label: "critica", type: "trap", p: [60, 80, 100, 100], color: "#b91c1c" }
    }
  }
};

const BASE_CONFIG = cloneConfig(CONFIG);

function severitySets() {
  return {
    baja: { label: "baja", type: "trap", p: [0, 0, 20, 45], color: "#2563eb" },
    media: { label: "media", type: "tri", p: [25, 50, 75], color: "#b45309" },
    alta: { label: "alta", type: "trap", p: [55, 80, 100, 100], color: "#b91c1c" }
  };
}

const RULES = {
  fis1: [
    ["pequena", "corta", "baja"],
    ["pequena", "media", "baja"],
    ["pequena", "larga", "media"],
    ["media", "corta", "baja"],
    ["media", "media", "media"],
    ["media", "larga", "alta"],
    ["grande", "corta", "media"],
    ["grande", "media", "alta"],
    ["grande", "larga", "alta"]
  ],
  fis2: [
    ["completa", "baja", "baja"],
    ["completa", "media", "media"],
    ["completa", "alta", "alta"],
    ["parcial", "baja", "baja"],
    ["parcial", "media", "media"],
    ["parcial", "alta", "alta"],
    ["truncada", "baja", "media"],
    ["truncada", "media", "media"],
    ["truncada", "alta", "alta"]
  ],
  fis3: [
    ["baja", "baja", "leve"],
    ["baja", "media", "leve"],
    ["baja", "alta", "moderada"],
    ["media", "baja", "leve"],
    ["media", "media", "moderada"],
    ["media", "alta", "critica"],
    ["alta", "baja", "moderada"],
    ["alta", "media", "critica"],
    ["alta", "alta", "critica"]
  ]
};

const state = {
  w: 6,
  l: 800,
  d: 0.3,
  c: 0.8,
  last: null,
  membershipVariable: "W",
  editorVariable: "W",
  editorSelectedSet: null,
  editorDrag: null,
  surfaceViews: {}
};

const DEFAULT_SURFACE_VIEW = { rotX: -0.96, rotZ: 0.72, zoom: 1 };
const SURFACE_GRID = { cols: 18, rows: 16, smoothing: 1 };

const SURFACE_DEFS = {
  surfaceWL: {
    title: "FIS 1: W, L -> SD",
    xVar: CONFIG.W,
    yVar: CONFIG.L,
    zVar: CONFIG.SD,
    xLabel: "W",
    yLabel: "L",
    zLabel: "SD",
    valueAt: (x, y) => inferTwoInput({ xValue: x, yValue: y, xVar: CONFIG.W, yVar: CONFIG.L, outVar: CONFIG.SD, rules: RULES.fis1 }).value,
    marker: () => ({ x: state.w, y: state.l, z: state.last ? state.last.sd : 0 })
  },
  surfaceDC: {
    title: "FIS 2: D, C -> SE",
    xVar: CONFIG.D,
    yVar: CONFIG.C,
    zVar: CONFIG.SE,
    xLabel: "D",
    yLabel: "C",
    zLabel: "SE",
    valueAt: (x, y) => inferTwoInput({ xValue: y, yValue: x, xVar: CONFIG.C, yVar: CONFIG.D, outVar: CONFIG.SE, rules: RULES.fis2 }).value,
    marker: () => ({ x: state.d, y: state.c, z: state.last ? state.last.se : 0 })
  },
  surfaceFinal: {
    title: "FIS 3: SD, SE -> SF",
    xVar: CONFIG.SD,
    yVar: CONFIG.SE,
    zVar: CONFIG.SF,
    xLabel: "SD",
    yLabel: "SE",
    zLabel: "SF",
    valueAt: (x, y) => inferTwoInput({ xValue: x, yValue: y, xVar: CONFIG.SD, yVar: CONFIG.SE, outVar: CONFIG.SF, rules: RULES.fis3 }).value,
    marker: () => {
      const current = state.last || evaluateFis(state.w, state.l, state.d, state.c);
      return { x: current.sd, y: current.se, z: current.sf };
    }
  }
};

const els = {};

document.addEventListener("DOMContentLoaded", () => {
  cacheElements();
  bindInputs();
  bindTabs();
  bindPresets();
  bindSurfaceControls();
  bindMembershipEditor();
  bindVisualMembershipEditor();
  bindResponsiveCanvasRedraw();
  renderMembershipEditor();
  renderVisualMembershipEditor();
  renderConfiguration();
  drawStaticCharts();
  redrawSurfaces();
  update();
});

function cacheElements() {
  Object.assign(els, {
    wInput: document.getElementById("wInput"),
    lInput: document.getElementById("lInput"),
    dInput: document.getElementById("dInput"),
    cInput: document.getElementById("cInput"),
    wValue: document.getElementById("wValue"),
    lValue: document.getElementById("lValue"),
    dValue: document.getElementById("dValue"),
    cValue: document.getElementById("cValue"),
    sdMetric: document.getElementById("sdMetric"),
    seMetric: document.getElementById("seMetric"),
    sfMetric: document.getElementById("sfMetric"),
    statusLabel: document.getElementById("statusLabel"),
    statusScore: document.getElementById("statusScore"),
    recommendationText: document.getElementById("recommendationText"),
    fis1Rules: document.getElementById("fis1Rules"),
    fis2Rules: document.getElementById("fis2Rules"),
    fis3Rules: document.getElementById("fis3Rules"),
    resetViewButton: document.getElementById("resetViewButton"),
    membershipVariableSelect: document.getElementById("membershipVariableSelect"),
    membershipSetControls: document.getElementById("membershipSetControls"),
    resetVariableButton: document.getElementById("resetVariableButton"),
    resetAllMembershipsButton: document.getElementById("resetAllMembershipsButton"),
    editorInputVariables: document.getElementById("editorInputVariables"),
    editorOutputVariables: document.getElementById("editorOutputVariables"),
    mfEditorCanvas: document.getElementById("mfEditorCanvas"),
    mfEditorVariableTitle: document.getElementById("mfEditorVariableTitle"),
    mfEditorVariableMeta: document.getElementById("mfEditorVariableMeta"),
    mfEditorParameterPanel: document.getElementById("mfEditorParameterPanel"),
    resetEditorVariableButton: document.getElementById("resetEditorVariableButton"),
    resetEditorAllButton: document.getElementById("resetEditorAllButton"),
    resetEditorViewButton: document.getElementById("resetEditorViewButton"),
    configArchitecture: document.getElementById("configArchitecture"),
    configVariables: document.getElementById("configVariables"),
    configRules: document.getElementById("configRules"),
    configSurfaces: document.getElementById("configSurfaces")
  });
}

function bindInputs() {
  [
    ["wInput", "w", "wValue", 1],
    ["lInput", "l", "lValue", 0],
    ["dInput", "d", "dValue", 3],
    ["cInput", "c", "cValue", 2]
  ].forEach(([inputId, key, outputId, digits]) => {
    els[inputId].addEventListener("input", (event) => {
      state[key] = Number(event.target.value);
      els[outputId].value = format(state[key], digits);
      update();
    });
  });
}

function bindMembershipEditor() {
  if (!els.membershipVariableSelect || !els.membershipSetControls) return;

  Object.keys(CONFIG).forEach((key) => {
    const option = document.createElement("option");
    option.value = key;
    option.textContent = `${key}: ${CONFIG[key].title}`;
    els.membershipVariableSelect.appendChild(option);
  });
  els.membershipVariableSelect.value = state.membershipVariable;

  els.membershipVariableSelect.addEventListener("change", (event) => {
    state.membershipVariable = event.target.value;
    renderMembershipEditor();
  });

  if (els.resetVariableButton) {
    els.resetVariableButton.addEventListener("click", () => {
      const key = state.membershipVariable;
      CONFIG[key].sets = cloneConfig(BASE_CONFIG[key].sets);
      renderMembershipEditor();
      refreshAfterMembershipChange();
    });
  }

  if (els.resetAllMembershipsButton) {
    els.resetAllMembershipsButton.addEventListener("click", () => {
      Object.keys(BASE_CONFIG).forEach((key) => {
        CONFIG[key].sets = cloneConfig(BASE_CONFIG[key].sets);
      });
      renderMembershipEditor();
      refreshAfterMembershipChange();
    });
  }
}

function bindVisualMembershipEditor() {
  renderEditorVariableLists();

  if (els.mfEditorCanvas) {
    els.mfEditorCanvas.addEventListener("pointerdown", startMembershipDrag);
    els.mfEditorCanvas.addEventListener("pointermove", dragMembershipHandle);
    els.mfEditorCanvas.addEventListener("pointerup", endMembershipDrag);
    els.mfEditorCanvas.addEventListener("pointercancel", endMembershipDrag);
    els.mfEditorCanvas.addEventListener("mouseleave", endMembershipDrag);
  }

  if (els.resetEditorVariableButton) {
    els.resetEditorVariableButton.addEventListener("click", () => {
      const key = state.editorVariable;
      CONFIG[key].sets = cloneConfig(BASE_CONFIG[key].sets);
      state.editorSelectedSet = firstSetKey(CONFIG[key]);
      renderMembershipEditor();
      renderVisualMembershipEditor();
      refreshAfterMembershipChange();
    });
  }

  if (els.resetEditorAllButton) {
    els.resetEditorAllButton.addEventListener("click", () => {
      Object.keys(BASE_CONFIG).forEach((key) => {
        CONFIG[key].sets = cloneConfig(BASE_CONFIG[key].sets);
      });
      state.editorSelectedSet = firstSetKey(CONFIG[state.editorVariable]);
      renderMembershipEditor();
      renderVisualMembershipEditor();
      refreshAfterMembershipChange();
    });
  }

  if (els.resetEditorViewButton) {
    els.resetEditorViewButton.addEventListener("click", () => {
      surfaceCanvasIds().forEach((id) => {
        state.surfaceViews[id] = { ...DEFAULT_SURFACE_VIEW };
      });
      redrawEditorSurfaces();
    });
  }
}

function renderEditorVariableLists() {
  const groups = [
    [els.editorInputVariables, ["W", "L", "D", "C"]],
    [els.editorOutputVariables, ["SD", "SE", "SF"]]
  ];

  groups.forEach(([container, keys]) => {
    if (!container) return;
    container.innerHTML = "";
    keys.forEach((key) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = key === state.editorVariable ? "active" : "";
      button.dataset.editorVariable = key;
      button.innerHTML = `<strong>${key}</strong><span>${CONFIG[key].title}</span>`;
      button.addEventListener("click", () => {
        state.editorVariable = key;
        state.editorSelectedSet = firstSetKey(CONFIG[key]);
        state.editorDrag = null;
        renderVisualMembershipEditor();
      });
      container.appendChild(button);
    });
  });
}

function renderVisualMembershipEditor() {
  renderEditorVariableLists();
  drawEditableMembershipChart();
  renderEditorParameterPanel();
  redrawEditorSurfaces();
}

function drawEditableMembershipChart() {
  const canvas = els.mfEditorCanvas;
  if (!canvas) return;
  const variable = CONFIG[state.editorVariable];
  if (!state.editorSelectedSet || !variable.sets[state.editorSelectedSet]) {
    state.editorSelectedSet = firstSetKey(variable);
  }

  if (els.mfEditorVariableTitle) {
    els.mfEditorVariableTitle.textContent = `${variable.label}: ${variable.title}`;
  }
  if (els.mfEditorVariableMeta) {
    els.mfEditorVariableMeta.textContent = `Rango ${variable.min} a ${variable.max}. Arrastra los puntos blancos para modificar la funcion seleccionada.`;
  }

  const { ctx, w, h } = prepareCanvas(canvas, 760 / 250);
  const pad = editableChartPadding();
  ctx.clearRect(0, 0, w, h);
  drawAxes(ctx, w, h, pad, variable);
  drawMembershipGrid(ctx, w, h, pad, variable);

  Object.entries(variable.sets).forEach(([setKey, set]) => {
    const selected = setKey === state.editorSelectedSet;
    drawMembershipCurve(ctx, variable, set, pad, w, h, selected);
  });

  drawEditableLegend(ctx, variable, w);
  drawMembershipHandles(ctx, variable, state.editorSelectedSet, pad, w, h);
}

function renderEditorParameterPanel() {
  if (!els.mfEditorParameterPanel) return;
  const variable = CONFIG[state.editorVariable];
  const selectedKey = state.editorSelectedSet || firstSetKey(variable);
  const selectedSet = variable.sets[selectedKey];
  if (!selectedSet) {
    els.mfEditorParameterPanel.innerHTML = "";
    return;
  }

  els.mfEditorParameterPanel.innerHTML = Object.entries(variable.sets).map(([setKey, set]) => `
    <article class="${setKey === selectedKey ? "selected" : ""}">
      <button type="button" data-select-set="${setKey}">
        <span class="swatch" style="background:${set.color}"></span>
        <strong>${set.label || setKey}</strong>
      </button>
      <label>
        <span>Forma</span>
        <select data-editor-shape="${setKey}">
          <option value="trap"${set.type === "trap" ? " selected" : ""}>Trapezoidal</option>
          <option value="tri"${set.type === "tri" ? " selected" : ""}>Triangular</option>
          <option value="gauss"${set.type === "gauss" ? " selected" : ""}>Gaussiana</option>
        </select>
      </label>
      <code>[${set.p.map((value) => formatEditorValue(value, variable)).join(", ")}]</code>
    </article>
  `).join("");

  els.mfEditorParameterPanel.querySelectorAll("[data-select-set]").forEach((button) => {
    button.addEventListener("click", () => {
      state.editorSelectedSet = button.dataset.selectSet;
      drawEditableMembershipChart();
      renderEditorParameterPanel();
    });
  });

  els.mfEditorParameterPanel.querySelectorAll("[data-editor-shape]").forEach((select) => {
    select.addEventListener("change", () => {
      const setKey = select.dataset.editorShape;
      const set = variable.sets[setKey];
      set.p = convertSetParams(set, variable, select.value);
      set.type = select.value;
      state.editorSelectedSet = setKey;
      renderMembershipEditor();
      renderVisualMembershipEditor();
      refreshAfterMembershipChange();
    });
  });
}

function startMembershipDrag(event) {
  const hit = hitTestMembershipEditor(event);
  if (!hit) return;
  const canvas = els.mfEditorCanvas;
  state.editorSelectedSet = hit.setKey;
  state.editorDrag = hit;
  canvas.setPointerCapture(event.pointerId);
  canvas.classList.add("dragging");
  applyMembershipHandleDrag(event);
}

function dragMembershipHandle(event) {
  if (!state.editorDrag) return;
  applyMembershipHandleDrag(event);
}

function endMembershipDrag(event) {
  if (!state.editorDrag) return;
  if (els.mfEditorCanvas && event.pointerId !== undefined) {
    try {
      els.mfEditorCanvas.releasePointerCapture(event.pointerId);
    } catch (_) {
      // Pointer capture can already be released by the browser.
    }
    els.mfEditorCanvas.classList.remove("dragging");
  }
  state.editorDrag = null;
  renderMembershipEditor();
  renderVisualMembershipEditor();
}

function applyMembershipHandleDrag(event) {
  const variable = CONFIG[state.editorVariable];
  const set = variable.sets[state.editorDrag.setKey];
  const value = valueFromCanvasEvent(event, variable);

  if (set.type === "gauss" && state.editorDrag.role === "sigma") {
    const center = set.p[0];
    const span = variable.max - variable.min;
    set.p[1] = clamp(Math.abs(value - center), Math.max(span * 0.002, 1e-6), span);
  } else {
    set.p[state.editorDrag.paramIndex] = value;
  }

  set.p = sanitizeSetParams(set, variable);
  drawEditableMembershipChart();
  renderEditorParameterPanel();
  refreshAfterMembershipChange();
}

function hitTestMembershipEditor(event) {
  const variable = CONFIG[state.editorVariable];
  const canvas = els.mfEditorCanvas;
  const rect = canvas.getBoundingClientRect();
  const pad = editableChartPadding();
  const cssWidth = rect.width || canvas.clientWidth;
  const cssHeight = rect.height || canvas.clientHeight;
  const x = event.clientX - rect.left;
  const y = event.clientY - rect.top;
  let closest = null;

  Object.entries(variable.sets).forEach(([setKey, set]) => {
    membershipHandlesForSet(set, variable).forEach((handle) => {
      const hx = scaleX(handle.x, variable.min, variable.max, pad, cssWidth);
      const hy = scaleY(handle.y, 0, 1, pad, cssHeight);
      const distance = Math.hypot(x - hx, y - hy);
      if (distance <= 16 && (!closest || distance < closest.distance)) {
        closest = { ...handle, setKey, distance };
      }
    });
  });

  if (closest) return closest;

  const nearestSet = nearestMembershipCurveSet(x, y, variable, pad, cssWidth, cssHeight);
  if (nearestSet) {
    state.editorSelectedSet = nearestSet;
    drawEditableMembershipChart();
    renderEditorParameterPanel();
  }
  return null;
}

function nearestMembershipCurveSet(px, py, variable, pad, width, height) {
  let closest = null;
  Object.entries(variable.sets).forEach(([setKey, set]) => {
    sampleRange(variable.min, variable.max, 220).forEach((x) => {
      const cx = scaleX(x, variable.min, variable.max, pad, width);
      const cy = scaleY(membership(set, x), 0, 1, pad, height);
      const distance = Math.hypot(px - cx, py - cy);
      if (distance <= 10 && (!closest || distance < closest.distance)) {
        closest = { setKey, distance };
      }
    });
  });
  return closest ? closest.setKey : null;
}

function valueFromCanvasEvent(event, variable) {
  const rect = els.mfEditorCanvas.getBoundingClientRect();
  const pad = editableChartPadding();
  const x = clamp(event.clientX - rect.left, pad.left, rect.width - pad.right);
  const span = variable.max - variable.min;
  const t = (x - pad.left) / (rect.width - pad.left - pad.right);
  return variable.min + t * span;
}

function membershipHandlesForSet(set, variable) {
  if (set.type === "gauss") {
    const center = clamp(set.p[0], variable.min, variable.max);
    const sigma = Math.max(Math.abs(set.p[1]), (variable.max - variable.min) * 0.002);
    const y = Math.exp(-0.5);
    return [
      { x: center, y: 1, paramIndex: 0, role: "center" },
      { x: clamp(center - sigma, variable.min, variable.max), y, paramIndex: 1, role: "sigma" },
      { x: clamp(center + sigma, variable.min, variable.max), y, paramIndex: 1, role: "sigma" }
    ];
  }
  if (set.type === "tri") {
    return [
      { x: set.p[0], y: 0, paramIndex: 0, role: "vertex" },
      { x: set.p[1], y: 1, paramIndex: 1, role: "vertex" },
      { x: set.p[2], y: 0, paramIndex: 2, role: "vertex" }
    ];
  }
  return [
    { x: set.p[0], y: 0, paramIndex: 0, role: "vertex" },
    { x: set.p[1], y: 1, paramIndex: 1, role: "vertex" },
    { x: set.p[2], y: 1, paramIndex: 2, role: "vertex" },
    { x: set.p[3], y: 0, paramIndex: 3, role: "vertex" }
  ];
}

function drawMembershipCurve(ctx, variable, set, pad, w, h, selected) {
  ctx.save();
  ctx.beginPath();
  const points = sampleRange(variable.min, variable.max, 720).map((x) => ({
    x,
    y: membership(set, x)
  }));
  points.forEach((point, index) => {
    const px = scaleX(point.x, variable.min, variable.max, pad, w);
    const py = scaleY(point.y, 0, 1, pad, h);
    if (index === 0) ctx.moveTo(px, py);
    else ctx.lineTo(px, py);
  });
  ctx.strokeStyle = set.color;
  ctx.lineWidth = selected ? 4 : 2.2;
  ctx.globalAlpha = selected ? 1 : 0.55;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  ctx.stroke();
  ctx.restore();
}

function drawMembershipHandles(ctx, variable, setKey, pad, w, h) {
  const set = variable.sets[setKey];
  if (!set) return;
  membershipHandlesForSet(set, variable).forEach((handle) => {
    const x = scaleX(handle.x, variable.min, variable.max, pad, w);
    const y = scaleY(handle.y, 0, 1, pad, h);
    ctx.save();
    ctx.fillStyle = "#ffffff";
    ctx.strokeStyle = set.color;
    ctx.lineWidth = 2.5;
    if (handle.role === "sigma") {
      ctx.beginPath();
      ctx.rect(x - 5.5, y - 5.5, 11, 11);
    } else {
      ctx.beginPath();
      ctx.arc(x, y, 6.5, 0, Math.PI * 2);
    }
    ctx.fill();
    ctx.stroke();
    ctx.restore();
  });
}

function drawMembershipGrid(ctx, w, h, pad, variable) {
  ctx.save();
  ctx.strokeStyle = "#edf2f7";
  ctx.lineWidth = 1;
  for (let i = 1; i < 5; i += 1) {
    const y = scaleY(i / 5, 0, 1, pad, h);
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(w - pad.right, y);
    ctx.stroke();
  }
  for (let i = 1; i < 6; i += 1) {
    const x = scaleX(variable.min + ((variable.max - variable.min) * i) / 6, variable.min, variable.max, pad, w);
    ctx.beginPath();
    ctx.moveTo(x, pad.top);
    ctx.lineTo(x, h - pad.bottom);
    ctx.stroke();
  }
  ctx.restore();
}

function drawEditableLegend(ctx, variable, width) {
  let x = 54;
  const y = 34;
  Object.entries(variable.sets).forEach(([setKey, set]) => {
    const selected = setKey === state.editorSelectedSet;
    ctx.fillStyle = selected ? "#e6f3f1" : "#ffffff";
    const textWidth = ctx.measureText(set.label).width + 38;
    ctx.fillRect(x - 7, y - 9, textWidth, 24);
    ctx.strokeStyle = selected ? "#0f766e" : "#dbe4ec";
    ctx.strokeRect(x - 7, y - 9, textWidth, 24);
    ctx.fillStyle = set.color;
    ctx.fillRect(x, y, 10, 10);
    ctx.fillStyle = "#334155";
    ctx.font = "700 12px system-ui, sans-serif";
    ctx.fillText(set.label, x + 14, y + 10);
    x += Math.min(textWidth + 10, width - 100);
  });
}

function editableChartPadding() {
  return { left: 54, right: 20, top: 44, bottom: 42 };
}

function firstSetKey(variable) {
  return Object.keys(variable.sets)[0];
}

function bindTabs() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      const tab = button.dataset.tab;
      document.querySelectorAll(".tab-button").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".tab-page").forEach((item) => item.classList.remove("active"));
      button.classList.add("active");
      document.getElementById(tab).classList.add("active");
      if (tab === "surfaces") redrawSurfaces();
      if (tab === "membership") {
        renderMembershipEditor();
        drawStaticCharts();
      }
      if (tab === "mfeditor") renderVisualMembershipEditor();
      if (tab === "configuration") renderConfiguration();
    });
  });
}

function renderMembershipEditor() {
  if (!els.membershipSetControls || !els.membershipVariableSelect) return;
  const key = state.membershipVariable;
  const variable = CONFIG[key];
  els.membershipVariableSelect.value = key;
  els.membershipSetControls.innerHTML = "";

  Object.entries(variable.sets).forEach(([setKey, set]) => {
    const card = document.createElement("article");
    card.className = "membership-set-card";
    card.innerHTML = `
      <div class="set-card-title">
        <span class="swatch" style="background:${set.color}"></span>
        <strong>${set.label || setKey}</strong>
        <small>${key}</small>
      </div>
      <label class="shape-control">
        <span>Forma</span>
        <select data-set="${setKey}" data-action="shape">
          <option value="trap"${set.type === "trap" ? " selected" : ""}>Trapezoidal</option>
          <option value="tri"${set.type === "tri" ? " selected" : ""}>Triangular</option>
          <option value="gauss"${set.type === "gauss" ? " selected" : ""}>Gaussiana</option>
        </select>
      </label>
      <div class="param-grid">
        ${parameterLabels(set.type).map((label, index) => `
          <label>
            <span>${label}</span>
            <input
              type="number"
              step="${editorStep(variable)}"
              min="${index === 1 && set.type === "gauss" ? editorStep(variable) : variable.min}"
              max="${set.type === "gauss" && index === 1 ? variable.max - variable.min : variable.max}"
              value="${formatEditorValue(set.p[index], variable)}"
              data-set="${setKey}"
              data-param-index="${index}">
          </label>
        `).join("")}
      </div>
    `;
    els.membershipSetControls.appendChild(card);
  });

  els.membershipSetControls.querySelectorAll("[data-action='shape']").forEach((select) => {
    select.addEventListener("change", (event) => {
      const setKey = event.target.dataset.set;
      const set = variable.sets[setKey];
      const nextType = event.target.value;
      set.p = convertSetParams(set, variable, nextType);
      set.type = nextType;
      renderMembershipEditor();
      refreshAfterMembershipChange();
    });
  });

  els.membershipSetControls.querySelectorAll("[data-param-index]").forEach((input) => {
    input.addEventListener("input", (event) => {
      const setKey = event.target.dataset.set;
      const index = Number(event.target.dataset.paramIndex);
      const set = variable.sets[setKey];
      const raw = Number(event.target.value);
      if (!Number.isFinite(raw)) return;
      set.p[index] = raw;
      set.p = sanitizeSetParams(set, variable);
      refreshAfterMembershipChange();
    });
    input.addEventListener("blur", () => renderMembershipEditor());
  });
}

function refreshAfterMembershipChange() {
  update();
  renderConfiguration();
  drawStaticCharts();
  if (document.getElementById("mfeditor")?.classList.contains("active")) {
    redrawEditorSurfaces();
  }
}

function bindSurfaceControls() {
  document.querySelectorAll("[data-surface]").forEach((canvas) => {
    const id = canvas.id;
    const def = getSurfaceDefForCanvas(canvas);
    state.surfaceViews[id] = { ...DEFAULT_SURFACE_VIEW };
    let dragging = false;
    let lastX = 0;
    let lastY = 0;

    canvas.addEventListener("pointerdown", (event) => {
      dragging = true;
      lastX = event.clientX;
      lastY = event.clientY;
      canvas.setPointerCapture(event.pointerId);
    });

    canvas.addEventListener("pointermove", (event) => {
      if (!dragging) return;
      const view = state.surfaceViews[id];
      view.rotZ += (event.clientX - lastX) * 0.01;
      view.rotX += (event.clientY - lastY) * 0.01;
      view.rotX = clamp(view.rotX, -1.45, -0.28);
      lastX = event.clientX;
      lastY = event.clientY;
      drawSurface3D(id, def);
    });

    canvas.addEventListener("pointerup", (event) => {
      dragging = false;
      canvas.releasePointerCapture(event.pointerId);
    });

    canvas.addEventListener("pointercancel", () => {
      dragging = false;
    });
  });

  if (els.resetViewButton) {
    els.resetViewButton.addEventListener("click", () => {
      surfaceCanvasIds().forEach((id) => {
        state.surfaceViews[id] = { ...DEFAULT_SURFACE_VIEW };
      });
      redrawSurfaces();
    });
  }
}

function bindResponsiveCanvasRedraw() {
  let resizeTimer = 0;
  window.addEventListener("resize", () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      drawStaticCharts();
      redrawSurfaces();
    }, 120);
  });
}

function bindPresets() {
  const presets = {
    light: { w: 1.5, l: 300, d: 0.04, c: 1 },
    medium: { w: 6, l: 800, d: 0.3, c: 0.8 },
    critical: { w: 20, l: 1500, d: 0.4, c: 1 },
    truncated: { w: 6, l: 800, d: 0.04, c: 0 }
  };
  document.querySelectorAll("[data-preset]").forEach((button) => {
    button.addEventListener("click", () => {
      Object.assign(state, presets[button.dataset.preset]);
      syncInputs();
      update();
    });
  });
}

function syncInputs() {
  els.wInput.value = state.w;
  els.lInput.value = state.l;
  els.dInput.value = state.d;
  els.cInput.value = state.c;
  els.wValue.value = format(state.w, 1);
  els.lValue.value = format(state.l, 0);
  els.dValue.value = format(state.d, 3);
  els.cValue.value = format(state.c, 2);
}

function update() {
  syncInputs();
  const result = evaluateFis(state.w, state.l, state.d, state.c);
  state.last = result;

  els.sdMetric.textContent = `${format(result.sd, 1)}%`;
  els.seMetric.textContent = `${format(result.se, 1)}%`;
  els.sfMetric.textContent = `${format(result.sf, 1)}%`;
  els.statusScore.textContent = `SF ${format(result.sf, 1)}%`;
  els.statusLabel.textContent = result.nivel;
  els.statusLabel.className = `status-pill ${statusClass(result.nivel)}`;
  els.recommendationText.textContent = result.recomendacion;

  renderRuleTable(els.fis1Rules, result.fis1.rules, "W", "L");
  renderRuleTable(els.fis2Rules, result.fis2.rules, "C", "D");
  renderRuleTable(els.fis3Rules, result.fis3.rules, "SD", "SE");
  redrawSurfaceMarkers(result);
  drawStaticCharts();
}

function evaluateFis(w, l, d, c) {
  const fis1 = inferTwoInput({
    xValue: w,
    yValue: l,
    xVar: CONFIG.W,
    yVar: CONFIG.L,
    outVar: CONFIG.SD,
    rules: RULES.fis1
  });
  const fis2 = inferTwoInput({
    xValue: c,
    yValue: d,
    xVar: CONFIG.C,
    yVar: CONFIG.D,
    outVar: CONFIG.SE,
    rules: RULES.fis2
  });
  const fis3 = inferTwoInput({
    xValue: fis1.value,
    yValue: fis2.value,
    xVar: CONFIG.SD,
    yVar: CONFIG.SE,
    outVar: CONFIG.SF,
    rules: RULES.fis3
  });

  const label = labelForSf(fis3.value);
  return {
    sd: fis1.value,
    se: fis2.value,
    sf: fis3.value,
    nivel: label,
    recomendacion: recommendationFor(label),
    fis1,
    fis2,
    fis3
  };
}

function inferTwoInput({ xValue, yValue, xVar, yVar, outVar, rules }) {
  const xMu = memberships(xVar, xValue);
  const yMu = memberships(yVar, yValue);
  const fired = rules.map(([xSet, ySet, outSet], index) => ({
    index: index + 1,
    xSet,
    ySet,
    outSet,
    strength: (xMu[xSet] || 0) * (yMu[ySet] || 0)
  }));
  return {
    value: smoothRuleCentroid(outVar, fired),
    xMu,
    yMu,
    rules: fired
  };
}

function memberships(variable, value) {
  return Object.fromEntries(
    Object.entries(variable.sets).map(([key, set]) => [key, membership(set, value)])
  );
}

function membership(set, x) {
  if (set.type === "gauss") return gauss(x, set.p);
  return set.type === "tri" ? tri(x, set.p) : trap(x, set.p);
}

function gauss(x, [center, sigma]) {
  if (sigma <= 0) return x === center ? 1 : 0;
  return Math.exp(-0.5 * ((x - center) / sigma) ** 2);
}

function tri(x, [a, b, c]) {
  if (x <= a || x >= c) return 0;
  if (x === b) return 1;
  if (x < b) return safeRatio(x - a, b - a);
  return safeRatio(c - x, c - b);
}

function trap(x, [a, b, c, d]) {
  if (x < a || x > d) return 0;
  if (x >= b && x <= c) return 1;
  if (x >= a && x < b) return safeRatio(x - a, b - a);
  if (x > c && x <= d) return safeRatio(d - x, d - c);
  return 0;
}

function safeRatio(num, den) {
  if (den === 0) return num >= 0 ? 1 : 0;
  return clamp(num / den, 0, 1);
}

function aggregateOutput(outVar, firedRules) {
  const n = Math.round((outVar.max - outVar.min) / outVar.step) + 1;
  const values = new Array(n);
  for (let i = 0; i < n; i += 1) {
    const x = outVar.min + i * outVar.step;
    let y = 0;
    for (const rule of firedRules) {
      if (rule.strength <= 0) continue;
      const mf = membership(outVar.sets[rule.outSet], x);
      const contribution = rule.strength * mf;
      y = y + contribution - y * contribution;
    }
    values[i] = { x, y: clamp(y, 0, 1) };
  }
  return values;
}

function smoothRuleCentroid(outVar, firedRules) {
  let total = 0;
  let weighted = 0;
  for (const rule of firedRules) {
    if (rule.strength <= 0) continue;
    const center = setCenter(outVar.sets[rule.outSet]);
    total += rule.strength;
    weighted += rule.strength * center;
  }
  if (total <= 1e-12) return 0;
  return weighted / total;
}

function setCenter(set) {
  if (set.type === "gauss") return set.p[0];
  if (set.type === "tri") return set.p[1];
  return (set.p[1] + set.p[2]) / 2;
}

function defuzzCentroid(outVar, aggregated) {
  let area = 0;
  let moment = 0;
  for (const point of aggregated) {
    area += point.y;
    moment += point.x * point.y;
  }
  if (area <= 1e-12) return 0;
  return moment / area;
}

function labelForSf(value) {
  if (value < 35) return "LEVE";
  if (value < 70) return "MODERADA";
  return "CRITICA";
}

function recommendationFor(label) {
  if (label === "LEVE") return "Monitoreo periodico / sellado menor localizado en caso de desarrollo puntual.";
  if (label === "MODERADA") return "Sellado de grietas con asfalto modificado / fresado superficial localizado.";
  return "Rehabilitacion estructural / reencarpetado asfaltico completo de la seccion.";
}

function statusClass(label) {
  if (label === "LEVE") return "status-low";
  if (label === "MODERADA") return "status-mid";
  return "status-high";
}

function renderRuleTable(container, rules, xName, yName) {
  container.innerHTML = "";
  const sorted = [...rules].sort((a, b) => b.strength - a.strength);
  sorted.forEach((rule) => {
    const row = document.createElement("div");
    row.className = `rule-row ${rule.strength > 0 ? "active-rule" : ""}`;
    const alpha = clamp(rule.strength, 0, 1);
    if (alpha > 0) {
      row.style.boxShadow = `inset 4px 0 0 rgba(15, 118, 110, ${0.25 + alpha * 0.75})`;
    }
    row.innerHTML = `
      <span>R${rule.index}: ${xName}=${rule.xSet}, ${yName}=${rule.ySet} -> ${rule.outSet}</span>
      <strong>${format(rule.strength, 3)}</strong>
      <em>${rule.strength > 0 ? "activa" : "-"}</em>
    `;
    container.appendChild(row);
  });
}

function drawStaticCharts() {
  drawMembershipChart("chartW", CONFIG.W, state.w);
  drawMembershipChart("chartL", CONFIG.L, state.l);
  drawMembershipChart("chartD", CONFIG.D, state.d);
  drawMembershipChart("chartC", CONFIG.C, state.c);
  drawMembershipChart("chartSD", CONFIG.SD, state.last ? state.last.sd : null);
  drawMembershipChart("chartSE", CONFIG.SE, state.last ? state.last.se : null);
  drawMembershipChart("chartSF", CONFIG.SF, state.last ? state.last.sf : null);
}

function drawMembershipChart(canvasId, variable, markerValue) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;
  const { ctx, w, h } = prepareCanvas(canvas, 420 / 240);
  const pad = { left: 44, right: 14, top: 18, bottom: 34 };
  ctx.clearRect(0, 0, w, h);
  drawAxes(ctx, w, h, pad, variable);

  Object.values(variable.sets).forEach((set) => {
    ctx.beginPath();
    const points = sampleRange(variable.min, variable.max, 720).map((x) => ({
      x,
      y: membership(set, x)
    }));
    points.forEach((point, index) => {
      const px = scaleX(point.x, variable.min, variable.max, pad, w);
      const py = scaleY(point.y, 0, 1, pad, h);
      if (index === 0) ctx.moveTo(px, py);
      else ctx.lineTo(px, py);
    });
    ctx.strokeStyle = set.color;
    ctx.lineWidth = 2.4;
    ctx.lineJoin = "round";
    ctx.lineCap = "round";
    ctx.stroke();
  });

  drawLegend(ctx, variable);

  if (markerValue !== null && markerValue !== undefined) {
    const x = scaleX(markerValue, variable.min, variable.max, pad, w);
    ctx.save();
    ctx.strokeStyle = "#111827";
    ctx.lineWidth = 2;
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.moveTo(x, pad.top);
    ctx.lineTo(x, h - pad.bottom);
    ctx.stroke();
    ctx.restore();
  }
}

function drawAxes(ctx, w, h, pad, variable) {
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, w, h);
  ctx.strokeStyle = "#cbd5e1";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(pad.left, pad.top);
  ctx.lineTo(pad.left, h - pad.bottom);
  ctx.lineTo(w - pad.right, h - pad.bottom);
  ctx.stroke();

  ctx.fillStyle = "#475569";
  ctx.font = "12px system-ui, sans-serif";
  ctx.fillText(variable.title, pad.left, 13);
  ctx.fillText(String(variable.min), pad.left - 4, h - 12);
  const maxText = String(variable.max);
  ctx.fillText(maxText, w - pad.right - ctx.measureText(maxText).width, h - 12);
  ctx.fillText("1", 16, pad.top + 5);
  ctx.fillText("0", 16, h - pad.bottom + 4);
}

function drawLegend(ctx, variable) {
  let x = 54;
  const y = 30;
  Object.values(variable.sets).forEach((set) => {
    ctx.fillStyle = set.color;
    ctx.fillRect(x, y, 10, 10);
    ctx.fillStyle = "#334155";
    ctx.font = "12px system-ui, sans-serif";
    ctx.fillText(set.label, x + 14, y + 10);
    x += ctx.measureText(set.label).width + 34;
  });
}

function redrawSurfaces() {
  ["surfaceWL", "surfaceDC", "surfaceFinal"].forEach((canvasId) => {
    drawSurface3D(canvasId, getSurfaceDefForCanvasId(canvasId));
  });
}

function redrawEditorSurfaces() {
  ["editorSurfaceWL", "editorSurfaceDC", "editorSurfaceFinal"].forEach((canvasId) => {
    drawSurface3D(canvasId, getSurfaceDefForCanvasId(canvasId));
  });
}

function redrawSurfaceMarkers() {
  if (document.getElementById("surfaces")?.classList.contains("active")) {
    redrawSurfaces();
  }
  if (document.getElementById("mfeditor")?.classList.contains("active")) {
    redrawEditorSurfaces();
  }
}

function drawSurface3D(canvasId, def) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !def) return;
  const { ctx, w, h } = prepareCanvas(canvas, 560 / 390);
  const view = state.surfaceViews[canvasId] || DEFAULT_SURFACE_VIEW;
  const { cols, rows } = SURFACE_GRID;
  const points = buildSurfacePoints(def, cols, rows);

  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, w, h);
  drawSurfaceTitle(ctx, def, w);
  drawSurfaceAxes(ctx, def, view, w, h);
  drawSurfaceMesh(ctx, points, cols, rows, view, w, h);
  drawSurfaceMarker(ctx, def, view, w, h);
  drawSurfaceHint(ctx, w, h);
}

function getSurfaceDefForCanvas(canvas) {
  return getSurfaceDefForCanvasId(canvas.dataset.surfaceKey || canvas.id);
}

function getSurfaceDefForCanvasId(canvasId) {
  const canvas = document.getElementById(canvasId);
  const key = canvas?.dataset.surfaceKey || canvasId;
  return SURFACE_DEFS[key];
}

function surfaceCanvasIds() {
  return Array.from(document.querySelectorAll("[data-surface]")).map((canvas) => canvas.id);
}

function prepareCanvas(canvas, aspectRatio) {
  const rect = canvas.getBoundingClientRect();
  const fallbackWidth = Number(canvas.getAttribute("width")) || 420;
  const cssWidth = Math.max(260, Math.round(rect.width || canvas.parentElement?.clientWidth || fallbackWidth));
  const cssHeight = Math.max(160, Math.round(cssWidth / aspectRatio));
  const dpr = Math.min(window.devicePixelRatio || 1, 3);
  const pixelWidth = Math.round(cssWidth * dpr);
  const pixelHeight = Math.round(cssHeight * dpr);
  if (canvas.width !== pixelWidth || canvas.height !== pixelHeight) {
    canvas.width = pixelWidth;
    canvas.height = pixelHeight;
  }
  canvas.style.height = `${cssHeight}px`;
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  return { ctx, w: cssWidth, h: cssHeight };
}

function buildSurfacePoints(def, cols, rows) {
  const values = [];
  for (let row = 0; row < rows; row += 1) {
    values[row] = [];
    for (let col = 0; col < cols; col += 1) {
      const x = def.xVar.min + (col / (cols - 1)) * (def.xVar.max - def.xVar.min);
      const y = def.yVar.min + (row / (rows - 1)) * (def.yVar.max - def.yVar.min);
      values[row][col] = def.valueAt(x, y);
    }
  }
  const smoothValues = smoothSurfaceValues(values, cols, rows, SURFACE_GRID.smoothing);
  const points = [];
  for (let row = 0; row < rows; row += 1) {
    for (let col = 0; col < cols; col += 1) {
      const x = def.xVar.min + (col / (cols - 1)) * (def.xVar.max - def.xVar.min);
      const y = def.yVar.min + (row / (rows - 1)) * (def.yVar.max - def.yVar.min);
      const z = smoothValues[row][col];
      points.push({ x, y, z, nx: norm(x, def.xVar), ny: norm(y, def.yVar), nz: norm(z, def.zVar) });
    }
  }
  return points;
}

function smoothSurfaceValues(values, cols, rows, iterations) {
  let current = values.map((row) => row.slice());
  for (let pass = 0; pass < iterations; pass += 1) {
    const next = current.map((row) => row.slice());
    for (let row = 1; row < rows - 1; row += 1) {
      for (let col = 1; col < cols - 1; col += 1) {
        next[row][col] = (
          current[row][col] * 4 +
          current[row - 1][col] * 2 +
          current[row + 1][col] * 2 +
          current[row][col - 1] * 2 +
          current[row][col + 1] * 2 +
          current[row - 1][col - 1] +
          current[row - 1][col + 1] +
          current[row + 1][col - 1] +
          current[row + 1][col + 1]
        ) / 16;
      }
    }
    current = next;
  }
  return current;
}

function drawSurfaceMesh(ctx, points, cols, rows, view, w, h) {
  const quads = [];
  for (let row = 0; row < rows - 1; row += 1) {
    for (let col = 0; col < cols - 1; col += 1) {
      const a = points[row * cols + col];
      const b = points[row * cols + col + 1];
      const c = points[(row + 1) * cols + col + 1];
      const d = points[(row + 1) * cols + col];
      const projected = [a, b, c, d].map((point) => projectPoint(point.nx, point.ny, point.nz, view, w, h));
      const depth = projected.reduce((sum, point) => sum + point.depth, 0) / projected.length;
      const avgZ = (a.nz + b.nz + c.nz + d.nz) / 4;
      quads.push({ projected, depth, avgZ });
    }
  }

  quads.sort((a, b) => a.depth - b.depth);
  quads.forEach((quad) => {
    ctx.beginPath();
    quad.projected.forEach((point, index) => {
      if (index === 0) ctx.moveTo(point.x, point.y);
      else ctx.lineTo(point.x, point.y);
    });
    ctx.closePath();
    ctx.fillStyle = heatColor(quad.avgZ);
    ctx.strokeStyle = "rgba(0, 0, 0, 0.48)";
    ctx.lineWidth = 0.72;
    ctx.fill();
    ctx.stroke();
  });
}

function drawSurfaceAxes(ctx, def, view, w, h) {
  const origin = projectPoint(0, 0, 0, view, w, h);
  const xEnd = projectPoint(1.08, 0, 0, view, w, h);
  const yEnd = projectPoint(0, 1.08, 0, view, w, h);
  const zEnd = projectPoint(0, 0, 1.08, view, w, h);
  [
    [origin, xEnd, def.xLabel],
    [origin, yEnd, def.yLabel],
    [origin, zEnd, def.zLabel]
  ].forEach(([from, to, label]) => {
    ctx.strokeStyle = "#475569";
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(from.x, from.y);
    ctx.lineTo(to.x, to.y);
    ctx.stroke();
    ctx.fillStyle = "#17212b";
    ctx.font = "700 12px system-ui, sans-serif";
    ctx.fillText(label, to.x + 5, to.y - 5);
  });
}

function drawSurfaceMarker(ctx, def, view, w, h) {
  const marker = def.marker();
  const point = {
    nx: norm(marker.x, def.xVar),
    ny: norm(marker.y, def.yVar),
    nz: norm(marker.z, def.zVar)
  };
  const projected = projectPoint(point.nx, point.ny, point.nz, view, w, h);
  ctx.save();
  ctx.fillStyle = "#ffffff";
  ctx.strokeStyle = "#111827";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(projected.x, projected.y, 6.5, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#111827";
  ctx.font = "700 11px system-ui, sans-serif";
  ctx.fillText(`${format(marker.z, 1)}%`, projected.x + 9, projected.y - 8);
  ctx.restore();
}

function drawSurfaceTitle(ctx, def, w) {
  ctx.fillStyle = "#17212b";
  ctx.font = "700 14px system-ui, sans-serif";
  ctx.fillText(def.title, 16, 24);
  const scaleW = 92;
  const x0 = w - scaleW - 18;
  for (let i = 0; i < scaleW; i += 1) {
    ctx.fillStyle = heatColor(i / (scaleW - 1));
    ctx.fillRect(x0 + i, 15, 1, 8);
  }
  ctx.fillStyle = "#64748b";
  ctx.font = "10px system-ui, sans-serif";
  ctx.fillText("0", x0, 36);
  ctx.fillText("100", x0 + scaleW - 20, 36);
}

function drawSurfaceHint(ctx, w, h) {
  ctx.fillStyle = "#64748b";
  ctx.font = "11px system-ui, sans-serif";
  ctx.fillText("arrastrar para rotar", 16, h - 14);
}

function projectPoint(nx, ny, nz, view, width, height) {
  let x = nx - 0.5;
  let y = ny - 0.5;
  let z = nz * 0.72;
  const cosZ = Math.cos(view.rotZ);
  const sinZ = Math.sin(view.rotZ);
  const x1 = x * cosZ - y * sinZ;
  const y1 = x * sinZ + y * cosZ;
  const cosX = Math.cos(view.rotX);
  const sinX = Math.sin(view.rotX);
  const y2 = y1 * cosX - z * sinX;
  const z2 = y1 * sinX + z * cosX;
  const scale = Math.min(width, height) * 0.62 * view.zoom;
  return {
    x: width / 2 + x1 * scale,
    y: height * 0.58 - y2 * scale,
    depth: z2
  };
}

function norm(value, variable) {
  return clamp((value - variable.min) / (variable.max - variable.min), 0, 1);
}

function renderConfiguration() {
  renderArchitectureConfig();
  renderVariableConfig();
  renderRuleConfig();
  renderSurfaceConfig();
}

function renderArchitectureConfig() {
  if (!els.configArchitecture) return;
  const steps = [
    { title: "FIS 1", body: "W + L -> SD", note: "Severidad dimensional" },
    { title: "FIS 2", body: "C + D -> SE", note: "Severidad de extension" },
    { title: "FIS 3", body: "SD + SE -> SF", note: "Severidad final" }
  ];
  els.configArchitecture.innerHTML = steps.map((step) => `
    <div class="flow-step">
      <strong>${step.title}</strong>
      <span>${step.body}</span>
      <small>${step.note}</small>
    </div>
  `).join("");
}

function renderVariableConfig() {
  if (!els.configVariables) return;
  const variables = [
    ["W", CONFIG.W, "Entrada", "Umbrales directos SICT/IMT para anchura: <3 mm, 3-19 mm y >19 mm."],
    ["L", CONFIG.L, "Entrada", "Metrica requerida por manuales; umbrales iniciales propios."],
    ["D", CONFIG.D, "Entrada", "Densidad de mascara calculada desde pixeles segmentados; umbrales propios pendientes de calibracion."],
    ["C", CONFIG.C, "Entrada", "Variable propia para continuidad/calidad de observacion; no normativa."],
    ["SD", CONFIG.SD, "Salida intermedia", "Severidad dimensional usada como entrada del FIS 3."],
    ["SE", CONFIG.SE, "Salida intermedia", "Severidad de extension usada como entrada del FIS 3."],
    ["SF", CONFIG.SF, "Salida final", "Escala interna 0-100% con cortes preliminares de interpretacion."]
  ];
  els.configVariables.innerHTML = variables.map(([key, variable, role, support]) => `
    <section class="variable-config">
      <div>
        <h4>${key}: ${variable.title}</h4>
        <p>${role}. Universo: ${formatRange(variable.min, variable.max, variable.step)}.</p>
        <p>${support}</p>
      </div>
      <table>
        <thead>
          <tr><th>Conjunto</th><th>Tipo</th><th>Parametros</th></tr>
        </thead>
        <tbody>
          ${Object.entries(variable.sets).map(([setKey, set]) => `
            <tr>
              <td><span class="swatch" style="background:${set.color}"></span>${set.label || setKey}</td>
              <td>${shapeName(set.type)}</td>
              <td>[${set.p.join(", ")}]</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </section>
  `).join("");
}

function renderRuleConfig() {
  if (!els.configRules) return;
  const groups = [
    ["FIS 1: W, L -> SD", "W", "L", "SD", RULES.fis1],
    ["FIS 2: C, D -> SE", "C", "D", "SE", RULES.fis2],
    ["FIS 3: SD, SE -> SF", "SD", "SE", "SF", RULES.fis3]
  ];
  els.configRules.innerHTML = groups.map(([title, xLabel, yLabel, outLabel, rules]) => `
    <section class="rules-config-group">
      <h4>${title}</h4>
      <table>
        <thead>
          <tr><th>Regla</th><th>${xLabel}</th><th>${yLabel}</th><th>${outLabel}</th></tr>
        </thead>
        <tbody>
          ${rules.map(([xSet, ySet, outSet], index) => `
            <tr>
              <td>R${index + 1}</td>
              <td>${xSet}</td>
              <td>${ySet}</td>
              <td>${outSet}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </section>
  `).join("");
}

function renderSurfaceConfig() {
  if (!els.configSurfaces) return;
  els.configSurfaces.innerHTML = Object.values(SURFACE_DEFS).map((surface) => `
    <div class="surface-config-row">
      <strong>${surface.title}</strong>
      <span>Ejes: ${surface.xLabel}, ${surface.yLabel}, ${surface.zLabel}. Resolucion visual: malla ${SURFACE_GRID.cols} x ${SURFACE_GRID.rows} con suavizado espacial ligero; el valor Z se calcula por inferencia difusa suavizada y centroide ponderado de consecuentes.</span>
    </div>
  `).join("");
}

function cloneConfig(value) {
  return JSON.parse(JSON.stringify(value));
}

function parameterLabels(type) {
  if (type === "gauss") return ["Centro", "Sigma"];
  if (type === "tri") return ["a", "b", "c"];
  return ["a", "b", "c", "d"];
}

function editorStep(variable) {
  if (variable.max <= 1) return "0.005";
  if (variable.max <= 30) return "0.1";
  return "1";
}

function formatEditorValue(value, variable) {
  if (variable.max <= 1) return Number(value).toFixed(3);
  if (variable.max <= 30) return Number(value).toFixed(2);
  return Number(value).toFixed(1);
}

function convertSetParams(set, variable, nextType) {
  const center = clamp(setCenter(set), variable.min, variable.max);
  const span = Math.max(variable.max - variable.min, 1e-9);
  const currentSpread = set.type === "gauss"
    ? Math.max(set.p[1] * 3, span * 0.08)
    : Math.max(Math.abs(set.p[set.p.length - 1] - set.p[0]), span * 0.08);
  const width = clamp(currentSpread, span * 0.04, span * 0.65);

  if (nextType === "gauss") {
    return [roundParam(center, variable), roundParam(Math.max(width / 2.5, span * 0.015), variable)];
  }
  if (nextType === "tri") {
    return sanitizeParamArray([center - width / 2, center, center + width / 2], variable);
  }
  return sanitizeParamArray([
    center - width / 2,
    center - width / 6,
    center + width / 6,
    center + width / 2
  ], variable);
}

function sanitizeSetParams(set, variable) {
  if (set.type === "gauss") {
    const span = variable.max - variable.min;
    const center = clamp(set.p[0], variable.min, variable.max);
    const sigma = clamp(Math.abs(set.p[1] || span * 0.05), Math.max(span * 0.002, 1e-6), span);
    return [roundParam(center, variable), roundParam(sigma, variable)];
  }
  return sanitizeParamArray(set.p, variable);
}

function sanitizeParamArray(params, variable) {
  return params
    .map((value) => clamp(Number(value), variable.min, variable.max))
    .sort((a, b) => a - b)
    .map((value) => roundParam(value, variable));
}

function roundParam(value, variable) {
  if (variable.max <= 1) return Number(value.toFixed(4));
  if (variable.max <= 30) return Number(value.toFixed(3));
  return Number(value.toFixed(2));
}

function formatRange(min, max, step) {
  return `${min} a ${max}; paso ${step}`;
}

function shapeName(type) {
  if (type === "gauss") return "gaussiana";
  if (type === "tri") return "triangular";
  return "trapezoidal";
}

function heatColor(t) {
  const stops = [
    [0, 72, 255],
    [0, 213, 255],
    [98, 255, 112],
    [255, 242, 0]
  ];
  const v = clamp(t, 0, 1);
  const scaled = v * (stops.length - 1);
  const idx = Math.min(Math.floor(scaled), stops.length - 2);
  const local = scaled - idx;
  const a = stops[idx];
  const b = stops[idx + 1];
  const rgb = a.map((channel, i) => Math.round(channel + (b[i] - channel) * local));
  return `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;
}

function sampleRange(min, max, count) {
  return Array.from({ length: count }, (_, i) => min + (i / (count - 1)) * (max - min));
}

function scaleX(value, min, max, pad, width) {
  return pad.left + ((value - min) / (max - min)) * (width - pad.left - pad.right);
}

function scaleY(value, min, max, pad, height) {
  return height - pad.bottom - ((value - min) / (max - min)) * (height - pad.top - pad.bottom);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function format(value, digits) {
  return Number(value).toFixed(digits);
}

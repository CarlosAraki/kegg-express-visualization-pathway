import { initPathwayViewer } from "./viewer/pathwayScene";
import { PAYLOAD_STORAGE_KEY, type VisualizationPayload } from "./types";

const raw = sessionStorage.getItem(PAYLOAD_STORAGE_KEY);
if (!raw) {
  window.location.href = "/";
} else {
  const payload = JSON.parse(raw) as VisualizationPayload;
  initPathwayViewer(payload, document.getElementById("canvas-host")!, {
    title: document.getElementById("viewer-title")!,
    intro: document.getElementById("viewer-intro")!,
    summary: document.getElementById("viewer-summary")!,
    legendPos: document.getElementById("legend-pos")!,
    legendNeg: document.getElementById("legend-neg")!,
    tooltip: document.getElementById("tooltip")!,
    exportPng: document.getElementById("export-png") as HTMLButtonElement,
    exportSvg: document.getElementById("export-svg") as HTMLButtonElement,
    pvalueMin: document.getElementById("pvalue-min") as HTMLInputElement,
    pvalueMax: document.getElementById("pvalue-max") as HTMLInputElement,
    pvalueMinLabel: document.getElementById("pvalue-min-label")!,
    pvalueMaxLabel: document.getElementById("pvalue-max-label")!,
    pvalueCount: document.getElementById("pvalue-count")!,
    pvalueReset: document.getElementById("pvalue-reset") as HTMLButtonElement,
  });
}

import type { OverlayShape, VisualizationPayload } from "../types";
import { formatPvalue } from "./pvalueFilter";

function colorForLog2Overlay(
  value: number,
  log2Min: number,
  log2Max: number,
): string {
  if (log2Max === log2Min) return "rgba(200,200,200,0.62)";
  const t = (value - log2Min) / (log2Max - log2Min);
  const r = Math.round(33 + t * (178 - 33));
  const g = Math.round(102 + t * (24 - 102));
  const b = Math.round(172 + t * (43 - 172));
  return `rgba(${r},${g},${b},0.62)`;
}

function overlayShapeMarkup(
  shape: OverlayShape,
  log2Min: number,
  log2Max: number,
): string {
  const color = colorForLog2Overlay(shape.log2, log2Min, log2Max);
  if (shape.shape === "rect" && shape.coords.length >= 4) {
    const x = Math.min(shape.coords[0], shape.coords[2]);
    const y = Math.min(shape.coords[1], shape.coords[3]);
    const w = Math.abs(shape.coords[2] - shape.coords[0]);
    const h = Math.abs(shape.coords[3] - shape.coords[1]);
    return `<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${color}" stroke="none" />`;
  }
  if (shape.shape === "circle" && shape.coords.length >= 3) {
    return `<circle cx="${shape.coords[0]}" cy="${shape.coords[1]}" r="${shape.coords[2]}" fill="${color}" stroke="none" />`;
  }
  return "";
}

function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = fileName;
  link.click();
  URL.revokeObjectURL(url);
}

function dataUrlToBlob(dataUrl: string): Blob {
  const parts = dataUrl.split(",");
  const mime = parts[0].match(/:(.*?);/)?.[1] ?? "image/png";
  const binary = atob(parts[1]);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Blob([bytes], { type: mime });
}

export function exportIsometricPng(
  canvas: HTMLCanvasElement,
  mapId: string,
) {
  downloadBlob(
    dataUrlToBlob(canvas.toDataURL("image/png")),
    `${mapId}-isometric-log2fc.png`,
  );
}

export function exportPathwaySvg(
  payload: VisualizationPayload,
  range: { min: number; max: number },
) {
  const imageDataUrl = `data:image/png;base64,${payload.imageBase64}`;
  const overlayParts = payload.overlayShapes
    .filter((shape) => shape.pvalue >= range.min && shape.pvalue <= range.max)
    .map((shape) =>
      overlayShapeMarkup(shape, payload.log2Min, payload.log2Max),
    )
    .filter(Boolean);

  const svg =
    `<?xml version="1.0" encoding="UTF-8"?>` +
    `<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" ` +
    `width="${payload.mapW}" height="${payload.mapH}" viewBox="0 0 ${payload.mapW} ${payload.mapH}">` +
    `<image href="${imageDataUrl}" x="0" y="0" width="${payload.mapW}" height="${payload.mapH}" />` +
    overlayParts.join("") +
    `</svg>`;

  downloadBlob(
    new Blob([svg], { type: "image/svg+xml;charset=utf-8" }),
    `${payload.mapId}-log2fc-pathway.svg`,
  );
}

export function formatTooltip(entries: VisualizationPayload["areas"][0]["entries"]) {
  if (entries.length === 1) {
    const e = entries[0];
    return (
      `<strong>${e.symbol}</strong><br>` +
      `log2FC: ${e.log2.toFixed(3)}<br>` +
      `|log2FC|: ${Math.abs(e.log2).toFixed(3)}<br>` +
      `p-value: ${formatPvalue(e.pvalue)}`
    );
  }
  return entries
    .map(
      (e) =>
        `<strong>${e.symbol}</strong>: log2 ${e.log2.toFixed(3)}, p ${formatPvalue(e.pvalue)}`,
    )
    .join("<br>");
}

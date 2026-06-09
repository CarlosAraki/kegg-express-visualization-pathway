export interface GeneEntry {
  symbol: string;
  log2: number;
  pvalue: number;
}

export interface AreaData {
  id: string;
  symbols: string[];
  entries: GeneEntry[];
  log2: number;
  pvalue: number;
  abs: number;
  cx: number;
  cy: number;
  w: number;
  h: number;
}

export interface OverlayShape {
  id: string;
  shape: "rect" | "circle" | string;
  coords: number[];
  log2: number;
  pvalue: number;
}

export interface VisualizationSummary {
  genesInput: number;
  genesCorrelated: number;
  areasWithData: number;
  keggGeneAreas: number;
}

export interface VisualizationPayload {
  mapId: string;
  mapW: number;
  mapH: number;
  areas: AreaData[];
  overlayShapes: OverlayShape[];
  log2Min: number;
  log2Max: number;
  absMax: number;
  pvalueMin: number;
  pvalueMax: number;
  imageBase64: string;
  summary: VisualizationSummary;
}

export const PAYLOAD_STORAGE_KEY = "kegg-viz-payload";

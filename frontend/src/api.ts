import type { VisualizationPayload } from "./types";

export async function visualizePathway(
  pathway: string,
  file: File,
): Promise<VisualizationPayload> {
  const form = new FormData();
  form.append("pathway", pathway);
  form.append("file", file);

  const response = await fetch("/api/visualize", {
    method: "POST",
    body: form,
  });

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "Visualization failed");
  }
  return data as VisualizationPayload;
}

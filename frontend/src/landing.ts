import { visualizePathway } from "./api";
import { PAYLOAD_STORAGE_KEY } from "./types";

const form = document.getElementById("visualize-form") as HTMLFormElement;
const statusEl = document.getElementById("status") as HTMLParagraphElement;
const submitBtn = document.getElementById("submit-btn") as HTMLButtonElement;

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusEl.textContent = "";
  statusEl.className = "status";

  const pathway = (document.getElementById("pathway") as HTMLInputElement).value.trim();
  const fileInput = document.getElementById("csv-file") as HTMLInputElement;
  const file = fileInput.files?.[0];

  if (!pathway || !file) {
    statusEl.textContent = "Please provide a pathway and CSV file.";
    statusEl.classList.add("error");
    return;
  }

  submitBtn.disabled = true;
  statusEl.textContent = "Fetching pathway, correlating genes…";
  statusEl.classList.add("loading");

  try {
    const payload = await visualizePathway(pathway, file);
    sessionStorage.setItem(PAYLOAD_STORAGE_KEY, JSON.stringify(payload));
    window.location.href = "/viewer.html";
  } catch (error) {
    statusEl.textContent =
      error instanceof Error ? error.message : "Unexpected error";
    statusEl.classList.remove("loading");
    statusEl.classList.add("error");
    submitBtn.disabled = false;
  }
});

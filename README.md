# KEGG Expression Visualization Pathway

Generic web app to visualize **differential gene expression** on **any KEGG pathway**. Upload a CSV with `symbol`, `pvalue`, and `log2foldchange`, enter a pathway ID or URL, and explore an interactive **3D isometric** view with p-value filtering and PNG/SVG exports.

## Features

- **Any KEGG pathway** — accepts `map05163` or `https://www.kegg.jp/pathway/map05163`
- **CSV upload** — required columns only; extra columns ignored; duplicate symbols deduped by lowest p-value
- **3D isometric bars** — height = |log2FC|, red (up) / blue (down), Three.js + OrbitControls
- **p-value filter** — log-scale dual slider with `0.01e-5` padding; full range shows 100% of bars
- **Exports** — PNG (current 3D view + filter) and SVG (flat pathway with gradient overlay)

## Project structure

```text
server/
  kegg/           fetch HTML + PNG, parse mapdata areas
  expression/     CSV load, correlate, aggregate
  viz/            build visualization JSON payload
  pipeline.py     end-to-end orchestration
  main.py         FastAPI (/visualize, /health)
frontend/         Vite + TypeScript (landing + 3D viewer)
api/index.py      Vercel serverless entry
tests/            pytest unit + map05171 regression
pathwayApp/       reference assets (map05171 fixtures)
```

## CSV format

```csv
symbol,pvalue,log2foldchange
IL6,0.128,-1.1835
SELP,0.00113,1.37716
```

- `symbol` — gene symbol (e.g. `IL6`, `SELP`)
- `pvalue` — statistical significance (scientific notation OK, e.g. `7.38e-05`)
- `log2foldchange` — differential expression
- Additional columns are **ignored**
- Duplicate `symbol` rows → row with **lowest p-value** is kept

## Local development

### Prerequisites

- Python 3.11+
- Node.js 18+

### Setup

```bash
# Python dependencies
pip install -r requirements.txt
pip install pytest

# Frontend dependencies
cd frontend && npm install && cd ..

# Root (concurrently for dev)
npm install
```

### Run

```bash
npm run dev
```

- Landing: [http://localhost:5173](http://localhost:5173)
- API: [http://localhost:8000/health](http://localhost:8000/health)

The Vite dev server proxies `/api/*` to the FastAPI backend.

### Tests

```bash
pytest
```

Regression tests use `pathwayApp/pathway.html` and `pathwayApp/silver_pathway_areasv1.csv` for **map05171**.

## Pipeline

```text
[Form] pathway URL + CSV
    ↓
POST /api/visualize
    ↓
1. normalize_map_id → map05163
2. fetch_kegg_html + fetch_kegg_image (@2x PNG)
3. parse_mapdata_areas (human genes: href /entry/K...)
4. load_csv_genes (dedupe by symbol)
5. correlate (SYMBOL) in area title
6. aggregate_by_idarea (mean log2, min pvalue)
7. return JSON + base64 image
    ↓
[Viewer] Three.js 3D + exports
```

## Deploy (Vercel)

Use **Framework Preset: Vite** with **Output Directory: `public`**.

The frontend is static. The Python API is a **single serverless function** at `api/index.py` that handles all `/api/*` routes. FastAPI routes must use the **full path** (e.g. `/api/health`, not `/`).

**Project Settings → Build & Development:**
- Framework Preset: **Vite**
- Build Command: `npm run build`
- Output Directory: `public`
- Install Command: `npm install` (Vercel also installs `requirements.txt` for `/api/*.py`)

After deploy:

```bash
curl https://your-app.vercel.app/api/health
```

## Example pathways

| ID | Description |
|---|---|
| [map05171](https://www.kegg.jp/pathway/map05171) | Coronavirus disease (regression fixture) |
| [map05163](https://www.kegg.jp/pathway/map05163) | Human cytomegalovirus infection |

## License

Academic / research use. KEGG pathway maps © Kanehisa Laboratories.

# Song Poster Studio

A small Streamlit application that turns the mood of a song lyric excerpt into an abstract poster. It includes a fully local demo path, six poster styles, a fictional sample chart, PNG export, and tests.

> **What this is:** an independent demo implementation based on the feature specification provided for this project. It is not a copy of the source code in the linked third-party repository. It does not claim to implement the original project's live Claude, FLUX, Last.fm, Hugging Face, or Colab integrations.

## Run locally

Python 3.10 or newer is recommended.

```bash
python -m venv .venv
```

Activate the environment:

- macOS/Linux: `source .venv/bin/activate`
- Windows PowerShell: `.venv\Scripts\Activate.ps1`

Install and launch:

```bash
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open the local URL printed by Streamlit (usually <http://localhost:8501>).

## Run tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Features included

- Song selection from CSV files in `data/charts/`, plus custom title and artist input.
- Six visual presets: Aurora, Minimal, Retro, Noir, Dreamscape, and Geometric.
- Deterministic local art direction that returns a lyric-free `ArtBrief`.
- Abstract background artwork rendered locally with Pillow.
- Song title and artist overlaid as real text, with PNG download.
- Demo mode works without API keys or network calls.
- Session-only usage counters (10 briefs and 6 posters).
- A test checks that a unique lyric canary is not present in the generated art brief.
- GitHub Actions runs the test suite on pushes and pull requests.

## Privacy behavior and limitations

The app does not intentionally write lyric text to files, logs, or a database. The lyric value is read by the form-submit callback, passed to the local art-director function, and removed from Streamlit session state before the next page render. The returned brief contains mood and visual direction only, not lyric text.

This is not a guarantee about the hosting provider's transport, memory, backups, or operational logs. Avoid entering confidential or sensitive text.

## Sample chart data

`data/charts/sample_chart.csv` contains fictional example tracks. Add your own CSV files to `data/charts/` with at least these column names:

```csv
title,artist
Example Song,Example Artist
```

No automated chart collector is included. No Last.fm data is fetched.

## Deploy on Streamlit Community Cloud

1. Push the **contents** of this project folder to the root of a GitHub repository.
   Do not upload only the ZIP archive.
2. Confirm that `streamlit_app.py`, `requirements.txt`, and the `songposter/`
   folder appear together at the repository root.
3. In Streamlit Community Cloud, choose **Create app**.
4. Select your repository, branch, and `streamlit_app.py` as the main file.
5. Deploy. No secrets are required for demo mode.

See [`DEPLOYMENT_FIX.md`](DEPLOYMENT_FIX.md) for troubleshooting the
`ModuleNotFoundError: No module named 'songposter'` error.

## Project structure

```text
song-poster-studio/
├── streamlit_app.py
├── songposter/
│   ├── art_director.py
│   ├── charts.py
│   ├── image_engine.py
│   ├── limits.py
│   ├── models.py
│   ├── overlay.py
│   ├── safety.py
│   └── styles.py
├── data/charts/sample_chart.csv
├── tests/test_core.py
├── .github/workflows/ci.yml
├── .streamlit/config.toml
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## Before adding real AI services

Live Claude and FLUX integrations are intentionally not included in this starter. Add them only after reviewing their current API documentation, supported model IDs, pricing, terms, and request schemas. Keep keys in Streamlit secrets or environment variables; never commit them to GitHub. Retain this demo fallback so the app remains usable when keys or external engines are unavailable.

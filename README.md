# Amane

> A cozy little tool to turn your documents into audio… because reading is overrated sometimes.  

Amane is a FastAPI-based project for managing PDFs and audio files, with plans to transform your documents into audiobooks read by your favorite fictional characters. It comes with a **built-in web UI** (`index.html`) so you don’t even have to touch the API if you don’t want to.

---

## Features (Current)

- **Web UI**: interact with your files and audiobooks without touching the API.
- Upload, list, download, replace, and delete **PDF files**.
- Upload, list, download, replace, and delete **audio files**.
- Convert a PDF into an audiobook (PDF → Text → Audio).  
- Simple REST API endpoints for power users.

---

## Planned Features / Roadmap

- Support for **more document formats** beyond PDFs.
- Separate **text extraction** from the TTS process (PDF → TXT → Audio).
- **RVC voice support** for reading documents in your favorite character’s voice.  
- AI-powered **PDF summarization**, so a pile of PDFs can turn into a narrated lecture.
- Basically: “turn your PDF library into a lecture hall hosted by anime characters.”

---

## Installation

1. Clone the repo:  
```bash
git clone https://github.com/Iteranya/amane.git
cd amane
````

2. Install Tesseract Here:

```
https://github.com/UB-Mannheim/tesseract/wiki
```

3. Install dependencies:

```bash
python -m venv venv
venv/scripts/activate
pip install uv
uv pip install -r requirements.txt
```

4. Run the server:

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8888
```

5. Open your browser at [http://127.0.0.1:8888](http://127.0.0.1:8888) to use the built-in UI.

---

## API Overview

### Root / UI

* `GET /` – Serves the built-in **frontend UI** (`index.html`).

### File Management (PDFs)

* `GET /files` – List all uploaded files.
* `POST /files` – Upload a new file.
* `GET /files/{filename}` – Download a file.
* `PUT /files/{filename}` – Replace an existing file.
* `DELETE /files/{filename}` – Delete a file.

### Audio Management

* `GET /audio` – List all audio files.
* `POST /audio` – Upload audio.
* `GET /audio/{filename}` – Download audio.
* `PUT /audio/{filename}` – Replace audio.
* `DELETE /audio/{filename}` – Delete audio.

### PDF → Audiobook

* `POST /audiobooks/from-pdf`
  Convert a PDF into an audio file. Requires:

  * `pdf_filename` – name of the PDF to convert
  * `audio_filename` – name of the output audio file
  * `character` – voice character (default: `af_bella`)
  * `language` – language option (default: `a`)

---

## Directory Structure

```
data/
  ├─ audio/    # Generated audio files
  └─ file/     # Uploaded PDFs
core/
  ├─ text_parser/  # PDF → Text
  └─ voice_gen/    # Text → Speech
main.py
index.html       # Built-in UI
```

---

## Attributions

* **Text-to-Speech (TTS) AI**: Kokoro by Hexgrad
* **OCR Engine**: Tesseract OCR by [Google](https://github.com/tesseract-ocr/tesseract)
* **Web Framework**: FastAPI by [Sebastián Ramírez](https://fastapi.tiangolo.com/)
* **Python** and its ecosystem of libraries for PDF parsing, audio handling, and file management.

Please respect the licenses of these projects when using Amane.

---

## License & Pledge

* **License:** [AGPL-3.0](LICENSE)
* **Pledge:** [Read the ethical pledge here](PLEDGE.md)

By Artes Paradox. Have fun and keep it legal-ish. 😎

---

## Bug
* I might forgot a few dependencies, just raise issue if you run into any problem
* Might be hardcoded to use CUDA, or maybe not, I dunno... Just raise issue if you can't run it with CPU
* UI language and character selector is broken, I know, will fix

## Notes

* Use the UI if you’re lazy. Use the API if you’re a masochist.
* Keep PDFs clean — large messy PDFs may produce… chaotic audiobooks.
* RVC integration and AI summaries: coming in the far future.

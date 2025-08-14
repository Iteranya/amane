# Putting everything here for now, just for now~


from fastapi import FastAPI, UploadFile, File, Form, HTTPException, status
from fastapi.responses import FileResponse
from typing import List, Optional
from pathlib import Path
from mimetypes import guess_type
import shutil

import uvicorn

# Your existing libs
from core.voice_gen.kokoro_tts import generate_speech
from core.text_parser.pdf_to_text import pdf_to_text_pipeline

app = FastAPI()

AUDIO_LOCATION = Path("data/audio")
FILE_LOCATION = Path("data/file")

# Ensure directories exist on startup
@app.on_event("startup")
def ensure_dirs():
    AUDIO_LOCATION.mkdir(parents=True, exist_ok=True)
    FILE_LOCATION.mkdir(parents=True, exist_ok=True)

# Helpers
def _safe_name(name: str) -> str:
    # Prevent path traversal
    if not name or name != Path(name).name or any(part in ("..", "") for part in Path(name).parts):
        raise HTTPException(status_code=400, detail="Invalid filename")
    return name

def _list_files(dir_path: Path) -> List[str]:
    return sorted(p.name for p in dir_path.iterdir() if p.is_file())

async def _save_upload(dest_dir: Path, upload: UploadFile, filename: Optional[str] = None, overwrite: bool = False) -> str:
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = _safe_name(filename or upload.filename)
    target = dest_dir / name
    if target.exists() and not overwrite:
        raise HTTPException(status_code=409, detail="File already exists")
    with target.open("wb") as f:
        shutil.copyfileobj(upload.file, f)
    return name

def _file_response(path: Path) -> FileResponse:
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    media_type = guess_type(str(path))[0] or "application/octet-stream"
    return FileResponse(path, media_type=media_type, filename=path.name)

# Your async wrappers (as per your snippets)
async def convert_text_to_voice(text: str, filename: str, character: str = "af_bella", language: str = "a") -> bool:
    out_path = AUDIO_LOCATION / filename
    return await generate_speech(text, str(out_path), language, character)

async def parse_text(file_name: str) -> str:
    path_to_file = FILE_LOCATION / file_name
    return await pdf_to_text_pipeline(str(path_to_file))

# ---------------------------
# Serve the Frontend 
# ---------------------------
@app.get("/", response_class=FileResponse)
async def read_root():
    # Assumes index.html is in the same directory as your Python script
    return "index.html"

# ---------------------------
# Files (PDFs) CRUD
# ---------------------------

@app.get("/files", response_model=List[str])
async def list_files():
    return _list_files(FILE_LOCATION)

@app.post("/files", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), filename: Optional[str] = Form(None)):
    saved = await _save_upload(FILE_LOCATION, file, filename=filename, overwrite=False)
    return {"ok": True, "filename": saved}

@app.get("/files/{filename}")
async def download_file(filename: str):
    filename = _safe_name(filename)
    path = FILE_LOCATION / filename
    return _file_response(path)

@app.put("/files/{filename}")
async def replace_file(filename: str, file: UploadFile = File(...)):
    filename = _safe_name(filename)
    saved = await _save_upload(FILE_LOCATION, file, filename=filename, overwrite=True)
    return {"ok": True, "filename": saved}

@app.delete("/files/{filename}")
async def delete_file(filename: str):
    filename = _safe_name(filename)
    path = FILE_LOCATION / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()
    return {"ok": True, "deleted": filename}

# ---------------------------
# Audio CRUD
# ---------------------------

@app.get("/audio", response_model=List[str])
async def list_audio():
    return _list_files(AUDIO_LOCATION)

@app.post("/audio", status_code=status.HTTP_201_CREATED)
async def upload_audio(file: UploadFile = File(...), filename: Optional[str] = Form(None)):
    saved = await _save_upload(AUDIO_LOCATION, file, filename=filename, overwrite=False)
    return {"ok": True, "filename": saved}

@app.get("/audio/{filename}")
async def download_audio(filename: str):
    filename = _safe_name(filename)
    path = AUDIO_LOCATION / filename
    return _file_response(path)

@app.put("/audio/{filename}")
async def replace_audio(filename: str, file: UploadFile = File(...)):
    filename = _safe_name(filename)
    saved = await _save_upload(AUDIO_LOCATION, file, filename=filename, overwrite=True)
    return {"ok": True, "filename": saved}

@app.delete("/audio/{filename}")
async def delete_audio(filename: str):
    filename = _safe_name(filename)
    path = AUDIO_LOCATION / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    path.unlink()
    return {"ok": True, "deleted": filename}

# ---------------------------
# Convert a PDF to an audiobook
# ---------------------------

@app.post("/audiobooks/from-pdf")
async def pdf_to_audiobook(
    pdf_filename: str = Form(...),
    audio_filename: str = Form(...),
    character: str = Form("af_bella"),
    language: str = Form("a"),
):
    pdf_filename = _safe_name(pdf_filename)
    audio_filename = _safe_name(audio_filename)

    pdf_path = FILE_LOCATION / pdf_filename
    if not pdf_path.exists():
        raise HTTPException(status_code=404, detail="PDF not found")

    text = await parse_text(pdf_filename)
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Parsed text is empty")

    AUDIO_LOCATION.mkdir(parents=True, exist_ok=True)
    ok = await convert_text_to_voice(text, audio_filename, character=character, language=language)
    if not ok:
        raise HTTPException(status_code=500, detail="Text-to-speech failed")

    audio_path = AUDIO_LOCATION / audio_filename
    return {"ok": True, "audio_file": audio_filename, "audio_path": str(audio_path)}


if __name__ == "__main__":
    
    uvicorn.run("main:app", host="127.0.0.1", port=8888) 
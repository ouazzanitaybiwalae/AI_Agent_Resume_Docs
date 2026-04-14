from fastapi import FastAPI, UploadFile, File, Form
from typing import Optional
from file_reader import read_file
from summarizer import summarize_text

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "API opérationnelle"}

@app.post("/summarize")
async def summarize(
    file: UploadFile = File(...),
    doc_type: Optional[str] = Form("général"),
    instructions: Optional[str] = Form(""),
    output_format: Optional[str] = Form("structuré"),
):
    content = await file.read()

    try:
        text = read_file(content, file.filename)
    except ValueError as e:
        return {"error": str(e)}

    summary = summarize_text(
        text=text,
        doc_type=doc_type,
        instructions=instructions,
        output_format=output_format,
    )

    return {
        "filename": file.filename,
        "summary": summary,
        "status": "ok"
    }
from fastapi import FastAPI, UploadFile, File
from file_reader import read_file
from summarizer import summarize_text

app = FastAPI()

@app.get("/")
def hello():
    return {"message": "API opérationnelle"}

@app.post("/summarize")
async def summarize(file: UploadFile = File(...)):

    content = await file.read()

    try:
        text = read_file(content, file.filename)
    except ValueError as e:
        return {"error": str(e)}

    summary = summarize_text(text)

    return {
        "filename": file.filename,
        "summary": summary,
        "status": "ok"
    }
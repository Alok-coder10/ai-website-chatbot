from pypdf import PdfReader
from docx import Document
from pathlib import Path
import shutil

UPLOAD_DIR = "uploads"
Path(UPLOAD_DIR).mkdir(exist_ok=True)

class DocumentService:
    async def save_file(self, file):
        path = Path(UPLOAD_DIR) / file.filename
        with open(path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return str(path)


    def extract_pdf(self, path):
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        
        return text
    
    def extract_docx(self, path):
        doc = Document(path)

        return "\n".join(p.text for p in doc.paragraphs)

    
    def extract_text(self, path):
        with open(path, encoding="utf-8") as file:
            return file.read()

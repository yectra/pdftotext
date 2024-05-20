from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import PyPDF2
import aiofiles

app = FastAPI()

# Enable CORS to allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfFileReader(file)
        for page_num in range(pdf_reader.numPages):
            page = pdf_reader.getPage(page_num)
            text += page.extractText()
    return text

@app.post("/extract_text/")
async def extract_text_from_uploaded_pdf(pdf: UploadFile = File(...)):
    if not pdf.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    try:
        # Save the uploaded PDF file temporarily
        temp_pdf_path = f"/tmp/{pdf.filename}"
        async with aiofiles.open(temp_pdf_path, "wb") as buffer:
            await buffer.write(await pdf.read())

        # Extract text from the PDF
        extracted_text = extract_text_from_pdf(temp_pdf_path)

        # Check if the file exists before serving
        if not extracted_text:
            raise HTTPException(status_code=500, detail="Error: No text extracted from the PDF")

        # Return the extracted text as plain text response
        return PlainTextResponse(content=extracted_text)

    except PyPDF2.utils.PdfReadError as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")

    finally:
        # Remove the temporary PDF file
        if os.path.exists(temp_pdf_path):
            os.remove(temp_pdf_path)
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import io
from PIL import Image
import base64
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# Enable CORS to allow requests from any origin (for development)
# In production, you should specify your frontend URL
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get API key from .env file
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY not found in environment variables")
    
genai.configure(api_key=API_KEY)

class AnalysisResponse(BaseModel):
    analysis: str

@app.post("/api/analyze-image", response_model=AnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    # Read the image file
    image_bytes = await file.read()
    
    # Process the image with PIL
    image = Image.open(io.BytesIO(image_bytes))
    image_bytes_io = io.BytesIO()
    image.save(image_bytes_io, format='JPEG')
    processed_image_bytes = image_bytes_io.getvalue()
    
    # Initialize the Gemini model
    model = genai.GenerativeModel(model_name="models/gemini-1.5-flash")
    
    # Generate content with the image
    response = model.generate_content(
        contents=[
            {
                "role": "user",
                "parts": [
                    {
                        "text": "Analyze this face and tell me the likely face shape (e.g., oval, round, square, heart, diamond). Rate the hairstyle out of 10 and suggest one that would look good. Then suggest suitable accessories like sunglasses and earrings. No bold text."
                    },
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": processed_image_bytes
                        }
                    }
                ]
            }
        ]
    )
    
    # Return the analysis
    return AnalysisResponse(analysis=response.text)

# Add a simple health check endpoint
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    # Use PORT environment variable if available (for cloud deployment)
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

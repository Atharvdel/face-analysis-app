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
    allow_origins=["https://face-analysis-app.vercel.app"],  # Allow all origins for now
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
                        "text": """You are an expert virtual stylist and facial recognition analyst. A user has uploaded their photo for a face shape analysis. Your task is to:
                        1)  Identify the users face shape (choose one from: oval, round, square, heart, diamond, rectangle, triangle, oblong).

                        2) Describe the facial structure clearly, covering:

                            Forehead width

                            Jawline shape and width

                            Cheekbone prominence

                            Chin type (pointed, round, wide, etc.)

                        3) Based on the identified face shape and structure:

                            Recommend 3 to 4 hairstyles (men/women depending on input) that suit this shape

                            Suggest face-framing techniques (e.g., layers, fringes, volume, etc.)

                            Recommend 3 suitable accessories (like sunglasses shape, earrings style, hats) that complement the shape

                            ✳ Ensure that all recommendations are appropriate for the users apparent age and gender. For example, avoid suggesting earrings to an elderly man unless culturally or personally relevant.

                        4) Give a brief reasoning (1 to 2 lines) behind each suggestion to help the user understand what works and why.

                        5) Keep tone friendly and professional, and output should be in simple, easy-to-understand language. """
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
    # Default to 10000 which is Render's default port
    port = int(os.getenv("PORT", "10000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

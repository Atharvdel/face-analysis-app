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
    allow_origins=[
        "https://face-analysis-app.vercel.app",  # Production Vercel URL
        "http://localhost:3000"  # Local development URL
    ],
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
                        "text": """You are a virtual stylist. A user has uploaded their photo. Analyze and respond *based entirely on the image* as follows:

                                1. Identify their *face shape* (oval, round, square, heart, diamond, rectangle, triangle, oblong).
                                2. Describe their *facial structure* (forehead, jawline, cheekbones, chin).

                                3. Rate their *current look* on a scale of 1 to 100, based on these specific criteria:
                                  - Proportion (0-25): How well the hairstyle balances facial asymmetries
                                  - Harmony (0-25): How well the hairstyle complements face shape
                                  - Styling (0-25): How well the current style is executed and maintained
                                  - Personalization (0-25): How unique and personally fitting the style appears
                                  Calculate and provide a detailed breakdown of scores for each criterion.

                                4. Suggest improvements:
                                  - 3 hairstyles that suit their face shape
                                  - 1 face-framing tip (e.g., layers, volume, fringe)
                                  - 2–3 accessories (like sunglasses, earrings, or hats)

                                5. Estimate a *potential improved rating* by recalculating each criterion after your suggestions, providing both the new breakdown and total.

                                IMPORTANT INSTRUCTIONS FOR SCORING:
                                - Be critical and realistic in your initial assessment
                                - Vary your scores meaningfully across users (range should be 45-85 for initial scores)
                                - Higher scores should only be given when hairstyle truly optimizes face shape
                                - Lower scores indicate significant room for improvement
                                - No perfect scores (85+ should be rare and only for exceptional matches)

                                Describe clearly what you see in the image (hairstyle, structure) before giving the rating.

                                Speak directly to the user as "you". Keep it friendly and style-focused. Do not comment on skin tone, beauty, or age inappropriately. """
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

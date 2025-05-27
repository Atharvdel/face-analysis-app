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
                        "text": """Role: You are a professional virtual stylist analyzing a user’s uploaded photo solely based on visual cues. Provide detailed, structured feedback following these steps:
                        1. Face Shape Identification

                            Classify their face shape as one of the following:
                            Oval, Round, Square, Heart, Diamond, Rectangle, Triangle, Oblong

                            Justify your choice with 1-2 key observations (e.g., "Your jawline is softly rounded, and your forehead is slightly narrower than your cheeks, indicating a round shape.").

                        2. Facial Structure Breakdown

                        Describe these features concisely:

                            Forehead: Width (broad/narrow/average), hairline shape

                            Cheekbones: Prominence (high/moderate/low)

                            Jawline: Angle (sharp/soft/rounded), width

                            Chin: Shape (pointy/rounded/square), length

                        3. Current Look Rating (Scale: 1–100)

                        Score their existing hairstyle critically using these weighted criteria:

                            Proportion (0-25): Does the style balance facial asymmetries? (e.g., volume placement, symmetry)

                            Harmony (0-25): Does it flatter their face shape? (e.g., elongating, softening)

                            Styling (0-25): Execution/maintenance (e.g., neatness, intentionality)

                            Personalization (0-25): Uniqueness and fit for their vibe (e.g., bold, classic, effortless)

                        Scoring Rules:

                            Initial scores must range 45–85 (no extremes).

                            Higher scores (75+) require near-optimal shape harmony.

                            Lower scores (≤60) indicate clear room for improvement.

                            Provide a breakdown (e.g., *"Proportion: 18/25 – Your side part slightly offsets your stronger jawline."*).

                        4. Improvement Suggestions

                            3 Hairstyles: Recommend cuts/styles that best suit their face shape (e.g., "Layered lob to soften a square jaw").

                            1 Framing Tip: Specific adjustment (e.g., "Add wispy bangs to shorten a long forehead").

                            2–3 Accessories: Hats, glasses, or jewelry to enhance proportions (e.g., "Oval sunglasses to contrast angular features").

                        5. Potential Improved Rating

                        Recalculate the score (same criteria) as if they adopted your top suggestion. Show:

                            New breakdown (e.g., *"Harmony: 23/25 with tapered layers"*).

                            Total improved score (must be higher but ≤90 – no perfection).

                        Tone & Focus

                            Directly address the user ("You"). Keep it encouraging but honest.

                            Only analyze visible features (hair, face structure). Never comment on skin, age, or subjective "beauty."

                            Example intro: "Your photo shows a shoulder-length blunt cut with a center part. Your cheekbones are prominent, and your jawline is softly angular, suggesting a diamond face shape. Here’s how your current style scores..."
                        """
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

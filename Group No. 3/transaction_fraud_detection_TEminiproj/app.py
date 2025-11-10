from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pipeline import FraudDetectionPipeline
from PIL import Image
import io

app = FastAPI(title="Transaction Fraud Detection API")

# Initialize pipeline
pipeline = FraudDetectionPipeline(model_path="models/")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "active", "message": "Transaction Fraud Detection API"}

@app.post("/predict")
async def predict_transaction(image: UploadFile = File(...)):
    """
    Analyze transaction image for fraud detection
    Accepts: Image file (PNG, JPG, JPEG)
    Returns: Extracted text, transaction details, and fraud analysis
    """
    try:
        # Validate file type
        content_type = image.content_type
        if content_type is None or not content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes))
        
        # Run pipeline analysis
        result = pipeline.analyze_message(img)
        
        # Return structured response matching frontend expectations
        return {
            "extracted_text": result['extracted_text'],
            "transaction_details": result['transaction_details'],
            "fraud_analysis": result['fraud_analysis']
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Transaction Fraud Detection API...")
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

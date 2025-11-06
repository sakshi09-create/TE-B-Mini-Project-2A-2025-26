import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pytesseract
from PIL import Image
import os
import joblib
import re
import requests
from urllib.parse import urlparse

app = Flask(__name__)
CORS(app)  # Enable CORS for React

# Set UTF-8 encoding for template rendering
app.config['JSON_AS_ASCII'] = False

# Path to Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Enhanced fraud keywords - Including Hindi and Marathi translations
strong_fraud_keywords = [
    # English keywords
    "bank alert", "zelle payment", "fraud alert", "click here", "reply yes", 
    "urgent", "suspended", "verify now", "claim", "won", "lottery", "prize",
    "account blocked", "update details", "suspicious activity", "j.p. morgan",
    "chase bank", "free msg", "attempt a", "decline fraud alerts",
    # Hindi keywords
    "बैंक अलर्ट", "धोखाधड़ी चेतावनी", "यहां क्लिक करें", "जवाब दें हाँ", 
    "तत्काल", "निलंबित", "अभी सत्यापित करें", "दावा", "जीत गए", "लॉटरी", "पुरस्कार",
    "खाता अवरुद्ध", "अद्यतन विवरण", "संदिग्ध गतिविधि",
    # Marathi keywords
    "बँक अलर्ट", "फ्रॉड अलर्ट", "इथे क्लिक करा", "उत्तर होय", 
    "तातडीने", "निलंबित", "आता सत्यापित करा", "दावा", "जिंकले", "लॉटरी", "बक्षीस",
    "खाते अवरोधित", "अद्ययावत तपशील", "संशयास्पद क्रियाकलाप"
]

# Load the trained model
try:
    model = joblib.load("fraud_detector.pkl")
    use_ml_model = True
    print("✅ ML Model loaded successfully")
except Exception as e:
    use_ml_model = False
    print(f"⚠️ ML Model not found: {e}, using keyword matching")

def enhanced_fraud_check(text):
    """Enhanced and more precise fraud detection"""
    
    # Ensure text is properly encoded
    if isinstance(text, bytes):
        text = text.decode('utf-8', errors='ignore')
    
    text_lower = text.lower()
    
    # Extract URLs from text
    urls = extract_urls(text)
    link_analysis = analyze_links(urls) if urls else None
    
    # POSITIVE indicators (safe message patterns) - Including Hindi and Marathi
    safe_patterns = [
        # English safe patterns
        "say no to drugs", "anti narcotics", "crime branch", "police", 
        "health", "safety", "education", "community", "public service",
        "awareness", "helpline", "government", "ministry", "department",
        "traffic police", "fire safety", "blood donation", "vaccination",
        "election commission", "vote", "library", "school", "hospital",
        # Hindi safe patterns
        "नशे कहें नहीं", "एंटी नारकोटिक्स", "क्राइम ब्रांच", "पुलिस", 
        "स्वास्थ्य", "सुरक्षा", "शिक्षा", "समुदाय", "सार्वजनिक सेवा",
        "जागरूकता", "हेल्पलाइन", "सरकार", "मंत्रालय", "विभाग",
        "ट्रैफिक पुलिस", "अग्निशमन सुरक्षा", "रक्तदान", "टीकाकरण",
        "चुनाव आयोग", "मतदान", "पुस्तकालय", "स्कूल", "अस्पताल",
        # Marathi safe patterns
        "नशा म्हणा नाही", "ॲन्टी नारकोटिक्स", "क्राइम ब्रांच", "पोलिस", 
        "आरोग्य", "सुरक्षा", "शिक्षण", "समुदाय", "सार्वजनिक सेवा",
        "जागरूकता", "हेल्पलाइन", "शासन", "मंत्रालय", "विभाग",
        "ट्राफिक पोलिस", "अग्निशमन सुरक्षा", "रक्तदान", "लसीकरण",
        "निवडणूक आयोग", "मतदान", "ग्रंथालय", "शाळा", "रुग्णालय"
    ]
    
    # Check for safe patterns first
    safe_matches = [pattern for pattern in safe_patterns if pattern in text_lower]
    if safe_matches and len(safe_matches) >= 1:
        return {
            "is_fraud": False,
            "confidence": 0.95,
            "method": "Safe Pattern Recognition",
            "matched_keywords": safe_matches,
            "reason": "Identified as legitimate public service/educational message"
        }
    
    # Strong fraud indicators (financial/urgent action required) - Including Hindi and Marathi
    strong_fraud_keywords = [
        # English fraud keywords
        "click here to claim", "reply yes", "account suspended", "verify immediately",
        "limited time offer", "act now", "claim prize", "won lottery", 
        "bank alert", "zelle payment", "fraud alert", "update details",
        "account blocked", "suspicious activity", "call immediately",
        "your account will be", "click to unlock", "verify your account",
        # Hindi fraud keywords
        "दावा करने के लिए यहां क्लिक करें", "जवाब दें हाँ", "खाता निलंबित", "तुरंत सत्यापित करें",
        "सीमित समय की पेशकश", "अभी कार्रवाई करें", "पुरस्कार का दावा करें", "लॉटरी जीते",
        "बैंक अलर्ट", "झेले भुगतान", "धोखाधड़ी चेतावनी", "विवरण अद्यतन करें",
        "खाता अवरुद्ध", "संदिग्ध गतिविधि", "तुरंत कॉल करें",
        "आपका खाता होगा", "अनलॉक करने के लिए क्लिक करें", "अपने खाते को सत्यापित करें",
        # Marathi fraud keywords
        "दावा करण्यासाठी इथे क्लिक करा", "उत्तर होय", "खाते निलंबित", "लगेच सत्यापित करा",
        "मर्यादित कालावधी ऑफर", "आता कृती करा", "बक्षीस दावा करा", "लॉटरी जिंकली",
        "बँक अलर्ट", "झेले पेमेंट", "फ्रॉड अलर्ट", "तपशील अद्ययावत करा",
        "खाते अवरोधित", "संशयास्पद क्रियाकलाप", "लगेच कॉल करा",
        "तुमचे खाते असेल", "अनलॉक करण्यासाठी क्लिक करा", "तुमचे खाते सत्यापित करा"
    ]
    
    # Check for fraud patterns
    strong_matches = [kw for kw in strong_fraud_keywords if kw in text_lower]
    
    # Financial fraud patterns - Including Hindi and Marathi currency symbols
    financial_fraud_patterns = [
        # English patterns
        ("$" in text and "won" in text_lower),
        ("$" in text and "claim" in text_lower),
        ("$" in text and "prize" in text_lower),
        ("bank" in text_lower and "alert" in text_lower and "$" in text),
        ("reply yes" in text_lower and "$" in text),
        ("click" in text_lower and ("prize" in text_lower or "claim" in text_lower)),
        # Indian currency patterns
        ("₹" in text and "won" in text_lower),
        ("₹" in text and "claim" in text_lower),
        ("₹" in text and "prize" in text_lower),
        ("bank" in text_lower and "alert" in text_lower and "₹" in text),
        ("reply yes" in text_lower and "₹" in text),
        ("click" in text_lower and ("prize" in text_lower or "claim" in text_lower)),
        # Hindi patterns
        ("रु" in text and "जीत" in text_lower),
        ("रु" in text and "दावा" in text_lower),
        ("रु" in text and "पुरस्कार" in text_lower),
        # Marathi patterns
        ("रु" in text and "जिंकले" in text_lower),
        ("रु" in text and "दावा" in text_lower),
        ("रु" in text and "बक्षीस" in text_lower)
    ]
    
    # If multiple strong fraud indicators, likely fraud
    if len(strong_matches) >= 2 or any(financial_fraud_patterns):
        result = {
            "is_fraud": True,
            "confidence": 0.9,
            "method": "Fraud Pattern Recognition",
            "matched_keywords": strong_matches,
            "reason": "Multiple fraud indicators detected"
        }
        if link_analysis:
            result["link_analysis"] = link_analysis
        return result
    
    # Use ML model with better error handling
    if use_ml_model:
        try:
            prediction = model.predict([text])[0]
            confidence = max(model.predict_proba([text])[0])
            
            # Don't override high-confidence safe predictions for legitimate messages
            if prediction == "safe" and confidence > 0.7:
                result = {
                    "is_fraud": False,
                    "confidence": float(confidence),
                    "method": "Machine Learning Model",
                    "matched_keywords": safe_matches or [],
                    "prediction": prediction
                }
                if link_analysis:
                    result["link_analysis"] = link_analysis
                return result
            
            # Don't override high-confidence fraud predictions
            if prediction == "fraud" and confidence > 0.8:
                result = {
                    "is_fraud": True,
                    "confidence": float(confidence),
                    "method": "Machine Learning Model",
                    "matched_keywords": strong_matches,
                    "prediction": prediction
                }
                if link_analysis:
                    result["link_analysis"] = link_analysis
                return result
            
            # For low-confidence predictions, use keyword analysis as backup
            if confidence < 0.7:
                keyword_result = keyword_fallback_analysis(text_lower, strong_matches, safe_matches)
                if keyword_result:
                    if link_analysis:
                        keyword_result["link_analysis"] = link_analysis
                    return keyword_result
            
            result = {
                "is_fraud": prediction == "fraud",
                "confidence": float(confidence),
                "method": "Machine Learning Model",
                "matched_keywords": strong_matches or safe_matches,
                "prediction": prediction
            }
            if link_analysis:
                result["link_analysis"] = link_analysis
            return result
            
        except Exception as e:
            print(f"ML Model error: {e}")
    
    # Fallback keyword analysis
    result = keyword_fallback_analysis(text_lower, strong_matches, safe_matches)
    if link_analysis:
        result["link_analysis"] = link_analysis
    return result

def keyword_fallback_analysis(text_lower, strong_matches, safe_matches):
    """Fallback analysis using keywords"""
    
    # If safe patterns found, mark as safe
    if safe_matches:
        return {
            "is_fraud": False,
            "confidence": 0.85,
            "method": "Keyword Analysis - Safe",
            "matched_keywords": safe_matches,
            "reason": "Contains legitimate service keywords"
        }
    
    # If fraud patterns found, mark as fraud
    if strong_matches:
        fraud_score = len(strong_matches)
        confidence = min(fraud_score * 0.4, 0.9)
        return {
            "is_fraud": True,
            "confidence": confidence,
            "method": "Keyword Analysis - Fraud",
            "matched_keywords": strong_matches,
            "fraud_score": fraud_score
        }
    
    # No clear indicators - default to safe with low confidence
    return {
        "is_fraud": False,
        "confidence": 0.6,
        "method": "Default Classification",
        "matched_keywords": [],
        "reason": "No clear fraud indicators found"
    }

def extract_urls(text):
    """Extract URLs from text"""
    url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+'
    urls = re.findall(url_pattern, text)
    
    # Also find URLs without protocol
    domain_pattern = r'(?<!\w)(?:www\.)?[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+(?:/[^\s]*)?'
    domains = re.findall(domain_pattern, text)
    
    # Combine and deduplicate
    all_urls = list(set(urls + domains))
    return all_urls

def analyze_links(urls):
    """Analyze URLs for potential fraud/safety issues"""
    if not urls:
        return None
    
    link_results = []
    
    for url in urls:
        # Ensure URL has protocol
        if not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        
        analysis = {
            "url": url,
            "is_suspicious": False,
            "issues": [],
            "safety_score": 1.0
        }
        
        # Parse URL
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check for suspicious domain patterns
            suspicious_patterns = [
                r'tiny\.url', r'bit\.ly', r't\.co', r'goo\.gl',
                r'shorturl', r'url\.short', r'link\.short',
                r'[0-9]{5,}',  # Many numbers in domain
                r'[a-z]{15,}\.[a-z]{2,}'  # Very long random domains
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, domain):
                    analysis["is_suspicious"] = True
                    analysis["issues"].append(f"Suspicious domain pattern: {pattern}")
                    analysis["safety_score"] *= 0.5
            
            # Check for known banking domains (legitimate)
            legitimate_banks = [
                'bankofamerica.com', 'chase.com', 'wellsfargo.com',
                'citibank.com', 'hsbc.com', 'icicibank.com',
                'hdfcbank.com', 'axisbank.com', 'sbi.co.in'
            ]
            
            is_legitimate_bank = any(bank in domain for bank in legitimate_banks)
            
            if not is_legitimate_bank:
                # Check for banking-related keywords in suspicious domains
                banking_keywords = ['bank', 'secure', 'login', 'account', 'verify', 
                                  'बैंक', 'सुरक्षित', 'लॉगिन', 'खाता', 'सत्यापित',
                                  'बँक', 'सुरक्षा', 'लॉगइन', 'खाते', 'सत्यापन']
                if any(keyword in domain for keyword in banking_keywords):
                    analysis["is_suspicious"] = True
                    analysis["issues"].append("Banking-related domain that isn't a known bank")
                    analysis["safety_score"] *= 0.3
            
            # Try to check if URL is accessible (basic check)
            try:
                response = requests.head(url, timeout=5, allow_redirects=True)
                if response.status_code >= 400:
                    analysis["issues"].append(f"URL returns error status: {response.status_code}")
                    analysis["safety_score"] *= 0.7
            except requests.exceptions.RequestException:
                analysis["issues"].append("URL is not accessible")
                analysis["safety_score"] *= 0.8
                
        except Exception as e:
            analysis["issues"].append(f"Parsing error: {str(e)}")
            analysis["safety_score"] *= 0.9
        
        link_results.append(analysis)
    
    # Overall assessment
    suspicious_count = sum(1 for link in link_results if link["is_suspicious"])
    if suspicious_count > 0:
        overall_assessment = {
            "total_links": len(link_results),
            "suspicious_links": suspicious_count,
            "is_suspicious": True,
            "risk_level": "high" if suspicious_count/len(link_results) > 0.5 else "medium"
        }
    else:
        overall_assessment = {
            "total_links": len(link_results),
            "suspicious_links": 0,
            "is_suspicious": False,
            "risk_level": "low"
        }
    
    return {
        "links": link_results,
        "overall": overall_assessment
    }


def check_fraud(text):
    """Simple function for HTML template compatibility"""
    result = enhanced_fraud_check(text)
    return "⚠️ Fraudulent Message Detected!" if result["is_fraud"] else "✅ Safe Message"

def check_fraud_analysis(text):
    """Detailed analysis function for API"""
    return enhanced_fraud_check(text)

# Original route for HTML template
@app.route("/")
def index():
    return render_template("index.html")

# Original upload route for HTML template
@app.route("/upload", methods=["POST"])
def upload():
    if "screenshot" not in request.files:
        return "No file uploaded", 400

    file = request.files["screenshot"]
    if file.filename == "":
        return "No file selected", 400

    # Save the file temporarily
    filepath = os.path.join("static", file.filename or "upload.png")
    file.save(filepath)

    try:
        # OCR extraction with language support
        img = Image.open(filepath)
        # Try to extract text in multiple languages
        extracted_text = pytesseract.image_to_string(img, lang='eng+hin+mar')
        print(f"HTML Upload - Extracted text: {extracted_text}")

        # Check fraud using enhanced method
        result = check_fraud(extracted_text)
        print(f"HTML Upload - Result: {result}")

        return render_template("index.html", result=result, text=extracted_text, image=filepath)
    
    except Exception as e:
        print(f"Error in HTML upload: {e}")
        return f"Error processing image: {str(e)}", 500

# API endpoint for React
@app.route("/api/analyze", methods=["POST"])
def analyze_screenshot():
    try:
        print("📥 Received analyze request")
        
        if "screenshot" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["screenshot"]
        if file.filename == "":
            return jsonify({"error": "No file selected"}), 400

        print(f"📁 Processing file: {file.filename}")

        # Create uploads directory if it doesn't exist
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file temporarily
        filename = file.filename or "upload.png"
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        print(f"💾 File saved to: {filepath}")

        try:
            # OCR extraction with multi-language support
            print("🔍 Starting OCR extraction...")
            img = Image.open(filepath)
            # Extract text in English, Hindi, and Marathi
            extracted_text = pytesseract.image_to_string(img, lang='eng+hin+mar').strip()
            print(f"📝 API - Extracted text: {extracted_text}")
            
            if not extracted_text:
                print("⚠️ No text found in image")
                return jsonify({
                    "success": True,
                    "extracted_text": "",
                    "fraud_analysis": {
                        "is_fraud": False,
                        "confidence": 0,
                        "method": "No text detected",
                        "message": "No readable text found in image"
                    }
                })

            # Fraud detection using enhanced method
            print("🔍 Starting fraud analysis...")
            fraud_result = check_fraud_analysis(extracted_text)
            print(f"✅ API - Analysis result: {fraud_result}")

            return jsonify({
                "success": True,
                "extracted_text": extracted_text,
                "fraud_analysis": fraud_result
            })

        finally:
            # Clean up uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Cleaned up file: {filepath}")

    except Exception as e:
        print(f"❌ Error in analyze_screenshot: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Processing failed: {str(e)}"}), 500

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy", 
        "ml_model_loaded": use_ml_model,
        "tesseract_configured": True
    })

if __name__ == "__main__":
    # First, train the model if it doesn't exist
    if not os.path.exists("fraud_detector.pkl"):
        print("🔄 Training fraud detection model...")
        try:
            exec(open("fraud_model.py").read())
            print("✅ Model trained and saved")
        except Exception as e:
            print(f"❌ Failed to train model: {e}")
    
    print("🚀 Starting Flask server...")
    app.run(debug=True, port=5000, host='0.0.0.0')
"""
Transaction Fraud Detection Pipeline
Handles OCR, text extraction, preprocessing, and prediction
"""

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

import re
import joblib
import numpy as np
from PIL import Image
import pytesseract
import cv2
import os
import requests
from urllib.parse import urlparse
from typing import Optional, Dict, List, Any, Union

# Make EasyOCR optional
try:
    import easyocr
    EASYOCR_AVAILABLE: bool = True
except ImportError:
    easyocr = None  # type: ignore
    EASYOCR_AVAILABLE = False
    print("⚠️ EasyOCR not available. Using Pytesseract only.")

class FraudDetectionPipeline:
    """Complete pipeline for fraud detection from image to prediction"""
    
    def __init__(self, model_path: str = 'models'):
        """Initialize the pipeline with trained models"""
        self.model_path = model_path
        self.model: Any = None
        self.vectorizer: Any = None
        self.label_encoder: Any = None
        self.easyocr_reader: Any = None
        self.load_models()
    
    def load_models(self) -> None:
        """Load trained models"""
        try:
            self.model = joblib.load(f'{self.model_path}/fraud_classifier.pkl')
            self.vectorizer = joblib.load(f'{self.model_path}/vectorizer.pkl')
            self.label_encoder = joblib.load(f'{self.model_path}/label_encoder.pkl')
            print("✅ Models loaded successfully")
        except Exception as e:
            print(f"❌ Error loading models: {e}")
            raise
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocess image for better OCR results"""
        # Convert PIL Image to numpy array
        img = np.array(image)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return denoised
    
    def extract_text_pytesseract(self, image: Image.Image) -> str:
        """Extract text using Pytesseract with multi-language support"""
        try:
            preprocessed = self.preprocess_image(image)
            # Extract text in English, Hindi, and Marathi
            text = pytesseract.image_to_string(preprocessed, lang='eng+hin+mar')
            return text.strip()
        except Exception as e:
            print(f"Pytesseract error: {e}")
            return ""
    
    def extract_text_easyocr(self, image: Image.Image) -> str:
        """Extract text using EasyOCR"""
        if not EASYOCR_AVAILABLE or easyocr is None:
            return ""
        
        try:
            if self.easyocr_reader is None:
                # Include Hindi and Marathi in EasyOCR languages
                self.easyocr_reader = easyocr.Reader(['en', 'hi', 'mr'], gpu=False)
            
            img_array = np.array(image)
            results = self.easyocr_reader.readtext(img_array)
            
            # Combine all detected text
            text_parts: List[str] = []
            for result in results:
                if len(result) > 1 and result[1] is not None:
                    text_parts.append(str(result[1]))
            text = ' '.join(text_parts)
            return text.strip()
        except Exception as e:
            print(f"EasyOCR error: {e}")
            return ""
    
    def extract_text(self, image: Image.Image) -> str:
        """Extract text using both OCR methods and combine"""
        text1 = self.extract_text_pytesseract(image)
        
        # Only use EasyOCR if available
        if EASYOCR_AVAILABLE:
            text2 = self.extract_text_easyocr(image)
        else:
            text2 = ""
        
        # Use the longer text or combine both
        if len(text1) > len(text2):
            final_text = text1
        else:
            final_text = text2 if text2 else text1
        
        # If both have content, combine unique parts
        if text1 and text2 and text1 != text2:
            final_text = f"{text1} {text2}"
        
        # Return the extracted text as is (no translation)
        return final_text if final_text else "No text detected in image"
    
    def extract_transaction_details(self, text: str) -> Dict[str, Optional[Union[float, str]]]:
        """Extract transaction-specific information - Including Hindi and Marathi"""
        details: Dict[str, Optional[Union[float, str]]] = {
            'amount': None,
            'transaction_type': None,
            'recipient': None,
            'upi_id': None,
            'account_number': None,
            'transaction_id': None
        }
        
        # Extract amount (Rs, ₹, INR) - Including Hindi and Marathi variations
        amount_patterns = [
            # English patterns
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'INR\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(?:paid|credited|debited|received|transferred)\s+(?:Rs\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            # Hindi patterns
            r'रुपये\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'आईएनआर\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(?:भुगतान|श्रेय|डेबिट|प्राप्त|स्थानांतरित)\s+(?:रुपये\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            # Marathi patterns
            r'रु\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'आयएनआर\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(?:भरले|श्रेय|डेबिट|प्राप्त|हस्तांतरित)\s+(?:रु\.?|₹)?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    details['amount'] = float(amount_str)
                except ValueError:
                    pass
                break
        
        # Transaction type - Including Hindi and Marathi
        text_lower = text.lower()
        if any(word in text_lower for word in ['debited', 'paid', 'payment', 'withdrawn', 
                                              'डेबिट', 'भुगतान', 'निकासी', 'काढले']):
            details['transaction_type'] = 'Debit'
        elif any(word in text_lower for word in ['credited', 'received', 'deposit', 'refund',
                                                'श्रेय', 'प्राप्त', 'जमा', 'परतावा']):
            details['transaction_type'] = 'Credit'
        elif any(word in text_lower for word in ['transferred', 'transfer', 'sent',
                                                'स्थानांतरित', 'पाठविले', 'हस्तांतरण']):
            details['transaction_type'] = 'Transfer'
        
        # UPI ID - Including Hindi and Marathi
        upi_match = re.search(r'(\d{10})@[\w\.]+', text)
        if upi_match:
            details['upi_id'] = upi_match.group(0)
        
        # Account number (masked) - Including Hindi and Marathi
        acc_match = re.search(r'(?:account|a/c|ac|खाता|खाते)\s*(?:no\.?|number|संख्या|क्रमांक)?\s*[:\s]*([X\*]{2,}\d{4})', text, re.IGNORECASE)
        if acc_match:
            details['account_number'] = acc_match.group(1)
        
        # Transaction ID / Reference - Including Hindi and Marathi
        txn_patterns = [
            # English patterns
            r'(?:txn|transaction|ref|reference|upi ref)\.?\s*(?:id|no|number)?[:\s]*(\w+)',
            r'(?:order|payment)\s*id[:\s]*(\w+)',
            # Hindi patterns
            r'(?:टीएक्सएन|लेनदेन|संदर्भ|यूपीआई संदर्भ)\.?\s*(?:आईडी|नंबर)?[:\s]*(\w+)',
            r'(?:आदेश|भुगतान)\s*आईडी[:\s]*(\w+)',
            # Marathi patterns
            r'(?:टीएक्सएन|लेनदेन|संदर्भ|यूपीआई संदर्भ)\.?\s*(?:आयडी|क्रमांक)?[:\s]*(\w+)',
            r'(?:ऑर्डर|देयक)\s*आयडी[:\s]*(\w+)'
        ]
        
        for pattern in txn_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                details['transaction_id'] = match.group(1)
                break
        
        # Recipient name (basic extraction) - Including Hindi and Marathi
        if 'to ' in text_lower or 'प्रति ' in text_lower or 'ला ' in text_lower:
            # English pattern
            recipient_match = re.search(r'to\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text)
            if recipient_match:
                details['recipient'] = recipient_match.group(1)
            else:
                # Hindi pattern
                hindi_recipient_match = re.search(r'प्रति\s+([\u0900-\u097F]+(?:\s+[\u0900-\u097F]+)*)', text)
                if hindi_recipient_match:
                    details['recipient'] = hindi_recipient_match.group(1)
                else:
                    # Marathi pattern
                    marathi_recipient_match = re.search(r'ला\s+([\u0900-\u097F]+(?:\s+[\u0900-\u097F]+)*)', text)
                    if marathi_recipient_match:
                        details['recipient'] = marathi_recipient_match.group(1)
        
        return details
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for model"""
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def predict_fraud(self, text: str) -> Dict[str, Any]:
        """Predict if message is fraudulent"""
        if not text or text == "No text detected in image":
            return {
                'verdict': 'error',
                'confidence': 0.0,
                'probabilities': {},
                'reasoning': 'No text found in the image'
            }
        
        # Preprocess
        processed_text = self.preprocess_text(text)
        
        # Vectorize
        if self.vectorizer is None:
            raise ValueError("Vectorizer not loaded")
        text_vectorized = self.vectorizer.transform([processed_text])
        
        # Predict
        if self.model is None:
            raise ValueError("Model not loaded")
        prediction = self.model.predict(text_vectorized)[0]
        probabilities = self.model.predict_proba(text_vectorized)[0]
        
        # Get label
        if self.label_encoder is None:
            raise ValueError("Label encoder not loaded")
        predicted_label = self.label_encoder.inverse_transform([prediction])[0]
        confidence = probabilities[prediction]
        
        # Get all class probabilities
        all_probs: Dict[str, float] = {}
        for idx, prob in enumerate(probabilities):
            label = self.label_encoder.inverse_transform([idx])[0]
            all_probs[label] = float(prob)
        
        # Generate explanation
        explanation = self.generate_explanation(predicted_label, confidence, text)
        
        return {
            'verdict': predicted_label,
            'confidence': float(confidence),
            'probabilities': all_probs,
            'reasoning': explanation
        }
    
    def generate_explanation(self, label: str, confidence: float, text: str) -> str:
        """Generate human-readable explanation - Including Hindi and Marathi context"""
        explanations = {
            'legitimate': "✅ This appears to be a legitimate transaction message. It contains standard banking/payment information without suspicious elements.",
            'phishing': "⚠️ DANGER: This is a phishing attempt! It tries to lure you to click malicious links or provide sensitive information. Never click unknown links.",
            'otp_request': "⚠️ FRAUD ALERT: This message requests your OTP, PIN, or CVV. Banks NEVER ask for these details. Do not share any codes!",
            'fake_kyc': "⚠️ SCAM: This is a fake KYC update message. Banks don't ask for KYC through SMS/messages with suspicious links. Verify through official channels.",
            'lottery_scam': "⚠️ SCAM: This is a lottery/prize scam. You cannot win a lottery you never entered. Ignore and delete this message.",
            'blocking_threat': "⚠️ THREAT SCAM: This uses fear tactics by threatening account blocking. Banks provide proper notice through official channels, not threats.",
            'delivery_scam': "⚠️ SCAM: This is a fake delivery charge message. Verify any delivery notifications through official courier websites or apps.",
            'tax_scam': "⚠️ SCAM: This is a fake tax refund message. Income tax department communicates through official portals, not SMS/messages with links."
        }
        
        # Hindi explanations
        hindi_explanations = {
            'legitimate': "✅ यह एक वैध लेन-देन संदेश प्रतीत होता है। इसमें मानक बैंकिंग/भुगतान जानकारी है बिना किसी संदिग्ध तत्व के।",
            'phishing': "⚠️ खतरा: यह एक फ़िशिंग प्रयास है! यह आपको दुर्भावनापूर्ण लिंक पर क्लिक करने या संवेदनशील जानकारी प्रदान करने के लिए लुभाता है। कभी अज्ञात लिंक पर क्लिक न करें।",
            'otp_request': "⚠️ धोखाधड़ी चेतावनी: यह संदेश आपके OTP, पिन, या CVV का अनुरोध करता है। बैंक कभी भी इन विवरणों के लिए नहीं पूछते हैं। कोई भी कोड साझा न करें!",
            'fake_kyc': "⚠️ घोटाला: यह एक नकली KYC अपडेट संदेश है। बैंक संदिग्ध लिंक के साथ एसएमएस/संदेश के माध्यम से KYC के लिए नहीं पूछते हैं। आधिकारिक चैनलों के माध्यम से सत्यापित करें।",
            'lottery_scam': "⚠️ घोटाला: यह एक लॉटरी/पुरस्कार घोटाला है। आप जिस लॉटरी में प्रवेश नहीं करते हैं, उसे नहीं जीत सकते हैं। इस संदेश को नजरअंदाज करें और हटा दें।",
            'blocking_threat': "⚠️ धमकी घोटाला: यह खतरा के तरीकों का उपयोग करके खाता अवरुद्ध करने की धमकी देता है। बैंक आधिकारिक चैनलों के माध्यम से सही नोटिस प्रदान करते हैं, धमकियों के माध्यम से नहीं।",
            'delivery_scam': "⚠️ घोटाला: यह एक नकली डिलीवरी शुल्क संदेश है। किसी भी डिलीवरी सूचना को आधिकारिक कूरियर वेबसाइटों या ऐप्स के माध्यम से सत्यापित करें।",
            'tax_scam': "⚠️ घोटाला: यह एक नकली कर वापसी संदेश है। आयकर विभाग आधिकारिक पोर्टल के माध्यम से संवाद करता है, लिंक के साथ एसएमएस/संदेश के माध्यम से नहीं।"
        }
        
        # Marathi explanations
        marathi_explanations = {
            'legitimate': "✅ हा एक वैध व्यवहार संदेश आहे. त्यात प्रमाणिक बँकिंग/देयक माहिती आहे विना कोणत्याही संशयास्पद घटकांच्या.",
            'phishing': "⚠️ धोका: हा एक फिशिंग प्रयत्न आहे! तो तुम्हाला दुर्भावनापूर्ण दुव्यांवर क्लिक करण्यास किंवा संवेदनशील माहिती प्रदान करण्यास लुभवतो. कधीही अज्ञात दुव्यांवर क्लिक करू नका.",
            'otp_request': "⚠️ फ्रॉड चेतावणी: या संदेशामध्ये तुमचा OTP, पिन किंवा CVV विचारला जात आहे. बँका कधीही या तपशीलांसाठी विचारत नाहीत. कोणतेही कोड शेअर करू नका!",
            'fake_kyc': "⚠️ खोटा: हा एक खोटा KYC अद्यतन संदेश आहे. बँका संशयास्पद दुव्यांसह SMS/संदेशांद्वारे KYC साठी विचारत नाहीत. अधिकृत माध्यमांद्वारे सत्यापित करा.",
            'lottery_scam': "⚠️ खोटा: हा एक लॉटरी/बक्षीस खोटा आहे. तुम्ही ज्या लॉटरीमध्ये प्रवेश केलेला नाही, ती तुम्ही जिंकू शकत नाही. हा संदेश दुर्लक्ष करा आणि हटवा.",
            'blocking_threat': "⚠️ धमकी खोटा: हा खतरा वापरून खाते अवरोधित करण्याची धमकी देतो. बँका अधिकृत माध्यमांद्वारे योग्य सूचना प्रदान करतात, धमक्यांद्वारे नाही.",
            'delivery_scam': "⚠️ खोटा: हा एक खोटा डिलिव्हरी शुल्क संदेश आहे. कोणत्याही डिलिव्हरी सूचनेची अधिकृत करिअर वेबसाइट्स किंवा अॅप्सद्वारे तपासणी करा.",
            'tax_scam': "⚠️ खोटा: हा एक खोटा कर परतावा संदेश आहे. उत्पन्नकर विभाग अधिकृत पोर्टलद्वारे संवाद साधतो, दुव्यांसह SMS/संदेशांद्वारे नाही."
        }
        
        # Check if text contains Hindi or Marathi characters and provide appropriate explanation
        if any('\u0900' <= char <= '\u097F' for char in text):  # Hindi/Marathi characters
            # Simple heuristic: if text contains more Devanagari characters, assume it's Hindi or Marathi
            devanagari_chars = sum(1 for char in text if '\u0900' <= char <= '\u097F')
            total_chars = len(text)
            if devanagari_chars / total_chars > 0.1:  # If more than 10% Devanagari chars
                if any(word in text for word in ['आपले', 'आम्ही', 'कृपया', 'आहे']):  # Marathi words
                    base_explanation = marathi_explanations.get(label, marathi_explanations.get('legitimate', "संदेश प्रकार निर्धारित करण्यात अक्षम"))
                else:  # Assume Hindi
                    base_explanation = hindi_explanations.get(label, hindi_explanations.get('legitimate', "संदेश प्रकार निर्धारित करण्यात अक्षम"))
            else:
                base_explanation = explanations.get(label, "Unable to determine message type")
        else:
            base_explanation = explanations.get(label, "Unable to determine message type")
        
        # Add confidence level
        if confidence > 0.9:
            confidence_text = f"Very high confidence ({confidence*100:.1f}%)"
        elif confidence > 0.75:
            confidence_text = f"High confidence ({confidence*100:.1f}%)"
        elif confidence > 0.6:
            confidence_text = f"Moderate confidence ({confidence*100:.1f}%)"
        else:
            confidence_text = f"Low confidence ({confidence*100:.1f}%) - Please verify manually"
        
        # Add red flags if fraud detected
        if label != 'legitimate':
            red_flags = []
            text_lower = text.lower()
            
            if any(word in text_lower for word in ['click', 'link', 'bit.ly', 'tiny.url', 'www.', 'क्लिक', 'दुवा', 'लिंक']):
                red_flags.append("Contains suspicious links")
            
            if any(word in text_lower for word in ['otp', 'pin', 'cvv', 'password', 'ओटीपी', 'पिन', 'पासवर्ड']):
                red_flags.append("Asks for sensitive credentials")
            
            if any(word in text_lower for word in ['urgent', 'immediately', 'within', 'hours', 'blocked', 'तत्काल', 'अवरुद्ध']):
                red_flags.append("Uses urgency tactics")
            
            if any(word in text_lower for word in ['won', 'winner', 'prize', 'lottery', 'congratulations', 'lakh', 'जिंकले', 'विजेता', 'पुरस्कार', 'लॉटरी', 'अभिनंदन', 'लाख']):
                red_flags.append("Promises unrealistic rewards")
            
            if any(word in text_lower for word in ['verify', 'update', 'confirm', 'validate', 'सत्यापित', 'अद्ययावत', 'पुष्टी']):
                red_flags.append("Requests verification/update")
            
            if red_flags:
                red_flag_text = "\n\n🚩 Red Flags Detected:\n" + "\n".join([f"  • {flag}" for flag in red_flags])
            else:
                red_flag_text = ""
            
            return f"{base_explanation}\n\n{confidence_text}{red_flag_text}"
        
        return f"{base_explanation}\n\n{confidence_text}"

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text"""
        # More comprehensive URL pattern
        url_pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:/[^\s]*)?'
        urls = re.findall(url_pattern, text)
        
        # Also find URLs without protocol that look like domains
        domain_pattern = r'(?<!\w)(?:www\.)?[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z]{2,})+(?:/[^\s]*)?'
        domains = re.findall(domain_pattern, text)
        
        # Combine and deduplicate
        all_urls = list(set(urls + domains))
        return [url for url in all_urls if len(url) > 5]  # Filter out very short strings

    def analyze_links(self, urls: List[str]) -> Optional[Dict[str, Any]]:
        """Analyze URLs for potential fraud/safety issues"""
        if not urls:
            return None
        
        link_results: List[Dict[str, Any]] = []
        
        for url in urls:
            # Ensure URL has protocol
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            analysis: Dict[str, Any] = {
                "url": url,
                "is_suspicious": False,
                "issues": [],
                "safety_score": 1.0
            }
            
            # Parse URL
            try:
                parsed = urlparse(url)
                domain = parsed.netloc.lower()
                
                # Skip if domain is empty
                if not domain:
                    continue
                
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
                    # Check for banking-related keywords in suspicious domains - Including Hindi and Marathi
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
        
        # If no valid links were found, return None
        if not link_results:
            return None
        
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

    def analyze_message(self, image: Image.Image) -> Dict[str, Any]:
        """Complete analysis pipeline: OCR -> Extract -> Predict"""
        # Extract text
        extracted_text = self.extract_text(image)
        
        # Extract URLs from text
        urls = self.extract_urls(extracted_text)
        link_analysis = self.analyze_links(urls) if urls else None
        
        # Extract transaction details
        transaction_details = self.extract_transaction_details(extracted_text)
        
        # Predict fraud
        prediction_result = self.predict_fraud(extracted_text)
        
        # Add link analysis to fraud result ONLY if there are actual links
        if link_analysis and link_analysis["overall"]["total_links"] > 0:
            prediction_result["link_analysis"] = link_analysis
        
        # Make sure these lines are indented with the SAME spaces/tabs
        print("=" * 50)
        print("EXTRACTED TEXT:", extracted_text)
        print("TRANSACTION DETAILS:", transaction_details)
        print("PREDICTION RESULT:", prediction_result)
        print("=" * 50)
        
        return {
            'extracted_text': extracted_text,
            'transaction_details': transaction_details,
            'fraud_analysis': prediction_result
        }

def format_amount(amount: Optional[float]) -> str:
    """Format amount in Indian currency style"""
    if amount is None:
        return "Not detected"
    
    amount_str = f"{amount:,.2f}"
    # Indian number format (lakhs, crores)
    if amount >= 10000000:  # 1 crore
        return f"₹{amount/10000000:.2f} Cr"
    elif amount >= 100000:  # 1 lakh
        return f"₹{amount/100000:.2f} L"
    else:
        return f"₹{amount_str}"

if __name__ == "__main__":
    print("Pipeline module loaded successfully")
    print("Import this module in app.py to use the fraud detection pipeline")
"""
Transaction Fraud Detection Model Training
Trains a Random Forest classifier on transaction messages
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib
import os
import re
from typing import Tuple, Any, Optional
from scipy.sparse import csr_matrix

# Create necessary directories
os.makedirs('models', exist_ok=True)
os.makedirs('data', exist_ok=True)

def generate_training_data() -> pd.DataFrame:
    """Generate comprehensive training dataset for fraud detection - Including Hindi and Marathi"""
    
    # Legitimate transactions (English)
    legitimate_en = [
        "Rs.500 debited from account XX1234 on 15-Jan-24. UPI/GPAY/9876543210. Available balance: Rs.5000",
        "Rs.1000 credited to account XX5678 on 20-Jan-24. NEFT from JOHN DOE. Balance: Rs.15000",
        "You have successfully paid Rs.250 to ABC Store via UPI. Txn ID: 402345678901",
        "Rs.2500 transferred to 9876543210 via PhonePe. UPI Ref: 401234567890",
        "Your account XX9012 has been credited with Rs.5000 on 22-Jan-24. IMPS from JANE SMITH",
        "Payment of Rs.799 to Amazon Pay successful. Order ID: 123-4567890-1234567",
        "Rs.150 debited for Swiggy order. Txn successful. Balance: Rs.8500",
        "Salary credited: Rs.45000 in account XX3456 on 01-Feb-24. From: XYZ COMPANY LTD",
        "Rs.300 paid to Uber via UPI. Trip ID: AB1234CD5678. Payment successful",
        "Received Rs.2000 from 8765432109. UPI Ref: 403456789012. Balance: Rs.12000",
        "Rs.1200 debited for electricity bill payment. Transaction successful",
        "Cashback of Rs.50 credited to your Paytm wallet. Total balance: Rs.550",
        "Rs.5000 withdrawn from ATM at MG Road on 18-Jan-24. Available balance: Rs.20000",
        "Rs.899 paid to Zomato. Order #987654. Payment via UPI successful",
        "Rent payment of Rs.15000 to landlord successful via NEFT. Ref: N12345678",
        "Rs.3500 refund credited for cancelled order. Amazon Refund ID: RF123456",
        "Insurance premium of Rs.2400 paid successfully. Policy: LIC/12345678",
        "Rs.750 debited for mobile recharge. Number: 9876543210. Balance: Rs.9250",
        "Credit card bill of Rs.8500 paid. Card XX1234. Due cleared",
        "Rs.200 donated to charity via UPI. Txn ID: 404567890123. Thank you!",
    ]
    
    # Legitimate transactions (Hindi)
    legitimate_hi = [
        "15-जन-24 को खाता XX1234 से 500 रुपये डेबिट किए गए। UPI/GPAY/9876543210। उपलब्ध शेष: 5000 रुपये",
        "20-जन-24 को खाता XX5678 में 1000 रुपये जमा किए गए। JOHN DOE से NEFT। शेष: 15000 रुपये",
        "आपने सफलतापूर्वक ABC स्टोर को UPI के माध्यम से 250 रुपये का भुगतान किया है। लेन-देन आईडी: 402345678901",
        "PhonePe के माध्यम से 9876543210 को 2500 रुपये हस्तांतरित किए गए। UPI संदर्भ: 401234567890",
        "22-जन-24 को आपके खाता XX9012 में 5000 रुपये जमा किए गए हैं। JANE SMITH से IMPS",
        "Amazon Pay को 799 रुपये का भुगतान सफल हुआ। ऑर्डर आईडी: 123-4567890-1234567",
        "Swiggy ऑर्डर के लिए 150 रुपये डेबिट किए गए। लेन-देन सफल। शेष: 8500 रुपये",
        "01-फर-24 को खाता XX3456 में वेतन जमा: 45000 रुपये। XYZ COMPANY LTD से",
        "UPI के माध्यम से Uber को 300 रुपये का भुगतान किया गया। ट्रिप आईडी: AB1234CD5678। भुगतान सफल",
        "8765432109 से 2000 रुपये प्राप्त हुए। UPI संदर्भ: 403456789012। शेष: 12000 रुपये",
        "बिजली बिल भुगतान के लिए 1200 रुपये डेबिट किए गए। लेन-देन सफल",
        "आपके Paytm वॉलेट में 50 रुपये कैशबैक जमा किए गए। कुल शेष: 550 रुपये",
        "18-जन-24 को MG रोड से ATM से 5000 रुपये निकाले गए। उपलब्ध शेष: 20000 रुपये",
        "Zomato को 899 रुपये का भुगतान किया गया। ऑर्डर #987654। UPI के माध्यम से भुगतान सफल",
        "NEFT के माध्यम से किरायेदार को 15000 रुपये का भुगतान सफल। संदर्भ: N12345678",
        "रद्द ऑर्डर के लिए 3500 रुपये का रिफंड जमा किया गया। Amazon रिफंड आईडी: RF123456",
        "बीमा प्रीमियम 2400 रुपये सफलतापूर्वक भुगतान किया गया। नीति: LIC/12345678",
        "मोबाइल रिचार्ज के लिए 750 रुपये डेबिट किए गए। नंबर: 9876543210। शेष: 9250 रुपये",
        "क्रेडिट कार्ड बिल 8500 रुपये का भुगतान किया गया। कार्ड XX1234। बकाया समाप्त",
        "UPI के माध्यम से दान 200 रुपये का भुगतान किया गया। लेन-देन आईडी: 404567890123। धन्यवाद!",
    ]
    
    # Legitimate transactions (Marathi)
    legitimate_mr = [
        "15-जानेवारी-24 रोजी खाते XX1234 मधून 500 रुपये डेबिट केले. UPI/GPAY/9876543210. उपलब्ध शिल्लक: 5000 रुपये",
        "20-जानेवारी-24 रोजी खाते XX5678 मध्ये 1000 रुपये जमा केले. JOHN DOE कडून NEFT. शिल्लक: 15000 रुपये",
        "तुम्ही ABC Store ला UPI मार्फत 250 रुपये यशस्वीरित्या भरले आहेत. व्यवहार ID: 402345678901",
        "PhonePe मार्फत 9876543210 ला 2500 रुपये हस्तांतरित केले. UPI संदर्भ: 401234567890",
        "22-जानेवारी-24 रोजी तुमच्या खात्यात XX9012 मध्ये 5000 रुपये जमा केले आहेत. JANE SMITH कडून IMPS",
        "Amazon Pay ला 799 रुपये चे भुगतान यशस्वी. ऑर्डर ID: 123-4567890-1234567",
        "Swiggy ऑर्डरसाठी 150 रुपये डेबिट केले. व्यवहार यशस्वी. शिल्लक: 8500 रुपये",
        "01-फेब्रुवारी-24 रोजी खाते XX3456 मध्ये पगार जमा: 45000 रुपये. XYZ COMPANY LTD कडून",
        "UPI मार्फत Uber ला 300 रुपये भरले. ट्रिप ID: AB1234CD5678. भुगतान यशस्वी",
        "8765432109 कडून 2000 रुपये प्राप्त झाले. UPI संदर्भ: 403456789012. शिल्लक: 12000 रुपये",
        "वीज बिल भुगतानासाठी 1200 रुपये डेबिट केले. व्यवहार यशस्वी",
        "तुमच्या Paytm वॉलेटमध्ये 50 रुपये कॅशबॅक जमा केले. एकूण शिल्लक: 550 रुपये",
        "18-जानेवारी-24 रोजी MG Road वरील ATM मधून 5000 रुपये काढले. उपलब्ध शिल्लक: 20000 रुपये",
        "Zomato ला 899 रुपये भरले. ऑर्डर #987654. UPI मार्फत भुगतान यशस्वी",
        "NEFT मार्फत किरायेदाराला 15000 रुपये चे भुगतान यशस्वी. संदर्भ: N12345678",
        "रद्द ऑर्डरसाठी 3500 रुपये चा परतावा जमा केला. Amazon परतावा ID: RF123456",
        "विमा प्रीमियम 2400 रुपये यशस्वीरित्या भरला. धोरण: LIC/12345678",
        "मोबाईल रिचार्जसाठी 750 रुपये डेबिट केले. नंबर: 9876543210. शिल्लक: 9250 रुपये",
        "क्रेडिट कार्ड बिल 8500 रुपये चे भुगतान केले. कार्ड XX1234. बाकी निकळली",
        "UPI मार्फत दानासाठी 200 रुपये भरले. व्यवहार ID: 404567890123. धन्यवाद!",
    ]
    
    # Phishing attempts (English)
    phishing_en = [
        "URGENT: Your bank account will be blocked. Click here immediately: bit.ly/fake123 to verify",
        "Congratulations! You've won Rs.5 Lakhs. Claim now at www.fakesite.com/claim with your details",
        "Your KYC is pending. Update now at www.updatekyc-fake.com or account will be suspended",
        "Dear customer, unusual activity detected. Verify your account: tiny.url/scam123",
        "Action Required! Your account has been compromised. Click to secure: fakbank.com/secure",
        "Limited time offer! Get Rs.10000 cashback. Register at www.freemoney.fake.com",
        "Your PAN card is not linked. Click here to link immediately or face penalty",
        "Confirm your mobile number by clicking this link: bit.ly/confirm-fake or service will stop",
        "You have unclaimed tax refund of Rs.25000. Apply at www.taxrefund-fake.in",
        "Dear user, your account shows suspicious activity. Verify at www.verify-account.fake",
        "ALERT: Someone is trying to access your account. Secure it now: securebank.fake",
        "Your credit card is expired. Update details at www.updatecard.fake.com immediately",
        "Claim your insurance bonus of Rs.50000 at www.insurance-bonus.fake within 24 hours",
        "Your electricity bill payment failed. Retry at www.billpay.fake.com with card details",
        "Government subsidy of Rs.15000 available for you. Apply: www.subsidy-fake.gov.in",
    ]
    
    # Phishing attempts (Hindi)
    phishing_hi = [
        "तत्काल: आपका बैंक खाता अवरुद्ध हो जाएगा। तुरंत यहां क्लिक करें: bit.ly/fake123 सत्यापित करने के लिए",
        "बधाई हो! आपने 5 लाख रुपये जीते हैं। अब यहां दावा करें www.fakesite.com/claim अपने विवरण के साथ",
        "आपका KYC लंबित है। अब यहां अपडेट करें www.updatekyc-fake.com या खाता निलंबित हो जाएगा",
        "प्रिय ग्राहक, असामान्य गतिविधि का पता चला। अपने खाते को सत्यापित करें: tiny.url/scam123",
        "कार्रवाई आवश्यक! आपका खाता संकट में है। सुरक्षित करने के लिए क्लिक करें: fakbank.com/secure",
        "सीमित समय की पेशकश! 10000 रुपये कैशबैक प्राप्त करें। यहां पंजीकरण करें www.freemoney.fake.com",
        "आपका PAN कार्ड लिंक नहीं है। तुरंत यहां क्लिक करें लिंक करने के लिए या जुर्माना का सामना करें",
        "इस लिंक पर क्लिक करके अपना मोबाइल नंबर पुष्टि करें: bit.ly/confirm-fake या सेवा बंद हो जाएगी",
        "आपके पास 25000 रुपये का नहीं मिला कर रिफंड है। यहां आवेदन करें www.taxrefund-fake.in",
        "प्रिय उपयोगकर्ता, आपके खाते में संदिग्ध गतिविधि दिखाई दे रही है। यहां सत्यापित करें www.verify-account.fake",
        "चेतावनी: कोई आपके खाते को एक्सेस करने का प्रयास कर रहा है। अब इसे सुरक्षित करें: securebank.fake",
        "आपका क्रेडिट कार्ड समाप्त हो गया है। विवरण अपडेट करें www.updatecard.fake.com तुरंत",
        "24 घंटों के भीतर अपना 50000 रुपये का बीमा बोनस दावा करें www.insurance-bonus.fake",
        "आपका बिजली बिल भुगतान विफल हुआ। फिर से प्रयास करें www.billpay.fake.com कार्ड विवरण के साथ",
        "आपके लिए 15000 रुपये की सरकारी सब्सिडी उपलब्ध है। आवेदन करें: www.subsidy-fake.gov.in",
    ]
    
    # Phishing attempts (Marathi)
    phishing_mr = [
        "तातडीने: तुमचे बँक खाते अवरोधित केले जाईल. लगेच इथे क्लिक करा: bit.ly/fake123 सत्यापित करण्यासाठी",
        "अभिनंदन! तुम्ही 5 लाख रुपये जिंकले आहेत. आता इथे दावा करा www.fakesite.com/claim तुमच्या तपशीलांसह",
        "तुमचा KYC बाकी आहे. आता इथे अद्ययावत करा www.updatekyc-fake.com किंवा खाते निलंबित केले जाईल",
        "प्रिय ग्राहक, असामान्य क्रियाकलाप आढळला. तुमचे खाते सत्यापित करा: tiny.url/scam123",
        "कृती आवश्यक! तुमचे खाते संकटात आहे. सुरक्षित करण्यासाठी क्लिक करा: fakbank.com/secure",
        "मर्यादित कालावधी ऑफर! 10000 रुपये कॅशबॅक मिळवा. येथे नोंदणी करा www.freemoney.fake.com",
        "तुमचे PAN कार्ड लिंक केलेले नाही. लगेच इथे क्लिक करा लिंक करण्यासाठी किंवा दंडाचा सामना करा",
        "हा दुवा क्लिक करून तुमचा मोबाईल नंबर पुष्टी करा: bit.ly/confirm-fake किंवा सेवा बंद होईल",
        "तुमच्याकडे 25000 रुपये चा न मिळालेला कर परतावा आहे. येथे अर्ज करा www.taxrefund-fake.in",
        "प्रिय वापरकर्ता, तुमच्या खात्यात संशयास्पद क्रियाकलाप दिसत आहे. येथे सत्यापित करा www.verify-account.fake",
        "चेतावणी: कोणी तुमच्या खात्यात प्रवेश करण्याचा प्रयत्न करत आहे. आता ते सुरक्षित करा: securebank.fake",
        "तुमचे क्रेडिट कार्ड संपले आहे. तपशील अद्ययावत करा www.updatecard.fake.com लगेच",
        "24 तासांच्या आत तुमचा 50000 रुपये चा विमा बोनस दावा करा www.insurance-bonus.fake",
        "तुमचा वीज बिल भुगतान अयशस्वी झाले. पुन्हा प्रयत्न करा www.billpay.fake.com कार्ड तपशीलांसह",
        "तुमच्यासाठी 15000 रुपये ची शासकीय सब्सिडी उपलब्ध आहे. अर्ज करा: www.subsidy-fake.gov.in",
    ]
    
    # OTP/PIN/CVV requests (English)
    otp_requests_en = [
        "Dear customer, share OTP 123456 to complete your transaction. Valid for 10 minutes",
        "Your verification code is 987654. Please share this to verify your identity",
        "Enter your ATM PIN and OTP to receive cashback of Rs.500 in your account",
        "To unblock your account, reply with your CVV number and card expiry date",
        "Confirm transaction by sharing 6-digit OTP sent to your mobile: XXXXXX",
        "Update KYC by providing your card CVV and OTP. Call 1800-XXX-FAKE",
        "Share your internet banking password and OTP to activate new features",
        "Verification needed: Send your ATM PIN and OTP to 9999988888",
        "Your account verification requires CVV, PIN and OTP. Share immediately",
        "To reverse unauthorized transaction, provide your debit card PIN and OTP",
        "Customer care calling: Please share OTP to help you with refund process",
        "Confirm your identity by replying with OTP, CVV and card number",
        "Account locked! Share OTP and PIN to unlock within 1 hour",
        "Prize delivery requires verification. Send OTP and CVV to claim",
        "Update Aadhaar link by providing OTP, PIN and CVV via SMS",
    ]
    
    # OTP/PIN/CVV requests (Hindi)
    otp_requests_hi = [
        "प्रिय ग्राहक, अपना लेन-देन पूरा करने के लिए OTP 123456 साझा करें। 10 मिनट के लिए मान्य",
        "आपका सत्यापन कोड 987654 है। कृपया अपनी पहचान सत्यापित करने के लिए इसे साझा करें",
        "अपने खाते में 500 रुपये कैशबैक प्राप्त करने के लिए अपना ATM पिन और OTP दर्ज करें",
        "अपने खाते को अनब्लॉक करने के लिए, अपना CVV नंबर और कार्ड समाप्ति तिथि के साथ उत्तर दें",
        "मोबाइल पर भेजे गए 6-अंकीय OTP को साझा करके लेन-देन की पुष्टि करें: XXXXXX",
        "अपने कार्ड CVV और OTP प्रदान करके KYC अपडेट करें। 1800-XXX-FAKE कॉल करें",
        "नए सुविधाओं को सक्रिय करने के लिए अपना इंटरनेट बैंकिंग पासवर्ड और OTP साझा करें",
        "सत्यापन आवश्यक: अपना ATM पिन और OTP 9999988888 पर भेजें",
        "आपके खाते के सत्यापन के लिए CVV, पिन और OTP की आवश्यकता है। तुरंत साझा करें",
        "अनधिकृत लेन-देन को उलटने के लिए, अपना डेबिट कार्ड पिन और OTP प्रदान करें",
        "ग्राहक सेवा कॉल कर रही है: कृपया रिफंड प्रक्रिया में मदद के लिए OTP साझा करें",
        "OTP, CVV और कार्ड नंबर के साथ उत्तर देकर अपनी पहचान की पुष्टि करें",
        "खाता लॉक हो गया है! 1 घंटे के भीतर अनलॉक करने के लिए OTP और पिन साझा करें",
        "पुरस्कार डिलीवरी के लिए सत्यापन की आवश्यकता है। दावा करने के लिए OTP और CVV भेजें",
        "SMS के माध्यम से OTP, पिन और CVV प्रदान करके आधार लिंक अपडेट करें",
    ]
    
    # OTP/PIN/CVV requests (Marathi)
    otp_requests_mr = [
        "प्रिय ग्राहक, तुमचे व्यवहार पूर्ण करण्यासाठी OTP 123456 सामायिक करा. 10 मिनिटांसाठी वैध",
        "तुमचा सत्यापन कोड 987654 आहे. कृपया तुमची ओळख सत्यापित करण्यासाठी हे सामायिक करा",
        "तुमच्या खात्यात 500 रुपये कॅशबॅक मिळवण्यासाठी तुमचा ATM पिन आणि OTP प्रविष्ट करा",
        "तुमचे खाते अनब्लॉक करण्यासाठी, तुमचा CVV क्रमांक आणि कार्ड समाप्ती तारीख द्या",
        "तुमच्या मोबाईलवर पाठविलेला 6-अंकी OTP सामायिक करून व्यवहार पुष्टी करा: XXXXXX",
        "तुमचा कार्ड CVV आणि OTP प्रदान करून KYC अद्ययावत करा. 1800-XXX-FAKE ला कॉल करा",
        "नवीन वैशिष्ट्ये सक्रिय करण्यासाठी तुमचा इंटरनेट बँकिंग पासवर्ड आणि OTP सामायिक करा",
        "सत्यापन आवश्यक: तुमचा ATM पिन आणि OTP 9999988888 वर पाठवा",
        "तुमच्या खात्याच्या सत्यापनासाठी CVV, पिन आणि OTP आवश्यक आहे. लगेच सामायिक करा",
        "अनधिकृत व्यवहार उलटवण्यासाठी, तुमचा डेबिट कार्ड पिन आणि OTP प्रदान करा",
        "ग्राहकसेवा कॉल करत आहे: कृपया परतावा प्रक्रियेत मदत करण्यासाठी OTP सामायिक करा",
        "OTP, CVV आणि कार्ड क्रमांक द्या आणि तुमची ओळख पुष्टी करा",
        "खाते लॉक केले गेले आहे! 1 तासाच्या आत अनलॉक करण्यासाठी OTP आणि पिन सामायिक करा",
        "बक्षीस वितरणासाठी सत्यापन आवश्यक आहे. दावा करण्यासाठी OTP आणि CVV पाठवा",
        "SMS मार्फत OTP, पिन आणि CVV प्रदान करून आधार दुवा अद्ययावत करा",
    ]
    
    # Fake KYC updates (English)
    fake_kyc_en = [
        "Your KYC verification is incomplete. Update at www.kyc-update.fake within 24 hours",
        "Dear customer, KYC documents expired. Re-submit PAN, Aadhaar at www.ekyc.fake",
        "Action required: Complete video KYC at www.vkyc-fake.com or account will be frozen",
        "Your bank KYC is not updated as per RBI guidelines. Update now: www.rbikyc.fake",
        "E-KYC mandatory from tomorrow. Submit documents at www.mandate-kyc.fake",
        "Account suspension in 48 hours due to pending KYC. Update at www.urgent-kyc.fake",
        "New KYC norms: Upload selfie with PAN and Aadhaar at www.newkyc.fake",
        "Your account is temporarily blocked. Complete KYC at www.unblock-kyc.fake",
        "RBI regulation: Update KYC or face Rs.10000 penalty. Visit www.penalty-kyc.fake",
        "Dear valued customer, KYC update pending. Click www.customer-kyc.fake to continue services",
    ]
    
    # Fake KYC updates (Hindi)
    fake_kyc_hi = [
        "आपका KYC सत्यापन अपूर्ण है। 24 घंटों के भीतर यहां अपडेट करें www.kyc-update.fake",
        "प्रिय ग्राहक, KYC दस्तावेज़ समाप्त हो गए हैं। PAN, आधार को पुनः प्रस्तुत करें www.ekyc.fake",
        "कार्रवाई आवश्यक: www.vkyc-fake.com पर वीडियो KYC पूरा करें या खाता फ्रीज हो जाएगा",
        "RBI दिशानिर्देशों के अनुसार आपका बैंक KYC अपडेट नहीं है। अब अपडेट करें: www.rbikyc.fake",
        "कल से E-KYC अनिवार्य। दस्तावेज़ प्रस्तुत करें www.mandate-kyc.fake",
        "लंबित KYC के कारण 48 घंटों में खाता निलंबन। यहां अपडेट करें www.urgent-kyc.fake",
        "नए KYC नियम: www.newkyc.fake पर PAN और आधार के साथ सेल्फी अपलोड करें",
        "आपका खाता अस्थायी रूप से अवरुद्ध है। www.unblock-kyc.fake पर KYC पूरा करें",
        "RBI नियम: KYC अपडेट करें या 10000 रुपये का जुर्माना सामना करें। www.penalty-kyc.fake पर जाएं",
        "प्रिय मूल्यवान ग्राहक, KYC अपडेट लंबित है। सेवाएं जारी रखने के लिए www.customer-kyc.fake पर क्लिक करें",
    ]
    
    # Fake KYC updates (Marathi)
    fake_kyc_mr = [
        "तुमचे KYC सत्यापन अपूर्ण आहे. 24 तासांच्या आत इथे अद्ययावत करा www.kyc-update.fake",
        "प्रिय ग्राहक, KYC दस्तऐवज संपले आहेत. PAN, आधार पुन्हा सादर करा www.ekyc.fake",
        "कृती आवश्यक: www.vkyc-fake.com वर व्हिडिओ KYC पूर्ण करा किंवा खाते फ्रीझ होईल",
        "RBI मार्गदर्शकतेनुसार तुमचे बँक KYC अद्ययावत नाही. आता अद्ययावत करा: www.rbikyc.fake",
        "उद्यापासून E-KYC अनिवार्य. दस्तऐवज सादर करा www.mandate-kyc.fake",
        "लंबित KYC मुळे 48 तासांत खाते निलंबन. इथे अद्ययावत करा www.urgent-kyc.fake",
        "नवीन KYC नियम: www.newkyc.fake वर PAN आणि आधारसह सेल्फी अपलोड करा",
        "तुमचे खाते तात्पुरते अवरोधित आहे. www.unblock-kyc.fake वर KYC पूर्ण करा",
        "RBI नियम: KYC अद्ययावत करा किंवा 10000 रुपये चा दंड सामना करा. www.penalty-kyc.fake ला भेट द्या",
        "प्रिय मौल्यवान ग्राहक, KYC अद्ययावत बाकी आहे. सेवा सुरू ठेवण्यासाठी www.customer-kyc.fake वर क्लिक करा",
    ]
    
    # Lottery/Prize scams (English)
    lottery_scams_en = [
        "Congratulations! You won Rs.25 Lakh in lucky draw. Claim at www.lottery-win.fake",
        "You are selected winner of iPhone 15 Pro! Pay Rs.500 delivery fee to claim",
        "LUCKY WINNER ALERT! Rs.10 Lakhs prize. Send Rs.2000 processing fee to claim",
        "You won Rs.5 Crore in KBC lottery! Contact immediately with your bank details",
        "Congratulations! Rs.50000 Amazon gift voucher won. Claim with card details",
        "You are our 1 millionth visitor! Claim Rs.1 Lakh reward at www.visitor-prize.fake",
        "Dear winner, you won luxury car! Pay Rs.5000 registration fee to claim",
        "Google anniversary winner! Rs.15 Lakh prize. Verify identity with OTP and CVV",
        "Lucky draw: You won Rs.7 Lakh. Transfer Rs.3000 tax to receive prize money",
        "Congratulations! WhatsApp lottery winner Rs.20 Lakh. Click www.whatsapp-lottery.fake",
    ]
    
    # Lottery/Prize scams (Hindi)
    lottery_scams_hi = [
        "बधाई हो! आपने लकी ड्रा में 25 लाख रुपये जीते हैं। www.lottery-win.fake पर दावा करें",
        "आप iPhone 15 Pro के चयनित विजेता हैं! दावा करने के लिए 500 रुपये की डिलीवरी फीस का भुगतान करें",
        "लकी विजेता चेतावनी! 10 लाख रुपये का पुरस्कार। दावा करने के लिए 2000 रुपये की प्रसंस्करण शुल्क भेजें",
        "आपने KBC लॉटरी में 5 करोड़ रुपये जीते! अपने बैंक विवरण के साथ तुरंत संपर्क करें",
        "बधाई हो! 50000 रुपये का अमेज़ॅन गिफ्ट वाउचर जीता। कार्ड विवरण के साथ दावा करें",
        "आप हमारे 1 मिलियनवां आगंतुक हैं! www.visitor-prize.fake पर 1 लाख रुपये का पुरस्कार दावा करें",
        "प्रिय विजेता, आपने लक्ज़री कार जीती है! दावा करने के लिए 5000 रुपये की पंजीकरण फीस का भुगतान करें",
        "गूगल वर्षगांठ विजेता! 15 लाख रुपये का पुरस्कार। OTP और CVV के साथ पहचान सत्यापित करें",
        "लकी ड्रा: आपने 7 लाख रुपये जीते हैं। पुरस्कार धन प्राप्त करने के लिए 3000 रुपये कर ट्रांसफर करें",
        "बधाई हो! व्हाट्सएप लॉटरी विजेता 20 लाख रुपये। www.whatsapp-lottery.fake पर क्लिक करें",
    ]
    
    # Lottery/Prize scams (Marathi)
    lottery_scams_mr = [
        "अभिनंदन! तुम्ही लकी ड्रॉ मध्ये 25 लाख रुपये जिंकले आहेत. www.lottery-win.fake वर दावा करा",
        "तुम्ही iPhone 15 Pro चे निवडलेले विजेते आहात! दावा करण्यासाठी 500 रुपये डिलिव्हरी फी भरा",
        "लकी विजेता चेतावणी! 10 लाख रुपये चा बक्षीस. दावा करण्यासाठी 2000 रुपये प्रक्रिया शुल्क पाठवा",
        "तुम्ही KBC लॉटरी मध्ये 5 कोटी रुपये जिंकले आहेत! तुमच्या बँक तपशीलांसह लगेच संपर्क साधा",
        "अभिनंदन! 50000 रुपये चा अमेझॉन भेट वाऊचर जिंकला. कार्ड तपशीलांसह दावा करा",
        "तुम्ही आमचे 1 मिलियनवा अतिथी आहात! www.visitor-prize.fake वर 1 लाख रुपये चा बक्षीस दावा करा",
        "प्रिय विजेता, तुम्ही लक्झरी कार जिंकली आहे! दावा करण्यासाठी 5000 रुपये नोंदणी शुल्क भरा",
        "गूगल वार्षिकोत्सव विजेता! 15 लाख रुपये चा बक्षीस. OTP आणि CVV सह ओळख पडताळा",
        "लकी ड्रॉ: तुम्ही 7 लाख रुपये जिंकले आहेत. बक्षीस रक्कम मिळवण्यासाठी 3000 रुपये कर हस्तांतरित करा",
        "अभिनंदन! व्हॉट्सॲप लॉटरी विजेता 20 लाख रुपये. www.whatsapp-lottery.fake वर क्लिक करा",
    ]
    
    # Account blocking threats (English)
    blocking_threats_en = [
        "URGENT: Your account will be blocked in 2 hours. Verify now: www.verify-urgent.fake",
        "Immediate action required! Account suspension in 24 hours. Update at www.save-account.fake",
        "Dear customer, non-compliance detected. Account blocked. Unblock: www.unblock-now.fake",
        "Your account activity is suspicious. Will be frozen tomorrow. Verify: www.freeze-stop.fake",
        "ALERT: Account will be permanently closed in 6 hours. Prevent: www.account-close.fake",
        "Unusual activity detected. Account locked for security. Unlock: www.security-unlock.fake",
        "Your bank account will be deactivated due to pending verification. Act now!",
        "Final warning! Account blockage in 1 hour. Immediate verification required",
        "Service discontinued due to policy violation. Restore at www.restore-service.fake",
        "Your account is marked for closure. Prevent by verifying at www.prevent-closure.fake",
    ]
    
    # Account blocking threats (Hindi)
    blocking_threats_hi = [
        "तत्काल: आपका खाता 2 घंटे में अवरुद्ध हो जाएगा। अब सत्यापित करें: www.verify-urgent.fake",
        "तुरंत कार्रवाई आवश्यक! 24 घंटों में खाता निलंबन। यहां अपडेट करें www.save-account.fake",
        "प्रिय ग्राहक, अनुपालन नहीं मिला। खाता अवरुद्ध। अनब्लॉक करें: www.unblock-now.fake",
        "आपके खाते की गतिविधि संदिग्ध है। कल फ्रीज हो जाएगा। सत्यापित करें: www.freeze-stop.fake",
        "चेतावनी: खाता 6 घंटों में स्थायी रूप से बंद हो जाएगा। रोकें: www.account-close.fake",
        "असामान्य गतिविधि का पता चला। सुरक्षा के लिए खाता लॉक हो गया है। अनलॉक करें: www.security-unlock.fake",
        "लंबित सत्यापन के कारण आपका बैंक खाता निष्क्रिय कर दिया जाएगा। अब कार्रवाई करें!",
        "अंतिम चेतावनी! 1 घंटे में खाता अवरोधन। तुरंत सत्यापन आवश्यक",
        "नीति उल्लंघन के कारण सेवा बंद कर दी गई है। www.restore-service.fake पर पुनर्स्थापित करें",
        "आपका खाता बंद होने के लिए चिह्नित है। www.prevent-closure.fake पर सत्यापित करके रोकें",
    ]
    
    # Account blocking threats (Marathi)
    blocking_threats_mr = [
        "तातडीने: तुमचे खाते 2 तासांत अवरोधित केले जाईल. आता सत्यापित करा: www.verify-urgent.fake",
        "लगेचच कृती आवश्यक! 24 तासांत खाते निलंबन. इथे अद्ययावत करा www.save-account.fake",
        "प्रिय ग्राहक, अनुपालन आढळले नाही. खाते अवरोधित. अनब्लॉक करा: www.unblock-now.fake",
        "तुमच्या खात्याची क्रियाकलाप संशयास्पद आहे. उद्या फ्रीझ केले जाईल. सत्यापित करा: www.freeze-stop.fake",
        "चेतावणी: खाते 6 तासांत कायमचे बंद केले जाईल. प्रतिबंधित करा: www.account-close.fake",
        "असामान्य क्रियाकलाप आढळला. सुरक्षिततेसाठी खाते लॉक केले गेले आहे. अनलॉक करा: www.security-unlock.fake",
        "लंबित सत्यापनामुळे तुमचे बँक खाते निष्क्रिय केले जाईल. आता कृती करा!",
        "शेवटची चेतावणी! 1 तासात खाते अवरोधन. लगेचच सत्यापन आवश्यक",
        "धोरण उल्लंघनामुळे सेवा बंद केली गेली आहे. www.restore-service.fake वर पुनर्संचयित करा",
        "तुमचे खाते बंद करण्यासाठी चिन्हांकित केले गेले आहे. www.prevent-closure.fake वर सत्यापित करून प्रतिबंधित करा",
    ]
    
    # Fake delivery charges (English)
    delivery_scams_en = [
        "Your parcel is held at customs. Pay Rs.500 clearance fee: www.customs-pay.fake",
        "Delivery pending! Pay Rs.200 charges to receive your Amazon package",
        "Courier notification: Pay Rs.150 redelivery fee at www.courier-fake.com",
        "Your package delivery failed. Pay Rs.300 at www.delivery-retry.fake to reschedule",
        "DTDC Alert: Parcel stuck. Clear Rs.250 fee at www.dtdc-fake.com for delivery",
        "Blue Dart: Delivery charges Rs.180 pending. Pay at www.bluedart-fake.in",
        "Your Flipkart order delivery requires Rs.99 fee. Pay now: www.flipkart-delivery.fake",
        "International parcel held. Clear customs duty Rs.800 at www.intl-customs.fake",
        "Dear customer, pay Rs.120 delivery fee for pending parcel. COD not available",
        "Package undeliverable. Pay storage charges Rs.500 at www.warehouse-fake.com",
    ]
    
    # Fake delivery charges (Hindi)
    delivery_scams_hi = [
        "आपका पार्सल कस्टम्स में रोका गया है। 500 रुपये की साफ़-सफाई शुल्क का भुगतान करें: www.customs-pay.fake",
        "डिलीवरी लंबित है! अमेज़ॅन पैकेज प्राप्त करने के लिए 200 रुपये शुल्क का भुगतान करें",
        "कूरियर अधिसूचना: www.courier-fake.com पर 150 रुपये की पुनः डिलीवरी शुल्क का भुगतान करें",
        "आपके पैकेज की डिलीवरी विफल हुई। पुनः निर्धारित करने के लिए www.delivery-retry.fake पर 300 रुपये का भुगतान करें",
        "DTDC चेतावनी: पार्सल अटका हुआ है। डिलीवरी के लिए www.dtdc-fake.com पर 250 रुपये की शुल्क साफ़ करें",
        "ब्लू डार्ट: 180 रुपये का डिलीवरी शुल्क लंबित है। www.bluedart-fake.in पर भुगतान करें",
        "आपके फ्लिपकार्ट ऑर्डर की डिलीवरी के लिए 99 रुपये की शुल्क की आवश्यकता है। अब भुगतान करें: www.flipkart-delivery.fake",
        "अंतरराष्ट्रीय पार्सल रोका गया है। www.intl-customs.fake पर 800 रुपये की कस्टम शुल्क साफ़ करें",
        "प्रिय ग्राहक, लंबित पार्सल के लिए 120 रुपये की डिलीवरी शुल्क का भुगतान करें। COD उपलब्ध नहीं है",
        "पैकेज डिलीवर करने में असमर्थ। www.warehouse-fake.com पर 500 रुपये की स्टोरेज शुल्क का भुगतान करें",
    ]
    
    # Fake delivery charges (Marathi)
    delivery_scams_mr = [
        "तुमचा पार्सल सीमा मध्ये रोखला गेला आहे. 500 रुपये साफ करणे शुल्क भरा: www.customs-pay.fake",
        "डिलिव्हरी बाकी! तुमचा अमेझॉन पॅकेज मिळवण्यासाठी 200 रुपये शुल्क भरा",
        "करिअर सूचना: www.courier-fake.com वर 150 रुपये पुन्हा डिलिव्हरी शुल्क भरा",
        "तुमच्या पॅकेज डिलिव्हरी अयशस्वी झाली. पुन्हा निर्धारित करण्यासाठी www.delivery-retry.fake वर 300 रुपये भरा",
        "DTDC चेतावणी: पार्सल अडकला आहे. डिलिव्हरीसाठी www.dtdc-fake.com वर 250 रुपये शुल्क साफ करा",
        "ब्लू डार्ट: 180 रुपये डिलिव्हरी शुल्क बाकी. www.bluedart-fake.in वर भरा",
        "तुमच्या फ्लिपकार्ट ऑर्डर डिलिव्हरीसाठी 99 रुपये शुल्क आवश्यक आहे. आता भरा: www.flipkart-delivery.fake",
        "आंतरराष्ट्रीय पार्सल रोखला गेला आहे. www.intl-customs.fake वर 800 रुपये सीमा शुल्क साफ करा",
        "प्रिय ग्राहक, बाकी पार्सलसाठी 120 रुपये डिलिव्हरी शुल्क भरा. COD उपलब्ध नाही",
        "पॅकेज डिलिव्हर करता येत नाही. www.warehouse-fake.com वर 500 रुपये साठवण शुल्क भरा",
    ]
    
    # Tax refund scams (English)
    tax_scams_en = [
        "You are eligible for income tax refund of Rs.35000. Claim at www.incometax-refund.fake",
        "Dear taxpayer, refund of Rs.12000 approved. Verify bank details at www.tax-refund.fake",
        "ITR refund Rs.25000 pending. Process at www.itr-process.fake with PAN details",
        "GST refund Rs.8000 available. Claim at www.gst-refund-fake.com within 7 days",
        "Tax rebate of Rs.18000 approved. Update bank account at www.rebate-claim.fake",
        "You have unclaimed tax refund Rs.30000. Apply: www.unclaimed-tax.fake with Aadhaar",
        "Income tax department: Refund Rs.22000 ready. Verify at www.it-dept.fake.gov.in",
        "Your TDS refund of Rs.15000 is pending. Claim: www.tds-refund.fake",
        "Tax refund Rs.40000 approved by finance ministry. Process at www.finmin-fake.gov",
        "Dear assessee, expedite refund Rs.20000 by paying Rs.500 processing fee",
    ]
    
    # Tax refund scams (Hindi)
    tax_scams_hi = [
        "You are eligible for income tax refund of Rs.35000. Claim at www.incometax-refund.fake",
        "Dear taxpayer, refund of Rs.12000 approved. Verify bank details at www.tax-refund.fake",
        "ITR refund Rs.25000 pending. Process at www.itr-process.fake with PAN details",
        "GST refund Rs.8000 available. Claim at www.gst-refund-fake.com within 7 days",
        "Tax rebate of Rs.18000 approved. Update bank account at www.rebate-claim.fake",
        "You have unclaimed tax refund Rs.30000. Apply: www.unclaimed-tax.fake with Aadhaar",
        "Income tax department: Refund Rs.22000 ready. Verify at www.it-dept.fake.gov.in",
        "Your TDS refund of Rs.15000 is pending. Claim: www.tds-refund.fake",
        "Tax refund Rs.40000 approved by finance ministry. Process at www.finmin-fake.gov",
        "Dear assessee, expedite refund Rs.20000 by paying Rs.500 processing fee",
    ]
    
    # Tax refund scams (Marathi)
    tax_scams_mr = [
        "तुम्ही उत्पन्नकर रिफंडच्या 35000 रुपये च्या पात्र आहात. www.incometax-refund.fake वर दावा करा",
        "प्रिय करदाता, 12000 रुपये चा रिफंड मंजूर केला. www.tax-refund.fake वर बँक तपशील सत्यापित करा",
        "ITR रिफंड 25000 रुपये बाकी. PAN तपशीलांसह www.itr-process.fake वर प्रक्रिया करा",
        "GST रिफंड 8000 रुपये उपलब्ध. 7 दिवसांच्या आत www.gst-refund-fake.com वर दावा करा",
        "18000 रुपये ची कर सूट मंजूर केली. www.rebate-claim.fake वर बँक खाते अद्ययावत करा",
        "तुमच्याकडे 30000 रुपये चा न मिळालेला कर रिफंड आहे. आधारासह www.unclaimed-tax.fake वर अर्ज करा",
        "उत्पन्नकर विभाग: 22000 रुपये चा रिफंड तयार. www.it-dept.fake.gov.in वर सत्यापित करा",
        "तुमचा TDS रिफंड 15000 रुपये बाकी आहे. दावा: www.tds-refund.fake",
        "वित्त मंत्रालयाने 40000 रुपये चा कर रिफंड मंजूर केला. www.finmin-fake.gov वर प्रक्रिया करा",
        "प्रिय असेसी, 500 रुपये चा प्रक्रिया शुल्क भरून 20000 रुपये चा रिफंड गती करा",
    ]
    
    # Combine all data into a single DataFrame
    data = pd.DataFrame({
        'message': legitimate_en + legitimate_hi + legitimate_mr + phishing_en + phishing_hi + phishing_mr + otp_requests_en + otp_requests_hi + otp_requests_mr + fake_kyc_en + fake_kyc_hi + fake_kyc_mr + lottery_scams_en + lottery_scams_hi + lottery_scams_mr + blocking_threats_en + blocking_threats_hi + blocking_threats_mr + delivery_scams_en + delivery_scams_hi + delivery_scams_mr + tax_scams_en + tax_scams_hi + tax_scams_mr,
        'label': ['legitimate'] * (len(legitimate_en) + len(legitimate_hi) + len(legitimate_mr)) + ['phishing'] * (len(phishing_en) + len(phishing_hi) + len(phishing_mr)) + ['otp_request'] * (len(otp_requests_en) + len(otp_requests_hi) + len(otp_requests_mr)) + ['fake_kyc'] * (len(fake_kyc_en) + len(fake_kyc_hi) + len(fake_kyc_mr)) + ['lottery_scam'] * (len(lottery_scams_en) + len(lottery_scams_hi) + len(lottery_scams_mr)) + ['blocking_threat'] * (len(blocking_threats_en) + len(blocking_threats_hi) + len(blocking_threats_mr)) + ['delivery_scam'] * (len(delivery_scams_en) + len(delivery_scams_hi) + len(delivery_scams_mr)) + ['tax_scam'] * (len(tax_scams_en) + len(tax_scams_hi) + len(tax_scams_mr))
    })
    
    return data

from typing import cast

def preprocess_data(data: pd.DataFrame) -> Tuple[csr_matrix, np.ndarray, LabelEncoder, TfidfVectorizer]:
    """Preprocess the data for training"""
    # Encode labels
    label_encoder = LabelEncoder()
    data.loc[:, 'label'] = label_encoder.fit_transform(data['label'])
    
    # Vectorize text data
    vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
    X = cast(csr_matrix, vectorizer.fit_transform(data['message']))
    y = np.array(data['label'].astype(int))  # Ensure labels are integers and properly typed as np.ndarray
    
    return X, y, label_encoder, vectorizer

def train_model(X: csr_matrix, y: np.ndarray) -> RandomForestClassifier:
    """Train a Random Forest classifier"""
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate model
    y_pred = model.predict(X_test)
    print("Classification Report:\n", classification_report(y_test, y_pred))
    print("Confusion Matrix:\n", confusion_matrix(y_test, y_pred))
    print("Accuracy:", accuracy_score(y_test, y_pred))
    
    return model

def main() -> None:
    """Main function to train the model"""
    data = generate_training_data()
    X, y, label_encoder, vectorizer = preprocess_data(data)
    model = train_model(X, y)
    
    # Save the model and label encoder
    joblib.dump(model, 'models/fraud_detection_model.pkl')
    joblib.dump(label_encoder, 'models/label_encoder.pkl')
    print("✅ Models saved in 'models/' directory")
    
    # Feature importance
    print("\n🔍 Top 20 Important Features:")
    feature_names = vectorizer.get_feature_names_out()
    importances = model.feature_importances_
    indices = np.argsort(importances)[-20:]
    
    for idx in indices[::-1]:
        print(f"   {feature_names[idx]}: {importances[idx]:.4f}")
    
    print("\n✅ Training complete! Models ready for deployment.")

if __name__ == "__main__":
    main()

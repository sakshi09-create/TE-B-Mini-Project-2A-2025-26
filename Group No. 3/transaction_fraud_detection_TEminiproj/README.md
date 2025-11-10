# Transaction Fraud Detection

Advanced AI-powered system to detect fraudulent transactions from screenshots using OCR and machine learning.

## Features

- OCR text extraction from transaction screenshots
- Transaction detail extraction (amount, recipient, UPI ID, etc.)
- Multi-class fraud classification (8 fraud types + legitimate)
- **🔗 Link fraud detection** - Analyzes URLs in messages for suspicious patterns
- Detailed fraud explanations with confidence levels
- RESTful API for integration

## Supported Fraud Types

1. Legitimate transactions
2. Phishing attempts
3. OTP/CVV/PIN requests
4. Fake KYC updates
5. Lottery/prize scams
6. Account blocking threats
7. Fake delivery charges
8. Fake tax refunds

## Link Fraud Detection

The system now includes advanced link analysis capabilities:

- Extracts URLs from message text
- Checks for suspicious domain patterns (shortened URLs, random domains)
- Verifies against known legitimate banking domains
- Performs accessibility checks on links
- Provides safety scores and detailed issue reports

## API Endpoints

- `POST /predict` - Analyze a transaction screenshot
- `GET /` - Health check

## Setup

1. Install requirements: `pip install -r requirements.txt`
2. Ensure Tesseract OCR is installed and configured
3. Train the model: `python train_model.py`
4. Run the server: `python app.py`

## Requirements

See [requirements.txt](requirements.txt)

# Link Fraud Detection Feature Implementation

## Overview

This document describes the implementation of the link fraud detection feature for the ParentShield.AI project. The feature enhances the existing fraud detection capabilities by analyzing URLs found in message screenshots for potential fraud indicators.

## Components Updated

### 1. Backend - Fraud Detection Module (`backend/fraud/app.py`)

#### New Functionality Added:
- **URL Extraction**: `extract_urls()` function to identify URLs in text
- **Link Analysis**: `analyze_links()` function to evaluate URL safety
- **Integration**: Link analysis results integrated into fraud detection output

#### Key Features:
- Detects suspicious domain patterns (shortened URLs like bit.ly, tiny.url)
- Identifies banking-related domains that aren't legitimate banks
- Performs accessibility checks on links
- Provides safety scores for each analyzed link
- Overall risk assessment for messages with multiple links

### 2. Backend - Transaction Fraud Detection (`backend/transaction_fraud_detection_TEminiproj/pipeline.py`)

#### New Functionality Added:
- **URL Extraction**: `extract_urls()` function to identify URLs in text
- **Link Analysis**: `analyze_links()` function to evaluate URL safety
- **Integration**: Link analysis results integrated into fraud detection output

#### Key Features:
- Same link analysis capabilities as the main fraud module
- Integrated with existing transaction detail extraction
- Combined with ML-based fraud classification

### 3. Frontend - Message Fraud Page (`frontend/src/pages/MessageFraud.jsx`)

#### New UI Components:
- Link analysis results display section
- Visual indicators for suspicious links
- Safety scores for each link
- Detailed issue reporting for problematic URLs
- Overall risk level assessment

### 4. Frontend - Transaction Fraud Page (`frontend/src/pages/TransactionFraud.jsx`)

#### New UI Components:
- Link analysis results display section
- Visual indicators for suspicious links
- Safety scores for each link
- Detailed issue reporting for problematic URLs
- Overall risk level assessment

### 5. Dependencies Updated

#### Backend Requirements:
- Added `requests==2.31.0` to both modules for URL accessibility checking

## Technical Implementation Details

### URL Extraction

The system uses regex patterns to identify URLs in text:
1. Standard URLs with protocols (http://, https://)
2. Domain-only patterns (www.example.com, example.com)

### Link Analysis Criteria

1. **Suspicious Domain Patterns**:
   - Shortened URLs (bit.ly, tiny.url, goo.gl, etc.)
   - Domains with excessive numbers
   - Very long random domain names

2. **Banking Domain Verification**:
   - Compares against a list of known legitimate banking domains
   - Flags banking-related keywords in non-legitimate domains

3. **Accessibility Checking**:
   - Performs HTTP HEAD requests to verify if URLs are accessible
   - Records error status codes

4. **Safety Scoring**:
   - Each link receives a safety score (0.0 to 1.0)
   - Score decreases based on identified issues
   - Overall message risk level determined by proportion of suspicious links

## API Response Format

The fraud analysis now includes an additional `link_analysis` field:

```json
{
  "fraud_analysis": {
    // ... existing fields ...
    "link_analysis": {
      "links": [
        {
          "url": "http://example.com",
          "is_suspicious": true,
          "issues": ["Suspicious domain pattern: bit\\.ly"],
          "safety_score": 0.5
        }
      ],
      "overall": {
        "total_links": 3,
        "suspicious_links": 2,
        "is_suspicious": true,
        "risk_level": "high"
      }
    }
  }
}
```

## Testing

A test script (`backend/test_link_detection.py`) was created to verify functionality with various URL patterns.

## Future Enhancements

Potential improvements for future versions:
1. Integration with external threat intelligence APIs
2. More sophisticated domain reputation checking
3. JavaScript execution analysis for advanced phishing detection
4. Screenshot-based link preview generation
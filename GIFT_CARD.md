# Code Generator API Documentation

## Overview
API for generating promotional codes at Rosedale Massage. Requires API key authentication.

## Authentication
Header: `X-API-KEY: your_api_key_here`

## Rate Limits
- 200/day
- 50/hour
- 10/minute per endpoint

## Endpoints

### 1. Unlimited Massage Package Codes
Generate unlimited package codes.

**Endpoint:** `/api/v1/code-generator/generate/unlimited`  
**Method:** GET  
**Parameters:**
- `duration`: (Required) Minutes: 60, 90, 110
- `first_name`: (Required) Customer's first name

**Example:**  
```
GET /api/v1/code-generator/generate/unlimited?duration=90&first_name=Rebecca
Response: {"code": "UL-90-REBECCA-ABCD12"}
```

### 2. School Discount Codes
Generate school group discount codes.

**Endpoint:** `/api/v1/code-generator/generate/school-code`  
**Method:** GET  
**Parameters:**
- `discount`: (Required) Percentage: 1-100

**Example:**  
```
GET /api/v1/code-generator/generate/school-code?discount=20
Response: {"code": "SCHL-20-ABCD12"}
```

### 3. Referral Discount Codes
Generate referral discount codes.

**Endpoint:** `/api/v1/code-generator/generate/referral-code`  
**Method:** GET  
**Parameters:**
- `first_name`: (Required) Referring customer's name
- `discount`: (Required) Percentage: 1-100

**Example:**  
```
GET /api/v1/code-generator/generate/referral-code?first_name=Rebecca&discount=50
Response: {"code": "REF-50-REBECCA-ABCD12"}
```

### 4. Free Guest Pass Codes
Generate free guest passes.

**Endpoint:** `/api/v1/code-generator/generate/guest-pass`  
**Method:** GET  
**Parameters:**
- `duration`: (Required) Minutes: 60, 90, 110
- `first_name`: (Required) Referring customer's name

**Example:**  
```
GET /api/v1/code-generator/generate/guest-pass?duration=60&first_name=Rebecca
Response: {"code": "FREE-60-REBECCA-ABCD12"}
```

### 5. Gift Card Codes
Generate gift card codes.

**Endpoint:** `/api/v1/code-generator/generate/gift-card`  
**Method:** GET  
**Parameters:**
- `amount`: (Required) Value in pounds
- `type`: (Required) DIGITAL or PREMIUM
- `first_name`: (Optional) Recipient's name

**Examples:**  
```
GET /api/v1/code-generator/generate/gift-card?amount=150&type=DIGITAL&first_name=Rebecca
Response: {"code": "GIFT-DGTL-150-REBECCA-K7M2P9X4"}

GET /api/v1/code-generator/generate/gift-card?amount=150&type=PREMIUM
Response: {"code": "GIFT-PREM-150-B7K2N8L4"}
```

### 6. Bulk Gift Card Codes
Generate multiple premium gift cards.

**Endpoint:** `/api/v1/code-generator/generate/gift-card/bulk`  
**Method:** GET  
**Parameters:**
- `amount`: (Required) Value in pounds
- `quantity`: (Required) Number of codes (max 50)

**Example:**  
```
GET /api/v1/code-generator/generate/gift-card/bulk?amount=150&quantity=2
Response: {
    "codes": [
        "GIFT-PREM-150-B7K2N8L4",
        "GIFT-PREM-150-X9Y4M7P2"
    ]
}
```

### 7. Personal Massage Codes
Generate personal massage codes.

**Endpoint:** `/api/v1/code-generator/generate/personal-code`  
**Method:** GET  
**Parameters:**
- `first_name`: (Required) Customer's name
- Either:
  - `duration`: Minutes: 60, 90, 110
  - OR
  - `discount`: Percentage: 1-100

**Examples:**  
```
GET /api/v1/code-generator/generate/personal-code?duration=90&first_name=Rebecca
Response: {"code": "PERS-90-REBECCA-ABCD12"}

GET /api/v1/code-generator/generate/personal-code?discount=25&first_name=Emily
Response: {"code": "PERS-25-EMILY-ABCD12"}
```

## Code Format Details

Each code type follows a specific format with unique identifiers:

1. **Unlimited Package**: `UL-[DURATION]-[NAME]-[6 chars]`
2. **School Discount**: `SCHL-[DISCOUNT]-[6 chars]`
3. **Referral Discount**: `REF-[DISCOUNT]-[NAME]-[6 chars]`
4. **Guest Pass**: `FREE-[DURATION]-[NAME]-[6 chars]`
5. **Gift Card**: `GIFT-[TYPE]-[AMOUNT]-[NAME]-[8 chars]` or `GIFT-[TYPE]-[AMOUNT]-[8 chars]`
6. **Personal Code**: `PERS-[DURATION/DISCOUNT]-[NAME]-[6 chars]`

Notes:
- All codes use uppercase letters and numbers
- Gift cards use 8-character unique suffixes, all others use 6 characters
- Names are automatically converted to uppercase
- [TYPE] is either DGTL or PREM for gift cards
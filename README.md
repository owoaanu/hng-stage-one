# HNG 13 Stage 1 - String Analyzer API

A RESTful API service that analyzes strings and stores their computed properties. Built with Django and Django REST Framework.

## Live Deployment

**Base URL:** https://hng-stage-one-production-sam.up.railway.app

## Features

- **String Analysis**: Computes length, palindrome status, unique characters, word count, SHA-256 hash, and character frequency
- **CRUD Operations**: Create, retrieve, and delete analyzed strings
- **Advanced Filtering**: Filter strings by multiple criteria (palindrome, length, word count, character presence)
- **Natural Language Queries**: Filter strings using plain English (e.g., "all single word palindromic strings")
- **Duplicate Detection**: Prevents storing identical strings using SHA-256 hashing

## Tech Stack

- **Python**: 3.13.3
- **Django**: 5.x
- **Django REST Framework**: 3.x
- **Database**: SQLite (development), PostgreSQL-ready
- **Deployment**: Railway

## Prerequisites

- Python 3.13.3 or higher
- pip (Python package manager)
- Git

## Local Setup Instructions

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd string_analyzer
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
```

**Note**: For production, set `DEBUG=False` and configure appropriate `ALLOWED_HOSTS`.

### 5. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Start Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Create/Analyze String
```http
POST /strings
Content-Type: application/json

{
  "value": "string to analyze"
}
```

**Success Response (201 Created):**
```json
{
  "id": "sha256_hash_value",
  "value": "string to analyze",
  "properties": {
    "length": 17,
    "is_palindrome": false,
    "unique_characters": 12,
    "word_count": 3,
    "sha256_hash": "abc123...",
    "character_frequency_map": {
      "s": 2,
      "t": 3,
      "r": 2
    }
  },
  "created_at": "2025-10-24T10:00:00Z"
}
```

**Error Responses:**
- `409 Conflict`: String already exists
- `400 Bad Request`: Missing "value" field
- `422 Unprocessable Entity`: Invalid data type for "value"

### 2. Get Specific String
```http
GET /strings/{string_value}
```

**Example:**
```http
GET /strings/hello world
```

**Success Response (200 OK):** Same structure as POST response

**Error Response:**
- `404 Not Found`: String does not exist

### 3. Get All Strings with Filtering
```http
GET /strings?is_palindrome=true&min_length=5&max_length=20&word_count=2&contains_character=a
```

**Query Parameters:**
- `is_palindrome`: boolean (true/false)
- `min_length`: integer (minimum string length)
- `max_length`: integer (maximum string length)
- `word_count`: integer (exact word count)
- `contains_character`: string (single character to search for)

**Success Response (200 OK):**
```json
{
  "data": [
    {
      "id": "hash1",
      "value": "string1",
      "properties": { },
      "created_at": "2025-10-24T10:00:00Z"
    }
  ],
  "count": 1,
  "filters_applied": {
    "is_palindrome": true,
    "min_length": 5,
    "max_length": 20,
    "word_count": 2,
    "contains_character": "a"
  }
}
```

### 4. Natural Language Filtering
```http
GET /strings/filter-by-natural-language?query=all single word palindromic strings
```

**Supported Query Patterns:**
- "all single word palindromic strings" → `word_count=1`, `is_palindrome=true`
- "strings longer than 10 characters" → `min_length=11`
- "palindromic strings containing the letter z" → `is_palindrome=true`, `contains_character=z`
- "strings containing the first vowel" → `contains_character=a`

**Success Response (200 OK):**
```json
{
  "data": [ ],
  "count": 3,
  "interpreted_query": {
    "original": "all single word palindromic strings",
    "parsed_filters": {
      "word_count": 1,
      "is_palindrome": true
    }
  }
}
```

**Error Responses:**
- `400 Bad Request`: Unable to parse query or missing query parameter

### 5. Delete String
```http
DELETE /strings/{string_value}
```

**Success Response:** `204 No Content` (empty body)

**Error Response:**
- `404 Not Found`: String does not exist

## Project Structure

```
string_analyzer/
├── string_analyzer/          # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── analyzer/                 # Main app
│   ├── models.py            # AnalyzedString model
│   ├── serializers.py       # StringSerializer
│   ├── views.py             # StringAnalyzerViewSet
│   ├── filters.py           # AnalyzedStringFilter
│   └── utils.py             # String analysis functions
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (not in repo)
├── manage.py
└── README.md
```

## Dependencies

Key packages in `requirements.txt`:

- `Django>=5.0,<6.0` - Web framework
- `djangorestframework>=3.14.0` - REST API framework
- `django-cors-headers>=4.0.0` - CORS support
- `django-filter>=23.0` - Advanced filtering
- `python-dotenv>=1.0.0` - Environment variable management
- `gunicorn>=21.0.0` - WSGI HTTP server for deployment

Install all dependencies with:
```bash
pip install -r requirements.txt
```

## Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Django secret key for cryptographic signing | Yes | - |
| `DEBUG` | Enable/disable debug mode | No | `False` |


## Deployment

This application is deployed on **Railway**.

### Deploy to Railway:

1. Push your code to GitHub
2. Connect your GitHub repo to Railway
3. Set environment variables in Railway dashboard:
   - `SECRET_KEY`
   - `DEBUG=False`
4. Railway will automatically detect Django and deploy

## Testing the API

### Using cURL:

```bash
# Create a string
curl -X POST https://hng-stage-one-production-sam.up.railway.app/strings \
  -H "Content-Type: application/json" \
  -d '{"value": "racecar"}'

# Get a string
curl https://hng-stage-one-production-sam.up.railway.app/strings/racecar

# Filter strings
curl "https://hng-stage-one-production-sam.up.railway.app/strings?is_palindrome=true"

# Natural language filter
curl "https://hng-stage-one-production-sam.up.railway.app/strings/filter-by-natural-language?query=single%20word%20palindromes"

# Delete a string
curl -X DELETE https://hng-stage-one-production-sam.up.railway.app/strings/racecar
```

## Notes

- Duplicate strings are detected by SHA-256 hash comparison
- Palindrome checking is case-insensitive ("Racecar" = palindrome)
- Word count is determined by whitespace splitting
- Character frequency map includes all characters (including spaces and punctuation)
- Natural language parsing supports flexible query formats
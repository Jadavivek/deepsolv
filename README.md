# Shopify Store Insights Fetcher

A comprehensive Python application that extracts insights from Shopify stores without using official APIs. Built with FastAPI and designed for scalability and maintainability.

## Features

### Mandatory Features
- **Product Catalog Extraction**: Complete list of products from any Shopify store
- **Hero Products**: Products featured on the homepage
- **Policy Extraction**: Privacy policy, return/refund policies
- **FAQ Extraction**: Brand FAQs with intelligent parsing
- **Social Media Handles**: Instagram, Facebook, TikTok links
- **Contact Information**: Email addresses, phone numbers
- **Brand Context**: About the brand information
- **Important Links**: Order tracking, contact pages, blogs

### Bonus Features
- **Competitor Analysis**: Automatic competitor discovery and analysis
- **Database Persistence**: MySQL database for storing insights
- **LLM Integration**: OpenAI integration for better data structuring

## Requirements

- Python 3.13+
- MySQL 8.0+ (for database features)
- OpenAI API Key (optional, for enhanced data structuring)

## Installation & Setup

### Method 1: Local Development

1. **Clone and setup the project:**
\`\`\`bash
git clone <repository-url>
cd shopify-insights-fetcher
\`\`\`

2. **Create virtual environment:**
\`\`\`bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

3. **Install dependencies:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

4. **Setup environment variables:**
\`\`\`bash
cp .env.example .env
# Edit .env with your configuration
\`\`\`

5. **Setup MySQL database:**
\`\`\`bash
# Create database
mysql -u root -p -e "CREATE DATABASE shopify_insights;"

# Run migrations (after completing all setup steps)
alembic upgrade head
\`\`\`

6. **Run the application:**
\`\`\`bash
python main.py
\`\`\`

### Method 2: Docker Compose (Recommended)

1. **Clone the project:**
\`\`\`bash
git clone <repository-url>
cd shopify-insights-fetcher
\`\`\`

2. **Run with Docker Compose:**
\`\`\`bash
docker-compose up --build
\`\`\`

This will start both the application and MySQL database automatically.

## Usage

### API Endpoints

#### Get Store Insights
\`\`\`bash
POST /api/v1/insights/extract
Content-Type: application/json

{
    "website_url": "https://memy.co.in"
}
\`\`\`

#### Response Format
\`\`\`json
{
    "success": true,
    "data": {
        "brand_name": "Memy",
        "website_url": "https://memy.co.in",
        "product_catalog": [...],
        "hero_products": [...],
        "privacy_policy": "...",
        "return_policy": "...",
        "faqs": [...],
        "social_handles": {...},
        "contact_details": {...},
        "brand_context": "...",
        "important_links": {...}
    }
}
\`\`\`

#### Get Competitor Analysis (Bonus)
\`\`\`bash
POST /api/v1/insights/competitors
Content-Type: application/json

{
    "website_url": "https://memy.co.in"
}
\`\`\`

### Testing with Postman

1. Import the API collection (will be provided)
2. Set base URL to `http://localhost:8000`
3. Test with sample Shopify stores:
   - https://memy.co.in
   - https://hairoriginals.com
   - https://colourpop.com

## Development

### Project Structure
\`\`\`
shopify-insights-fetcher/
├── app/
│   ├── api/routes/          # API endpoints
│   ├── core/                # Configuration
│   ├── database/            # Database models & connection
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── alembic/                 # Database migrations
├── main.py                  # Application entry point
├── requirements.txt         # Dependencies
└── README.md
\`\`\`

### Running Tests
\`\`\`bash
pytest tests/ -v
\`\`\`

### Code Formatting
\`\`\`bash
black app/ tests/
flake8 app/ tests/
\`\`\`

## Error Handling

The API returns appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid URL format)
- `401`: Website not found
- `500`: Internal server error

## Performance Considerations

- Implements request caching
- Concurrent scraping for multiple pages
- Rate limiting to respect target websites
- Efficient database queries with proper indexing

## Contributing

1. Follow PEP 8 style guidelines
2. Write comprehensive tests
3. Use type hints
4. Follow SOLID principles
5. Maintain clean, readable code

## License

This project is for educational and development purposes.
\`\`\`

```python file="run.py"
"""
Alternative entry point for running the application
"""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
# deepsolv

# API Documentation

Complete API documentation for the Shopify Store Insights Fetcher.

## Base URL

\`\`\`
http://localhost:8000/api/v1
\`\`\`

## Authentication

Currently, the API does not require authentication. In production, consider implementing API key authentication.

## Endpoints

### Health Check

Check if the API is running and healthy.

**Endpoint:** \`GET /health\`

**Response:**
\`\`\`json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

### Extract Store Insights

Extract comprehensive insights from a Shopify store.

**Endpoint:** \`POST /insights/extract\`

**Request Body:**
\`\`\`json
{
  "website_url": "https://memy.co.in"
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Insights extracted successfully in 15.23 seconds",
  "data": {
    "brand_name": "Memy",
    "website_url": "https://memy.co.in",
    "product_catalog": [
      {
        "id": "12345",
        "title": "Organic Cotton T-Shirt",
        "handle": "organic-cotton-tshirt",
        "description": "Comfortable organic cotton t-shirt",
        "price": "29.99",
        "compare_at_price": null,
        "vendor": "Memy",
        "product_type": "T-Shirts",
        "tags": ["organic", "cotton"],
        "images": ["https://example.com/image.jpg"],
        "variants": [...],
        "available": true,
        "url": "https://memy.co.in/products/organic-cotton-tshirt"
      }
    ],
    "hero_products": [...],
    "privacy_policy": {
      "content": "Privacy policy content...",
      "url": "https://memy.co.in/pages/privacy-policy",
      "last_updated": null
    },
    "return_policy": {...},
    "refund_policy": {...},
    "terms_of_service": {...},
    "faqs": [
      {
        "question": "Do you offer international shipping?",
        "answer": "Yes, we ship worldwide.",
        "category": "Shipping"
      }
    ],
    "social_handles": {
      "instagram": "@memy_official",
      "facebook": "memyofficial",
      "twitter": "@memy",
      "tiktok": null,
      "youtube": null,
      "linkedin": null,
      "pinterest": null
    },
    "contact_details": {
      "emails": ["info@memy.co.in"],
      "phone_numbers": ["+91-9876543210"],
      "address": "123 Fashion Street, Mumbai, India",
      "support_hours": "9 AM - 6 PM IST"
    },
    "important_links": {
      "order_tracking": "https://memy.co.in/pages/track-order",
      "contact_us": "https://memy.co.in/pages/contact",
      "blogs": "https://memy.co.in/blogs/news",
      "size_guide": "https://memy.co.in/pages/size-guide",
      "shipping_info": "https://memy.co.in/pages/shipping",
      "careers": null,
      "about_us": "https://memy.co.in/pages/about"
    },
    "brand_context": "Memy is a sustainable fashion brand...",
    "extraction_timestamp": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

**Error Responses:**

\`\`\`json
// 400 Bad Request - Invalid URL
{
  "success": false,
  "error": "Invalid website URL format",
  "error_code": "400",
  "timestamp": "2024-01-01T12:00:00.000Z"
}

// 401 Website Not Found
{
  "success": false,
  "error": "Website not found or not accessible",
  "error_code": "401",
  "timestamp": "2024-01-01T12:00:00.000Z"
}

// 500 Internal Server Error
{
  "success": false,
  "error": "Internal server error occurred during extraction",
  "error_code": "500",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

### Competitor Analysis (Bonus Feature)

Analyze competitors for a given brand.

**Endpoint:** \`POST /insights/competitors\`

**Request Body:**
\`\`\`json
{
  "website_url": "https://memy.co.in",
  "max_competitors": 5
}
\`\`\`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Competitor analysis completed successfully in 45.67 seconds",
  "data": {
    "main_brand": {
      // Same structure as insights extraction
    },
    "competitors": [
      {
        "competitor_name": "Fashion Nova",
        "website_url": "https://fashionnova.com",
        "insights": {
          // Same structure as insights extraction
        },
        "similarity_score": 0.75,
        "competitive_advantages": [
          "Larger product catalog",
          "Stronger social media presence"
        ]
      }
    ],
    "analysis_summary": "Analyzed 3 competitors for Memy. The brand shows strong positioning in sustainable fashion with competitive pricing...",
    "extraction_timestamp": "2024-01-01T12:00:00.000Z"
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

### Get Extraction History

Get extraction history for a specific website.

**Endpoint:** \`GET /insights/history/{website_url}\`

**Query Parameters:**
- \`limit\` (optional): Maximum number of records to return (default: 10)

**Example:** \`GET /insights/history/https://memy.co.in?limit=5\`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Retrieved 5 extraction records",
  "data": [
    {
      "id": 123,
      "status": "success",
      "error_message": null,
      "extraction_time_seconds": 15.23,
      "data_points_extracted": 45,
      "created_at": "2024-01-01T12:00:00.000Z"
    }
  ],
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

### Get Extraction Statistics

Get overall extraction statistics.

**Endpoint:** \`GET /insights/stats\`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Extraction statistics retrieved successfully",
  "data": {
    "total_extractions": 150,
    "successful_extractions": 142,
    "failed_extractions": 8,
    "success_rate": 94.67,
    "average_extraction_time_seconds": 18.45,
    "total_brands_analyzed": 75,
    "total_products_extracted": 3420
  },
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

### Delete Insights

Delete stored insights for a website.

**Endpoint:** \`DELETE /insights/{website_url}\`

**Example:** \`DELETE /insights/https://memy.co.in\`

**Response:**
\`\`\`json
{
  "success": true,
  "message": "Insights deleted successfully for https://memy.co.in",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

## Rate Limiting

Currently, there are no rate limits implemented. In production, consider implementing rate limiting to prevent abuse.

## Error Handling

All endpoints return consistent error responses with the following structure:

\`\`\`json
{
  "success": false,
  "error": "Error description",
  "error_code": "HTTP_STATUS_CODE",
  "timestamp": "2024-01-01T12:00:00.000Z"
}
\`\`\`

## Data Models

### Product Schema
\`\`\`json
{
  "id": "string",
  "title": "string",
  "handle": "string",
  "description": "string",
  "price": "string",
  "compare_at_price": "string",
  "vendor": "string",
  "product_type": "string",
  "tags": ["string"],
  "images": ["string"],
  "variants": [{}],
  "available": boolean,
  "url": "string"
}
\`\`\`

### FAQ Schema
\`\`\`json
{
  "question": "string",
  "answer": "string",
  "category": "string"
}
\`\`\`

### Social Handles Schema
\`\`\`json
{
  "instagram": "string",
  "facebook": "string",
  "twitter": "string",
  "tiktok": "string",
  "youtube": "string",
  "linkedin": "string",
  "pinterest": "string"
}
\`\`\`

## Testing

Use the provided Postman collection (\`postman/Shopify_Insights_API.postman_collection.json\`) to test all endpoints.

## Support

For API support and questions, please refer to the main README.md file or create an issue in the project repository.
\`\`\`

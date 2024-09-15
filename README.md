# 21BAI1713
 Ai Intern Task
# Document Retrieval System

## Overview
This document retrieval system provides a backend for retrieving documents to be used as context in chat applications. It includes caching, rate limiting, and background scraping features.

## Features
- REST API with endpoints `/health` and `/search`
- Caching with Redis
- Rate limiting for users
- Background scraping of news articles

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   ```

2. **Navigate to the project directory:**
   ```bash
   cd document-retrieval-system
   ```

3. **Build and run the Docker container:**
   ```bash
   docker build -t document-retrieval-system .
   docker run -p 5000:5000 document-retrieval-system
   ```

## Usage

- **Health Check Endpoint:**
  - URL: `/health`
  - Method: GET
  - Description: Returns a random response to check if the API is active.

- **Search Endpoint:**
  - URL: `/search`
  - Method: POST
  - Body:
    ```json
    {
      "text": "search query",
      "top_k": 5,
      "threshold": 0.7,
      "user_id": "unique_user_id"
    }
    ```
  - Description: Returns a list of top results for the given query.

## Caching
- **Redis** is used for caching search results. Cached results are stored with an expiration time of 300 seconds.

## Rate Limiting
- Users are limited to 5 requests per hour. Exceeding this limit will result in a 429 status code.

## Background Scraper
- A background thread scrapes news articles every hour and updates the document database.


# Website Crawler App with ScrapeGraphAI

A simple Flask web application that crawls websites and scrapes all content using ScrapeGraphAI.

## Features

- 🕷️ Crawl all links from a starting URL
- 📄 Scrape content from every page
- 📊 Parallel processing for faster crawling
- 💾 Download results as JSON
- 🎨 Clean, modern web interface

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
python -m playwright install
```

### 2. Configure Azure OpenAI

Edit `crawler_app.py` and update the Azure OpenAI configuration:

```python
AZURE_CONFIG = {
    "llm": {
        "api_key": "YOUR_AZURE_API_KEY",  # Your Azure OpenAI API key
        "model": "azure_openai/gpt-5.4-pro",  # Your deployment name
        "api_base": "https://YOUR_RESOURCE_NAME.openai.azure.com/",  # Your endpoint
        "api_version": "2024-02-15-preview",
    },
    "verbose": False,
    "headless": True,
}
```

**OR** set environment variables:

```bash
# Windows PowerShell
$env:AZURE_OPENAI_API_KEY="your-key-here"
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Mac/Linux
export AZURE_OPENAI_API_KEY="your-key-here"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

### 3. Run the App

```bash
python crawler_app.py
```

The app will start at: `http://localhost:5000`

## Usage

1. Open your browser and go to `http://localhost:5000`
2. Enter the URL you want to crawl
3. Set the maximum depth (how many levels deep to crawl)
4. Set the maximum pages (total number of pages to scrape)
5. Click "Start Crawling"
6. Wait for the crawl to complete
7. Download the JSON result

## API Endpoints

### Start a Crawl
```
POST /api/crawl
Content-Type: application/json

{
  "url": "https://example.com",
  "maxDepth": 2,
  "maxPages": 50
}
```

### Get Crawl Result
```
GET /api/crawl/{crawl_id}
```

### Download Result
```
GET /api/download/{crawl_id}
```

## Output Format

The JSON output follows the same structure as ScrapeGraphAI's crawl feature:

```json
{
  "id": "uuid-here",
  "params": {
    "url": "starting-url",
    "maxDepth": 2,
    "maxPages": 50
  },
  "status": "completed",
  "total": 50,
  "finished": 50,
  "pages": [
    {
      "url": "page-url",
      "depth": 0,
      "links": [...],
      "status": "completed",
      "scrape": {
        "results": {
          "markdown": {
            "data": ["scraped content here"]
          }
        }
      }
    }
  ]
}
```

## Configuration Options

- **Max Depth**: How many levels deep to follow links (1-5 recommended)
- **Max Pages**: Maximum number of pages to crawl (1-500)
- **headless**: Set to `True` for background crawling, `False` to see the browser

## Performance Tips

1. Start with small values (depth=2, pages=50) to test
2. Increase max_workers in ThreadPoolExecutor for faster crawling (default: 5)
3. Use headless mode for production (`headless: True`)
4. Monitor your Azure OpenAI API usage

## Troubleshooting

**Issue**: "playwright not found"
```bash
python -m playwright install
```

**Issue**: "Azure API error"
- Check your API key is correct
- Verify your endpoint URL
- Make sure your deployment name matches

**Issue**: "Crawl is slow"
- Reduce max_pages or max_depth
- Increase max_workers (but watch API rate limits)
- Use a faster Azure deployment

## Notes

- The app stores results in memory, so restarting will clear all crawls
- Large crawls may take several minutes depending on the number of pages
- Be respectful of websites' robots.txt and rate limits
- Monitor your Azure OpenAI token usage

## License

MIT

# Quick Start Guide - Website Crawler App

## What You Got

I've created a complete web crawler application with:

✅ **Flask Web App** - Simple interface to crawl websites
✅ **ScrapeGraphAI Integration** - Uses your Azure OpenAI to scrape content
✅ **Real-time Progress** - See crawling progress live
✅ **JSON Export** - Download results in the same format as your example
✅ **Parallel Processing** - Faster crawling with threading

## Files Created

```
/home/claude/
├── crawler_app_v2.py       ← Main app (USE THIS ONE)
├── templates/
│   └── index.html          ← Web interface
├── requirements.txt        ← Dependencies
└── README.md              ← Full documentation
```

## Quick Setup (3 Steps)

### Step 1: Install Dependencies

```bash
pip install flask scrapegraphai beautifulsoup4 requests
python -m playwright install
```

### Step 2: Configure Azure OpenAI

**Option A: Edit the file directly**

Open `crawler_app_v2.py` and find line 20:

```python
AZURE_CONFIG = {
    "llm": {
        "api_key": "YOUR_AZURE_API_KEY_HERE",  # ← Put your key here
        "model": "azure_openai/gpt-5.4-pro",
        "api_base": "https://YOUR_RESOURCE.openai.azure.com/",  # ← Put your endpoint
        "api_version": "2024-02-15-preview",
    },
}
```

**Option B: Use environment variables** (recommended)

```bash
# Windows PowerShell
$env:AZURE_OPENAI_API_KEY="your-azure-key"
$env:AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"

# Mac/Linux
export AZURE_OPENAI_API_KEY="your-azure-key"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
```

### Step 3: Run the App

```bash
cd /home/claude
python crawler_app_v2.py
```

Open your browser: **http://localhost:5000**

## How to Use

1. Enter a URL
2. Set max depth (how deep to crawl, 1-5)
3. Set max pages (total pages to scrape, 1-100)
4. Click "Start Crawling"
5. Watch the progress bar
6. Download the JSON when done!

## Example JSON Output

The output matches your uploaded file format:

```json
{
  "id": "uuid-here",
  "params": {
    "url": "https://www.bitdeer.ai/en/docs/center/",
    "maxDepth": 2,
    "maxPages": 20
  },
  "status": "completed",
  "total": 20,
  "finished": 20,
  "pages": [
    {
      "url": "page-url",
      "depth": 0,
      "links": ["link1", "link2"],
      "scrape": {
        "results": {
          "markdown": {
            "data": ["All the scraped content here..."]
          }
        }
      }
    }
  ]
}
```

## Performance Tips

**Start Small**: Begin with maxDepth=1 and maxPages=10 to test
**Monitor Usage**: Each page uses Azure OpenAI tokens
**Speed**: ~1-3 pages per minute (depends on Azure response time)

## Common Issues

**"playwright not found"**
```bash
python -m playwright install
```

**"Azure API error"**
- Check your API key
- Verify endpoint URL
- Confirm deployment name matches

**Crawl is slow**
- This is normal! Each page needs AI processing
- Reduce maxPages for faster testing
- Consider using a faster Azure model

## Next Steps

- Test with a small crawl first (10 pages)
- Check the JSON output format
- Adjust maxDepth and maxPages as needed
- Download and use the JSON data!

## Need Help?

The full README.md has more details on:
- API endpoints
- Configuration options
- Troubleshooting
- Advanced features

Happy crawling! 🕷️

"""
Enhanced Web Crawler App using ScrapeGraphAI
With real-time progress updates and better error handling
"""

from flask import Flask, render_template, request, jsonify, send_file
from scrapegraphai.graphs import SmartScraperGraph
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin, urlparse
import json
import os
from datetime import datetime
import uuid
import threading

app = Flask(__name__)

# Azure OpenAI Configuration - UPDATE THESE VALUES
AZURE_CONFIG = {
    "llm": {
        "api_key": "your_api_key_here",  # Replace with your Azure OpenAI API key
        "model": "azure_openai/gpt-5.4-pro",    
        "azure_endpoint": "https://sg-strategic-marketing-resource.services.ai.azure.com/",
        "api_version": "2024-02-15-preview",
    },
    "verbose": True,
    "headless": True,
}

# Store crawl results
crawl_results = {}


def get_all_links(url):
    """Extract all links from a given URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, timeout=15, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        links = set()
        base_domain = urlparse(url).netloc
        
        for a_tag in soup.find_all('a', href=True):
            link = urljoin(url, a_tag['href'])
            # Only include links from the same domain, no anchors
            parsed_link = urlparse(link)
            if parsed_link.netloc == base_domain and not parsed_link.fragment:
                clean_link = f"{parsed_link.scheme}://{parsed_link.netloc}{parsed_link.path}"
                if parsed_link.query:
                    clean_link += f"?{parsed_link.query}"
                links.add(clean_link)
        
        return list(links)
    except Exception as e:
        print(f"Error extracting links from {url}: {str(e)}")
        return []


def scrape_page(url):
    """Scrape a single page"""
    try:
        scraper = SmartScraperGraph(
            prompt="Extract all the text content from this page in markdown format. Include all headings, paragraphs, lists, and important information.",
            source=url,
            config=AZURE_CONFIG
        )
        
        result = scraper.run()
        return {"success": True, "content": str(result)}
    except Exception as e:
        return {"success": False, "error": str(e)}


def crawl_worker(crawl_id, start_url, max_depth, max_pages):
    """Background worker for crawling"""
    try:
        visited = set()
        to_visit = [(start_url, 0, None)]  # (url, depth, parent)
        pages = []
        
        while to_visit and len(visited) < max_pages:
            url, depth, parent = to_visit.pop(0)
            
            if url in visited or depth > max_depth:
                continue
            
            visited.add(url)
            
            # Update status
            crawl_results[crawl_id]["status"] = "running"
            crawl_results[crawl_id]["finished"] = len(pages)
            crawl_results[crawl_id]["current_url"] = url
            
            print(f"Scraping ({len(pages)+1}/{max_pages}): {url}")
            
            # Get links first
            links = get_all_links(url)
            
            # Scrape page content
            scrape_result = scrape_page(url)
            
            page_data = {
                "url": url,
                "depth": depth,
                "links": links[:100],  # Limit to 100 links
                "title": "",
                "status": "completed" if scrape_result["success"] else "failed",
                "parentUrl": parent,
                "contentType": "text/html",
            }
            
            if scrape_result["success"]:
                page_data["scrape"] = {
                    "results": {
                        "markdown": {
                            "data": [scrape_result["content"]]
                        }
                    },
                    "metadata": {
                        "provider": "scrapegraphai",
                        "contentType": "text/html"
                    }
                }
            else:
                page_data["error"] = scrape_result["error"]
            
            pages.append(page_data)
            
            # Add new links to visit
            if depth < max_depth:
                for link in links[:100]:
                    if link not in visited and len(visited) + len(to_visit) < max_pages:
                        to_visit.append((link, depth + 1, url))
        
        # Mark as completed
        crawl_results[crawl_id]["status"] = "completed"
        crawl_results[crawl_id]["finished"] = len(pages)
        crawl_results[crawl_id]["total"] = len(pages)
        crawl_results[crawl_id]["pages"] = pages
        crawl_results[crawl_id]["completedAt"] = datetime.now().isoformat()
        
        print(f"Crawl {crawl_id} completed: {len(pages)} pages")
        
    except Exception as e:
        crawl_results[crawl_id]["status"] = "failed"
        crawl_results[crawl_id]["error"] = str(e)
        print(f"Crawl {crawl_id} failed: {str(e)}")


@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')


@app.route('/api/crawl', methods=['POST'])
def api_crawl():
    """Start a new crawl"""
    data = request.json
    url = data.get('url')
    max_depth = int(data.get('maxDepth', 2))
    max_pages = int(data.get('maxPages', 50))
    
    if not url:
        return jsonify({"error": "URL is required"}), 400
    
    crawl_id = str(uuid.uuid4())
    
    # Initialize crawl result
    crawl_results[crawl_id] = {
        "id": crawl_id,
        "params": {
            "url": url,
            "formats": [{"mode": "normal", "type": "markdown"}],
            "maxDepth": max_depth,
            "maxPages": max_pages,
            "allowExternal": False,
            "maxLinksPerPage": 100
        },
        "status": "started",
        "total": max_pages,
        "finished": 0,
        "pages": [],
        "startedAt": datetime.now().isoformat()
    }
    
    # Start crawling in background thread
    thread = threading.Thread(
        target=crawl_worker,
        args=(crawl_id, url, max_depth, max_pages)
    )
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "crawl_id": crawl_id,
        "status": "started",
        "message": "Crawl started"
    })


@app.route('/api/crawl/<crawl_id>')
def get_crawl_status(crawl_id):
    """Get crawl status"""
    if crawl_id not in crawl_results:
        return jsonify({"error": "Crawl not found"}), 404
    
    return jsonify(crawl_results[crawl_id])


@app.route('/api/download/<crawl_id>')
def download_result(crawl_id):
    """Download crawl result as JSON"""
    if crawl_id not in crawl_results:
        return jsonify({"error": "Crawl not found"}), 404
    
    filename = f"crawl_{crawl_id}.json"
    import tempfile
    temp_dir = tempfile.gettempdir()
    filepath = os.path.join(temp_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(crawl_results[crawl_id], f, indent=2, ensure_ascii=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == '__main__':
    print("=" * 60)
    print("Website Crawler App - ScrapeGraphAI")
    print("=" * 60)
    print("\nIMPORTANT: Configure your Azure OpenAI credentials!")
    print("\nEdit AZURE_CONFIG in crawler_app_v2.py or set environment variables:")
    print("  - AZURE_OPENAI_API_KEY")
    print("  - AZURE_OPENAI_ENDPOINT")
    print("\nStarting server at http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

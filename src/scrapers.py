import requests
from bs4 import BeautifulSoup
import re
import time
import json
import logging
from typing import Dict, List, Any, Optional, Union
from urllib.parse import urljoin
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BenchmarkScraper:
    """
    Base class for scraping AI model benchmark information.
    """
    
    def __init__(self, use_selenium: bool = False, headless: bool = True):
        """
        Initialize the scraper.
        
        Args:
            use_selenium: Whether to use Selenium for JavaScript-heavy pages
            headless: Whether to run the browser in headless mode (Selenium only)
        """
        self.use_selenium = use_selenium
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ModelBenchmarking Research Tool/1.0'
        })
        
        self.driver = None
        if use_selenium:
            chrome_options = Options()
            if headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=chrome_options)
    
    def __del__(self):
        """Clean up resources on deletion."""
        if self.driver:
            self.driver.quit()
    
    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch a page using either requests or Selenium.
        
        Args:
            url: URL to fetch
            timeout: Timeout in seconds
            
        Returns:
            Page HTML content or None if failed
        """
        try:
            if self.use_selenium:
                self.driver.get(url)
                WebDriverWait(self.driver, timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                return self.driver.page_source
            else:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                return response.text
        except (requests.RequestException, TimeoutException) as e:
            logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML using BeautifulSoup.
        
        Args:
            html: HTML content
            
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'html.parser')


class PaperWithCodeScraper(BenchmarkScraper):
    """
    Scraper for Papers With Code website.
    """
    
    BASE_URL = "https://paperswithcode.com"
    
    def get_benchmark_tasks(self) -> List[Dict[str, str]]:
        """
        Get a list of benchmark tasks available on the site.
        
        Returns:
            List of tasks with name and URL
        """
        url = f"{self.BASE_URL}/sota"
        html = self.fetch_page(url)
        if not html:
            return []
        
        soup = self.parse_html(html)
        task_list = []
        
        for task_div in soup.select(".row.infinite-item"):
            task_link = task_div.select_one("h1 a")
            if task_link:
                task_name = task_link.text.strip()
                task_url = urljoin(self.BASE_URL, task_link["href"])
                task_list.append({
                    "name": task_name,
                    "url": task_url
                })
        
        return task_list
    
    def get_benchmark_results(self, task_url: str) -> Dict[str, Any]:
        """
        Get benchmark results for a specific task.
        
        Args:
            task_url: URL of the task page
            
        Returns:
            Dictionary with task details and results
        """
        html = self.fetch_page(task_url)
        if not html:
            return {}
        
        soup = self.parse_html(html)
        
        # Extract task info
        task_title = soup.select_one("h1").text.strip() if soup.select_one("h1") else "Unknown Task"
        
        # Extract dataset info
        dataset_elem = soup.select_one(".sota-page__dataset")
        dataset = dataset_elem.text.strip() if dataset_elem else "Unknown Dataset"
        
        # Extract results table
        results = []
        table = soup.select_one(".leaderboard-table")
        if table:
            for row in table.select("tbody tr"):
                cells = row.select("td")
                if len(cells) >= 6:
                    method_cell = cells[1]
                    method_link = method_cell.select_one("a")
                    method_name = method_link.text.strip() if method_link else cells[1].text.strip()
                    method_url = urljoin(self.BASE_URL, method_link["href"]) if method_link else None
                    
                    result = {
                        "model": method_name,
                        "score": cells[2].text.strip(),
                        "paper_title": cells[3].text.strip(),
                        "paper_url": urljoin(self.BASE_URL, cells[3].select_one("a")["href"]) if cells[3].select_one("a") else None,
                        "code_url": urljoin(self.BASE_URL, cells[4].select_one("a")["href"]) if cells[4].select_one("a") else None,
                        "model_url": method_url
                    }
                    results.append(result)
        
        return {
            "task": task_title,
            "dataset": dataset,
            "results": results
        }
    
    def get_model_details(self, model_url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_url: URL of the model page
            
        Returns:
            Dictionary with model details
        """
        html = self.fetch_page(model_url)
        if not html:
            return {}
        
        soup = self.parse_html(html)
        
        # Basic model info
        model_name = soup.select_one("h1").text.strip() if soup.select_one("h1") else "Unknown Model"
        
        # Extract model description
        description_elem = soup.select_one(".method__description")
        description = description_elem.text.strip() if description_elem else ""
        
        # Extract model architecture details
        architecture_details = {}
        architecture_elem = soup.select_one(".method__architecture")
        if architecture_elem:
            for item in architecture_elem.select("li"):
                key_elem = item.select_one("strong")
                if key_elem:
                    key = key_elem.text.strip().rstrip(":")
                    value = item.text.replace(key_elem.text, "").strip()
                    architecture_details[key] = value
        
        # Extract performance across tasks
        performance = []
        results_table = soup.select_one(".card-table")
        if results_table:
            for row in results_table.select("tbody tr"):
                cells = row.select("td")
                if len(cells) >= 4:
                    task_elem = cells[0].select_one("a")
                    task = {
                        "task": task_elem.text.strip() if task_elem else cells[0].text.strip(),
                        "task_url": urljoin(self.BASE_URL, task_elem["href"]) if task_elem else None,
                        "dataset": cells[1].text.strip(),
                        "metric": cells[2].text.strip(),
                        "score": cells[3].text.strip()
                    }
                    performance.append(task)
        
        return {
            "name": model_name,
            "description": description,
            "architecture": architecture_details,
            "performance": performance
        }


class HuggingFaceScraper(BenchmarkScraper):
    """
    Scraper for Hugging Face model hub.
    """
    
    BASE_URL = "https://huggingface.co"
    
    def __init__(self, use_selenium: bool = True, headless: bool = True):
        """
        Initialize with Selenium enabled by default since HF is JS-heavy.
        """
        super().__init__(use_selenium=use_selenium, headless=headless)
    
    def get_popular_models(self, task: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get popular models, optionally filtered by task.
        
        Args:
            task: Task to filter by
            limit: Maximum number of models to return
            
        Returns:
            List of model information
        """
        url = f"{self.BASE_URL}/models"
        if task:
            url += f"?pipeline_tag={task}"
        
        html = self.fetch_page(url)
        if not html:
            return []
        
        soup = self.parse_html(html)
        models = []
        
        for card in soup.select(".model-card")[:limit]:
            header = card.select_one(".model-name")
            if not header:
                continue
                
            model_link = header.select_one("a")
            if not model_link:
                continue
                
            model_name = model_link.text.strip()
            model_url = urljoin(self.BASE_URL, model_link["href"])
            
            # Extract model tags/tasks
            tags = []
            for tag in card.select(".model-tags .tag"):
                tags.append(tag.text.strip())
            
            # Extract downloads and likes
            downloads = None
            likes = None
            stats = card.select_one(".model-stats")
            if stats:
                downloads_elem = stats.select_one(".model-downloads-count")
                likes_elem = stats.select_one(".model-likes-count")
                
                if downloads_elem:
                    downloads_text = downloads_elem.text.strip()
                    downloads = self._parse_numeric(downloads_text)
                
                if likes_elem:
                    likes_text = likes_elem.text.strip()
                    likes = self._parse_numeric(likes_text)
            
            models.append({
                "name": model_name,
                "url": model_url,
                "tags": tags,
                "downloads": downloads,
                "likes": likes
            })
            
            if len(models) >= limit:
                break
                
        return models
    
    def get_model_details(self, model_url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific model.
        
        Args:
            model_url: URL of the model page
            
        Returns:
            Dictionary with model details
        """
        html = self.fetch_page(model_url)
        if not html:
            return {}
        
        soup = self.parse_html(html)
        
        # Model name and author
        model_name = soup.select_one("h1").text.strip() if soup.select_one("h1") else "Unknown Model"
        author_elem = soup.select_one(".author a")
        author = author_elem.text.strip() if author_elem else None
        
        # Model card content - this usually contains structured information
        card_content = ""
        model_card = soup.select_one(".model-card-content")
        if model_card:
            card_content = model_card.text.strip()
        
        # Metrics from model card
        metrics = {}
        metrics_table = soup.select_one(".metrics-table")
        if metrics_table:
            for row in metrics_table.select("tr"):
                cells = row.select("td")
                if len(cells) >= 2:
                    metric_name = cells[0].text.strip()
                    metric_value = cells[1].text.strip()
                    metrics[metric_name] = metric_value
        
        # Model tags
        tags = []
        for tag in soup.select(".model-tags .tag"):
            tags.append(tag.text.strip())
        
        # Extract downloads, likes and other stats
        downloads = None
        likes = None
        
        stats = soup.select_one(".model-summary-stats")
        if stats:
            downloads_elem = stats.select_one("[title='Downloads']")
            likes_elem = stats.select_one("[title='Likes']")
            
            if downloads_elem:
                downloads_text = downloads_elem.text.strip()
                downloads = self._parse_numeric(downloads_text)
            
            if likes_elem:
                likes_text = likes_elem.text.strip()
                likes = self._parse_numeric(likes_text)
        
        return {
            "name": model_name,
            "author": author,
            "card_content": card_content,
            "metrics": metrics,
            "tags": tags,
            "downloads": downloads,
            "likes": likes
        }
    
    def _parse_numeric(self, text: str) -> Optional[int]:
        """
        Parse numeric values that might include abbreviations like K, M.
        
        Args:
            text: Text with numeric value
            
        Returns:
            Parsed integer value or None
        """
        text = text.lower().strip()
        multiplier = 1
        
        if 'k' in text:
            multiplier = 1000
            text = text.replace('k', '')
        elif 'm' in text:
            multiplier = 1000000
            text = text.replace('m', '')
        
        try:
            return int(float(text) * multiplier)
        except ValueError:
            return None
"""
Web Scraper Module for Soil Research Agent
Scrapes agricultural and government websites for soil data.
"""

import requests
from bs4 import BeautifulSoup
import logging
import time
import re
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed

logger = logging.getLogger(__name__)

class WebScraper:
    def __init__(self, rate_limit=1.0):
        """
        Initialize web scraper with rate limiting.
        
        Args:
            rate_limit: Seconds to wait between requests (default 1.0 for safety)
        """
        self.rate_limit = rate_limit
        self.last_request_time = 0
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        
        # Priority sources for soil data
        self.priority_domains = [
            'data.gov.in',
            'icar.gov.in',
            'nbsslup.in',          # National Bureau of Soil Survey
            'crida.in',            # Central Research Institute for Dryland Agriculture
            'agricoop.nic.in',     # Ministry of Agriculture
            'apagrisnet.gov.in',   # AP Agriculture
            'fao.org',             # FAO
            'indiasoilinfo.in',
            'soilhealth.dac.gov.in',
            'wikipedia.org'
        ]
        
        # Fallback URLs for Indian soil data
        self.fallback_sources = [
            "https://en.wikipedia.org/wiki/{region}",
            "https://en.wikipedia.org/wiki/{region}_district",
            "https://en.wikipedia.org/wiki/Soil_types_of_India",
            "https://www.fao.org/soils-portal/data-hub/soil-maps-and-databases/en/",
        ]
        
    def _wait_for_rate_limit(self):
        """Enforce rate limiting between requests."""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit:
            time.sleep(self.rate_limit - elapsed)
        self.last_request_time = time.time()
    
    def search_duckduckgo(self, query, max_results=20):
        """
        Search using DuckDuckGo API wrapper.
        Falls back to static sources if search fails.
        """
        urls = []
        
        # Try using duckduckgo_search package (try both old and new names)
        try:
            try:
                from duckduckgo_search import DDGS
            except ImportError:
                from ddgs import DDGS
            
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=max_results))
                urls = [r['href'] for r in results if r.get('href')]
                logger.info(f"DDGS found {len(urls)} URLs for: {query}")
        except ImportError:
            logger.warning("duckduckgo_search not installed, using fallback")
        except Exception as e:
            logger.warning(f"DDGS search failed: {e}")
        
        # If search fails, try direct Google sites search via scraping
        if not urls:
            try:
                search_url = f"https://www.google.com/search?q={quote_plus(query + ' soil india')}"
                self._wait_for_rate_limit()
                response = self.session.get(search_url, timeout=10)
                
                # Extract URLs from Google results
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a'):
                    href = link.get('href', '')
                    if '/url?q=' in href:
                        actual_url = href.split('/url?q=')[1].split('&')[0]
                        if actual_url.startswith('http') and 'google' not in actual_url:
                            urls.append(actual_url)
                            if len(urls) >= max_results:
                                break
                
                logger.info(f"Google scrape found {len(urls)} URLs")
            except Exception as e:
                logger.warning(f"Google search failed: {e}")
        
        return urls
    
    def search_with_priority(self, region, state=None, max_total=20):
        """
        Searches for soil data with priority to government/research sites.
        
        Args:
            region: District/Mandal name
            state: State name (optional)
            max_total: Maximum total URLs to collect
            
        Returns:
            List of URLs sorted by priority
        """
        queries = [
            f"{region} {state or ''} soil type NPK pH",
            f"{region} soil profile agricultural",
            f"{region} soil health card data",
            f"{region} district soil characteristics India",
            f"soil survey {region} nitrogen phosphorus potassium"
        ]
        
        all_urls = set()
        priority_urls = []
        general_urls = []
        
        for query in queries:
            urls = self.search_duckduckgo(query, max_results=10)
            
            for url in urls:
                if url not in all_urls:
                    all_urls.add(url)
                    
                    # Check if priority domain
                    is_priority = any(domain in url.lower() for domain in self.priority_domains)
                    
                    if is_priority:
                        priority_urls.append(url)
                    else:
                        general_urls.append(url)
            
            if len(all_urls) >= max_total:
                break
        
        # Combine with priority first
        result = priority_urls + general_urls
        logger.info(f"Collected {len(priority_urls)} priority + {len(general_urls)} general URLs")
        
        return result[:max_total]
    
    def scrape_page(self, url, timeout=10):
        """
        Scrapes a single page and extracts text content.
        
        Args:
            url: URL to scrape
            timeout: Request timeout in seconds
            
        Returns:
            Dict with url, text, title, success status
        """
        result = {
            'url': url,
            'text': '',
            'title': '',
            'success': False
        }
        
        try:
            self._wait_for_rate_limit()
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Get title
            title_tag = soup.find('title')
            result['title'] = title_tag.get_text().strip() if title_tag else ''
            
            # Get main content text
            text = soup.get_text(separator=' ', strip=True)
            
            # Clean up text
            text = re.sub(r'\s+', ' ', text)
            text = text[:15000]  # Limit text length
            
            result['text'] = text
            result['success'] = True
            
            logger.debug(f"Scraped {len(text)} chars from {url}")
            
        except requests.Timeout:
            logger.warning(f"Timeout scraping {url}")
        except requests.RequestException as e:
            logger.warning(f"Failed to scrape {url}: {e}")
        except Exception as e:
            logger.error(f"Error scraping {url}: {e}")
        
        return result
    
    def scrape_multiple(self, urls, max_workers=3):
        """
        Scrapes multiple URLs in parallel with rate limiting.
        
        Args:
            urls: List of URLs to scrape
            max_workers: Maximum concurrent workers
            
        Returns:
            List of scrape results (successful only)
        """
        results = []
        
        # Use sequential for rate limiting compliance
        for url in urls:
            result = self.scrape_page(url)
            if result['success']:
                results.append(result)
                logger.info(f"Successfully scraped: {result['title'][:50]}...")
        
        logger.info(f"Successfully scraped {len(results)}/{len(urls)} pages")
        return results
    
    def extract_soil_keywords(self, text):
        """
        Quick extraction of soil-related keywords from text.
        Used for filtering relevant pages.
        
        Returns:
            Dict with found keywords
        """
        keywords = {
            'soil_types': [],
            'ph_values': [],
            'npk_values': [],
            'has_soil_data': False
        }
        
        text_lower = text.lower()
        
        # Soil type patterns
        soil_types = ['black cotton', 'red soil', 'alluvial', 'laterite', 'loamy', 
                      'sandy', 'clay', 'black soil', 'regur', 'vertisol']
        for st in soil_types:
            if st in text_lower:
                keywords['soil_types'].append(st)
        
        # pH patterns
        ph_pattern = r'ph\s*[:\s]*(\d+\.?\d*)'
        ph_matches = re.findall(ph_pattern, text_lower)
        keywords['ph_values'] = [float(p) for p in ph_matches if 4 <= float(p) <= 10]
        
        # NPK patterns
        npk_pattern = r'(nitrogen|phosphorus|potassium|n|p|k)\s*[:\s]*(\d+\.?\d*)\s*(kg|%|ppm)?'
        npk_matches = re.findall(npk_pattern, text_lower)
        keywords['npk_values'] = npk_matches
        
        keywords['has_soil_data'] = bool(keywords['soil_types'] or keywords['ph_values'])
        
        return keywords


# Convenience function
def create_scraper(rate_limit=1.0):
    return WebScraper(rate_limit=rate_limit)

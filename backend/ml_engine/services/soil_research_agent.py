"""
Soil Research Agent - Multi-Source Soil Data with Parallel Workers

Fetches soil data from multiple sources for unknown regions.
Sources: Soil Health Card Portal, ICAR, NBSS, data.gov.in, Wikipedia, FAO
Uses AI for data extraction and synthesis.
"""

import os
import json
import logging
import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import threading

logger = logging.getLogger(__name__)

# Cache Configuration
CACHE_DIR = os.path.join(os.path.dirname(__file__), '../data/soil_cache')
CACHE_TTL_DAYS = 30  # Soil data changes slowly

# Thread-safe lock
cache_lock = threading.Lock()

# ============ DATA SOURCE CONFIGURATIONS ============

# Source 1: Soil Health Card Portal
SHC_PORTAL = "https://soilhealth.dac.gov.in"

# Source 2: ICAR (Indian Council of Agricultural Research)
ICAR_URL = "https://icar.org.in"

# Source 3: NBSS (National Bureau of Soil Survey)
NBSS_URL = "https://nbsslup.in"

# Source 4: data.gov.in Soil Dataset
DATA_GOV_SOIL_API = "https://api.data.gov.in/resource/soil-data"
DATA_GOV_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"

# Source 5: Wikipedia for general soil info
WIKI_API = "https://en.wikipedia.org/api/rest_v1/page/summary"

# Source 6: FAO Soils Portal
FAO_URL = "https://www.fao.org/soils-portal"

# Default soil types for Indian states
STATE_DEFAULT_SOILS = {
    "Andhra Pradesh": {"soil": "Black Cotton", "ph": 7.8, "n": 200, "p": 50, "k": 280},
    "Telangana": {"soil": "Black Cotton", "ph": 7.5, "n": 180, "p": 45, "k": 260},
    "Karnataka": {"soil": "Red Soil", "ph": 6.5, "n": 170, "p": 40, "k": 220},
    "Tamil Nadu": {"soil": "Red Sandy Loam", "ph": 7.0, "n": 180, "p": 45, "k": 240},
    "Maharashtra": {"soil": "Black Cotton", "ph": 8.0, "n": 190, "p": 55, "k": 300},
    "Gujarat": {"soil": "Black Cotton", "ph": 7.8, "n": 185, "p": 50, "k": 290},
    "Madhya Pradesh": {"soil": "Black Cotton", "ph": 7.5, "n": 195, "p": 52, "k": 285},
    "Uttar Pradesh": {"soil": "Alluvial", "ph": 7.2, "n": 230, "p": 60, "k": 270},
    "Punjab": {"soil": "Alluvial", "ph": 7.5, "n": 250, "p": 65, "k": 280},
    "Haryana": {"soil": "Alluvial", "ph": 7.3, "n": 240, "p": 58, "k": 265},
    "Rajasthan": {"soil": "Sandy", "ph": 8.2, "n": 150, "p": 35, "k": 200},
    "West Bengal": {"soil": "Alluvial", "ph": 6.8, "n": 220, "p": 55, "k": 250},
    "Odisha": {"soil": "Laterite", "ph": 6.0, "n": 160, "p": 40, "k": 180},
    "Bihar": {"soil": "Alluvial", "ph": 7.0, "n": 210, "p": 52, "k": 245},
    "Kerala": {"soil": "Laterite", "ph": 5.5, "n": 150, "p": 35, "k": 170}
}

# Soil type patterns for extraction
SOIL_PATTERNS = [
    (r'black\s*(?:cotton|soil|regur)', 'Black Cotton'),
    (r'alluvial\s*(?:soil)?', 'Alluvial'),
    (r'red\s*(?:sandy)?\s*(?:loam|soil)', 'Red Sandy Loam'),
    (r'laterite\s*(?:soil)?', 'Laterite'),
    (r'loamy\s*(?:soil)?', 'Loamy'),
    (r'sandy\s*(?:loam|soil)?', 'Sandy'),
    (r'clay(?:ey)?\s*(?:soil)?', 'Clayey'),
    (r'vertisol', 'Black Cotton'),
    (r'alfisol', 'Red Soil'),
    (r'inceptisol', 'Alluvial'),
]


class SoilWorker:
    """Base class for soil data workers."""
    
    def __init__(self, name: str, timeout: int = 15):
        self.name = name
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/json,*/*',
        })
    
    def fetch(self, region: str, state: str, district: str = None) -> Optional[Dict]:
        raise NotImplementedError
    
    def _extract_soil_type(self, text: str) -> Optional[str]:
        """Extract soil type from text using patterns."""
        text_lower = text.lower()
        for pattern, soil_type in SOIL_PATTERNS:
            if re.search(pattern, text_lower):
                return soil_type
        return None
    
    def _extract_ph(self, text: str) -> Optional[float]:
        """Extract pH value from text."""
        patterns = [
            r'ph\s*[:\s]*(\d+\.?\d*)',
            r'ph\s*(?:value|level)?\s*[:\s]*(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*ph',
        ]
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    ph = float(match.group(1))
                    if 4.0 <= ph <= 10.0:
                        return ph
                except ValueError:
                    pass
        return None
    
    def _extract_npk(self, text: str) -> Dict[str, Optional[float]]:
        """Extract N, P, K values from text."""
        result = {'n': None, 'p': None, 'k': None}
        text_lower = text.lower()
        
        # Nitrogen patterns
        n_patterns = [
            r'nitrogen\s*[:\s]*(\d+\.?\d*)\s*(?:kg|%|ppm)?',
            r'n\s*[:\s]*(\d+\.?\d*)\s*(?:kg|%|ppm)?',
            r'available\s*n[:\s]*(\d+\.?\d*)',
        ]
        for pattern in n_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    result['n'] = float(match.group(1))
                    break
                except ValueError:
                    pass
        
        # Phosphorus patterns
        p_patterns = [
            r'phosphorus\s*[:\s]*(\d+\.?\d*)\s*(?:kg|%|ppm)?',
            r'p\s*[:\s]*(\d+\.?\d*)\s*(?:kg|%|ppm)?',
            r'available\s*p[:\s]*(\d+\.?\d*)',
        ]
        for pattern in p_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    result['p'] = float(match.group(1))
                    break
                except ValueError:
                    pass
        
        # Potassium patterns
        k_patterns = [
            r'potassium\s*[:\s]*(\d+\.?\d*)\s*(?:kg|%|ppm)?',
            r'k\s*[:\s]*(\d+\.?\d*)\s*(?:kg|%|ppm)?',
            r'available\s*k[:\s]*(\d+\.?\d*)',
        ]
        for pattern in k_patterns:
            match = re.search(pattern, text_lower)
            if match:
                try:
                    result['k'] = float(match.group(1))
                    break
                except ValueError:
                    pass
        
        return result


class WikipediaWorker(SoilWorker):
    """Worker for Wikipedia - General soil info."""
    
    def __init__(self):
        super().__init__("Wikipedia", timeout=10)
    
    def fetch(self, region: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            # Try multiple search terms
            search_terms = [
                f"{district or region}_district" if district else f"{region}_district",
                f"{region}",
                f"Soil_in_{state}",
                f"{state}_soil"
            ]
            
            for term in search_terms:
                url = f"{WIKI_API}/{term}"
                response = self.session.get(url, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    extract = data.get('extract', '')
                    
                    if extract and ('soil' in extract.lower() or 'agriculture' in extract.lower()):
                        soil_type = self._extract_soil_type(extract)
                        if soil_type:
                            logger.info(f"[Wikipedia] Found soil data for {region}: {soil_type}")
                            return {
                                "soil": soil_type,
                                "source": "Wikipedia",
                                "confidence": 60,
                                "raw_text": extract[:500]
                            }
            
            return None
            
        except Exception as e:
            logger.warning(f"[Wikipedia] Error: {e}")
            return None


class DataGovSoilWorker(SoilWorker):
    """Worker for data.gov.in soil datasets."""
    
    def __init__(self):
        super().__init__("data.gov.in", timeout=12)
    
    def fetch(self, region: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            # Try soil health card data
            params = {
                "api-key": DATA_GOV_KEY,
                "format": "json",
                "filters[state]": state,
                "limit": 20
            }
            
            if district:
                params["filters[district]"] = district
            
            # Multiple possible soil resources
            resources = [
                "soil-health-card-data",
                "district-wise-soil-data",
                "agricultural-soil-data"
            ]
            
            for resource in resources:
                try:
                    url = f"https://api.data.gov.in/resource/{resource}"
                    response = self.session.get(url, params=params, timeout=self.timeout)
                    
                    if response.status_code == 200:
                        data = response.json()
                        records = data.get('records', [])
                        
                        if records:
                            # Aggregate data from records
                            soil_types = []
                            ph_values = []
                            n_values = []
                            p_values = []
                            k_values = []
                            
                            for rec in records:
                                if rec.get('soil_type'):
                                    soil_types.append(rec['soil_type'])
                                if rec.get('ph'):
                                    try:
                                        ph_values.append(float(rec['ph']))
                                    except:
                                        pass
                                if rec.get('nitrogen') or rec.get('n'):
                                    try:
                                        n_values.append(float(rec.get('nitrogen') or rec.get('n')))
                                    except:
                                        pass
                            
                            if soil_types or ph_values:
                                logger.info(f"[data.gov.in] Found soil data for {region}")
                                return {
                                    "soil": soil_types[0] if soil_types else None,
                                    "ph": sum(ph_values) / len(ph_values) if ph_values else None,
                                    "n": sum(n_values) / len(n_values) if n_values else None,
                                    "source": "data.gov.in",
                                    "confidence": 85,
                                    "num_records": len(records)
                                }
                except:
                    continue
            
            return None
            
        except Exception as e:
            logger.warning(f"[data.gov.in] Error: {e}")
            return None


class SoilHealthCardWorker(SoilWorker):
    """Worker for Soil Health Card Portal scraping."""
    
    def __init__(self):
        super().__init__("SoilHealthCard", timeout=15)
    
    def fetch(self, region: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            # Try to access state-specific soil health data
            search_url = f"{SHC_PORTAL}/soilanalysis/districtwise"
            
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Extract soil health data from tables
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        row_text = ' '.join(c.get_text().strip() for c in cells).lower()
                        
                        # Check if this row matches our district/region
                        if district and district.lower() in row_text:
                            ph = self._extract_ph(row_text)
                            npk = self._extract_npk(row_text)
                            
                            if ph or any(npk.values()):
                                logger.info(f"[SHC] Found soil data for {district}")
                                return {
                                    "ph": ph,
                                    "n": npk.get('n'),
                                    "p": npk.get('p'),
                                    "k": npk.get('k'),
                                    "source": "Soil Health Card Portal",
                                    "confidence": 90
                                }
            
            return None
            
        except Exception as e:
            logger.warning(f"[SHC Portal] Error: {e}")
            return None


class WebSearchWorker(SoilWorker):
    """Worker for web search based soil research."""
    
    def __init__(self):
        super().__init__("WebSearch", timeout=20)
    
    def fetch(self, region: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            # Use DuckDuckGo search
            try:
                from duckduckgo_search import DDGS
                
                query = f"{district or region} {state} soil type NPK pH agriculture India"
                
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5))
                    
                    aggregated_text = ""
                    for r in results:
                        aggregated_text += f" {r.get('body', '')} "
                    
                    if aggregated_text:
                        soil_type = self._extract_soil_type(aggregated_text)
                        ph = self._extract_ph(aggregated_text)
                        npk = self._extract_npk(aggregated_text)
                        
                        if soil_type or ph:
                            logger.info(f"[WebSearch] Found soil data for {region}")
                            return {
                                "soil": soil_type,
                                "ph": ph,
                                "n": npk.get('n'),
                                "p": npk.get('p'),
                                "k": npk.get('k'),
                                "source": "Web Research",
                                "confidence": 65
                            }
            
            except ImportError:
                logger.warning("duckduckgo_search not installed")
            
            return None
            
        except Exception as e:
            logger.warning(f"[WebSearch] Error: {e}")
            return None


class NBSSWorker(SoilWorker):
    """Worker for National Bureau of Soil Survey."""
    
    def __init__(self):
        super().__init__("NBSS", timeout=12)
    
    def fetch(self, region: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            # Try NBSS soil map data
            search_url = f"{NBSS_URL}/soil-maps/{state.lower().replace(' ', '-')}"
            
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                
                soil_type = self._extract_soil_type(text)
                if soil_type:
                    logger.info(f"[NBSS] Found soil type for {region}: {soil_type}")
                    return {
                        "soil": soil_type,
                        "source": "NBSS Soil Survey",
                        "confidence": 88
                    }
            
            return None
            
        except Exception as e:
            logger.debug(f"[NBSS] Error: {e}")
            return None


class SoilResearchAgent:
    """
    Multi-source soil research agent using parallel workers.
    Researches unknown regions and synthesizes soil data.
    """
    
    def __init__(self, max_workers: int = 5):
        self._ensure_cache_dir()
        self.max_workers = max_workers
        
        # Initialize workers
        self.workers = [
            DataGovSoilWorker(),     # Government data
            SoilHealthCardWorker(),   # Soil Health Card
            WikipediaWorker(),        # Encyclopedia
            NBSSWorker(),             # Soil Survey
            WebSearchWorker(),        # Web search
        ]
        
        # Load regions database
        self.regions_db = self._load_regions_db()
        
        logger.info(f"Soil Research Agent initialized with {len(self.workers)} workers")
    
    def _ensure_cache_dir(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
    
    def _load_regions_db(self) -> Dict:
        """Load existing regions soil database."""
        db_path = os.path.join(os.path.dirname(__file__), '../data/regions_soil_db.json')
        try:
            with open(db_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _get_cache_key(self, region: str, state: str, district: str = None) -> str:
        key = f"soil_{region}_{state}_{district or ''}"
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    def _get_cached_data(self, cache_key: str) -> Optional[Dict]:
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        with cache_lock:
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cached = json.load(f)
                    cached_time = datetime.fromisoformat(cached['timestamp'])
                    if datetime.now() - cached_time < timedelta(days=CACHE_TTL_DAYS):
                        return cached['data']
                except:
                    pass
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        with cache_lock:
            try:
                with open(cache_file, 'w') as f:
                    json.dump({
                        'timestamp': datetime.now().isoformat(),
                        'data': data
                    }, f)
            except Exception as e:
                logger.warning(f"Cache save error: {e}")
    
    def research_soil(self, region: str, state: str = "Andhra Pradesh", 
                      district: str = None) -> Dict:
        """
        Research soil data for a region using parallel workers.
        
        Returns comprehensive soil data from multiple sources.
        """
        # Check existing database first
        db_result = self._check_database(region, state, district)
        if db_result:
            return db_result
        
        # Check cache
        cache_key = self._get_cache_key(region, state, district)
        cached = self._get_cached_data(cache_key)
        if cached:
            return cached
        
        # Research using parallel workers
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(worker.fetch, region, state, district): worker.name 
                for worker in self.workers
            }
            
            for future in as_completed(futures, timeout=30):
                worker_name = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.info(f"[{worker_name}] Found data: {result.get('soil', 'NPK data')}")
                except Exception as e:
                    logger.warning(f"[{worker_name}] Failed: {e}")
        
        # Aggregate results
        if results:
            aggregated = self._aggregate_results(results, region, state)
            self._save_to_cache(cache_key, aggregated)
            return aggregated
        
        # Fallback to state defaults
        logger.info(f"Using state default for {region}")
        return self._get_state_default(state, region)
    
    def _check_database(self, region: str, state: str, district: str = None) -> Optional[Dict]:
        """Check if region exists in database."""
        state_data = self.regions_db.get(state, {})
        
        # Check district level
        if district and district in state_data:
            district_data = state_data[district]
            if 'mandals' in district_data and region in district_data['mandals']:
                mandal_data = district_data['mandals'][region]
                return {
                    "soil": mandal_data.get('soil'),
                    "ph": mandal_data.get('ph'),
                    "n": mandal_data.get('n'),
                    "p": mandal_data.get('p'),
                    "k": mandal_data.get('k'),
                    "zone": mandal_data.get('zone'),
                    "source": "Database",
                    "confidence": 95
                }
        
        # Check if region is a district
        if region in state_data:
            district_data = state_data[region]
            return {
                "soil": district_data.get('default_soil'),
                "ph": 7.0,  # Default
                "source": "Database (District)",
                "confidence": 85
            }
        
        return None
    
    def _aggregate_results(self, results: List[Dict], region: str, state: str) -> Dict:
        """Aggregate results from multiple sources."""
        # Collect all values
        soil_types = []
        ph_values = []
        n_values = []
        p_values = []
        k_values = []
        sources = []
        total_confidence = 0
        
        for r in results:
            confidence = r.get('confidence', 50)
            total_confidence += confidence
            sources.append(r.get('source', 'Unknown'))
            
            if r.get('soil'):
                soil_types.append((r['soil'], confidence))
            if r.get('ph'):
                ph_values.append((r['ph'], confidence))
            if r.get('n'):
                n_values.append((r['n'], confidence))
            if r.get('p'):
                p_values.append((r['p'], confidence))
            if r.get('k'):
                k_values.append((r['k'], confidence))
        
        # Weighted selection for soil type (most confident wins)
        if soil_types:
            soil_types.sort(key=lambda x: x[1], reverse=True)
            final_soil = soil_types[0][0]
        else:
            final_soil = STATE_DEFAULT_SOILS.get(state, {}).get('soil', 'Loamy')
        
        # Weighted average for numerical values
        def weighted_avg(values: List[Tuple[float, int]]) -> Optional[float]:
            if not values:
                return None
            total_weight = sum(w for _, w in values)
            if total_weight == 0:
                return None
            return sum(v * w for v, w in values) / total_weight
        
        final_ph = weighted_avg(ph_values)
        final_n = weighted_avg(n_values)
        final_p = weighted_avg(p_values)
        final_k = weighted_avg(k_values)
        
        # Use state defaults for missing values
        defaults = STATE_DEFAULT_SOILS.get(state, {"ph": 7.0, "n": 180, "p": 45, "k": 220})
        
        return {
            "soil": final_soil,
            "ph": round(final_ph, 1) if final_ph else defaults.get('ph', 7.0),
            "n": round(final_n) if final_n else defaults.get('n', 180),
            "p": round(final_p) if final_p else defaults.get('p', 45),
            "k": round(final_k) if final_k else defaults.get('k', 220),
            "zone": f"Researched data for {region}",
            "source": f"Aggregated ({len(results)} sources)",
            "sources": sources,
            "confidence": min(95, total_confidence // len(results) + 10),
            "researched": True
        }
    
    def _get_state_default(self, state: str, region: str) -> Dict:
        """Get state default soil values."""
        defaults = STATE_DEFAULT_SOILS.get(state, {
            "soil": "Loamy",
            "ph": 7.0,
            "n": 180,
            "p": 45,
            "k": 220
        })
        
        return {
            "soil": defaults.get('soil', 'Loamy'),
            "ph": defaults.get('ph', 7.0),
            "n": defaults.get('n', 180),
            "p": defaults.get('p', 45),
            "k": defaults.get('k', 220),
            "zone": f"State default for {state}",
            "source": "State Default",
            "confidence": 70
        }
    
    def update_database(self, region: str, state: str, district: str, data: Dict) -> bool:
        """Add researched data to the regions database."""
        try:
            db_path = os.path.join(os.path.dirname(__file__), '../data/regions_soil_db.json')
            
            if state not in self.regions_db:
                self.regions_db[state] = {}
            
            if district not in self.regions_db[state]:
                self.regions_db[state][district] = {
                    "default_soil": data.get('soil', 'Loamy'),
                    "mandals": {}
                }
            
            # Add mandal data
            self.regions_db[state][district]['mandals'][region] = {
                "soil": data.get('soil'),
                "ph": data.get('ph'),
                "n": data.get('n'),
                "p": data.get('p'),
                "k": data.get('k'),
                "zone": data.get('zone', ''),
                "source": "AI Research",
                "researched_at": datetime.now().isoformat()
            }
            
            with open(db_path, 'w') as f:
                json.dump(self.regions_db, f, indent=4)
            
            logger.info(f"Updated database with {region} soil data")
            return True
            
        except Exception as e:
            logger.error(f"Database update failed: {e}")
            return False


# Singleton instance
_soil_research_agent = None

def get_soil_research_agent() -> SoilResearchAgent:
    """Get or create soil research agent singleton."""
    global _soil_research_agent
    if _soil_research_agent is None:
        _soil_research_agent = SoilResearchAgent(max_workers=5)
    return _soil_research_agent

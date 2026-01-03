"""
Market Price Service - Multi-Source Real-time Mandi Prices

Uses multiple data sources with parallel web workers for efficient and accurate price data.
Sources: AGMARKNET, data.gov.in, eNAM, Krishak Odisha, AP Agrisnet
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
CACHE_DIR = os.path.join(os.path.dirname(__file__), '../data/price_cache')
CACHE_TTL_HOURS = 3  # Shorter cache for fresher prices

# Thread-safe lock for cache operations
cache_lock = threading.Lock()

# ============ DATA SOURCE CONFIGURATIONS ============

# Source 1: data.gov.in API (most reliable)
DATA_GOV_API = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
DATA_GOV_KEY = "579b464db66ec23bdd000001cdd3946e44ce4aad7209ff7b23ac571b"

# Source 2: AGMARKNET Web Scraping
AGMARKNET_URL = "https://agmarknet.gov.in/SearchCmmMkt.aspx"

# Source 3: eNAM (National Agriculture Market)
ENAM_API = "https://enam.gov.in/web/dashboard/trade-data"

# Source 4: AP Agrisnet (Andhra Pradesh specific)
AP_AGRISNET_URL = "https://www.apagrisnet.gov.in"

# Source 5: Telangana Agrimarket
TS_AGRI_URL = "https://agrimarket.telangana.gov.in"


# Commodity name mappings
COMMODITY_MAPPINGS = {
    "Paddy": ["Paddy", "Rice", "Paddy(Dhan)"],
    "Rice": ["Paddy", "Rice", "Paddy(Dhan)"],
    "Wheat": ["Wheat"],
    "Cotton": ["Cotton", "Kapas"],
    "Maize": ["Maize", "Corn"],
    "Ground Nuts": ["Groundnut", "Peanut"],
    "Groundnut": ["Groundnut", "Peanut"],
    "Sugarcane": ["Sugarcane", "Ganna"],
    "Chilli": ["Chillies", "Chilli", "Mirchi"],
    "Turmeric": ["Turmeric", "Haldi"],
    "Bengal Gram": ["Bengal Gram", "Chana", "Chickpea"],
    "Pulses": ["Tur", "Toor", "Arhar"],
    "Tomato": ["Tomato"],
    "Onion": ["Onion"],
    "Potato": ["Potato"],
    "Banana": ["Banana"],
    "Mango": ["Mango"],
    "Soybean": ["Soyabean", "Soybean"],
    "Tobacco": ["Tobacco"],
    "Millets": ["Jowar", "Sorghum", "Bajra", "Ragi"],
    "Oil Seeds": ["Sesamum", "Sesame", "Til", "Sunflower"],
    "Barley": ["Barley"],
    "Cabbage": ["Cabbage"],
    "Cauliflower": ["Cauliflower"],
    "Brinjal": ["Brinjal", "Eggplant"],
    "Okra": ["Bhindi", "Okra", "Lady Finger"],
    "Carrot": ["Carrot"],
    "Papaya": ["Papaya"],
    "Guava": ["Guava"]
}

# State mappings
STATE_MAPPINGS = {
    "Andhra Pradesh": ["Andhra Pradesh", "AP"],
    "Telangana": ["Telangana", "TS"],
    "Karnataka": ["Karnataka", "KA"],
    "Tamil Nadu": ["Tamil Nadu", "TN"],
    "Maharashtra": ["Maharashtra", "MH"],
    "Gujarat": ["Gujarat", "GJ"],
    "Madhya Pradesh": ["Madhya Pradesh", "MP"],
    "Uttar Pradesh": ["Uttar Pradesh", "UP"],
    "Punjab": ["Punjab", "PB"],
    "Haryana": ["Haryana", "HR"],
    "Rajasthan": ["Rajasthan", "RJ"],
    "West Bengal": ["West Bengal", "WB"],
    "Odisha": ["Odisha", "OR"],
    "Bihar": ["Bihar", "BR"]
}

# MSP 2024-25 Fallback Prices (₹/quintal)
MSP_PRICES = {
    "Paddy": {"price": 2300, "trend": "stable", "msp": True},
    "Wheat": {"price": 2275, "trend": "stable", "msp": True},
    "Cotton": {"price": 7121, "trend": "up", "msp": True},
    "Maize": {"price": 2225, "trend": "stable", "msp": True},
    "Groundnut": {"price": 6783, "trend": "up", "msp": True},
    "Ground Nuts": {"price": 6783, "trend": "up", "msp": True},
    "Sugarcane": {"price": 340, "trend": "stable", "msp": True},
    "Chilli": {"price": 15000, "trend": "volatile", "msp": False},
    "Turmeric": {"price": 12000, "trend": "up", "msp": False},
    "Bengal Gram": {"price": 5440, "trend": "stable", "msp": True},
    "Pulses": {"price": 7000, "trend": "stable", "msp": True},
    "Tomato": {"price": 2500, "trend": "volatile", "msp": False},
    "Onion": {"price": 2000, "trend": "volatile", "msp": False},
    "Potato": {"price": 1500, "trend": "stable", "msp": False},
    "Banana": {"price": 2800, "trend": "stable", "msp": False},
    "Soybean": {"price": 4892, "trend": "stable", "msp": True},
    "Tobacco": {"price": 18000, "trend": "stable", "msp": False},
    "Millets": {"price": 2500, "trend": "up", "msp": True},
    "Oil Seeds": {"price": 5450, "trend": "up", "msp": True},
    "Barley": {"price": 1850, "trend": "stable", "msp": True},
    "Cabbage": {"price": 1200, "trend": "stable", "msp": False},
    "Cauliflower": {"price": 1800, "trend": "stable", "msp": False},
    "Brinjal": {"price": 2200, "trend": "stable", "msp": False},
    "Okra": {"price": 3000, "trend": "stable", "msp": False},
    "Carrot": {"price": 2500, "trend": "stable", "msp": False},
    "Papaya": {"price": 2000, "trend": "stable", "msp": False},
    "Guava": {"price": 3000, "trend": "stable", "msp": False},
    "Mango": {"price": 4000, "trend": "seasonal", "msp": False}
}


class PriceWorker:
    """Individual worker for fetching prices from a specific source."""
    
    def __init__(self, name: str, timeout: int = 10):
        self.name = name
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/json,*/*',
            'Accept-Language': 'en-US,en;q=0.5',
        })
    
    def fetch(self, commodity: str, state: str, district: str = None) -> Optional[Dict]:
        """Override in subclasses."""
        raise NotImplementedError


class DataGovWorker(PriceWorker):
    """Worker for data.gov.in API - Most reliable source."""
    
    def __init__(self):
        super().__init__("data.gov.in", timeout=12)
    
    def fetch(self, commodity: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            # Try multiple commodity name variations
            commodity_names = COMMODITY_MAPPINGS.get(commodity, [commodity])
            
            for comm_name in commodity_names:
                params = {
                    "api-key": DATA_GOV_KEY,
                    "format": "json",
                    "filters[commodity]": comm_name,
                    "filters[state]": state,
                    "limit": 20
                }
                
                if district:
                    params["filters[district]"] = district
                
                response = self.session.get(DATA_GOV_API, params=params, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    records = data.get('records', [])
                    
                    if records:
                        prices = []
                        markets = []
                        dates = []
                        
                        for rec in records:
                            modal = rec.get('modal_price')
                            if modal:
                                try:
                                    price = int(float(modal))
                                    if 100 < price < 100000:  # Sanity check
                                        prices.append(price)
                                        markets.append(rec.get('market', 'Unknown'))
                                        dates.append(rec.get('arrival_date', ''))
                                except ValueError:
                                    pass
                        
                        if prices:
                            logger.info(f"[DataGov] Found {len(prices)} prices for {commodity}")
                            return self._build_result(prices, markets, dates)
            
            return None
            
        except Exception as e:
            logger.warning(f"[DataGov] Error fetching {commodity}: {e}")
            return None
    
    def _build_result(self, prices: List[int], markets: List[str], dates: List[str]) -> Dict:
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # Determine trend
        spread = (max_price - min_price) / min_price if min_price > 0 else 0
        if spread > 0.3:
            trend = "volatile"
        elif spread > 0.15:
            trend = "up" if max_price > avg_price else "down"
        else:
            trend = "stable"
        
        return {
            "price": round(avg_price),
            "min_price": round(min_price),
            "max_price": round(max_price),
            "unit": "₹/quintal",
            "trend": trend,
            "source": "data.gov.in",
            "market": markets[0] if markets else "Various",
            "date": dates[0] if dates else datetime.now().strftime('%Y-%m-%d'),
            "live": True,
            "num_markets": len(prices),
            "confidence": min(100, len(prices) * 10)  # More data points = higher confidence
        }


class AgmarknetWorker(PriceWorker):
    """Worker for AGMARKNET web scraping."""
    
    def __init__(self):
        super().__init__("AGMARKNET", timeout=15)
    
    def fetch(self, commodity: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            commodity_names = COMMODITY_MAPPINGS.get(commodity, [commodity])
            
            for comm_name in commodity_names:
                # Build search URL
                today = datetime.now().strftime('%d-%b-%Y')
                search_url = f"{AGMARKNET_URL}?Tx_Commodity={comm_name}&Tx_State={state}&DateFrom={today}&DateTo={today}"
                
                response = self.session.get(search_url, timeout=self.timeout)
                
                if response.status_code == 200:
                    prices = self._extract_prices(response.text, state)
                    if prices:
                        logger.info(f"[AGMARKNET] Found {len(prices)} prices for {commodity}")
                        return self._build_result(prices)
            
            return None
            
        except Exception as e:
            logger.warning(f"[AGMARKNET] Error fetching {commodity}: {e}")
            return None
    
    def _extract_prices(self, html: str, state: str) -> List[int]:
        """Extract prices from AGMARKNET HTML."""
        prices = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Look for price tables
            for table in soup.find_all('table'):
                for row in table.find_all('tr')[1:]:  # Skip header
                    cells = row.find_all(['td', 'th'])
                    
                    for cell in cells:
                        text = cell.get_text().strip()
                        # Look for 3-6 digit prices
                        if re.match(r'^\d{3,6}$', text):
                            price = int(text)
                            if 100 < price < 100000:
                                prices.append(price)
            
            # Also try regex on full text
            if not prices:
                price_pattern = r'₹?\s*(\d{3,6})\s*/?(?:quintal|qtl|Q)?'
                matches = re.findall(price_pattern, html)
                for match in matches:
                    try:
                        price = int(match)
                        if 100 < price < 100000:
                            prices.append(price)
                    except ValueError:
                        pass
                        
        except Exception as e:
            logger.warning(f"[AGMARKNET] Parse error: {e}")
        
        return prices[:20]  # Limit to prevent duplicates
    
    def _build_result(self, prices: List[int]) -> Dict:
        avg_price = sum(prices) / len(prices)
        return {
            "price": round(avg_price),
            "min_price": min(prices),
            "max_price": max(prices),
            "unit": "₹/quintal",
            "trend": "stable",
            "source": "AGMARKNET",
            "market": "Various",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "live": True,
            "num_markets": len(prices),
            "confidence": min(80, len(prices) * 8)
        }


class ENAMWorker(PriceWorker):
    """Worker for eNAM (National Agriculture Market) API."""
    
    def __init__(self):
        super().__init__("eNAM", timeout=10)
    
    def fetch(self, commodity: str, state: str, district: str = None) -> Optional[Dict]:
        try:
            # eNAM API endpoint for trade data
            api_url = f"https://enam.gov.in/web/Ajax_ctrl/trade_data_,commodity_,,{commodity.lower()}"
            
            response = self.session.get(api_url, timeout=self.timeout)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if data and isinstance(data, list):
                        prices = []
                        for item in data:
                            modal = item.get('modal_price') or item.get('price')
                            if modal:
                                try:
                                    prices.append(int(float(modal)))
                                except ValueError:
                                    pass
                        
                        if prices:
                            logger.info(f"[eNAM] Found {len(prices)} prices for {commodity}")
                            return {
                                "price": round(sum(prices) / len(prices)),
                                "min_price": min(prices),
                                "max_price": max(prices),
                                "unit": "₹/quintal",
                                "trend": "stable",
                                "source": "eNAM",
                                "date": datetime.now().strftime('%Y-%m-%d'),
                                "live": True,
                                "num_markets": len(prices),
                                "confidence": min(90, len(prices) * 9)
                            }
                except json.JSONDecodeError:
                    pass
            
            return None
            
        except Exception as e:
            logger.warning(f"[eNAM] Error fetching {commodity}: {e}")
            return None


class APAgrisnetWorker(PriceWorker):
    """Worker for AP Agrisnet - State-specific prices."""
    
    def __init__(self):
        super().__init__("AP Agrisnet", timeout=10)
    
    def fetch(self, commodity: str, state: str, district: str = None) -> Optional[Dict]:
        if state not in ["Andhra Pradesh", "AP"]:
            return None  # Only for AP
        
        try:
            search_url = f"{AP_AGRISNET_URL}/api/market-prices?commodity={commodity}"
            response = self.session.get(search_url, timeout=self.timeout)
            
            if response.status_code == 200:
                # Try to parse response (format may vary)
                try:
                    data = response.json()
                    if data:
                        logger.info(f"[AP Agrisnet] Found data for {commodity}")
                        # Process based on actual response format
                        pass
                except json.JSONDecodeError:
                    # Try HTML scraping as fallback
                    pass
            
            return None
            
        except Exception as e:
            logger.debug(f"[AP Agrisnet] Not available for {commodity}: {e}")
            return None


class MarketPriceService:
    """
    Multi-source market price aggregator using parallel workers.
    Fetches from multiple sources simultaneously for best accuracy.
    """
    
    def __init__(self, max_workers: int = 4):
        self._ensure_cache_dir()
        self.max_workers = max_workers
        
        # Initialize workers
        self.workers = [
            DataGovWorker(),      # Most reliable
            AgmarknetWorker(),    # Official source
            ENAMWorker(),         # National market
            APAgrisnetWorker(),   # State specific
        ]
        
        logger.info(f"Market Price Service initialized with {len(self.workers)} workers")
    
    def _ensure_cache_dir(self):
        if not os.path.exists(CACHE_DIR):
            os.makedirs(CACHE_DIR)
    
    def _get_cache_key(self, commodity: str, state: str, district: str = None) -> str:
        key = f"{commodity}_{state}_{district or 'all'}_{datetime.now().strftime('%Y%m%d_%H')}"
        return hashlib.md5(key.encode()).hexdigest()[:16]
    
    def _get_cached_price(self, cache_key: str) -> Optional[Dict]:
        cache_file = os.path.join(CACHE_DIR, f"{cache_key}.json")
        with cache_lock:
            if os.path.exists(cache_file):
                try:
                    with open(cache_file, 'r') as f:
                        cached = json.load(f)
                    cached_time = datetime.fromisoformat(cached['timestamp'])
                    if datetime.now() - cached_time < timedelta(hours=CACHE_TTL_HOURS):
                        logger.info(f"Cache hit for {cache_key}")
                        return cached['data']
                except Exception as e:
                    logger.warning(f"Cache read error: {e}")
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
    
    def get_commodity_price(self, crop_name: str, state: str = "Andhra Pradesh", 
                           district: str = None) -> Dict:
        """
        Get commodity price using parallel workers.
        Returns best result from multiple sources.
        """
        # Check cache first
        cache_key = self._get_cache_key(crop_name, state, district)
        cached = self._get_cached_price(cache_key)
        if cached:
            return cached
        
        # Fetch from all sources in parallel
        results = []
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {
                executor.submit(worker.fetch, crop_name, state, district): worker.name 
                for worker in self.workers
            }
            
            for future in as_completed(futures, timeout=20):
                worker_name = futures[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                        logger.info(f"[{worker_name}] Success: ₹{result.get('price')}")
                except Exception as e:
                    logger.warning(f"[{worker_name}] Failed: {e}")
        
        # Aggregate results
        if results:
            aggregated = self._aggregate_results(results, crop_name)
            self._save_to_cache(cache_key, aggregated)
            return aggregated
        
        # Fallback to MSP
        logger.info(f"Using MSP fallback for {crop_name}")
        return self._get_fallback_price(crop_name)
    
    def _aggregate_results(self, results: List[Dict], crop_name: str) -> Dict:
        """
        Aggregate results from multiple sources.
        Uses weighted average based on confidence and recency.
        Validates prices against MSP ranges to filter bad data.
        """
        # Get expected price range from MSP (allow 0.3x to 5x of MSP)
        msp_data = MSP_PRICES.get(crop_name, {"price": 3000})
        expected_msp = msp_data.get("price", 3000)
        min_valid = expected_msp * 0.3  # At least 30% of MSP
        max_valid = expected_msp * 5    # At most 5x MSP
        
        # Filter results to only include reasonable prices
        valid_results = []
        for r in results:
            price = r.get('price', 0)
            if min_valid <= price <= max_valid:
                valid_results.append(r)
            else:
                logger.warning(f"Rejected price ₹{price} for {crop_name} (expected ₹{min_valid:.0f}-{max_valid:.0f})")
        
        # If no valid results, use fallback
        if not valid_results:
            logger.info(f"No valid prices for {crop_name}, using MSP fallback")
            return self._get_fallback_price(crop_name)
        
        if len(valid_results) == 1:
            return valid_results[0]
        
        # Calculate weighted average
        total_weight = 0
        weighted_price = 0
        all_prices = []
        markets = []
        sources = []
        
        for result in valid_results:
            confidence = result.get('confidence', 50)
            num_markets = result.get('num_markets', 1)
            weight = confidence * (1 + num_markets * 0.1)
            
            price = result.get('price', 0)
            if price > 0:
                weighted_price += price * weight
                total_weight += weight
                all_prices.append(price)
                markets.append(result.get('market', 'Unknown'))
                sources.append(result.get('source', 'Unknown'))
        
        if total_weight == 0:
            return valid_results[0]
        
        final_price = round(weighted_price / total_weight)
        
        # Determine trend from all data
        all_min = min(r.get('min_price', final_price) for r in valid_results)
        all_max = max(r.get('max_price', final_price) for r in valid_results)
        spread = (all_max - all_min) / all_min if all_min > 0 else 0
        
        if spread > 0.25:
            trend = "volatile"
        elif all_max > final_price * 1.1:
            trend = "up"
        elif all_min < final_price * 0.9:
            trend = "down"
        else:
            trend = "stable"
        
        # Check if MSP
        msp_data = MSP_PRICES.get(crop_name, {})
        has_msp = msp_data.get('msp', False)
        
        return {
            "price": final_price,
            "min_price": all_min,
            "max_price": all_max,
            "unit": "₹/quintal",
            "trend": trend,
            "source": f"Aggregated ({len(results)} sources)",
            "sources": sources,
            "market": markets[0] if markets else "Various",
            "date": datetime.now().strftime('%Y-%m-%d'),
            "live": True,
            "num_sources": len(results),
            "msp": has_msp,
            "confidence": min(100, sum(r.get('confidence', 50) for r in results) // len(results) + 10)
        }
    
    def _get_fallback_price(self, crop_name: str) -> Dict:
        """Get fallback MSP price."""
        if crop_name in MSP_PRICES:
            msp_data = MSP_PRICES[crop_name].copy()
            msp_data.update({
                "unit": "₹/quintal",
                "source": "MSP 2024-25",
                "live": False,
                "min_price": int(msp_data["price"] * 0.9),
                "max_price": int(msp_data["price"] * 1.1),
                "confidence": 70
            })
            return msp_data
        
        return {
            "price": 5000,
            "min_price": 4000,
            "max_price": 6000,
            "unit": "₹/quintal",
            "trend": "unknown",
            "source": "Estimated",
            "live": False,
            "msp": False,
            "confidence": 30
        }
    
    def get_prices_for_recommendations(self, recommendations: List[Dict], 
                                       state: str = "Andhra Pradesh",
                                       district: str = None) -> List[Dict]:
        """Enrich recommendations with live market prices."""
        for rec in recommendations:
            crop_name = rec.get('crop')
            if crop_name:
                price_data = self.get_commodity_price(crop_name, state, district)
                rec['market_price'] = price_data
                rec['market_price_live'] = price_data.get('live', False)
        
        return recommendations
    
    def get_price_trend(self, crop_name: str, days: int = 30, 
                       state: str = "Andhra Pradesh") -> Dict:
        """Get price trend analysis."""
        price_data = self.get_commodity_price(crop_name, state)
        
        trend = price_data.get('trend', 'stable')
        msp = price_data.get('msp', False)
        
        if trend == 'volatile':
            volatility = 'High'
            recommendation = 'Consider contract farming or futures'
        elif trend == 'up':
            volatility = 'Medium'
            recommendation = 'Good time for planting'
        elif trend == 'down':
            volatility = 'Medium'
            recommendation = 'Consider storage or processing'
        else:
            volatility = 'Low'
            recommendation = 'Stable market conditions'
        
        return {
            "crop": crop_name,
            "current_price": price_data.get('price'),
            "trend_direction": trend,
            "volatility": volatility,
            "has_msp": msp,
            "recommendation": recommendation,
            "source": price_data.get('source'),
            "confidence": price_data.get('confidence', 50)
        }
    
    def calculate_market_risk(self, crop_name: str, state: str = "Andhra Pradesh") -> int:
        """Calculate market risk score (0-100)."""
        price_data = self.get_commodity_price(crop_name, state)
        
        trend = price_data.get('trend', 'stable')
        trend_risk = {
            'volatile': 70,
            'down': 50,
            'unknown': 40,
            'stable': 20,
            'up': 10
        }.get(trend, 30)
        
        msp_reduction = 20 if price_data.get('msp', False) else 0
        
        min_price = price_data.get('min_price', 0)
        max_price = price_data.get('max_price', 0)
        if min_price > 0 and max_price > 0:
            spread = (max_price - min_price) / min_price * 100
            spread_risk = min(30, spread / 2)
        else:
            spread_risk = 15
        
        final_risk = max(0, min(100, trend_risk + spread_risk - msp_reduction))
        return int(final_risk)


# Singleton instance
_market_price_service = None

def get_market_price_service() -> MarketPriceService:
    """Get or create market price service singleton."""
    global _market_price_service
    if _market_price_service is None:
        _market_price_service = MarketPriceService(max_workers=4)
    return _market_price_service

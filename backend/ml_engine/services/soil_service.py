import json
import os
import pandas as pd
from collections import Counter

class SoilService:
    # Soil type mapping from Agritech to our standard
    SOIL_TYPE_MAPPING = {
        'Black': 'Black Cotton',
        'Alluvial': 'Alluvial',
        'Red': 'Red Soil',
        'Laterite': 'Laterite',
        'Peaty': 'Loamy',
        'Desert': 'Sandy',
        'Forest': 'Loamy',
        'Clay': 'Clay',
        'Sandy': 'Sandy',
        'Loamy': 'Loamy'
    }
    
    def __init__(self):
        self.db_path = os.path.join(os.path.dirname(__file__), '../data/regions_soil_db.json')
        self.raw_data = self._load_data()
        self.districts_map = self._flatten_districts()
        self.mandal_index = self._build_lookup_index()
        self.agritech_data = self._load_agritech_data()
    
    def _load_agritech_data(self):
        """Load Agritech.csv for fallback soil lookups."""
        try:
            agritech_path = os.path.join(os.path.dirname(__file__), '../../../Agritech.csv')
            if not os.path.exists(agritech_path):
                agritech_path = os.path.join(os.path.dirname(__file__), '../../Agritech.csv')
            if not os.path.exists(agritech_path):
                agritech_path = os.path.join(os.path.dirname(__file__), '../data/Agritech.csv')
            if not os.path.exists(agritech_path):
                agritech_path = os.path.join(os.path.dirname(__file__), '../../../../Agritech.csv')
            
            if os.path.exists(agritech_path):
                df = pd.read_csv(agritech_path)
                print(f"✅ Loaded Agritech.csv with {len(df)} records")
                return df
            else:
                print("⚠️ Agritech.csv not found, using DB only")
                return None
        except Exception as e:
            print(f"⚠️ Error loading Agritech.csv: {e}")
            return None
    
    def _lookup_agritech(self, location: str):
        """Look up soil data from Agritech.csv by district name."""
        if self.agritech_data is None:
            return None
        
        location_lower = location.lower().strip()
        
        # Search in district column
        matches = self.agritech_data[
            self.agritech_data['district'].str.lower().str.strip() == location_lower
        ]
        
        if len(matches) == 0:
            # Try partial match
            matches = self.agritech_data[
                self.agritech_data['district'].str.lower().str.contains(location_lower, na=False)
            ]
        
        if len(matches) > 0:
            # Get most common soil type
            soil_counts = Counter(matches['soil_type'])
            most_common_soil = soil_counts.most_common(1)[0][0]
            mapped_soil = self.SOIL_TYPE_MAPPING.get(most_common_soil, most_common_soil)
            
            # Calculate averages
            avg_ph = matches['soil_pH'].mean()
            avg_n = matches['nitrogen_mgkg'].mean()
            avg_p = matches['phosphorus_mgkg'].mean()
            avg_k = matches['potassium_mgkg'].mean()
            avg_lat = matches['latitude'].mean()
            avg_lon = matches['longitude'].mean()
            state = matches['state'].iloc[0]
            
            print(f"✅ Found {location} in Agritech.csv: {most_common_soil} → {mapped_soil}")
            
            return {
                "soil": mapped_soil,
                "original_soil": most_common_soil,
                "ph": round(avg_ph, 2),
                "n": round(avg_n, 0),
                "p": round(avg_p, 0),
                "k": round(avg_k, 0),
                "lat": round(avg_lat, 4),
                "lon": round(avg_lon, 4),
                "zone": f"{state} Region",
                "source": "Agritech.csv"
            }
        
        return None

    def _load_data(self):
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading soil DB: {e}")
            return {}

    def _flatten_districts(self):
        """Flattens State -> District hierarchy into a single District map."""
        flat_map = {}
        for state, districts in self.raw_data.items():
            for district_name, district_data in districts.items():
                flat_map[district_name] = district_data
        return flat_map

    def _build_lookup_index(self):
        """Builds a reverse lookup map: Mandal -> District"""
        index = {}
        for district, d_data in self.districts_map.items():
            mandals = d_data.get("mandals", {})
            for mandal in mandals:
                # Store lowercase for case-insensitive lookup
                index[mandal.lower()] = district
        return index

    def get_soil_info(self, district: str, mandal: str = None):
        """
        Retrieves soil info for a given District and Mandal.
        Auto-detects District if only Mandal is provided.
        """
        # Normalize inputs
        raw_district = district.strip() if district else ""
        raw_mandal = mandal.strip() if mandal else ""
        
        district_key = raw_district.title()
        mandal_key = raw_mandal.title()

        # 1. Direct District Lookup (using flattened map)
        if district_key in self.districts_map:
            district_data = self.districts_map[district_key]
            # Try to find mandal in this district
            if mandal_key and mandal_key in district_data.get("mandals", {}):
                return district_data["mandals"][mandal_key]
            # If mandal not found or not provided, return district default
            default_soil = district_data.get("default_soil", "Loamy")
            return {
                "soil": default_soil,
                "ph": 7.0,
                "n": 150,
                "p": 50,
                "k": 150,
                "zone": f"General zone of {district_key}"
            }

        # 2. Global Mandal Lookup (if District not found)
        # Treat the 'district' input as a potential Mandal name (e.g. user searched "Amalapuram")
        search_term = raw_district.lower()
        if search_term in self.mandal_index:
            detected_district = self.mandal_index[search_term]
            detected_mandal = raw_district.title() # The input was actually a mandal
            
            # Retrieve the specific mandal data
            return self.districts_map[detected_district]["mandals"][detected_mandal]
        
        # 3. Agritech.csv Lookup (NEW - check real data)
        agritech_result = self._lookup_agritech(raw_district)
        if agritech_result:
            return agritech_result
        
        # 4. Fallback
        return {
            "soil": "Loamy",
            "ph": 7.0,
            "n": 150,
            "p": 50,
            "k": 150,
            "zone": "Unknown Region"
        }

    def detect_location_from_lat_lon(self, lat, lon):
        # Placeholder for Reverse Geocoding Logic
        pass

    def update_soil_db(self, district: str, mandal: str, new_soil_type: str):
        """
        Updates the soil type for a specific Mandal (or District default) and persists to DB.
        """
        district = district.title() if district else ""
        mandal = mandal.title() if mandal else ""
        
        if not district:
            print("Error: District is required for update.")
            return False

        # Ensure District exists in raw_data (State lookup needed)
        # For simplicity, we search which state contains this district
        target_state = None
        for state, districts in self.raw_data.items():
            if district in districts:
                target_state = state
                break
        
        if not target_state:
            # Default to AP if not found (or create new state logic)
            target_state = "Andhra Pradesh" 
            if target_state not in self.raw_data:
                self.raw_data[target_state] = {}
            if district not in self.raw_data[target_state]:
                self.raw_data[target_state][district] = {"default_soil": new_soil_type, "mandals": {}}

        # Update Logic
        district_data = self.raw_data[target_state][district]
        
        if mandal:
            if "mandals" not in district_data:
                district_data["mandals"] = {}
            
            # Update or Create Mandal Entry
            if mandal in district_data["mandals"]:
                district_data["mandals"][mandal]["soil"] = new_soil_type
            else:
                district_data["mandals"][mandal] = {
                    "soil": new_soil_type,
                    "ph": 7.0, "n": 150, "p": 50, "k": 150, "zone": "User Verified"
                }
        else:
            # Update District Default
            district_data["default_soil"] = new_soil_type

        # Persist to File
        try:
            with open(self.db_path, 'w') as f:
                json.dump(self.raw_data, f, indent=4)
            
            # Refresh in-memory maps
            self.districts_map = self._flatten_districts()
            self.mandal_index = self._build_lookup_index()
            print(f"Successfully updated soil for {mandal}, {district} to {new_soil_type}")
            return True
        except Exception as e:
            print(f"Error saving soil DB: {e}")
            return False

    def get_soil_info_intelligent(self, district: str, mandal: str = None, state: str = None):
        """
        Retrieves soil info with intelligent fallback.
        If region is unknown, triggers AI research agent.
        
        Args:
            district: District name
            mandal: Mandal name (optional)
            state: State name (optional, for research)
            
        Returns:
            Soil data dict with source indicator
        """
        # First try standard lookup
        existing = self.get_soil_info(district, mandal)
        
        # Check if it's unknown or needs research
        if existing.get("zone") == "Unknown Region" or existing.get("source") == "fallback":
            try:
                # Import here to avoid circular imports
                from .soil_research_agent import SoilResearchAgent
                
                agent = SoilResearchAgent()
                
                print(f"🔍 Region '{district}' not in database. Starting AI research...")
                
                # Perform research
                researched_data = agent.research_region(district, mandal, state)
                
                if researched_data:
                    print(f"✅ Research complete! Found soil data for {district}")
                    return researched_data
                else:
                    print(f"⚠️ Research failed, using fallback data")
                    return existing
                    
            except Exception as e:
                print(f"⚠️ Research agent error: {e}")
                return existing
        
        return existing
    
    def force_research(self, district: str, mandal: str = None, state: str = None):
        """
        Forces re-research of a region, even if data exists.
        
        Args:
            district: District name
            mandal: Mandal name (optional)
            state: State name (optional)
            
        Returns:
            Researched soil data or None
        """
        try:
            from .soil_research_agent import SoilResearchAgent
            
            agent = SoilResearchAgent()
            print(f"🔄 Force re-researching soil data for {district}...")
            
            return agent.research_region(district, mandal, state)
            
        except Exception as e:
            print(f"❌ Research failed: {e}")
            return None

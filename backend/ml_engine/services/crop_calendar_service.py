"""
Crop Calendar Service for KisanMitra
Provides optimal sowing windows and harvest date estimation.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# Crop Calendar Database for Andhra Pradesh / Telangana
# Format: {crop: {season: {sow_start, sow_end, duration_days, harvest_window}}}
CROP_CALENDAR_AP = {
    "Paddy": {
        "Kharif": {
            "sow_start": (6, 1),   # June 1
            "sow_end": (7, 31),    # July 31
            "sow_window": "June - July",
            "duration_days": 120,
            "harvest_window": "October - November",
            "activities": [
                {"day": -15, "activity": "Nursery preparation", "type": "pre_sowing"},
                {"day": 0, "activity": "Transplanting", "type": "sowing"},
                {"day": 21, "activity": "First top dressing (Urea)", "type": "fertilizer"},
                {"day": 45, "activity": "Second top dressing", "type": "fertilizer"},
                {"day": 60, "activity": "Panicle initiation - critical irrigation", "type": "irrigation"},
                {"day": 90, "activity": "Grain filling stage", "type": "observation"},
                {"day": 120, "activity": "Harvesting", "type": "harvest"}
            ]
        },
        "Rabi": {
            "sow_start": (11, 1),  # November 1
            "sow_end": (12, 15),   # December 15
            "sow_window": "November - December",
            "duration_days": 130,
            "harvest_window": "March - April",
            "activities": [
                {"day": -15, "activity": "Nursery preparation", "type": "pre_sowing"},
                {"day": 0, "activity": "Transplanting", "type": "sowing"},
                {"day": 21, "activity": "First top dressing", "type": "fertilizer"},
                {"day": 45, "activity": "Second top dressing", "type": "fertilizer"},
                {"day": 130, "activity": "Harvesting", "type": "harvest"}
            ]
        }
    },
    "Cotton": {
        "Kharif": {
            "sow_start": (5, 15),  # May 15
            "sow_end": (7, 15),    # July 15
            "sow_window": "May - July (before monsoon)",
            "duration_days": 180,
            "harvest_window": "November - January",
            "activities": [
                {"day": 0, "activity": "Sowing", "type": "sowing"},
                {"day": 20, "activity": "Thinning & gap filling", "type": "management"},
                {"day": 30, "activity": "First earthing up", "type": "management"},
                {"day": 45, "activity": "First intercultivation", "type": "management"},
                {"day": 60, "activity": "Flowering stage - critical", "type": "observation"},
                {"day": 90, "activity": "Boll formation", "type": "observation"},
                {"day": 120, "activity": "First picking", "type": "harvest"},
                {"day": 150, "activity": "Second picking", "type": "harvest"},
                {"day": 180, "activity": "Final picking", "type": "harvest"}
            ]
        }
    },
    "Maize": {
        "Kharif": {
            "sow_start": (6, 15),  # June 15
            "sow_end": (7, 31),    # July 31
            "sow_window": "June - July",
            "duration_days": 100,
            "harvest_window": "September - October",
            "activities": [
                {"day": 0, "activity": "Sowing", "type": "sowing"},
                {"day": 25, "activity": "First top dressing (Urea)", "type": "fertilizer"},
                {"day": 45, "activity": "Second top dressing", "type": "fertilizer"},
                {"day": 55, "activity": "Tasseling stage - critical", "type": "observation"},
                {"day": 100, "activity": "Harvesting at 20% moisture", "type": "harvest"}
            ]
        },
        "Rabi": {
            "sow_start": (10, 15),
            "sow_end": (11, 30),
            "sow_window": "October - November",
            "duration_days": 110,
            "harvest_window": "February - March",
            "activities": [
                {"day": 0, "activity": "Sowing", "type": "sowing"},
                {"day": 25, "activity": "First top dressing", "type": "fertilizer"},
                {"day": 45, "activity": "Second top dressing", "type": "fertilizer"},
                {"day": 110, "activity": "Harvesting", "type": "harvest"}
            ]
        }
    },
    "Chilli": {
        "Kharif": {
            "sow_start": (6, 1),
            "sow_end": (8, 15),
            "sow_window": "June - August",
            "duration_days": 150,
            "harvest_window": "November - February",
            "activities": [
                {"day": -30, "activity": "Nursery sowing", "type": "pre_sowing"},
                {"day": 0, "activity": "Transplanting (30-40 day seedlings)", "type": "sowing"},
                {"day": 20, "activity": "First fertilizer dose", "type": "fertilizer"},
                {"day": 40, "activity": "Second fertilizer dose", "type": "fertilizer"},
                {"day": 60, "activity": "Flowering starts", "type": "observation"},
                {"day": 90, "activity": "First harvest", "type": "harvest"},
                {"day": 150, "activity": "Final harvest", "type": "harvest"}
            ]
        },
        "Rabi": {
            "sow_start": (9, 15),
            "sow_end": (10, 31),
            "sow_window": "September - October",
            "duration_days": 160,
            "harvest_window": "February - April",
            "activities": [
                {"day": -30, "activity": "Nursery sowing", "type": "pre_sowing"},
                {"day": 0, "activity": "Transplanting", "type": "sowing"},
                {"day": 160, "activity": "Harvest completion", "type": "harvest"}
            ]
        }
    },
    "Wheat": {
        "Rabi": {
            "sow_start": (11, 1),
            "sow_end": (11, 30),
            "sow_window": "November (optimal 15-25 Nov)",
            "duration_days": 120,
            "harvest_window": "March - April",
            "activities": [
                {"day": 0, "activity": "Sowing (seed drill)", "type": "sowing"},
                {"day": 21, "activity": "First irrigation (Crown root)", "type": "irrigation"},
                {"day": 42, "activity": "Second irrigation (Tillering)", "type": "irrigation"},
                {"day": 63, "activity": "Third irrigation (Jointing)", "type": "irrigation"},
                {"day": 84, "activity": "Fourth irrigation (Flowering)", "type": "irrigation"},
                {"day": 105, "activity": "Fifth irrigation (Milking)", "type": "irrigation"},
                {"day": 120, "activity": "Harvesting at 14% moisture", "type": "harvest"}
            ]
        }
    },
    "Pulses": {
        "Rabi": {
            "sow_start": (10, 1),
            "sow_end": (10, 31),
            "sow_window": "October",
            "duration_days": 100,
            "harvest_window": "January - February",
            "activities": [
                {"day": 0, "activity": "Sowing with Rhizobium treatment", "type": "sowing"},
                {"day": 1, "activity": "Pre-emergence herbicide", "type": "management"},
                {"day": 30, "activity": "Flowering stage", "type": "observation"},
                {"day": 45, "activity": "Pod formation - critical", "type": "observation"},
                {"day": 100, "activity": "Harvesting when pods turn brown", "type": "harvest"}
            ]
        }
    },
    "Ground Nuts": {
        "Kharif": {
            "sow_start": (6, 15),
            "sow_end": (7, 15),
            "sow_window": "June mid - July mid",
            "duration_days": 110,
            "harvest_window": "October - November",
            "activities": [
                {"day": 0, "activity": "Sowing (depth 5cm)", "type": "sowing"},
                {"day": 25, "activity": "First hoeing", "type": "management"},
                {"day": 35, "activity": "Flowering & Gypsum application", "type": "fertilizer"},
                {"day": 45, "activity": "Earthing up (pegging stage)", "type": "management"},
                {"day": 110, "activity": "Harvest when leaves turn yellow", "type": "harvest"}
            ]
        }
    }
}


class CropCalendarService:
    """
    Provides crop calendar information and optimal timing recommendations.
    """
    
    def __init__(self):
        self.calendar = CROP_CALENDAR_AP
    
    def get_optimal_sowing_window(self, crop: str, season: str = None) -> Optional[Dict]:
        """
        Get optimal sowing window for a crop.
        
        Args:
            crop: Crop name
            season: Specific season, or None for current season
            
        Returns:
            Sowing window info dict
        """
        crop = self._normalize_crop(crop)
        crop_data = self.calendar.get(crop)
        
        if not crop_data:
            return None
        
        if season:
            season_data = crop_data.get(season)
            if season_data:
                return self._format_sowing_info(crop, season, season_data)
        
        # Return all available seasons
        windows = []
        for s, data in crop_data.items():
            windows.append(self._format_sowing_info(crop, s, data))
        
        return windows if len(windows) > 1 else windows[0] if windows else None
    
    def _format_sowing_info(self, crop: str, season: str, data: Dict) -> Dict:
        """Format sowing information."""
        today = datetime.now()
        current_year = today.year
        
        sow_start = datetime(current_year, data["sow_start"][0], data["sow_start"][1])
        sow_end = datetime(current_year, data["sow_end"][0], data["sow_end"][1])
        
        # Adjust year if needed
        if sow_start < today - timedelta(days=120):
            sow_start = sow_start.replace(year=current_year + 1)
            sow_end = sow_end.replace(year=current_year + 1)
        
        status = "within_window" if sow_start <= today <= sow_end else \
                 "upcoming" if today < sow_start else "passed"
        
        days_until = (sow_start - today).days if status == "upcoming" else 0
        days_remaining = (sow_end - today).days if status == "within_window" else 0
        
        return {
            "crop": crop,
            "season": season,
            "sow_window": data["sow_window"],
            "sow_start": sow_start.strftime("%d %b"),
            "sow_end": sow_end.strftime("%d %b"),
            "duration_days": data["duration_days"],
            "harvest_window": data["harvest_window"],
            "status": status,
            "days_until_sowing": days_until,
            "days_remaining_in_window": days_remaining
        }
    
    def get_harvest_date(self, crop: str, sowing_date: datetime = None, 
                         season: str = None) -> Optional[Dict]:
        """
        Estimate harvest date based on sowing date.
        
        Args:
            crop: Crop name
            sowing_date: Date of sowing (defaults to today)
            season: Season name
            
        Returns:
            Harvest estimation dict
        """
        crop = self._normalize_crop(crop)
        crop_data = self.calendar.get(crop)
        
        if not crop_data:
            return None
        
        if not sowing_date:
            sowing_date = datetime.now()
        
        if not season:
            season = self._determine_season_for_date(sowing_date)
        
        season_data = crop_data.get(season)
        if not season_data:
            # Try any available season
            season = list(crop_data.keys())[0]
            season_data = crop_data[season]
        
        duration = season_data["duration_days"]
        harvest_date = sowing_date + timedelta(days=duration)
        days_remaining = (harvest_date - datetime.now()).days
        
        return {
            "crop": crop,
            "season": season,
            "sowing_date": sowing_date.strftime("%d %b %Y"),
            "estimated_harvest": harvest_date.strftime("%d %b %Y"),
            "duration_days": duration,
            "days_until_harvest": max(0, days_remaining),
            "stage": self._get_current_stage(sowing_date, season_data)
        }
    
    def get_upcoming_activities(self, crop: str, sowing_date: datetime = None,
                                 season: str = None, days_ahead: int = 14) -> List[Dict]:
        """
        Get upcoming activities for the next N days.
        
        Args:
            crop: Crop name
            sowing_date: Date of sowing
            season: Season name
            days_ahead: Days to look ahead
            
        Returns:
            List of upcoming activities
        """
        crop = self._normalize_crop(crop)
        crop_data = self.calendar.get(crop)
        
        if not crop_data:
            return []
        
        if not sowing_date:
            sowing_date = datetime.now()
        
        if not season:
            season = self._determine_season_for_date(sowing_date)
        
        season_data = crop_data.get(season, list(crop_data.values())[0])
        activities = season_data.get("activities", [])
        
        today = datetime.now()
        days_since_sowing = (today - sowing_date).days
        
        upcoming = []
        for act in activities:
            activity_day = act["day"]
            days_until = activity_day - days_since_sowing
            
            if 0 <= days_until <= days_ahead:
                activity_date = today + timedelta(days=days_until)
                upcoming.append({
                    "activity": act["activity"],
                    "type": act["type"],
                    "date": activity_date.strftime("%d %b"),
                    "days_until": days_until,
                    "day_after_sowing": activity_day
                })
        
        upcoming.sort(key=lambda x: x["days_until"])
        return upcoming
    
    def _get_current_stage(self, sowing_date: datetime, season_data: Dict) -> str:
        """Determine current crop stage."""
        days_since = (datetime.now() - sowing_date).days
        activities = season_data.get("activities", [])
        
        if days_since < 0:
            return "Pre-sowing"
        
        current_stage = "Sowing"
        for act in activities:
            if days_since >= act["day"]:
                current_stage = act["activity"]
            else:
                break
        
        return current_stage
    
    def _determine_season_for_date(self, date: datetime) -> str:
        """Determine season based on date."""
        month = date.month
        if 6 <= month <= 9:
            return "Kharif"
        elif 10 <= month <= 2:
            return "Rabi"
        else:
            return "Zaid"
    
    def _normalize_crop(self, crop: str) -> str:
        """Normalize crop name."""
        crop_mapping = {
            "rice": "Paddy",
            "paddy": "Paddy",
            "cotton": "Cotton",
            "chilli": "Chilli",
            "chili": "Chilli",
            "maize": "Maize",
            "corn": "Maize",
            "wheat": "Wheat",
            "pulses": "Pulses",
            "dal": "Pulses",
            "groundnut": "Ground Nuts",
            "groundnuts": "Ground Nuts",
            "peanut": "Ground Nuts",
        }
        return crop_mapping.get(crop.lower(), crop)
    
    def get_summary_sms(self, crop: str, sowing_date: datetime = None) -> str:
        """Generate SMS-friendly calendar summary."""
        window = self.get_optimal_sowing_window(crop)
        
        if not window:
            return f"Calendar data not available for {crop}."
        
        if isinstance(window, list):
            window = window[0]
        
        text = f"CROP CALENDAR - {crop.upper()}\n"
        text += "=" * 20 + "\n\n"
        text += f"Season: {window['season']}\n"
        text += f"Sow: {window['sow_window']}\n"
        text += f"Duration: {window['duration_days']} days\n"
        text += f"Harvest: {window['harvest_window']}\n\n"
        
        if window["status"] == "within_window":
            text += f"STATUS: Good time to sow!\n"
            text += f"{window['days_remaining_in_window']} days left in window."
        elif window["status"] == "upcoming":
            text += f"STATUS: {window['days_until_sowing']} days until sowing window."
        else:
            text += "STATUS: Sowing window passed for this season."
        
        return text


# Singleton
_calendar_service = None

def get_crop_calendar_service() -> CropCalendarService:
    global _calendar_service
    if _calendar_service is None:
        _calendar_service = CropCalendarService()
    return _calendar_service

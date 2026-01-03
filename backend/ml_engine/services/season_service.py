from datetime import datetime

class SeasonService:
    @staticmethod
    def get_season(month: int = None) -> str:
        """
        Determines the agricultural season based on the month.
        Kharif: June (6) - September (9)
        Rabi: October (10) - February (2)
        Zaid: March (3) - May (5)
        """
        if month is None:
            month = datetime.now().month

        if 6 <= month <= 9:
            return "Kharif"
        elif 3 <= month <= 5:
            return "Zaid"
        else:
            # October, November, December, January, February
            return "Rabi"

    @staticmethod
    def get_current_season_details():
        season = SeasonService.get_season()
        details = {
            "Kharif": "Monsoon season. Crops require good rainfall. (June - Sept)",
            "Rabi": "Winter season. Crops require cool weather. (Oct - Feb)",
            "Zaid": "Summer season. Short duration crops. (March - May)"
        }
        return {
            "season": season,
            "description": details.get(season, "")
        }

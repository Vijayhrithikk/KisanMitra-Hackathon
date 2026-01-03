import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

class DataLoader:
    def __init__(self, data_path):
        self.data_path = data_path

    def load_data(self):
        """
        Loads the core dataset.
        """
        if not os.path.exists(self.data_path):
            logger.error(f"Data file not found at: {self.data_path}")
            raise FileNotFoundError(f"Data file not found at: {self.data_path}")

        try:
            df = pd.read_csv(self.data_path)
            logger.info(f"Loaded {len(df)} records from {self.data_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            raise

    def get_soil_stats(self, df):
        """
        Returns basic stats about the dataset for verification.
        """
        return {
            "total_records": len(df),
            "columns": list(df.columns),
            "soil_types": df['Soil Type'].unique().tolist() if 'Soil Type' in df.columns else [],
            "crops": df['Crop Type'].unique().tolist() if 'Crop Type' in df.columns else []
        }

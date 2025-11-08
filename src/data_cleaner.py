"""
Formula 1 Data Cleaning and Preparation
Handles missing values, data normalization, and merging of tables
"""

import pandas as pd
import numpy as np
from pathlib import Path


class F1DataCleaner:
    """Clean and prepare F1 data for analysis"""
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.races = None
        self.drivers = None
        self.constructors = None
        self.results = None
        self.qualifying = None
        self.pitstops = None
        self.laptimes = None
        self.circuits = None
        
    def load_data(self):
        """Load all CSV files"""
        print("Loading data files...")
        
        self.races = pd.read_csv(self.data_dir / "races.csv")
        self.drivers = pd.read_csv(self.data_dir / "drivers.csv")
        self.constructors = pd.read_csv(self.data_dir / "constructors.csv")
        self.results = pd.read_csv(self.data_dir / "results.csv")
        
        # Optional files
        if (self.data_dir / "qualifying.csv").exists():
            self.qualifying = pd.read_csv(self.data_dir / "qualifying.csv")
        if (self.data_dir / "pitstops.csv").exists():
            self.pitstops = pd.read_csv(self.data_dir / "pitstops.csv")
        if (self.data_dir / "laptimes.csv").exists():
            self.laptimes = pd.read_csv(self.data_dir / "laptimes.csv")
        if (self.data_dir / "circuits.csv").exists():
            self.circuits = pd.read_csv(self.data_dir / "circuits.csv")
        
        print("Data loaded successfully!")
        return self
    
    def clean_races(self):
        """Clean races data"""
        if self.races is None:
            return self
        
        # Convert date to datetime
        if 'date' in self.races.columns:
            self.races['date'] = pd.to_datetime(self.races['date'], errors='coerce')
        
        # Ensure raceId is numeric
        self.races['raceId'] = pd.to_numeric(self.races['raceId'], errors='coerce')
        self.races['year'] = pd.to_numeric(self.races['year'], errors='coerce')
        
        # Drop duplicates
        self.races = self.races.drop_duplicates(subset=['year', 'round'])
        
        return self
    
    def clean_drivers(self):
        """Clean drivers data"""
        if self.drivers is None:
            return self
        
        # Create full name
        self.drivers['full_name'] = (
            self.drivers['forename'].fillna('') + ' ' + 
            self.drivers['surname'].fillna('')
        ).str.strip()
        
        # Convert DOB to datetime
        if 'dob' in self.drivers.columns:
            self.drivers['dob'] = pd.to_datetime(self.drivers['dob'], errors='coerce')
        
        return self
    
    def clean_results(self):
        """Clean results data"""
        if self.results is None:
            return self
        
        # Convert numeric columns
        numeric_cols = ['raceId', 'year', 'grid', 'position', 'positionOrder', 
                       'points', 'laps', 'milliseconds', 'fastestLap', 'rank']
        for col in numeric_cols:
            if col in self.results.columns:
                self.results[col] = pd.to_numeric(self.results[col], errors='coerce')
        
        # Handle position - convert 'R', 'D', 'E', 'W', 'F', 'N' to NaN
        if 'position' in self.results.columns:
            self.results['position'] = pd.to_numeric(
                self.results['position'], 
                errors='coerce'
            )
        
        # Create DNF flag
        if 'status' in self.results.columns:
            dnf_statuses = ['Accident', 'Collision', 'Engine', 'Gearbox', 'Hydraulics',
                          'Electrical', 'Spun off', 'Radiator', 'Suspension', 'Brakes',
                          'Differential', 'Overheating', 'Mechanical', 'Tyre', 'Driver',
                          'Puncture', 'Driveshaft', 'Retired', 'Fuel pressure', 'Clutch',
                          'Wheel', 'Technical', 'Electronics', 'Broken wing', 'Heat shield',
                          'Exhaust', 'Oil leak', 'Wheel rim', 'Water leak', 'Fuel leak',
                          'Transmission', 'Turbo', 'Water pump', 'Power Unit', 'ERS',
                          'Oil pressure', 'Power loss', 'Vibrations', '107% Rule', 'Safety',
                          'Drivetrain', 'Ignition', 'Damage', 'Debris', 'Illness', 'Injury']
            
            self.results['is_dnf'] = self.results['status'].isin(dnf_statuses)
        else:
            self.results['is_dnf'] = False
        
        # Calculate position change (grid to finish)
        if 'grid' in self.results.columns and 'position' in self.results.columns:
            self.results['position_change'] = (
                self.results['grid'] - self.results['position']
            )
        
        return self
    
    def clean_qualifying(self):
        """Clean qualifying data"""
        if self.qualifying is None:
            return self
        
        # Convert numeric columns
        numeric_cols = ['raceId', 'year', 'position', 'number']
        for col in numeric_cols:
            if col in self.qualifying.columns:
                self.qualifying[col] = pd.to_numeric(
                    self.qualifying[col], errors='coerce'
                )
        
        # Convert time columns to seconds
        time_cols = ['q1', 'q2', 'q3']
        for col in time_cols:
            if col in self.qualifying.columns:
                self.qualifying[f'{col}_seconds'] = self.qualifying[col].apply(
                    self._time_to_seconds
                )
        
        return self
    
    def clean_pitstops(self):
        """Clean pit stops data"""
        if self.pitstops is None:
            return self
        
        # Convert numeric columns
        numeric_cols = ['raceId', 'year', 'stop', 'lap']
        for col in numeric_cols:
            if col in self.pitstops.columns:
                self.pitstops[col] = pd.to_numeric(
                    self.pitstops[col], errors='coerce'
                )
        
        # Convert duration to seconds
        if 'duration' in self.pitstops.columns:
            self.pitstops['duration_seconds'] = self.pitstops['duration'].apply(
                self._time_to_seconds
            )
        
        return self
    
    def clean_laptimes(self):
        """Clean lap times data"""
        if self.laptimes is None:
            return self
        
        # Convert numeric columns
        numeric_cols = ['raceId', 'year', 'lap', 'position']
        for col in numeric_cols:
            if col in self.laptimes.columns:
                self.laptimes[col] = pd.to_numeric(
                    self.laptimes[col], errors='coerce'
                )
        
        # Convert time to seconds
        if 'time' in self.laptimes.columns:
            self.laptimes['time_seconds'] = self.laptimes['time'].apply(
                self._time_to_seconds
            )
        
        return self
    
    def _time_to_seconds(self, time_str):
        """Convert time string (MM:SS.mmm) to seconds"""
        if pd.isna(time_str) or time_str == '':
            return np.nan
        
        try:
            parts = str(time_str).split(':')
            if len(parts) == 2:
                minutes = int(parts[0])
                seconds = float(parts[1])
                return minutes * 60 + seconds
            else:
                return float(time_str)
        except:
            return np.nan
    
    def merge_data(self):
        """Merge all tables into a comprehensive dataset"""
        print("Merging data tables...")
        
        # Start with results
        merged = self.results.copy()
        
        # Merge with races
        if self.races is not None:
            merged = merged.merge(
                self.races[['raceId', 'year', 'round', 'circuitId', 'name', 'date']],
                on=['raceId', 'year'],
                how='left',
                suffixes=('', '_race')
            )
            merged = merged.rename(columns={'name': 'race_name'})
        
        # Merge with drivers
        if self.drivers is not None:
            merged = merged.merge(
                self.drivers[['driverId', 'full_name', 'nationality', 'code']],
                on='driverId',
                how='left'
            )
            merged = merged.rename(columns={'nationality': 'driver_nationality'})
        
        # Merge with constructors
        if self.constructors is not None:
            merged = merged.merge(
                self.constructors[['constructorId', 'name', 'nationality']],
                on='constructorId',
                how='left'
            )
            merged = merged.rename(columns={
                'name': 'constructor_name',
                'nationality': 'constructor_nationality'
            })
        
        # Merge with circuits
        if self.circuits is not None and 'circuitId' in merged.columns:
            merged = merged.merge(
                self.circuits[['circuitId', 'name', 'country', 'lat', 'lng']],
                on='circuitId',
                how='left'
            )
            merged = merged.rename(columns={
                'name': 'circuit_name',
                'country': 'circuit_country'
            })
        
        # Merge with qualifying
        if self.qualifying is not None:
            qual_agg = self.qualifying.groupby(['raceId', 'year', 'driverId']).agg({
                'position': 'first',
                'q1_seconds': 'first',
                'q2_seconds': 'first',
                'q3_seconds': 'first'
            }).reset_index()
            qual_agg = qual_agg.rename(columns={'position': 'qualifying_position'})
            
            merged = merged.merge(
                qual_agg,
                on=['raceId', 'year', 'driverId'],
                how='left'
            )
        
        print(f"Merged dataset shape: {merged.shape}")
        return merged
    
    def create_aggregated_tables(self):
        """Create pre-aggregated tables for faster analysis"""
        print("Creating aggregated tables...")
        
        # Driver statistics
        driver_stats = self.results.groupby('driverId').agg({
            'position': ['count', lambda x: (x == 1).sum(), lambda x: (x <= 3).sum()],
            'points': 'sum',
            'is_dnf': 'sum',
            'position_change': 'mean'
        }).reset_index()
        driver_stats.columns = ['driverId', 'races', 'wins', 'podiums', 'total_points', 'dnfs', 'avg_position_change']
        driver_stats = driver_stats.merge(
            self.drivers[['driverId', 'full_name']],
            on='driverId',
            how='left'
        )
        driver_stats['win_rate'] = driver_stats['wins'] / driver_stats['races']
        driver_stats['podium_rate'] = driver_stats['podiums'] / driver_stats['races']
        driver_stats['dnf_rate'] = driver_stats['dnfs'] / driver_stats['races']
        
        # Constructor statistics
        constructor_stats = self.results.groupby('constructorId').agg({
            'position': ['count', lambda x: (x == 1).sum(), lambda x: (x <= 3).sum()],
            'points': 'sum',
            'is_dnf': 'sum'
        }).reset_index()
        constructor_stats.columns = ['constructorId', 'races', 'wins', 'podiums', 'total_points', 'dnfs']
        constructor_stats = constructor_stats.merge(
            self.constructors[['constructorId', 'name']],
            on='constructorId',
            how='left'
        )
        constructor_stats['win_rate'] = constructor_stats['wins'] / constructor_stats['races']
        constructor_stats['podium_rate'] = constructor_stats['podiums'] / constructor_stats['races']
        
        return {
            'driver_stats': driver_stats,
            'constructor_stats': constructor_stats
        }
    
    def clean_all(self):
        """Run all cleaning steps"""
        self.load_data()
        self.clean_races()
        self.clean_drivers()
        self.clean_results()
        self.clean_qualifying()
        self.clean_pitstops()
        self.clean_laptimes()
        
        merged = self.merge_data()
        aggregated = self.create_aggregated_tables()
        
        # Save cleaned data
        merged.to_csv(self.data_dir / "merged_results.csv", index=False)
        aggregated['driver_stats'].to_csv(self.data_dir / "driver_stats.csv", index=False)
        aggregated['constructor_stats'].to_csv(self.data_dir / "constructor_stats.csv", index=False)
        
        print(f"\nCleaned data saved to {self.data_dir}/")
        return merged, aggregated


if __name__ == "__main__":
    cleaner = F1DataCleaner()
    merged, aggregated = cleaner.clean_all()


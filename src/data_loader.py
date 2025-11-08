"""
Formula 1 Data Loader
Fetches data from Ergast API and saves to CSV files for analysis
"""

import requests
import pandas as pd
import time
from pathlib import Path
import json


class F1DataLoader:
    """Load Formula 1 data from Ergast API"""
    
    BASE_URL = "http://ergast.com/api/f1"
    
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def _make_request(self, endpoint, limit=1000, offset=0):
        """Make API request with rate limiting"""
        url = f"{self.BASE_URL}/{endpoint}.json?limit={limit}&offset={offset}"
        print(f"Fetching: {url}")
        response = requests.get(url)
        response.raise_for_status()
        time.sleep(0.5)  # Rate limiting
        return response.json()
    
    def _get_all_pages(self, endpoint, limit=1000):
        """Fetch all pages of data"""
        all_data = []
        offset = 0
        
        while True:
            data = self._make_request(endpoint, limit=limit, offset=offset)
            mrd = data.get("MRData", {})
            table = mrd.get(endpoint.split("/")[-1], {})
            records = table.get("records", [])
            
            if not records:
                break
                
            all_data.extend(records)
            
            # Check if there are more pages
            total = int(mrd.get("total", 0))
            if offset + len(records) >= total:
                break
                
            offset += limit
        
        return all_data
    
    def load_races(self, start_year=1950, end_year=2024):
        """Load race data"""
        races = []
        for year in range(start_year, end_year + 1):
            endpoint = f"{year}/races"
            data = self._make_request(endpoint)
            mrd = data.get("MRData", {})
            race_table = mrd.get("RaceTable", {})
            race_list = race_table.get("Races", [])
            
            for race in race_list:
                races.append({
                    "raceId": race.get("round"),
                    "year": year,
                    "round": race.get("round"),
                    "circuitId": race.get("Circuit", {}).get("circuitId"),
                    "name": race.get("raceName"),
                    "date": race.get("date"),
                    "time": race.get("time"),
                    "url": race.get("url")
                })
        
        df = pd.DataFrame(races)
        df.to_csv(self.data_dir / "races.csv", index=False)
        return df
    
    def load_drivers(self):
        """Load all drivers"""
        endpoint = "drivers"
        data = self._get_all_pages(endpoint)
        
        drivers = []
        for driver in data:
            drivers.append({
                "driverId": driver.get("driverId"),
                "driverRef": driver.get("driverId"),
                "number": driver.get("permanentNumber"),
                "code": driver.get("code"),
                "forename": driver.get("givenName"),
                "surname": driver.get("familyName"),
                "dob": driver.get("dateOfBirth"),
                "nationality": driver.get("nationality"),
                "url": driver.get("url")
            })
        
        df = pd.DataFrame(drivers)
        df.to_csv(self.data_dir / "drivers.csv", index=False)
        return df
    
    def load_constructors(self):
        """Load all constructors"""
        endpoint = "constructors"
        data = self._get_all_pages(endpoint)
        
        constructors = []
        for constructor in data:
            constructors.append({
                "constructorId": constructor.get("constructorId"),
                "constructorRef": constructor.get("constructorId"),
                "name": constructor.get("name"),
                "nationality": constructor.get("nationality"),
                "url": constructor.get("url")
            })
        
        df = pd.DataFrame(constructors)
        df.to_csv(self.data_dir / "constructors.csv", index=False)
        return df
    
    def load_results(self, start_year=1950, end_year=2024):
        """Load race results"""
        results = []
        for year in range(start_year, end_year + 1):
            endpoint = f"{year}/results"
            data = self._make_request(endpoint, limit=1000)
            mrd = data.get("MRData", {})
            race_table = mrd.get("RaceTable", {})
            races = race_table.get("Races", [])
            
            for race in races:
                race_id = race.get("round")
                year_val = year
                for result in race.get("Results", []):
                    results.append({
                        "resultId": len(results) + 1,
                        "raceId": race_id,
                        "year": year_val,
                        "driverId": result.get("Driver", {}).get("driverId"),
                        "constructorId": result.get("Constructor", {}).get("constructorId"),
                        "number": result.get("number"),
                        "grid": result.get("grid"),
                        "position": result.get("position"),
                        "positionText": result.get("positionText"),
                        "positionOrder": result.get("positionOrder"),
                        "points": result.get("points"),
                        "laps": result.get("laps"),
                        "time": result.get("Time", {}).get("time") if isinstance(result.get("Time"), dict) else result.get("Time"),
                        "milliseconds": result.get("Time", {}).get("millis") if isinstance(result.get("Time"), dict) else None,
                        "fastestLap": result.get("FastestLap", {}).get("lap") if isinstance(result.get("FastestLap"), dict) else None,
                        "rank": result.get("FastestLap", {}).get("rank") if isinstance(result.get("FastestLap"), dict) else None,
                        "fastestLapTime": result.get("FastestLap", {}).get("Time", {}).get("time") if isinstance(result.get("FastestLap"), dict) else None,
                        "fastestLapSpeed": result.get("FastestLap", {}).get("AverageSpeed", {}).get("speed") if isinstance(result.get("FastestLap"), dict) else None,
                        "statusId": result.get("status"),
                        "status": result.get("status")
                    })
        
        df = pd.DataFrame(results)
        df.to_csv(self.data_dir / "results.csv", index=False)
        return df
    
    def load_qualifying(self, start_year=2003, end_year=2024):
        """Load qualifying results (available from 2003)"""
        qualifying = []
        for year in range(start_year, end_year + 1):
            endpoint = f"{year}/qualifying"
            try:
                data = self._make_request(endpoint, limit=1000)
                mrd = data.get("MRData", {})
                race_table = mrd.get("RaceTable", {})
                races = race_table.get("Races", [])
                
                for race in races:
                    race_id = race.get("round")
                    year_val = year
                    for qual in race.get("QualifyingResults", []):
                        qualifying.append({
                            "qualifyId": len(qualifying) + 1,
                            "raceId": race_id,
                            "year": year_val,
                            "driverId": qual.get("Driver", {}).get("driverId"),
                            "constructorId": qual.get("Constructor", {}).get("constructorId"),
                            "number": qual.get("number"),
                            "position": qual.get("position"),
                            "q1": qual.get("Q1"),
                            "q2": qual.get("Q2"),
                            "q3": qual.get("Q3")
                        })
            except Exception as e:
                print(f"Error loading qualifying for {year}: {e}")
                continue
        
        df = pd.DataFrame(qualifying)
        if not df.empty:
            df.to_csv(self.data_dir / "qualifying.csv", index=False)
        return df
    
    def load_circuits(self):
        """Load circuit information"""
        endpoint = "circuits"
        data = self._get_all_pages(endpoint)
        
        circuits = []
        for circuit in data:
            location = circuit.get("Location", {})
            circuits.append({
                "circuitId": circuit.get("circuitId"),
                "circuitRef": circuit.get("circuitId"),
                "name": circuit.get("circuitName"),
                "location": location.get("locality"),
                "country": location.get("country"),
                "lat": location.get("lat"),
                "lng": location.get("long"),
                "alt": location.get("alt"),
                "url": circuit.get("url")
            })
        
        df = pd.DataFrame(circuits)
        df.to_csv(self.data_dir / "circuits.csv", index=False)
        return df
    
    def load_pitstops(self, start_year=2011, end_year=2024):
        """Load pit stop data (available from 2011)"""
        pitstops = []
        for year in range(start_year, end_year + 1):
            endpoint = f"{year}/pitstops"
            try:
                data = self._make_request(endpoint, limit=1000)
                mrd = data.get("MRData", {})
                race_table = mrd.get("RaceTable", {})
                races = race_table.get("Races", [])
                
                for race in races:
                    race_id = race.get("round")
                    year_val = year
                    for stop in race.get("PitStops", []):
                        pitstops.append({
                            "raceId": race_id,
                            "year": year_val,
                            "driverId": stop.get("driverId"),
                            "stop": stop.get("stop"),
                            "lap": stop.get("lap"),
                            "time": stop.get("time"),
                            "duration": stop.get("duration")
                        })
            except Exception as e:
                print(f"Error loading pitstops for {year}: {e}")
                continue
        
        df = pd.DataFrame(pitstops)
        if not df.empty:
            df.to_csv(self.data_dir / "pitstops.csv", index=False)
        return df
    
    def load_laptimes(self, start_year=2011, end_year=2024, limit_races=50):
        """Load lap time data (limited to recent races due to API constraints)"""
        laptimes = []
        # Limit to most recent races to avoid overwhelming the API
        for year in range(max(2011, start_year), end_year + 1):
            endpoint = f"{year}/laps"
            try:
                # Get races for the year first
                races_data = self._make_request(f"{year}/races")
                races_list = races_data.get("MRData", {}).get("RaceTable", {}).get("Races", [])
                
                # Limit number of races
                for race in races_list[:limit_races]:
                    race_id = race.get("round")
                    round_num = race.get("round")
                    
                    # Get laps for this race
                    lap_endpoint = f"{year}/{round_num}/laps"
                    try:
                        lap_data = self._make_request(lap_endpoint, limit=1000)
                        mrd = lap_data.get("MRData", {})
                        race_table = mrd.get("RaceTable", {})
                        races = race_table.get("Races", [])
                        
                        for race_info in races:
                            for lap_num, drivers in race_info.get("Laps", {}).items():
                                for driver_lap in drivers:
                                    laptimes.append({
                                        "raceId": race_id,
                                        "year": year,
                                        "driverId": driver_lap.get("driverId"),
                                        "lap": lap_num,
                                        "position": driver_lap.get("position"),
                                        "time": driver_lap.get("time")
                                    })
                    except Exception as e:
                        print(f"Error loading laptimes for {year} race {race_id}: {e}")
                        continue
            except Exception as e:
                print(f"Error loading laptimes for {year}: {e}")
                continue
        
        df = pd.DataFrame(laptimes)
        if not df.empty:
            df.to_csv(self.data_dir / "laptimes.csv", index=False)
        return df
    
    def load_all(self, start_year=1950, end_year=2024):
        """Load all available data"""
        print("Loading Formula 1 data from Ergast API...")
        print("This may take several minutes due to API rate limiting...")
        
        self.load_circuits()
        self.load_drivers()
        self.load_constructors()
        self.load_races(start_year, end_year)
        self.load_results(start_year, end_year)
        self.load_qualifying(start_year, end_year)
        self.load_pitstops(start_year, end_year)
        # Note: laptimes loading is commented out by default due to API constraints
        # Uncomment if needed: self.load_laptimes(start_year, end_year)
        
        print(f"\nData loading complete! Files saved to {self.data_dir}/")


if __name__ == "__main__":
    loader = F1DataLoader()
    # Load data from 2000-2024 for faster loading (adjust as needed)
    loader.load_all(start_year=2000, end_year=2024)


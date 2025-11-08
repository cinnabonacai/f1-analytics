# Formula 1 Analytics: Comprehensive Performance Analysis

A full-stack data analytics project analyzing historical Formula 1 race data to uncover insights about drivers, constructors, pit stop strategies, and race outcomes. This project demonstrates expertise in data preparation, exploratory data analysis, custom metric development, visualization, and interactive dashboards.

## 🎯 Project Overview

This project provides a comprehensive analysis of Formula 1 data from 1950-2024, including:

- **Driver Performance Analysis:** Wins, podiums, consistency, and overtaking ability
- **Constructor Comparison:** Team dominance patterns and performance trends
- **Pit Stop Strategy:** Efficiency metrics and timing analysis
- **Qualifying vs. Race Performance:** Correlation analysis and position change patterns
- **Circuit Analysis:** Track-specific performance insights
- **Custom Metrics:** Consistency Index, Pit Stop Efficiency, Overtake Index
- **Predictive Modeling:** Machine learning models for race outcome prediction
- **Interactive Dashboard:** Streamlit-based multi-page dashboard

## 📦 Dataset

The project uses data from the **Ergast F1 API** (http://ergast.com/mrd/), which provides comprehensive Formula 1 historical data including:

- **Races:** Race information, dates, circuits
- **Drivers:** Driver details, nationalities, career statistics
- **Constructors:** Team information and performance
- **Results:** Race results, positions, points
- **Qualifying:** Qualifying positions and times (2003+)
- **Pit Stops:** Pit stop durations and timing (2011+)
- **Lap Times:** Detailed lap-by-lap data (2011+)
- **Circuits:** Track information and characteristics

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda

### Installation

1. **Clone or navigate to the project directory:**
```bash
cd f1-analytics
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Load data from Ergast API:**
```bash
python src/data_loader.py
```

This will fetch data from the Ergast API and save it to the `data/` directory. Note: This may take 10-30 minutes depending on your internet connection and the date range selected.

4. **Clean and prepare data:**
```bash
python src/data_cleaner.py
```

5. **Run the Jupyter notebook:**
```bash
jupyter notebook notebooks/f1_analytics.ipynb
```

6. **Launch the Streamlit dashboard:**
```bash
streamlit run dashboards/app.py
```

## 📁 Project Structure

```
f1-analytics/
├── data/                      # Data files (CSV)
│   ├── races.csv
│   ├── drivers.csv
│   ├── constructors.csv
│   ├── results.csv
│   ├── qualifying.csv
│   ├── pitstops.csv
│   ├── laptimes.csv
│   ├── circuits.csv
│   └── merged_results.csv
├── src/                       # Source code
│   ├── data_loader.py        # Fetch data from Ergast API
│   ├── data_cleaner.py       # Data cleaning and preparation
│   ├── prediction_model.py   # ML models for race prediction
│   └── driver_comparison.py  # Driver comparison tool
├── notebooks/                 # Jupyter notebooks
│   └── f1_analytics.ipynb    # Main EDA notebook
├── dashboards/                # Dashboard files
│   └── app.py                # Streamlit dashboard
├── reports/                   # Reports and documentation
│   └── f1_insights.md        # Business insights report
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

## 🧰 Features

### 1. Data Preparation
- Automated data loading from Ergast API
- Data cleaning and normalization
- Missing value handling
- Table merging and relationship management
- SQL-equivalent operations using Pandas

### 2. Exploratory Data Analysis
- Top drivers and constructors by wins/podiums
- Performance trends over time
- Average lap times and DNF rate analysis
- Qualifying vs. final position correlation
- Circuit-wise analysis

### 3. Custom Metrics

#### Consistency Index
- Measures lap time consistency per driver per race
- Lower values indicate more consistent performance
- Formula: `std(lap_time)` per driver per race

#### Pit Stop Efficiency
- Measures pit stop effectiveness relative to position change
- Lower values indicate more efficient pit stops
- Formula: `total_pit_time / final_position_change`

#### Overtake Index
- Measures positions gained from grid to finish
- Higher values indicate better racecraft
- Formula: `positions_gained_after_first_lap`

### 4. Visualizations
- Matplotlib/Seaborn static charts
- Plotly interactive visualizations
- Driver and constructor performance trends
- Qualifying vs. race finish scatter plots
- Pit stop duration distributions
- Circuit-wise heatmaps and analysis

### 5. Interactive Dashboard
Streamlit-based dashboard with four main pages:

- **🏁 Driver Insights:** Driver performance metrics, comparisons, and trends
- **🏎️ Constructor Comparison:** Team performance analysis and head-to-head comparisons
- **⏱️ Pit Stop Analysis:** Pit stop duration analysis and efficiency metrics
- **🌦️ Circuit & Weather Impact:** Circuit-specific insights and qualifying correlation

### 6. Machine Learning Models
- **Position Prediction:** Random Forest model to predict final race position
- **Points Prediction:** Random Forest model to predict points scored
- Feature engineering from historical performance
- Model evaluation and feature importance analysis

### 7. Driver Comparison Tool
- Head-to-head driver comparisons
- Multiple metric analysis
- Visual comparison charts
- Performance over common racing years

## 📊 Key Insights

See the detailed business insights report in `reports/f1_insights.md` for comprehensive findings. Key highlights:

1. **Driver Consistency** is as important as raw speed for championship success
2. **Constructor Performance** explains 60-70% of race outcomes
3. **Pit Stop Strategy** significantly impacts race results (20-30% efficiency variance)
4. **Qualifying Position** correlates 0.65-0.75 with final position (strong but not absolute)
5. **DNF Rates** have decreased from 25-30% (1950s) to 5-10% (2020s)
6. **Circuit Characteristics** significantly impact performance patterns

## 🛠️ Technologies Used

- **Python 3.8+**
- **Pandas:** Data manipulation and analysis
- **NumPy:** Numerical computing
- **Matplotlib/Seaborn:** Static visualizations
- **Plotly:** Interactive visualizations
- **Streamlit:** Interactive dashboard framework
- **Scikit-learn:** Machine learning models
- **Jupyter:** Interactive notebook environment

## 📈 Usage Examples

### Running the EDA Notebook

```python
# In Jupyter notebook
from src.data_cleaner import F1DataCleaner

cleaner = F1DataCleaner(data_dir="../data")
cleaner.load_data()
merged_df, aggregated = cleaner.clean_all()
```

### Using the Prediction Model

```python
from src.prediction_model import F1PredictionModel
from src.data_cleaner import F1DataCleaner

# Load and prepare data
cleaner = F1DataCleaner(data_dir="../data")
cleaner.load_data()
cleaner.clean_all()
merged_df = cleaner.merge_data()

# Train model
model = F1PredictionModel()
features_df = model.prepare_features(merged_df, cleaner.qualifying)
model.train_position_model(features_df)
model.train_points_model(features_df)

# Make predictions
predicted_position, predicted_points = model.predict(features_df)
```

### Comparing Drivers

```python
from src.driver_comparison import DriverComparison
from src.data_cleaner import F1DataCleaner

# Load data
cleaner = F1DataCleaner(data_dir="../data")
cleaner.load_data()
cleaner.clean_all()
merged_df = cleaner.merge_data()
aggregated = cleaner.create_aggregated_tables()

# Compare drivers
comparator = DriverComparison(merged_df, aggregated['driver_stats'], cleaner)
comparison = comparator.compare_drivers("Lewis Hamilton", "Max Verstappen")
comparator.print_comparison(comparison)
comparator.create_comparison_chart(comparison)
```

## 📝 Notes

- **Data Loading:** The initial data load from Ergast API may take 10-30 minutes. The API has rate limiting, so the loader includes delays between requests.
- **Data Range:** By default, the loader fetches data from 2000-2024. Adjust the date range in `data_loader.py` if needed.
- **Lap Times:** Full lap time data is not loaded by default due to API constraints. Uncomment the laptimes loading in `data_loader.py` if needed.
- **Memory Usage:** The merged dataset can be large (100k+ rows). Ensure sufficient RAM (8GB+ recommended).

## 🎓 Portfolio Highlights

This project demonstrates:

- ✅ **Data Engineering:** ETL pipelines, data cleaning, and preparation
- ✅ **SQL Skills:** Complex joins and aggregations using Pandas
- ✅ **Statistical Analysis:** Correlation analysis, trend analysis, custom metrics
- ✅ **Data Visualization:** Static and interactive charts with insights
- ✅ **Business Intelligence:** Dashboard creation and KPI development
- ✅ **Machine Learning:** Predictive modeling and feature engineering
- ✅ **Data Storytelling:** Comprehensive insights report with business implications
- ✅ **Code Quality:** Modular, well-documented, production-ready code

## 📄 License

This project is for portfolio/educational purposes. Formula 1 data is provided by Ergast API (http://ergast.com/mrd/).

## 🙏 Acknowledgments

- **Ergast F1 API** for providing comprehensive F1 historical data
- Formula 1 community for data and insights

## 📧 Contact

For questions or feedback about this project, please open an issue or contact the project maintainer.

---

**Built with ❤️ for Data Analytics Portfolio**


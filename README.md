# App Market Research - Data Engineering Pipeline

A complete data engineering pipeline for collecting, transforming, and analyzing Google Play Store app data. This project scrapes app metadata and user reviews, processes them through ETL stages, and generates an interactive dashboard for market insights.

## 📋 Project Overview

This pipeline performs the following stages:

1. **Data Generation**: Scrape Google Play Store for app metadata and reviews
2. **Data Transformation**: Clean and structure raw data into analytics-ready formats
3. **Data Serving**: Calculate KPIs and metrics for visualization
4. **Dashboard**: Generate interactive visualizations using Plotly

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Kobanka/TP-App-Market-Research.git
   cd "TP-Data-Engineering/App Market Research"
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv dataApps
   ```

3. **Activate the virtual environment**
   
   On Linux/Mac:
   ```bash
   source dataApps/bin/activate
   ```
   
   On Windows:
   ```bash
   dataApps\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install google-play-scraper pandas plotly
   ```

## 📊 Running the Pipeline

Run each stage in order from the project root directory:

### Step 1: Generate Raw Data

Scrapes Google Play Store for AI note-taking apps and their reviews:

```bash
python src/data_generation.py
```

**Output**: 
- `data/raw/apps_metadata.json` - App details (title, developer, ratings, installs, etc.)
- `data/raw/apps_reviews.json` - User reviews with ratings and timestamps

### Step 2: Transform Data

Cleans and structures the raw data into CSV format:

```bash
python src/data_transformation.py
```

**Output**:
- `data/processed/apps_metadata.csv` - Cleaned app catalog
- `data/processed/apps_reviews.csv` - Structured review data

### Step 3: Calculate Metrics

Aggregates data into KPIs and time-series metrics:

```bash
python src/serve.py
```

**Output**:
- `data/processed/serving_app_kpis.csv` - Per-app metrics (avg rating, review count, etc.)
- `data/processed/serving_daily_metrics.csv` - Daily trends

### Step 4: Generate Dashboard

Creates an interactive HTML dashboard:

```bash
python src/dashboard.py
```

**Output**:
- `data/processed/dashboard.html` - Interactive visualization dashboard

### Step 5: View the Dashboard

Start a local web server to view the interactive dashboard:

```bash
cd "data/processed"
python -m http.server 8000
```

Then open your browser and navigate to:
```
http://localhost:8000/dashboard.html
```

Press `Ctrl+C` in the terminal to stop the server when done.

## 📁 Project Structure

```
App Market Research/
├── README.md
├── requirements.txt
├── data/
│   ├── raw/              # Scraped JSON data
│   └── processed/        # Transformed CSV + dashboard
├── dataApps/             # Virtual environment (after setup)
└── src/
    ├── data_generation.py      # Stage 1: Scrape data
    ├── data_transformation.py  # Stage 2: Transform
    ├── serve.py                # Stage 3: Calculate metrics
    └── dashboard.py            # Stage 4: Visualize
```

## 📈 Dashboard Features

The generated dashboard includes:

1. **App Performance Scatter Plot**: Visualize rating vs review volume
2. **Daily Rating Trends**: Track average ratings over time
3. **Review Volume Analysis**: Weekly aggregation of review counts

## 🔧 Customization

- **Change search query**: Edit the `query` variable in `data_generation.py` (line 43)
- **Adjust review count**: Modify the `count` parameter in `fetch_app_reviews()` call (line 71)
- **Filter thresholds**: Update minimum review count in `dashboard.py` (line 33)

## 🛠️ Troubleshooting

**Import errors**: Make sure your virtual environment is activated and dependencies are installed:
```bash
pip install google-play-scraper pandas plotly
```

**Path errors**: Always run scripts from the `App Market Research` directory

**Empty data**: The scraper may return different results based on Google Play availability. Check that `data/raw/` contains JSON files with data.

## 📝 Notes

- The scraper uses the `google-play-scraper` library (unofficial API)
- Review data availability depends on Google Play Store's current state
- For production use, consider implementing continuation tokens for larger datasets
- Add error handling around API calls to prevent data loss during collection

## 📄 License

This project is for educational purposes as part of a Data Engineering workshop.
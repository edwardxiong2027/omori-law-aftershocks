# Testing Omori's Law: Mathematics of Earthquake Aftershocks

**NHSJS Research Project by Edward Xiong**
Diamond Bar High School, 11th Grade

## Abstract

This research tests Omori's Law (1894), which describes the temporal decay of earthquake aftershock frequency, using modern USGS seismic data. Analysis of 17 aftershock sequences (4,394 aftershocks) from M6.0+ earthquakes demonstrates that the modified Omori-Utsu formula accurately describes aftershock decay with an average R² of 0.912.

## Key Findings

| Metric | Value |
|--------|-------|
| Sequences Analyzed | 17 |
| Total Aftershocks | 4,394 |
| Successful Fits | 9 (R² > 0.5) |
| Mean Decay Exponent (p) | **0.92 ± 0.26** |
| Average R² | **0.912** |
| Literature p value | ~1.0-1.3 |

**Key Insight:** Our mean p = 0.92 is consistent with the classical Omori value of p ≈ 1, validating this 130-year-old seismological law with modern data.

## Omori's Law

```
n(t) = K / (c + t)^p
```

Where:
- n(t) = aftershock rate at time t
- K = productivity parameter
- c = characteristic time delay
- p = decay exponent

## Repository Structure

```
NHSJS_Research_Project/
├── data/
│   ├── collect_earthquake_data.py  # USGS API data collection
│   ├── earthquake_data.json        # Raw collected data
│   └── sequence_summary.csv        # Summary statistics
├── analysis/
│   ├── omori_analysis.py           # Omori's Law fitting
│   └── analysis_results.json       # Fitted parameters
├── figures/
│   ├── example_omori_fit.png       # Best fit visualization
│   ├── p_value_distribution.png    # Histogram of p values
│   ├── p_vs_magnitude.png          # p correlation analysis
│   └── r_squared_distribution.png  # Fit quality distribution
├── webapp/
│   └── app.py                      # Interactive Flask app
├── paper/
│   └── manuscript.md               # Research paper draft
└── README.md
```

## Installation

```bash
pip install requests numpy pandas scipy matplotlib flask plotly
```

## Usage

### 1. Collect Data
```bash
python data/collect_earthquake_data.py
```

### 2. Run Analysis
```bash
python analysis/omori_analysis.py
```

### 3. Launch Web App
```bash
python webapp/app.py
# Open http://localhost:5001
```

## Data Source

All earthquake data from [USGS Earthquake Hazards Program](https://earthquake.usgs.gov/) via their public API.

## Citation

```
Xiong, E. (2026). Testing Omori's Law: Mathematical Analysis of Earthquake
Aftershock Decay Patterns Using USGS Seismic Data.
National High School Journal of Science.
```

## License

MIT License

---

*Prepared for submission to the National High School Journal of Science (NHSJS)*

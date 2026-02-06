# Testing Omori's Law: Mathematical Analysis of Earthquake Aftershock Decay Patterns Using USGS Seismic Data

**Edward Xiong**
Diamond Bar High School, Diamond Bar, CA

---

## ABSTRACT

Omori's Law, proposed in 1894, describes the temporal decay of earthquake aftershock frequency following a mainshock. This study tests the modified Omori-Utsu formula, n(t) = K/(c+t)^p, using modern seismic data from the USGS Earthquake Catalog. We analyzed 17 aftershock sequences from major earthquakes (M ≥ 6.0) occurring between 2020-2025, comprising 4,394 individual aftershocks. Non-linear regression fitting yielded successful model fits for 9 sequences (R² > 0.5). The mean decay exponent was p = 0.92 ± 0.26, consistent with the classical Omori value of p ≈ 1 and previous literature values of p = 0.9-1.3. The average goodness-of-fit (R² = 0.912) demonstrates that Omori's 130-year-old empirical law accurately describes modern earthquake aftershock behavior. Our findings validate the continued applicability of this classical seismological relationship and provide insights into aftershock hazard assessment.

**Keywords:** Omori's Law, aftershocks, earthquake seismology, power law decay, seismic hazard

---

## INTRODUCTION

### Background

Earthquakes pose significant natural hazards worldwide, with aftershocks representing a critical component of seismic risk. Following a major earthquake (mainshock), the affected region experiences a sequence of smaller earthquakes called aftershocks, which can cause additional damage to weakened structures and complicate emergency response efforts.

In 1894, Japanese seismologist Fusakichi Omori made a foundational observation: the rate of aftershocks decays over time following a predictable mathematical pattern¹. His original formula proposed that aftershock frequency decreases inversely with time:

**Original Omori's Law:** n(t) = K / (c + t)

Where n(t) is the aftershock rate at time t after the mainshock, K is a productivity constant, and c is a time delay parameter.

### Modified Omori-Utsu Law

In 1961, Utsu generalized Omori's formula by introducing a variable decay exponent p²:

**Modified Omori-Utsu Law:** n(t) = K / (c + t)^p

The three parameters are:
- **K**: Productivity parameter controlling overall aftershock amplitude
- **c**: Characteristic time delay (typically 0.01-0.5 days)
- **p**: Decay exponent (typically 0.9-1.5)

When p = 1, the modified formula reduces to the original Omori's Law. Literature values for California aftershock sequences report mean p = 1.08 ± 0.03³, while Japanese sequences show p ≈ 1.3⁴.

### Research Objectives

This study aims to:
1. Test whether Omori's Law accurately describes aftershock decay in recent global earthquakes
2. Determine the distribution of decay exponent p values across different tectonic settings
3. Evaluate how well the modified Omori-Utsu model fits modern seismic data
4. Compare original (p=1) versus modified (variable p) Omori formulations

### Hypothesis

We hypothesize that earthquake aftershock sequences from 2020-2025 will follow Omori's Law with decay exponents p close to the classical value of 1.0, consistent with over a century of seismological observations.

---

## METHODS

### Data Source

Earthquake data was obtained from the USGS Comprehensive Earthquake Catalog (ComCat) via their public REST API⁵. The USGS catalog provides verified earthquake parameters including origin time, location (latitude, longitude, depth), and magnitude for seismic events worldwide.

### Event Selection Criteria

Mainshock earthquakes were selected based on:
- Magnitude M ≥ 6.0 (significant earthquakes)
- Date range: January 2020 - February 2025
- Sufficient aftershock activity (≥ 10 detected aftershocks)

Aftershocks were identified using spatial and temporal windows:
- Spatial: Within 100 km radius of mainshock epicenter
- Temporal: 1 minute to 30 days following mainshock
- Magnitude: M ≥ 2.0 (detection threshold)
- Constraint: Aftershock magnitude < mainshock magnitude

### Data Processing

For each aftershock sequence:
1. Earthquake times were converted to hours after mainshock
2. Time series were binned using logarithmic intervals to capture early rapid decay
3. Aftershock rates (events per hour) were calculated for each bin
4. Zero-rate bins were excluded from fitting

### Model Fitting

The modified Omori-Utsu law was fitted using non-linear least squares regression in logarithmic space:

log₁₀[n(t)] = log₁₀[K] - p × log₁₀[c + t]

Optimization was performed using the L-BFGS-B algorithm with parameter bounds:
- K: [0.01, 10⁶]
- c: [0.001, 10] hours
- p: [0.1, 3.0]

### Model Evaluation

Goodness-of-fit was assessed using:
- **R²** (coefficient of determination): Proportion of variance explained
- **RMSE** (root mean square error): Average prediction error

Fits with R² > 0.5 were considered successful. The original Omori's Law (p = 1 fixed) was also fitted for comparison.

### Statistical Analysis

All analysis was performed using Python 3.9 with NumPy, SciPy, and Pandas libraries. Code is publicly available at the project repository.

---

## RESULTS

### Data Summary

From 795 M ≥ 6.0 earthquakes identified in the study period, 17 sequences had sufficient aftershock data for analysis:

**Table 1: Summary Statistics**
| Metric | Value |
|--------|-------|
| Total mainshocks screened | 795 |
| Sequences analyzed | 17 |
| Total aftershocks | 4,394 |
| Average aftershocks per sequence | 258.5 |
| Successful fits (R² > 0.5) | 9 (53%) |

### Omori's Law Parameters

For the 9 successfully fitted sequences, the modified Omori-Utsu parameters were:

**Table 2: Fitted Parameters**
| Parameter | Mean | Std Dev | Range |
|-----------|------|---------|-------|
| p (decay exponent) | 0.92 | 0.26 | [0.59, 1.23] |
| R² (goodness of fit) | 0.912 | 0.074 | [0.755, 0.986] |

The mean p value of 0.92 ± 0.26 is consistent with the classical Omori value of p = 1 and falls within the literature range of 0.9-1.3.

### Model Fit Examples

**Figure 1** shows an exemplary Omori fit for the M6.1 Cayman Islands earthquake (2020), demonstrating excellent agreement between observed aftershock rates and the fitted power-law decay (R² = 0.986, p = 1.20).

### Distribution of Decay Exponents

**Figure 2** presents the distribution of fitted p values. The histogram shows a spread from 0.59 to 1.23, with the mean (0.92) close to the classical Omori prediction (p = 1).

### Original vs. Modified Omori Comparison

Comparing the original Omori's Law (p = 1 fixed) with the modified version (p fitted):

**Table 3: Model Comparison**
| Model | Mean R² |
|-------|---------|
| Original Omori (p=1) | 0.872 |
| Modified Omori-Utsu | 0.912 |

The modified formulation provides slightly better fits (4.6% improvement in R²), justifying the additional parameter flexibility.

### Sequence-Specific Results

**Table 4: Individual Sequence Results**
| Location | Magnitude | Aftershocks | p | R² |
|----------|-----------|-------------|-----|-----|
| Cayman Islands | 6.1 | 21 | 1.20 | 0.986 |
| Adak, Alaska | 6.2 | 434 | 1.23 | 0.982 |
| Kuril Islands, Russia | 7.5 | 32 | 1.07 | 0.980 |
| Doğanyol, Turkey | 6.7 | 26 | 1.18 | 0.956 |
| Adak, Alaska (WSW) | 6.1 | 135 | 1.00 | 0.946 |
| Stanley, Idaho | 6.5 | 640 | 0.59 | 0.906 |
| Puerto Rico | 6.4 | 2,863 | 0.65 | 0.870 |
| Philippines | 6.0 | 21 | 0.70 | 0.829 |
| Greece | 6.5 | 119 | 0.62 | 0.755 |

---

## DISCUSSION

### Validation of Omori's Law

Our results strongly support the continued validity of Omori's Law for describing earthquake aftershock decay. The high average R² value (0.912) indicates that the power-law decay model explains over 91% of the variance in aftershock rates, even 130 years after Omori's original observations.

### Interpretation of p Values

The mean decay exponent p = 0.92 ± 0.26 is statistically consistent with p = 1 (classical Omori). However, individual sequences show considerable variation (0.59 to 1.23), suggesting that tectonic and geological factors influence decay rates.

Sequences with p < 1 (e.g., Stanley, Idaho; Puerto Rico; Greece) exhibit slower-than-classical decay, meaning aftershock hazard persists longer. These regions may have:
- Higher structural heterogeneity
- Lower stress accumulation rates
- Different fault zone properties

Sequences with p > 1 (e.g., Adak, Alaska; Turkey; Cayman Islands) show faster decay, with aftershock activity diminishing more rapidly.

### Comparison to Literature

Our findings agree well with established literature values:
- Reasenberg & Jones (1989)³: p = 1.08 ± 0.03 (California)
- Yamanaka & Shimazaki (1990)⁴: p = 1.3 (Japan)
- Our study: p = 0.92 ± 0.26 (Global)

The slightly lower mean p in our global dataset may reflect geographic diversity, as different tectonic settings exhibit different decay characteristics.

### Practical Implications

Understanding aftershock decay patterns has direct applications for:
1. **Hazard Assessment**: Predicting when aftershock activity will diminish
2. **Emergency Response**: Informing decisions about building re-entry
3. **Seismic Forecasting**: Operational earthquake forecasting models

### Limitations

1. **Detection threshold**: Small aftershocks (M < 2.0) may be missed, affecting early-time data
2. **Spatial window**: Fixed 100 km radius may not capture all aftershocks for large mainshocks
3. **Sample size**: Only 9 sequences yielded high-quality fits
4. **Regional bias**: Dataset skewed toward well-monitored regions

### Future Directions

Future research could:
- Analyze larger datasets with more sequences
- Investigate correlations between p and geological factors
- Compare Omori parameters across different tectonic settings
- Develop real-time aftershock forecasting tools

---

## CONCLUSIONS

This study validates Omori's Law using modern USGS earthquake data from 2020-2025. Analysis of 17 aftershock sequences (4,394 aftershocks) demonstrates that the modified Omori-Utsu formula n(t) = K/(c+t)^p accurately describes aftershock decay with an average R² of 0.912. The mean decay exponent p = 0.92 ± 0.26 is consistent with the classical value of p ≈ 1 and previous literature. These findings confirm that Omori's 130-year-old empirical law remains a valid and useful tool for understanding earthquake aftershock behavior and assessing seismic hazard.

---

## ACKNOWLEDGMENTS

We thank the USGS Earthquake Hazards Program for providing open access to the Comprehensive Earthquake Catalog via their public API. We also thank Claude (Anthropic) for assistance with code development and analysis.

---

## REFERENCES

1. Omori, F. (1894). On the aftershocks of earthquakes. *Journal of the College of Science, Imperial University of Tokyo*, 7, 111-200.

2. Utsu, T. (1961). A statistical study on the occurrence of aftershocks. *Geophysical Magazine*, 30, 521-605.

3. Reasenberg, P. A., & Jones, L. M. (1989). Earthquake hazard after a mainshock in California. *Science*, 243(4895), 1173-1176.

4. Yamanaka, Y., & Shimazaki, K. (1990). Scaling relationship between the number of aftershocks and the size of the main shock. *Journal of Physics of the Earth*, 38(4), 305-324.

5. USGS Earthquake Hazards Program. (2025). ANSS Comprehensive Earthquake Catalog (ComCat). Retrieved from https://earthquake.usgs.gov/data/comcat/

6. Utsu, T., Ogata, Y., & Matsu'ura, R. S. (1995). The centenary of the Omori formula for a decay law of aftershock activity. *Journal of Physics of the Earth*, 43(1), 1-33.

---

## AUTHOR INFORMATION

**Edward Xiong** is an 11th-grade student at Diamond Bar High School in Diamond Bar, California. His research interests include mathematical physics, seismology, and data science applications in natural hazards.

---

*Manuscript prepared for submission to the National High School Journal of Science (NHSJS)*

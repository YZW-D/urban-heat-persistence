# Cities with persistent high urban heat effects more than doubled worldwide over two decades

Analysis code, city-year data and figure resources accompanying the manuscript *Cities with persistent high urban heat effects more than doubled worldwide over two decades*.

The analysis traces annual urban-added heat (UAH) states for 9,713 cities worldwide over 2001–2024. High-effect status is defined using the 90th percentile of the pooled 2001–2005 city-year UAH distribution (1.4258553988 °C). Persistence is defined as at least three consecutive high-effect years, counted through each observation year.

## Getting started

From the repository root, using Python 3.10 or later:

```bash
python -m pip install -r requirements.txt
python run_all.py --mode verify
python run_all.py --mode plot
```

For statistical analysis and figure generation:

| Command | Task |
| --- | --- |
| `python run_all.py --mode verify` | Check the city-year panel and main manuscript statistics |
| `python run_all.py --mode recompute-core` | Calculate state transitions, population decomposition and regional statistics |
| `python run_all.py --mode refit-gee` | Fit the continuous- and categorical-duration GEE models for next-year exit |
| `python run_all.py --mode scenarios` | Calculate the 2024–2030 conditional extensions and 1,500 stratified city-cluster bootstrap replicates |
| `python run_all.py --mode plot` | Generate Figures 1–5 |
| `python run_all.py --mode reproduce` | Run the complete city-year analysis, checks and figure-generation workflow |

Generated results are saved in `outputs/`; the main figures are also available as PDF and PNG files in `figures/main/`.

## Repository structure

| Path | Contents |
| --- | --- |
| `data/input/` | Annual city-level UAH, ambient population, area and IPCC reference-region data, 2001–2024 |
| `figure_packages/fig1/` | Global high-effect states, consecutive durations, annual population series and conditional 2030 extensions |
| `figure_packages/fig2/` | Historical composition, state transitions, duration distributions, exit rates and GEE analyses |
| `figure_packages/fig3/` | Annual and cumulative symmetric population decompositions |
| `figure_packages/fig4/` | IPCC AR6 regional high-effect entry and exit rates and regional patterns |
| `figure_packages/fig5/` | Regional persistence accumulation and associated population change |
| `analysis/` | Conditional annual-state propagation and population-stratified bootstrap |
| `basemap/` | Map layers for geographical figures |
| `scripts/` | Data-integrity checks and manuscript-statistic tests |
| `figures/main/` | PDF and PNG versions of the five main figures |
| `docs/` | Data dictionary, figure index and GitHub upload instructions |

Figure 4 summarizes annual entry into and exit from high-effect states. Figure 5 summarizes transitions into and out of persistent states, together with regional population components.

## Results

The annual dataset contains 233,112 records across 9,713 cities. The analysis identifies 706 persistent cities in 2003 and 1,509 in 2024, among 2,127 high-effect cities in 2024. Of the 2024 persistent cities, 537 remained high throughout the 24-year record and 830 had ongoing durations of at least 11 years.

Between 2003 and 2024, the population within persistent-city boundaries increased by 613.4 million. Exact annual symmetric decomposition attributed 488.5 million (79.6%) to changes in persistent-city membership and 124.9 million (20.4%) to changes in city populations. Under early-, full- and recent-period entry conditions, the expected persistent-city totals for 2030 are 1,764, 1,813 and 1,857, respectively.

## Data and methods

Annual urban-added heat was calculated as the UTCI difference between urban pixels and matched local natural-reference pixels, aggregated within fixed 2020 city boundaries. The city-year panel combines these thermal estimates with annual ambient population and IPCC AR6 region assignments. The figure packages provide the corresponding intermediate tables and statistical procedures.

Figure 1d is plotted using `figure_packages/fig1/Fig1D_scenarios_2030.csv`. Conditional state propagation and stratified bootstrap calculations are implemented in `analysis/scenario_2030.py`, with recalculated scenario series written to `outputs/scenarios/Fig1D_recomputed.csv`.

## Data sources

- GloUTCI-M global monthly 1-km UTCI dataset and 2023–2024 extension: [Zenodo, doi:10.5281/zenodo.8310513](https://doi.org/10.5281/zenodo.8310513).
- LandScan Mosaic Annual Global Ambient Population Time Series, Version 1.0, 1975–2024: [doi:10.48690/lsm/zew2-1n91](https://doi.org/10.48690/lsm/zew2-1n91).
- IPCC AR6 reference regions: Iturbide, M. et al., *Earth System Science Data* **12**, 2959–2970 (2020).

The methodological definitions and source bibliography are detailed in the accompanying manuscript.

For Chinese instructions, see [README_CN.md](README_CN.md). For variable definitions and analysis files, see [Data dictionary](docs/DATA_DICTIONARY.md) and [Figure and analysis index](docs/FIGURE_AND_ANALYSIS_INDEX.md).

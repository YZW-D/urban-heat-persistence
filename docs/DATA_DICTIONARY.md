# Data dictionary

## City-year panel

`data/input/city_year_2001_2024.csv` records 9,713 cities across 24 years (2001–2024), totaling 233,112 city-year observations.

| Field | Definition |
| --- | --- |
| `city_id` | City identifier linking observations across years |
| `year` | Calendar year, 2001–2024 |
| `UAH_mean` | Annual mean urban-added heat (°C), calculated relative to matched natural-reference pixels |
| `population` | Annual LandScan Mosaic ambient population within the fixed 2020 city boundary (persons) |
| `urbanArea` | City-area variable used in the regression analysis |
| `IPCC_Acronym` | IPCC AR6 reference-region code assigned to the city |

## Figure 1 spatial data

`figure_packages/fig1/Fig1B_city_map_2024.csv` contains city identifiers and map coordinates (`X`, `Y`), together with the figure-specific UAH and duration attributes for visualizing high-effect states.

## State-transition and regional data

Annual high-effect entry is defined as a transition from below the UAH threshold to at or above the threshold. Annual high-effect exit is the reverse transition. Persistence begins with the third consecutive high-effect year. The regional files use these definitions to summarize different transition events.

- `figure_packages/fig4/tables/Fig4A_regional_transition_scatter.csv` contains pooled entry and exit rates, denominators and regional attributes.
- `figure_packages/fig4/tables/Fig4B_regional_transition_patterns.csv` contains region-level classifications against global pooled rates.
- `figure_packages/fig4/tables/02_regional_summary_primary.csv` contains the city counts, persistent-state transitions and population components of the IPCC AR6 regions.
- `figure_packages/fig4/tables/Supplementary_Table_S4a_annual_transitions.csv` contains regional annual transition statistics.
- `figure_packages/fig4/tables/Supplementary_Table_S4b_persistence_decomposition.csv` contains regional persistence accumulation and population decomposition statistics.

## Conditional 2030 extensions

`figure_packages/fig1/Fig1D_scenarios_2030.csv` contains conditional expected counts, population equivalents and bootstrap intervals used in Fig. 1d. `analysis/scenario_2030.py` calculates the scenarios using the city-year panel and writes the results to `outputs/scenarios/Fig1D_recomputed.csv`. The script specifies the sampling strata, replicate count and random seed.

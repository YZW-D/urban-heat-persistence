# Figure and analysis index

| Figure or table | Analysis | Script | Main data files |
| --- | --- | --- | --- |
| Fig. 1a–c | High-effect history, annual city counts, consecutive durations and persistent-city population | `figure_packages/fig1/draw_fig1.py` | `figure_packages/fig1/Fig1B_city_map_2024.csv`, `Fig1C_annual_city_states.csv`, `Fig1C_annual_population.csv` |
| Fig. 1d | Conditional state propagation, population-stratified entry and duration-specific exit, bootstrap intervals | `figure_packages/fig1/draw_fig1.py`, `analysis/scenario_2030.py` | `figure_packages/fig1/Fig1D_scenarios_2030.csv` |
| Fig. 2 | Historical composition, high-effect transitions, duration-specific exits and GEE models | `figure_packages/fig2/compute_fig2_tables.py`, `compute_gee.py`, `draw_fig2.py` | `figure_packages/fig2/Fig2*.csv` |
| Fig. 3 | Annual and cumulative symmetric population decomposition | `figure_packages/fig3/compute_fig3_tables.py`, `draw_fig3.py` | `figure_packages/fig3/Fig3*.csv` |
| Fig. 4 | IPCC AR6 regional entry/exit rates and regional transition patterns | `figure_packages/fig4/compute_regional_rates.py`, `draw_fig4.py` | `figure_packages/fig4/tables/Fig4*.csv` |
| Fig. 5 | Regional persistent-city accumulation and population-change components | `figure_packages/fig4/scripts/compute_regional_dynamics.py`, `figure_packages/fig5/draw_fig5.py` | `figure_packages/fig4/tables/02_regional_summary_primary.csv` |
| Supplementary Table S4a | Regional annual transitions and persistent-city population | `figure_packages/fig4/scripts/compute_regional_dynamics.py` | `figure_packages/fig4/tables/Supplementary_Table_S4a_annual_transitions.csv` |
| Supplementary Table S4b | Regional persistence and population decomposition | `figure_packages/fig4/scripts/compute_regional_dynamics.py` | `figure_packages/fig4/tables/Supplementary_Table_S4b_persistence_decomposition.csv` |

The main figure PDFs and PNGs are organized under `figures/main/`. Calculation scripts read the city-year panel and figure-specific tables, and write updated tables and plots to their configured output paths.

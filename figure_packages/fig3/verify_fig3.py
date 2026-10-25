#!/usr/bin/env python3
"""Verify decomposition arithmetic and manuscript rounded values."""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
p=argparse.ArgumentParser();p.add_argument('--tables',type=Path,default=Path(__file__).resolve().parent)
r=p.parse_args().tables
annual=pd.read_csv(r/'Fig3A_annual_population_decomposition.csv')
cum=pd.read_csv(r/'Fig3B_cumulative_population_decomposition.csv')
s=dict(zip(*[pd.read_csv(r/'Fig3_summary_and_endpoint_sensitivity.csv')[c] for c in ('metric','value')]))
assert annual.transition_ending_year.tolist()==list(range(2004,2025))
assert cum.transition_ending_year.tolist()==list(range(2003,2025))
cols=['entry_population','exit_population','membership_component','population_change_component','observed_delta']
assert np.allclose(annual.entry_population+annual.exit_population,annual.membership_component)
assert np.allclose(annual.membership_component+annual.population_change_component,annual.observed_delta)
for c in cols:
    assert np.allclose(cum[c].to_numpy()[1:],annual[c].cumsum().to_numpy())
assert abs(s['total_population_increase']-613403392)<.01
assert abs(s['net_membership_contribution']-488505746.5)<.01
assert abs(s['population_change_contribution']-124897645.5)<.01
assert abs(s['membership_share_of_increase_percent']-79.63857925650336)<.000001
assert abs(s['endpoint_membership_share_percent']-77.087)<.02
assert s['largest_entry_year']==2021
assert s['largest_exit_year']==2022
print('PASS: 21 annual transitions; exact decomposition identities; totals, shares and extreme years.')

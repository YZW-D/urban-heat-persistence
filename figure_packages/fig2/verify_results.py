from pathlib import Path
import numpy as np,pandas as pd
P=Path(__file__).resolve().parent
stock=pd.read_csv(P/'Fig2A_state_transition_totals.csv').set_index('measure').value
rates=pd.read_csv(P/'Fig2B_period_pooled_rates.csv').set_index('period')
comp=pd.read_csv(P/'Fig2C_2024_duration_composition.csv')
obs=pd.read_csv(P/'Fig2D_observed_exit_rates.csv')
pred=pd.read_csv(P/'Fig2D_GEE_marginal_probabilities.csv')
or_=pd.read_csv(P/'Fig2D_GEE_duration_OR.csv').iloc[0]
checks={
 '2024 high total':int(stock.short_high_1_2y+stock.persistent_3plus)==2127,
 '2024 below count':int(stock.below_threshold)==7586,
 '2024 persistent count':int(stock.persistent_3plus)==1509,
 'high entries 2001-2024':int(stock.high_entries_2001_2024)==6081,
 'high exits 2001-2024':int(stock.high_exits_2001_2024)==4726,
 'persistent entries after 2003':int(stock.persistent_entries_after_2003)==1850,
 'persistent exits after 2003':int(stock.persistent_exits_after_2003)==1047,
 'net persistence expansion':int(stock.persistent_baseline_2003+stock.persistent_entries_after_2003-stock.persistent_exits_after_2003)==1509,
 'early entry pooled rate':abs(rates.loc['Earlier','pooled_entry_pct']-2.66)<.01,
 'late entry pooled rate':abs(rates.loc['Later','pooled_entry_pct']-3.57)<.01,
 'early exit pooled rate':abs(rates.loc['Earlier','pooled_exit_pct']-16.92)<.01,
 'late exit pooled rate':abs(rates.loc['Later','pooled_exit_pct']-14.94)<.01,
 '2024 duration total':int(comp.n_cities.sum())==2127,
 '2024 >=11 years count':int(comp.iloc[-1].n_cities)==830,
 'model risk records':int(or_.n_records)==29853,
 'model exits':int(or_.n_exits)==4726,
 'duration OR match':abs(or_.OR_per_doubling-.735)<.001,
 'categorical predictions match Supplementary Table S3':np.allclose(pred.adjusted_exit_probability_pct,[18.78,17.04,15.33,12.60,11.82,9.68],atol=.01),
 'exit group risk rows':int(obs.risk_city_years.sum())==29853,
 'exit group exits':int(obs.exits.sum())==4726,
}
print('Checks:',sum(checks.values()),'/',len(checks))
for name,ok in checks.items():print(('PASS' if ok else 'FAIL'),name)
assert all(checks.values()),'One or more validation checks failed'

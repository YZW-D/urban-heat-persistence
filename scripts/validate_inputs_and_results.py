"""Check master panel and central current-manuscript quantities."""
from pathlib import Path
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
a=pd.read_csv(ROOT/'data/input/city_year_2001_2024.csv').sort_values(['city_id','year'])
assert len(a)==233112 and a.city_id.nunique()==9713
assert a.groupby('city_id').year.nunique().eq(24).all()
assert not a.duplicated(['city_id','year']).any()
assert not a[['city_id','year','UAH_mean','population']].isna().any().any()
t=a.loc[a.year.between(2001,2005),'UAH_mean'].quantile(.9)
assert abs(t-1.4258553988)<1e-7
high=a.UAH_mean>=t;g=(~high).groupby(a.city_id).cumsum()
a['duration']=high.groupby([a.city_id,g],sort=False).cumsum().astype(int)
a['persistent']=a.duration>=3;a['high']=high
x=a[a.year==2024];y=a[a.year==2003]
assert (int(x.high.sum()),int(x.persistent.sum()),int(y.persistent.sum()))==(2127,1509,706)
p2003=int(y.loc[y.persistent,'population'].sum());p2024=int(x.loc[x.persistent,'population'].sum())
assert (p2003,p2024)==(410670865,1024074257)
f2=pd.read_csv(ROOT/'figure_packages/fig2/Fig2A_state_transition_totals.csv').set_index('measure').value
assert int(f2['persistent_entries_after_2003'])==1850
assert int(f2['persistent_exits_after_2003'])==1047
vals=pd.read_csv(ROOT/'figure_packages/fig4/tables/08_global_consistency_checks.csv')
vals=dict(zip(vals.metric,vals.value))
assert int(vals['persistence_2024'])==1509
assert abs(float(vals['population_membership_component'])-488505746.5)<1
assert abs(float(vals['population_demographic_component'])-124897645.5)<1
print('PASS: 233112 observations, 9713 cities, P90, 2003/2024 totals, population, global component checks.')
print('REGIONS: Regional assignments use IPCC_Acronym in the city-year panel.')

#!/usr/bin/env python3
"""Calculate the Fig. 4 regional high-effect entry and exit rates.

Regional statistics use the IPCC_Acronym attribute in the city-year panel.
"""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent/'tables'
OUT.mkdir(parents=True,exist_ok=True)
a=pd.read_csv(ROOT/'data/input/city_year_2001_2024.csv',usecols=['city_id','year','UAH_mean','population','IPCC_Acronym'])
a=a.sort_values(['city_id','year']).reset_index(drop=True)
assert a.groupby('city_id').IPCC_Acronym.nunique().eq(1).all()
threshold=a.loc[a.year.between(2001,2005),'UAH_mean'].quantile(.90)
a['high']=a.UAH_mean.ge(threshold)
g=(~a.high).groupby(a.city_id).cumsum()
a['duration']=a.high.groupby([a.city_id,g],sort=False).cumsum().astype(int)
a['persistent']=a.duration.ge(3)
a['next_high']=a.groupby('city_id',sort=False).high.shift(-1)
risk=a[a.year.lt(2024)].copy()
risk['eligible_entry']=(~risk.high).astype(int)
risk['eligible_exit']=risk.high.astype(int)
risk['entry']=(~risk.high & risk.next_high.eq(True)).astype(int)
risk['exit']=(risk.high & risk.next_high.eq(False)).astype(int)
risk_totals=risk.groupby('IPCC_Acronym')[['eligible_entry','eligible_exit','entry','exit']].sum()
last=a[a.year.eq(2024)].groupby('IPCC_Acronym').agg(cities=('city_id','size'),persistent_cities=('persistent','sum'),total_population=('population','sum'),persistent_population=('population',lambda s: s[a.loc[s.index,'persistent']].sum()))
z=last.join(risk_totals).reset_index().rename(columns={'IPCC_Acronym':'region','eligible_entry':'entry_risk','eligible_exit':'exit_risk','entry':'entries','exit':'exits'})
z['entry_rate_pct']=100*z.entries/z.entry_risk
z['exit_rate_pct']=100*z.exits/z.exit_risk.replace(0,np.nan)
z['persistent_city_share_pct']=100*z.persistent_cities/z.cities
z['persistent_population_million']=z.persistent_population/1e6
z['persistent_population_share_pct']=100*z.persistent_population/z.total_population
z['eligible_pattern']=z.cities.ge(50)
z['scatter_within_range']=z.entry_rate_pct.le(13.5)&z.exit_rate_pct.le(45)
entry_global=100*z.entries.sum()/z.entry_risk.sum()
exit_global=100*z.exits.sum()/z.exit_risk.sum()
def pattern(row):
    if not row.eligible_pattern:return 'sparse'
    return ('high' if row.entry_rate_pct>entry_global else 'low')+'_'+('high' if row.exit_rate_pct>exit_global else 'low')
z['pattern_code']=z.apply(pattern,axis=1)
names={'low_low':'Low entry, low exit','low_high':'Low entry, high exit','high_low':'High entry, low exit','high_high':'High entry, high exit','sparse':'Fewer than 50 cities'}
z['pattern_name']=z.pattern_code.map(names)
panel=z[['region','cities','entry_risk','entries','entry_rate_pct','exit_risk','exits','exit_rate_pct','persistent_cities','persistent_city_share_pct','persistent_population_million','eligible_pattern','scatter_within_range']]
panel.to_csv(OUT/'Fig4A_regional_transition_scatter.csv',index=False,float_format='%.10f')
z[['region','cities','entry_rate_pct','exit_rate_pct','pattern_code','pattern_name','eligible_pattern']].to_csv(OUT/'Fig4B_regional_transition_patterns.csv',index=False,float_format='%.10f')
s4=z[['region','cities','entry_rate_pct','exit_rate_pct','pattern_code','eligible_pattern','persistent_city_share_pct','persistent_population_million','persistent_population_share_pct']].rename(columns={'eligible_pattern':'eligible_quadrant'})
s4.to_csv(OUT/'Supplementary_Table_S4a_annual_transitions.csv',index=False,float_format='%.10f')
ref=[('UAH fixed threshold, 2001-2005 pooled P90 (deg C)',threshold),('city count',a.city_id.nunique()),('city-year records',len(a)),('regions with study cities',len(z)),('regions with >=50 cities',sum(z.eligible_pattern)),('global entry events',sum(z.entries)),('global entry eligible transitions',sum(z.entry_risk)),('global entry rate (%)',entry_global),('global exit events',sum(z.exits)),('global exit eligible transitions',sum(z.exit_risk)),('global exit rate (%)',exit_global)]
pd.DataFrame(ref,columns=['metric','value']).to_csv(OUT/'Fig4_global_reference_values.csv',index=False)
assert len(z)==43
assert (int(z.entries.sum()),int(z.exits.sum()))==(6081,4726)
assert abs(entry_global-3.141889)<.001 and abs(exit_global-15.8309)<.001
print(f'PASS: 43 regions; global entry {entry_global:.4f}%, exit {exit_global:.4f}%')

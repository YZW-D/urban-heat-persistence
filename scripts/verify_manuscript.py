#!/usr/bin/env python3
"""Numerical checks against the main-text results and figure tables."""
from pathlib import Path
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
a=pd.read_csv(ROOT/'data/input/city_year_2001_2024.csv').sort_values(['city_id','year'])
assert len(a)==233112 and a.city_id.nunique()==9713
assert a.groupby('city_id').year.nunique().eq(24).all()
t=a.loc[a.year.between(2001,2005),'UAH_mean'].quantile(.9)
assert abs(t-1.4258553988)<1e-7
h=a.UAH_mean.ge(t); reset=(~h).groupby(a.city_id).cumsum()
a['duration']=h.groupby([a.city_id,reset],sort=False).cumsum().astype(int)
a['high']=h;a['persistent']=a.duration.ge(3)
x=a[a.year.eq(2024)].copy();b=a[a.year.eq(2003)].copy()
assert (int(x.high.sum()),int(x.persistent.sum()),int(b.persistent.sum()))==(2127,1509,706)
assert (int(b.loc[b.persistent,'population'].sum()),int(x.loc[x.persistent,'population'].sum()))==(410670865,1024074257)
assert x.duration.ge(11).sum()==830
persistent=x[x.persistent].copy()
assert sum(persistent.duration.eq(24))==537
assert int(persistent.loc[persistent.duration.eq(24),'population'].sum())==451819489
first_year_ongoing=2025-persistent.duration
first_high_year=a[a.high].groupby('city_id').year.min()
persistent['previously_high']=persistent.city_id.map(first_high_year).lt(first_year_ongoing)
assert int(persistent.previously_high.sum())==840
assert int((~persistent.previously_high & persistent.duration.lt(24)).sum())==132
history=pd.read_csv(ROOT/'figure_packages/fig2/Fig2A_2024_history_composition.csv').set_index('history_class')
assert history.loc[['High in every year','Previously exited high state','First observed high spell'],'cities'].tolist()==[537,840,132]
assert int(history.population.sum())==1024074257
assert int(persistent.loc[persistent.previously_high,'population'].sum())==365053997
reg=x.groupby('IPCC_Acronym').agg(persistent_count=('persistent','sum'),
                                 persistent_population=('population',lambda s: s[x.loc[s.index,'persistent']].sum()))
assert int(reg.loc[['EAS','SEA'],'persistent_count'].sum())==446
assert abs(reg.loc[['EAS','SEA'],'persistent_population'].sum()/1e6-427.5)<.15
regional=pd.read_csv(ROOT/'figure_packages/fig4/tables/02_regional_summary_primary.csv')
assert len(regional)==43
assert int(regional.net.gt(0).sum())==38
assert int(regional.net.eq(0).sum())==5
assert not regional.net.lt(0).any()
assert int(regional.entry.sum())==1850 and int(regional.exit.sum())==1047
assert abs(regional.loc[regional.region.eq('EAS'),'population_change_m'].iloc[0]-166.1543)<.01
assert abs(regional.loc[regional.region.eq('SEA'),'population_change_m'].iloc[0]-87.6291)<.01
assert abs(regional.loc[regional.region.eq('EAS'),'membership_share_population_change_pct'].iloc[0]-98.843)<.01
assert abs(regional.loc[regional.region.eq('SEA'),'membership_share_population_change_pct'].iloc[0]-80.446)<.01
scenarios=pd.read_csv(ROOT/'figure_packages/fig1/Fig1D_scenarios_2030.csv')
expected=scenarios[scenarios.year.eq(2030)].set_index('scenario').expected_persistent_cities
assert abs(expected.Early-1764.48730071)<1e-5
assert abs(expected.Full-1813.18966087)<1e-5
assert abs(expected.Recent-1856.91665589)<1e-5
print('PASS: main-text counts, 2024 histories, regional changes, population, and 2030 scenarios.')

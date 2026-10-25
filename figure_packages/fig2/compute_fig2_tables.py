#!/usr/bin/env python3
"""Calculate Figure 2 statistics from the city-year analysis panel.
The high-effect threshold uses the full-precision pooled 2001–2005 P90 UAH value.
Annual transitions use (year t, t+1), with the calendar label being transition ending year.
"""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import norm

ROOT=Path(__file__).resolve().parent
SOURCE=ROOT.parents[1]/'data/input/city_year_2001_2024.csv'
df=pd.read_csv(SOURCE).sort_values(['city_id','year']).reset_index(drop=True)
thr=df.loc[df.year.between(2001,2005),'UAH_mean'].quantile(.90)
df['high']=df.UAH_mean>=thr
run=(~df.high).groupby(df.city_id).cumsum()
df['duration']=df.high.groupby([df.city_id,run],sort=False).cumsum().astype(int)
df['persistent']=df.duration.ge(3)
df['prev_high']=df.groupby('city_id').high.shift(1)
df['prev_persistent']=df.groupby('city_id').persistent.shift(1)
df['next_high']=df.groupby('city_id').high.shift(-1)
df['high_entry']=((df.high)&(df.prev_high==False)).astype(int)
df['high_exit']=((~df.high)&(df.prev_high==True)).astype(int)
df['persistent_entry']=((df.persistent)&(df.prev_persistent==False)).astype(int)
df['persistent_exit']=((~df.persistent)&(df.prev_persistent==True)).astype(int)
ann=df.groupby('year',as_index=False).agg(high_cities=('high','sum'),persistent_cities=('persistent','sum'),all_cities=('city_id','size'),high_entries=('high_entry','sum'),high_exits=('high_exit','sum'),persistent_entries=('persistent_entry','sum'),persistent_exits=('persistent_exit','sum'))
ann['short_high_cities']=ann.high_cities-ann.persistent_cities
ann['high_net_change']=ann.high_entries-ann.high_exits
ann['persistent_net_change']=ann.persistent_entries-ann.persistent_exits
ann.to_csv(ROOT/'Fig2B_annual_transitions.csv',index=False)
transitions=ann[ann.year.between(2002,2024)]
# eligibility denominators from starting-year state
rec=df[df.year<=2023].groupby('year').agg(risk_entry=('high',lambda z:(~z).sum()), risk_exit=('high','sum')).reset_index()
rec['ending_year']=rec.year+1
rates=transitions.merge(rec,left_on='year',right_on='ending_year',validate='one_to_one')
periods=[('Earlier',2002,2012),('Later',2014,2024),('Full record',2002,2024)]
pr=[]
for label,a,b in periods:
 sub=rates[rates.year_x.between(a,b)]
 entries=int(sub.high_entries.sum());exits=int(sub.high_exits.sum())
 entry_risk=int(sub.risk_entry.sum());exit_risk=int(sub.risk_exit.sum())
 pr.append(dict(period=label,transition_start=a-1,transition_end=b,transitions=len(sub),high_entries=entries,eligible_below=entry_risk,pooled_entry_pct=entries/entry_risk*100,high_exits=exits,eligible_above=exit_risk,pooled_exit_pct=exits/exit_risk*100))
period_rates=pd.DataFrame(pr)
period_rates.to_csv(ROOT/'Fig2B_period_pooled_rates.csv',index=False)
# Calculate the 2024 high-effect and persistent-city counts.
last=df[df.year==2024]
flow={'below_threshold':int((~last.high).sum()),'short_high_1_2y':int((last.high & ~last.persistent).sum()),'persistent_3plus':int(last.persistent.sum()),'high_entries_2001_2024':int(transitions.high_entries.sum()),'high_exits_2001_2024':int(transitions.high_exits.sum()),'high_exits_after_1_2y':int(((df.year>=2002)&(~df.high)&(df.prev_high==True)&(df.groupby('city_id').duration.shift(1).isin([1,2]))).sum()),'high_exits_after_3plusy':int(((df.year>=2002)&(~df.high)&(df.prev_high==True)&(df.groupby('city_id').duration.shift(1).ge(3))).sum()),'persistent_entries_after_2003':int(ann.loc[ann.year>=2004,'persistent_entries'].sum()),'persistent_exits_after_2003':int(ann.loc[ann.year>=2004,'persistent_exits'].sum()),'persistent_baseline_2003':int(ann.loc[ann.year==2003,'persistent_cities'].iloc[0])}
stock=pd.DataFrame([{'measure':k,'value':v} for k,v in flow.items()]);stock.to_csv(ROOT/'Fig2A_state_transition_totals.csv',index=False)
# Partition the 2024 persistent set by its observed spell history.
first_high_year=df[df.high].groupby('city_id').year.min()
persist2024=last[last.persistent].copy()
persist2024['current_spell_start']=2025-persist2024.duration
persist2024['history_class']='First observed high spell'
persist2024.loc[persist2024.city_id.map(first_high_year).lt(persist2024.current_spell_start),'history_class']='Previously exited high state'
persist2024.loc[persist2024.duration.eq(24),'history_class']='High in every year'
history_labels=['High in every year','Previously exited high state','First observed high spell']
history=(persist2024.groupby('history_class').agg(cities=('city_id','size'),population=('population','sum'))
         .reindex(history_labels).reset_index())
history['city_share_pct']=100*history.cities/len(persist2024)
history['population_share_pct']=100*history.population/persist2024.population.sum()
history.to_csv(ROOT/'Fig2A_2024_history_composition.csv',index=False)
assert history.cities.tolist()==[537,840,132]
assert history.population.tolist()==[451819489,365053997,207200771]

# Duration counts in 2024 (single-year snapshot avoids comparing unmatched observable durations)
classes=['1','2','3','4–5','6–10','≥11']
classify=lambda d:pd.cut(d,bins=[0,1,2,3,5,10,np.inf],labels=classes)
high_last=last[last.high].copy();high_last['duration_group']=classify(high_last.duration)
comp=high_last.groupby('duration_group',observed=False).agg(n_cities=('city_id','size')).reindex(classes).reset_index()
comp['share_high_pct']=100*comp.n_cities/len(high_last)
comp['cumulative_share_pct']=comp.share_high_pct.cumsum()
comp.to_csv(ROOT/'Fig2C_2024_duration_composition.csv',index=False)
# Historical observed next-year exit by duration; excludes 2024 from risk set
risk=df[(df.high)&(df.year<2024)].copy()
risk['exit_next_year']=(risk.next_high==False).astype(int)
risk['duration_group']=classify(risk.duration)
ex=risk.groupby('duration_group',observed=False).agg(risk_city_years=('city_id','size'),exits=('exit_next_year','sum')).reindex(classes).reset_index()
ex['observed_exit_pct']=100*ex.exits/ex.risk_city_years
# 95% city-cluster bootstrap for descriptive pooled exit rates;
# resampling cities preserves within-city correlation across years and duration categories.
z=norm.ppf(.975);n=ex.risk_city_years.to_numpy();k=ex.exits.to_numpy();p=k/n
center=(p+z*z/(2*n))/(1+z*z/n);half=z*np.sqrt((p*(1-p)/n)+(z*z/(4*n*n)))/(1+z*z/n)
ex['observed_wilson_ci_low_pct']=100*(center-half);ex['observed_wilson_ci_high_pct']=100*(center+half)
# Resample the 2,721 at-risk cities with replacement.
city_codes,unique_cities=pd.factorize(risk.city_id)
class_codes=risk.duration_group.cat.codes.to_numpy()
num_cities=len(unique_cities);num_classes=len(classes)
n_mat=np.zeros((num_cities,num_classes),dtype=np.int64)
k_mat=np.zeros((num_cities,num_classes),dtype=np.int64)
np.add.at(n_mat,(city_codes,class_codes),1)
np.add.at(k_mat,(city_codes,class_codes),risk.exit_next_year.to_numpy())
rng=np.random.default_rng(20261010)
boot=np.empty((1500,num_classes),dtype=float)
for bi in range(1500):
    ids=rng.integers(0,num_cities,size=num_cities)
    ns=n_mat[ids].sum(axis=0);ks=k_mat[ids].sum(axis=0)
    boot[bi]=np.divide(100*ks,ns,out=np.full(num_classes,np.nan),where=ns>0)
ex['observed_bootstrap_ci_low_pct']=np.nanquantile(boot,.025,axis=0)
ex['observed_bootstrap_ci_high_pct']=np.nanquantile(boot,.975,axis=0)
ex.to_csv(ROOT/'Fig2D_observed_exit_rates.csv',index=False)
# checks
assert len(df)==9713*24
assert [int(x) for x in stock.value[:3]]==[7586,618,1509],stock
assert flow['high_entries_2001_2024']==6081 and flow['high_exits_2001_2024']==4726,flow
assert flow['high_exits_after_1_2y']==3679 and flow['high_exits_after_3plusy']==1047,flow
assert flow['persistent_entries_after_2003']==1850 and flow['persistent_exits_after_2003']==1047,flow
assert ex.exits.sum()==4726 and ex.risk_city_years.sum()==29853
assert comp.n_cities.sum()==2127
assert comp.iloc[-1].n_cities==830
print('THRESHOLD',thr)
print('FLOW',flow)
print('PERIOD RATES\n',period_rates.to_string(index=False))
print('DURATION 2024\n',comp.to_string(index=False))
print('EXIT RISK\n',ex.to_string(index=False))

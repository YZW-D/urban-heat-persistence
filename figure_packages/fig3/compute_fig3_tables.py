#!/usr/bin/env python3
"""Reconstruct high-effect persistence and reproduce Figure 3 symmetric population decomposition.

Usage:
  python figure_packages/fig3/compute_fig3_tables.py --input data/input/city_year_2001_2024.csv --output figure_packages/fig3

Input requirements: city_id, year, UAH_mean, population. Threshold is the
90th percentile of the pooled 2001--2005 UAH city-years. Classification
uses the full-precision percentile value.

For each adjacent-year pair, write P_it for population and I_it for an indicator
that the high UAH run has persisted for at least three years. The exact identity:
  I_t*P_t - I_prev*P_prev =
    (I_t-I_prev) * (P_t+P_prev)/2 + (P_t-P_prev)*(I_t+I_prev)/2
The first term is the city-set membership component (positive entries, negative
exits). The second term includes the symmetrically weighted population changes
within cities whose persistence membership changes.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd


def compute(input_path: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(input_path, usecols=['city_id','year','UAH_mean','population'])
    df = df.sort_values(['city_id','year']).reset_index(drop=True)
    if df[['city_id','year','UAH_mean','population']].isna().any().any():
        raise ValueError('Missing values in required columns')
    if df.duplicated(['city_id','year']).any():
        raise ValueError('Duplicate city-year records')
    if df.year.nunique()!=24 or df.year.min()!=2001 or df.year.max()!=2024:
        raise ValueError('Expected complete 2001--2024 time coverage')
    cnt = df.groupby('city_id').year.size()
    if not cnt.eq(24).all():
        raise ValueError('Some cities do not have the complete 24-year record')
    threshold = df.loc[df.year.between(2001,2005),'UAH_mean'].quantile(.90)
    df['high'] = (df.UAH_mean >= threshold).astype(np.int8)
    # grouped cumsum that restarts after every year below the threshold
    reset = df['high'].eq(0) | df['city_id'].ne(df['city_id'].shift())
    df['duration'] = df.groupby(reset.cumsum(),sort=False)['high'].cumsum().astype(np.int8)
    df['persistent'] = (df.duration >= 3).astype(np.int8)
    g = df.groupby('city_id', sort=False)
    df['population_previous'] = g.population.shift(1)
    df['persistent_previous'] = g.persistent.shift(1)
    transitions = df[df.year.between(2004,2024)].copy()
    I_new = transitions.persistent.astype(float).to_numpy()
    I_old = transitions.persistent_previous.to_numpy()
    P_new = transitions.population.astype(float).to_numpy()
    P_old = transitions.population_previous.to_numpy()
    membership = (I_new-I_old)*(P_new+P_old)/2.0
    demographic = (P_new-P_old)*(I_new+I_old)/2.0
    direct_delta = (I_new*P_new)-(I_old*P_old)
    assert np.allclose(membership+demographic,direct_delta,atol=1e-7)
    transitions['entry_population'] = np.where(I_new>I_old,membership,0.)
    transitions['exit_population'] = np.where(I_new<I_old,membership,0.)
    transitions['membership_component'] = membership
    transitions['population_change_component'] = demographic
    transitions['observed_delta'] = direct_delta
    grouped = transitions.groupby('year', sort=True)[['entry_population','exit_population','membership_component','population_change_component','observed_delta']].sum()
    yearly = grouped.reset_index().rename(columns={'year':'transition_ending_year'})
    yearly.to_csv(output/'Fig3A_annual_population_decomposition.csv',index=False,float_format='%.6f')
    cumulative = yearly.copy()
    for col in grouped.columns:
        cumulative[col] = cumulative[col].cumsum()
    initial = {c:0. for c in grouped.columns}
    initial['transition_ending_year'] = 2003
    cumulative = pd.concat([pd.DataFrame([initial]),cumulative],ignore_index=True)
    cumulative.to_csv(output/'Fig3B_cumulative_population_decomposition.csv',index=False,float_format='%.6f')

    p2003 = float(df.loc[(df.year==2003)&(df.persistent==1),'population'].sum())
    p2024 = float(df.loc[(df.year==2024)&(df.persistent==1),'population'].sum())
    e = float(grouped.entry_population.sum()); x=float(grouped.exit_population.sum())
    m = float(grouped.membership_component.sum());d=float(grouped.population_change_component.sum())
    delta = float(grouped.observed_delta.sum())
    assert abs((e+x)-m)<1e-5
    assert abs(m+d-delta)<1e-5
    assert abs(p2024-p2003-delta)<1e-5
    assert abs((m/delta*100)-79.63857925650336)<0.01
    assert abs(e/1e6-776.0105865)<0.01 and abs(x/1e6+287.50484)<0.01
    # Calculate the direct 2003–2024 endpoint decomposition.
    t0=df[df.year==2003].set_index('city_id'); t1=df[df.year==2024].set_index('city_id')
    assert t0.index.equals(t1.index)
    i0=t0.persistent.to_numpy(dtype=float); i1=t1.persistent.to_numpy(dtype=float)
    n0=t0.population.to_numpy(dtype=float); n1=t1.population.to_numpy(dtype=float)
    endpoint_m=float(np.sum((i1-i0)*(n1+n0)/2))
    endpoint_d=float(np.sum((n1-n0)*(i1+i0)/2))
    assert abs(endpoint_m+endpoint_d-delta)<1e-5
    summary_rows = [
       ('city_count',df.city_id.nunique(),'cities'),
       ('city_year_records',len(df),'city-year records'),
       ('baseline_threshold_uah_c',threshold,'degrees C'),
       ('base_population_persistent_2003',p2003,'persons'),
       ('final_population_persistent_2024',p2024,'persons'),
       ('total_population_increase',delta,'persons'),
       ('cumulative_entry_contribution',e,'persons'),
       ('cumulative_exit_contribution',x,'persons'),
       ('net_membership_contribution',m,'persons'),
       ('population_change_contribution',d,'persons'),
       ('membership_share_of_increase_percent',m/delta*100,'percent'),
       ('population_change_share_of_increase_percent',d/delta*100,'percent'),
       ('endpoint_membership_contribution',endpoint_m,'persons'),
       ('endpoint_population_change_contribution',endpoint_d,'persons'),
       ('endpoint_membership_share_percent',endpoint_m/delta*100,'percent'),
       ('largest_entry_year',int(grouped.entry_population.idxmax()),'calendar year'),
       ('largest_entry_contribution',float(grouped.entry_population.max()),'persons'),
       ('largest_exit_year',int(grouped.exit_population.idxmin()),'calendar year'),
       ('largest_exit_contribution',float(grouped.exit_population.min()),'persons'),
    ]
    summary = pd.DataFrame(summary_rows,columns=['metric','value','unit'])
    summary.to_csv(output/'Fig3_summary_and_endpoint_sensitivity.csv',index=False,float_format='%.9f')
    print('FIG3 RECONCILIATION:')
    print(f'  Population 2003 / 2024: {p2003/1e6:,.3f} / {p2024/1e6:,.3f} million')
    print(f'  Entry / exit: {e/1e6:+,.3f} / {x/1e6:+,.3f} million')
    print(f'  Membership / population change: {m/1e6:+,.3f} / {d/1e6:+,.3f} million')
    print(f'  Total increase: {delta/1e6:+,.3f} million')
    print(f'  Shares: {m/delta*100:.3f}% / {d/delta*100:.3f}%')
    print(f'  Alternative endpoint membership share: {endpoint_m/delta*100:.3f}%')
    return yearly,cumulative,summary

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',type=Path,default=Path(__file__).resolve().parents[2]/'data/input/city_year_2001_2024.csv')
    ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
    args=ap.parse_args()
    compute(args.input,args.output)

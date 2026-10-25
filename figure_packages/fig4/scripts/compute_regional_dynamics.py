#!/usr/bin/env python3
"""Calculate regional high-effect and persistence statistics.
City-to-region assignments use the IPCC_Acronym attribute in the annual panel.
"""
from __future__ import annotations
import argparse,csv,math,collections
from pathlib import Path
import numpy as np

YEARS=tuple(range(2001,2025))
NUM_FIELDS=['entry','exit','net','entry_pop','exit_pop','membership_pop','demographic_pop','population_change']

def write_csv(p,rows,headers=None):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    rows=list(rows)
    if headers is None:headers=list(rows[0].keys()) if rows else []
    with p.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=headers,extrasaction='ignore');w.writeheader();w.writerows(rows)

def safe_pct(num,den):return 100*num/den if den else ''

def compute_groups(cities,assignments,threshold,validate_primary=True):
    # every city has a time series of all 24 years
    regional=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(float)))
    global_rows=collections.defaultdict(lambda:collections.defaultdict(float))
    all_city_events=[]
    for cid,series in cities.items():
        region=assignments[cid]
        persist={};pop={};high={};dur=0
        for year in YEARS:
            r=series[year];pop[year]=int(r['population']);high[year]=float(r['UAH_mean'])>=threshold
            dur=dur+1 if high[year] else 0
            persist[year]=int(dur>=3)
            if year>=2003:
                for bucket in [regional[region][year],global_rows[year]]:
                    bucket['cities']+=1
                    bucket['persistent_cities']+=persist[year]
                    bucket['population_total']+=pop[year]
                    bucket['persistent_population']+=persist[year]*pop[year]
        for year in range(2004,2025):
            a=persist[year-1];b=persist[year];p0=pop[year-1];p1=pop[year]
            entry=int(a==0 and b==1);ex=int(a==1 and b==0)
            membership=(b-a)*(p0+p1)/2
            demo=(p1-p0)*(a+b)/2
            values={'entry':entry,'exit':ex,'net':b-a,'entry_pop':max(membership,0) if entry else 0,
                    'exit_pop':membership if ex else 0,'membership_pop':membership,
                    'demographic_pop':demo,'population_change':b*p1-a*p0}
            for bucket in [regional[region][year],global_rows[year]]:
                for k,v in values.items():bucket[k]+=v
            if entry or ex:
                all_city_events.append({'city_id':cid,'year':year,'region':region,
                  'transition':'entry' if entry else 'exit','population_prev':p0,'population_current':p1,
                  'membership_contribution':membership,'population_change_contribution':demo})
    regional_summary=[];yearly=[]
    for region,d in sorted(regional.items()):
        s={'region':region,'cities':int(d[2024]['cities']),
           'persistent_2003':int(d[2003]['persistent_cities']),
           'persistent_2024':int(d[2024]['persistent_cities']),
           'population_persistent_2003':int(d[2003]['persistent_population']),
           'population_persistent_2024':int(d[2024]['persistent_population'])}
        for k in NUM_FIELDS:s[k]=sum(d[y][k] for y in range(2004,2025))
        s.update({
          'membership_share_population_change_pct':safe_pct(s['membership_pop'],s['population_change']),
          'demographic_share_population_change_pct':safe_pct(s['demographic_pop'],s['population_change']),
          'net_persistent_count_per_100_cities':safe_pct(s['net'],s['cities']),
          'persistent_population_2024_m':s['population_persistent_2024']/1e6,
          'population_change_m':s['population_change']/1e6,
          'membership_pop_m':s['membership_pop']/1e6,
          'demographic_pop_m':s['demographic_pop']/1e6})
        assert s['net']==s['persistent_2024']-s['persistent_2003'], (region,s)
        assert abs(s['population_change']-(s['population_persistent_2024']-s['population_persistent_2003']))<1,region
        assert abs(s['membership_pop']+s['demographic_pop']-s['population_change'])<1,region
        regional_summary.append(s)
        for yr in range(2003,2025):
            row={'region':region,'year':yr}
            row.update({k:v for k,v in d[yr].items()})
            yearly.append(row)
    gs= {'region':'GLOBAL','cities':int(global_rows[2024]['cities']),
       'persistent_2003':int(global_rows[2003]['persistent_cities']),
       'persistent_2024':int(global_rows[2024]['persistent_cities']),
       'population_persistent_2003':int(global_rows[2003]['persistent_population']),
       'population_persistent_2024':int(global_rows[2024]['persistent_population'])}
    for k in NUM_FIELDS:gs[k]=sum(global_rows[y][k] for y in range(2004,2025))
    if validate_primary:
        assert gs['net']==803 and gs['entry']==1850 and gs['exit']==1047,gs
    assert abs(gs['membership_pop']+gs['demographic_pop']-gs['population_change'])<1
    assert gs['cities']==9713,gs
    if validate_primary:
        assert gs['persistent_2024']==1509,gs
    for s in regional_summary:
        s['share_global_net_cities_pct']=safe_pct(s['net'],gs['net'])
        s['share_global_population_increase_pct']=safe_pct(s['population_change'],gs['population_change'])
        s['share_global_membership_increase_pct']=safe_pct(s['membership_pop'],gs['membership_pop'])
    return regional_summary,yearly,gs,all_city_events


def main(root):
    infile=root.parents[1]/'data/input/city_year_2001_2024.csv'
    rows=list(csv.DictReader(infile.open(encoding='utf-8-sig',newline='')))
    cities=collections.defaultdict(dict);early=[]
    for r in rows:
        cid=int(r['city_id']);y=int(r['year'])
        if y in cities[cid]:raise RuntimeError('Duplicate city-year')
        cities[cid][y]=r
        if y<=2005:early.append(float(r['UAH_mean']))
    assert len(rows)==233112 and len(cities)==9713
    for c,years in cities.items():
        assert set(years)==set(YEARS)
        assert len({v['IPCC_Acronym'] for v in years.values()})==1
    thresh=float(np.quantile(early,.90))
    labels={cid:r[2024]['IPCC_Acronym'] for cid,r in cities.items()}
    reg,annual,glob,events=compute_groups(cities,labels,thresh)
    t=root/'tables'
    write_csv(t/'02_regional_summary_primary.csv',reg)
    write_csv(t/'04_regional_annual_primary.csv',annual)
    write_csv(t/'05_persistence_transition_events.csv',events)
    measures={'cities':glob['cities'],'city_year_rows':len(rows),'threshold_P90_2001_2005':thresh,
        'persistence_2003':glob['persistent_2003'],'persistence_2024':glob['persistent_2024'],
        'persistence_entries_2004_2024':glob['entry'],'persistence_exits_2004_2024':glob['exit'],
        'persistence_net_change':glob['net'],'persistent_population_2003':glob['population_persistent_2003'],
        'persistent_population_2024':glob['population_persistent_2024'],
        'persistent_population_change':glob['population_change'],
        'population_membership_component':glob['membership_pop'],
        'population_demographic_component':glob['demographic_pop']}
    write_csv(t/'08_global_consistency_checks.csv',[{'metric':k,'value':v} for k,v in measures.items()])
    supplement = [dict(region=r['region'], persistent_2003=r['persistent_2003'],
          persistent_2024=r['persistent_2024'], entry=int(r['entry']), exit=int(r['exit']),
          net=int(r['net']), population_change_m=r['population_change_m'],
          membership_pop_m=r['membership_pop_m'], demographic_pop_m=r['demographic_pop_m'],
          membership_share_population_change_pct=r['membership_share_population_change_pct'])
          for r in reg]
    supplement.append(dict(region='GLOBAL', persistent_2003=glob['persistent_2003'],
          persistent_2024=glob['persistent_2024'], entry=int(glob['entry']),
          exit=int(glob['exit']), net=int(glob['net']),
          population_change_m=glob['population_change']/1e6,
          membership_pop_m=glob['membership_pop']/1e6,
          demographic_pop_m=glob['demographic_pop']/1e6,
          membership_share_population_change_pct=100*glob['membership_pop']/glob['population_change']))
    write_csv(t/'Supplementary_Table_S4b_persistence_decomposition.csv', supplement)
    print('Regional totals regenerated using master IPCC_Acronym region labels:',glob)
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(Path(__file__).resolve().parents[1]))
    args=ap.parse_args();main(Path(args.root).resolve())

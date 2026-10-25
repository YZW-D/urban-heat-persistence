#!/usr/bin/env python3
"""Reproduce continuous-duration and categorical-duration GEE exit models.

Response is next-year exit among high-effect city-years during 2001–2023.
Covariates: current excess UAH, city baseline (2001–2005), full-record city
linear trend and SD (2001–2024), log population, log urban area, and
IPCC AR6 region / calendar-year fixed effects.

Model is RETROSPECTIVE: city-specific full-record trend includes years after t.
Categorical marginal standardized probabilities use robust-covariance
delta-method intervals; duration-per-doubling OR uses continuous-duration GEE.
"""
from pathlib import Path
import pandas as pd,numpy as np,time
import statsmodels.api as sm
from statsmodels.genmod.cov_struct import Exchangeable
OUT=Path(__file__).resolve().parent
f=OUT.parents[1]/'data/input/city_year_2001_2024.csv'
t=time.time();df=pd.read_csv(f).sort_values(['city_id','year']).reset_index(drop=True)
thr=df.loc[df.year.between(2001,2005),'UAH_mean'].quantile(.9)
h=df.UAH_mean>=thr
run=(~h).groupby(df.city_id).cumsum();df['duration']=h.groupby([df.city_id,run],sort=False).cumsum().astype(int)
city=df.groupby('city_id',sort=False)
city_mean=df[df.year.between(2001,2005)].groupby('city_id')['UAH_mean'].mean()
trends=pd.Series({cid:np.polyfit(v.year,v.UAH_mean,1)[0] for cid,v in city})
stds=city.UAH_mean.std(ddof=0)
df['baseline']=df.city_id.map(city_mean);df['trend']=df.city_id.map(trends);df['volatility']=df.city_id.map(stds)
df['next_high']=df.groupby('city_id').duration.shift(-1)>0
risk=df[(df.duration>0)&(df.year<2024)].copy()
risk['exit']=(~risk.next_high).astype(int)
risk['log2duration']=np.log2(risk.duration)
risk['exceedance']=risk.UAH_mean-thr
risk['log_pop']=np.log(risk.population.clip(lower=1));risk['log_area']=np.log(risk.urbanArea.clip(lower=1e-8))
vars=['exceedance','baseline','trend','volatility','log_pop','log_area']
for name in vars:risk[name]=(risk[name]-risk[name].mean())/risk[name].std(ddof=0)
print('risk',len(risk),'exits',risk.exit.sum(),'cities',risk.city_id.nunique(),'threshold',thr,'prep_time',time.time()-t,flush=True)
X=risk[['log2duration']+vars].copy()
X=pd.concat([X,pd.get_dummies(risk['IPCC_Acronym'],prefix='region',drop_first=True,dtype=float),pd.get_dummies(risk.year,prefix='year',drop_first=True,dtype=float)],axis=1)
X=sm.add_constant(X)
print('X',X.shape,flush=True)
m=sm.GEE(risk.exit.to_numpy(),X.to_numpy(),groups=risk.city_id.to_numpy(),family=sm.families.Binomial(),cov_struct=Exchangeable())
t2=time.time()
try:
 fit=m.fit(maxiter=50)
 print('fit elapsed',time.time()-t2,'total',time.time()-t,flush=True)
 idx=list(X.columns).index('log2duration')
 print('OR',np.exp(fit.params[idx]),'CI',np.exp(fit.conf_int()[idx]),flush=True)
 print('corr',fit.cov_struct.dep_params,flush=True)
except Exception as e:
 raise RuntimeError('Continuous-duration GEE fitting failed') from e
# Categorical duration GEE and marginal standardization, with analytic delta-method CIs.
from scipy.special import expit
from scipy.stats import norm
out=OUT
labels=['1','2','3','4–5','6–10','≥11']
risk['durclass']=pd.cut(risk.duration,bins=[0,1,2,3,5,10,np.inf],labels=labels)
D=pd.get_dummies(risk.durclass,prefix='duration',drop_first=True,dtype=float)
X_cat=pd.concat([D,X.drop(columns=['log2duration','const'])],axis=1)
X_cat=sm.add_constant(X_cat)
model_cat=sm.GEE(risk.exit.to_numpy(),X_cat.to_numpy(),groups=risk.city_id.to_numpy(),family=sm.families.Binomial(),cov_struct=Exchangeable())
t3=time.time();fit_cat=model_cat.fit(maxiter=60)
print('category fit elapsed',time.time()-t3,flush=True)
rows=[]
inds=[X_cat.columns.get_loc(c) for c in D.columns]
base=X_cat.to_numpy().copy()
for name in D.columns:base[:,X_cat.columns.get_loc(name)]=0
for i, lab in enumerate(labels):
 predX=base.copy()
 if i>0:predX[:,inds[i-1]]=1
 eta=predX@fit_cat.params
 p=expit(eta)
 av=p.mean()
 gradient=(predX*(p*(1-p))[:,None]).mean(axis=0)
 se=np.sqrt(np.clip(gradient@fit_cat.cov_params()@gradient,0,np.inf))
 rows.append({'duration_group':lab,'adjusted_exit_probability_pct':av*100,
              'adjusted_ci_low_pct':max(0,av-1.96*se)*100,
              'adjusted_ci_high_pct':min(1,av+1.96*se)*100})

pd.DataFrame(rows).to_csv(out/'Fig2D_GEE_marginal_probabilities.csv',index=False)
print('probabilities',pd.DataFrame(rows),flush=True)
idx=list(X.columns).index('log2duration')
res=pd.DataFrame([{'OR_per_doubling':np.exp(fit.params[idx]),'CI_low':np.exp(fit.conf_int()[idx][0]),'CI_high':np.exp(fit.conf_int()[idx][1]),'n_records':len(risk),'n_cities':risk.city_id.nunique(),'n_exits':risk.exit.sum()}]);res.to_csv(out/'Fig2D_GEE_duration_OR.csv',index=False)

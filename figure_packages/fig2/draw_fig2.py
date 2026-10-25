#!/usr/bin/env python3
"""Publication-style Figure 2, compatible with the visual system of Fig1_redesigned.
Assumes results from compute_fig2_tables.py and compute_gee.py are present.
Outputs: Fig2_redesigned.pdf/.png.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory

R=Path(__file__).resolve().parent
ann=pd.read_csv(R/'Fig2B_annual_transitions.csv')
periods=pd.read_csv(R/'Fig2B_period_pooled_rates.csv')
flow=dict(zip(*[pd.read_csv(R/'Fig2A_state_transition_totals.csv')[k] for k in ['measure','value']]))
composition=pd.read_csv(R/'Fig2C_2024_duration_composition.csv')
history=pd.read_csv(R/'Fig2A_2024_history_composition.csv')
observed=pd.read_csv(R/'Fig2D_observed_exit_rates.csv')
adjusted=pd.read_csv(R/'Fig2D_GEE_marginal_probabilities.csv')
gee=pd.read_csv(R/'Fig2D_GEE_duration_OR.csv').iloc[0]
exit_data=observed.merge(adjusted,on='duration_group',validate='one_to_one')

# Visual system shared with redesigned Figure 1.
BG='#FFFFFF'; INK='#23313B'; MUTED='#697983'; HAIR='#E4E9EC'; GRID='#EBEFF1'
PERSIST='#C65B40'; DEEP='#832D28'; SHORT='#EBC9AC'; LOW='#C7D1D5'; TEAL='#348F8B'; BLUE='#6D93B5'
CORAL='#D16B62'; PALE='#F5E2D7'; LBLUE='#EBF1F5'; RED2='#A74335'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'font.weight':'regular',
                     'axes.labelcolor':INK,'text.color':INK,'xtick.color':MUTED,'ytick.color':MUTED,
                     'axes.edgecolor':'#D9E0E3','axes.unicode_minus':False,
                     'savefig.facecolor':BG,'pdf.fonttype':42,'ps.fonttype':42})
fig=plt.figure(figsize=(16,10.5),facecolor=BG)

def put(x,y,s,fs=9,color=INK,weight='regular',ha='left',va='top',**kw):
    return fig.text(x,y,s,fontsize=fs,color=color,fontweight=weight,ha=ha,va=va,**kw)
def rule(y):
    fig.add_artist(Line2D([.055,.95],[y,y],transform=fig.transFigure,color=HAIR,lw=1))
def section(x,y,letter,title):
    put(x,y,letter,fs=12,color=PERSIST,weight='bold')
    put(x+.026,y,title,fs=12,weight='bold')

# Header
put(.055,.985,'GLOBAL URBAN HEAT',fs=9,color=PERSIST,weight='bold')
put(.055,.957,'Persistent-city accumulation reflects turnover and duration-dependent exit',fs=17,weight='bold')
put(.055,.915,'23 annual transitions  /  6,081 high-state entries  /  4,726 exits',fs=10,color=MUTED)
rule(.894)
section(.055,.877,'A','Historical composition of persistent cities')
section(.500,.877,'B','Turnover persisted as the city pool expanded')

# Panel A: the 2024 persistent-city set, partitioned by observed history.
assert history.cities.sum()==1509 and int(history.population.sum())==1024074257
bar_left=.069; bar_width=.395
colors=[DEEP,'#D99075',SHORT]
labels=['High in every year','Previously exited','First high spell']
for y,shares,title,values in [
    (.767,history.city_share_pct.to_numpy()/100.,'1,509 persistent cities',[f"{n:,}" for n in history.cities]),
    (.675,history.population_share_pct.to_numpy()/100.,'1.024 billion people',[f"{v/1e6:.1f}M" for v in history.population])]:
    put(bar_left,y+.062,title,fs=9.6,color=INK,weight='bold')
    curr=bar_left
    for i,(fraction,color) in enumerate(zip(shares,colors)):
        width=bar_width*fraction
        fig.add_artist(Rectangle((curr,y),width,.034,transform=fig.transFigure,facecolor=color,lw=.5,edgecolor='white'))
        put(curr+width/2,y+.019,f'{fraction*100:.1f}%',fs=9.2,ha='center',va='center',weight='bold',color=BG if i!=2 else INK)
        curr+=width
for i,(label,color) in enumerate(zip(labels,colors)):
    xx=[.069,.217,.356][i]
    fig.add_artist(Rectangle((xx,.619),.011,.011,transform=fig.transFigure,facecolor=color,lw=0))
    put(xx+.015,.630,label,fs=8.0,color=MUTED,va='center')
put(.069,.584,'537 throughout 2001–2024  ·  840 with a previous exit  ·  132 in their first high spell',fs=8.1,color=MUTED)

# Panel B: annual high entries/exits bars + historical count lines.
ax=fig.add_axes([.525,.616,.401,.196])
s=ann[ann.year>=2002].copy()
x=s.year.to_numpy();
ax.axhspan(0,0,alpha=0)   # plotting coordinates reserve symmetric signed flows
ax.axvspan(2001.5,2012.5,color='#EEF3F7',zorder=0,alpha=.55)
ax.axvspan(2013.5,2024.5,color='#FEF3EC',zorder=0,alpha=.65)
ax.bar(x,s.high_entries,width=.74,color=BLUE,alpha=.93,zorder=2,label='Entries')
ax.bar(x,-s.high_exits,width=.74,color=CORAL,alpha=.9,zorder=2,label='Exits')
ax.axhline(0,color=HAIR,lw=1.0)
ax.set_xlim(2001.5,2024.5);ax.set_ylim(-450,470)
ax.set_yticks([-400,-200,0,200,400]);ax.set_ylabel('Annual city transitions',fontsize=9)
ax.set_xticks([2002,2006,2010,2014,2018,2022,2024]);ax.grid(axis='y',color=GRID,lw=.8,zorder=0)
ax.spines[['top','right']].set_visible(False)
axr=ax.twinx()
axr.plot(x,s.high_cities,color=INK,lw=2.1,zorder=5,label='High-effect cities')
axr.plot(x,s.persistent_cities,color=PERSIST,lw=2.0,zorder=5,label='Persistent cities')
axr.set_ylim(0,2500);axr.set_yticks([0,1000,2000]);axr.tick_params(axis='y',colors=MUTED)
axr.set_ylabel('City count',fontsize=9)
axr.spines[['top','left']].set_visible(False)
axr.spines['right'].set_color(HAIR)
axr.annotate('2,127',xy=(2024,2127),xytext=(2022.2,2285),color=INK,fontsize=9,ha='left',weight='bold',arrowprops={'arrowstyle':'-','lw':.75,'color':INK})
axr.annotate('1,509',xy=(2024,1509),xytext=(2021.65,1380),color=PERSIST,fontsize=9,ha='left',weight='bold',arrowprops={'arrowstyle':'-','lw':.75,'color':PERSIST})
# minimalist combined legend above chart in figure space
legend_items=[('Entry events',BLUE,'bar'),('Exit events',CORAL,'bar'),('High-effect cities',INK,'line'),('Persistent cities',PERSIST,'line')]
for xx,(lab,c,typ) in zip([.52,.62,.727,.852],legend_items):
    if typ=='bar':fig.add_artist(Rectangle((xx,.832),.014,.009,transform=fig.transFigure,color=c,lw=0))
    else:fig.add_artist(Line2D([xx,xx+.018],[.838,.838],transform=fig.transFigure,color=c,lw=2))
    put(xx+.022,.841,lab,fs=8.0,va='center',color=MUTED)
# period rate summaries in one-line cards along below plot
p_e=periods[periods.period=='Earlier'].iloc[0]; p_l=periods[periods.period=='Later'].iloc[0]
put(.525,.591,'EARLIER · 2001–2012',fs=8.2,weight='bold',color=BLUE)
put(.525,.568,f"Entry {p_e.pooled_entry_pct:.2f}%   ·   Exit {p_e.pooled_exit_pct:.2f}%",fs=9.2,color=INK)
put(.737,.591,'LATER · 2013–2024',fs=8.2,weight='bold',color=PERSIST)
put(.737,.568,f"Entry {p_l.pooled_entry_pct:.2f}%   ·   Exit {p_l.pooled_exit_pct:.2f}%",fs=9.2,color=INK)

rule(.510)
section(.055,.491,'C','The duration structure in 2024')
section(.500,.491,'D','Longer duration is associated with lower exit')
# Paired duration panels use six exact shared category rows.
# C, distribution horizontally with common y positions.
ax_c=fig.add_axes([.140,.164,.292,.266])
labels=composition.duration_group.tolist()
ys=np.arange(6)[::-1]
colors=[SHORT,'#E7B58E','#DD9A75','#CF7A57','#B8503A',DEEP]
shares=composition.share_high_pct.to_numpy();ns=composition.n_cities.to_numpy()
ax_c.barh(ys,shares,height=.56,color=colors,zorder=2)
ax_c.set_xlim(0,47);ax_c.set_ylim(-.65,5.65)
ax_c.set_yticks(ys);ax_c.set_yticklabels(labels,fontsize=9)
ax_c.set_xticks([0,10,20,30,40]);ax_c.set_xlabel('Share of high-effect cities (%)',fontsize=9)
ax_c.grid(axis='x',color=GRID,lw=.8,zorder=0)
ax_c.spines[['top','right','left']].set_visible(False)
ax_c.tick_params(axis='y',length=0,pad=9)
for y,p,n in zip(ys,shares,ns):
    ax_c.text(p+.6,y,f'{n:,}  ·  {p:.1f}%',fontsize=8.6,va='center',color=INK,weight='bold' if n==830 else 'regular')
put(.060,.450,'Consecutive years above threshold',fs=8.5,color=MUTED)
# two small summary metrics at the bottom left for 2024
put(.079,.113,'2,127',fs=18,color=INK,weight='bold')
put(.079,.079,'high-effect cities',fs=8.2,color=MUTED)
put(.285,.113,'39.0%',fs=18,color=DEEP,weight='bold')
put(.285,.079,'high for ≥11 years',fs=8.2,color=MUTED)

# D, duration-aligned dot and whisker chart for observed and standardized predicted risks.
ax_d=fig.add_axes([.575,.164,.338,.266])
observ=exit_data.observed_exit_pct.to_numpy();est=exit_data.adjusted_exit_probability_pct.to_numpy()
ax_d.set_xlim(-2,53);ax_d.set_ylim(-.65,5.65)
ax_d.set_yticks(ys);ax_d.set_yticklabels(labels,fontsize=9)
ax_d.set_xticks([0,10,20,30,40,50]);ax_d.set_xlabel('Next-year exit probability (%)',fontsize=9)
ax_d.tick_params(axis='y',length=0,pad=11)
ax_d.grid(axis='x',color=GRID,lw=.8,zorder=0)
ax_d.spines[['top','right','left']].set_visible(False)
for i,y in enumerate(ys):
    ax_d.plot([observ[i],est[i]],[y,y],lw=1.1,color='#D9E0E3',zorder=1)
    ax_d.plot([exit_data.iloc[i].observed_bootstrap_ci_low_pct,exit_data.iloc[i].observed_bootstrap_ci_high_pct],[y,y],lw=1.3,color='#96A6AE',zorder=3)
    ax_d.scatter(observ[i],y,s=37,facecolor='white',edgecolor='#7C909B',linewidth=1.6,zorder=5)
    ax_d.plot([exit_data.iloc[i].adjusted_ci_low_pct,exit_data.iloc[i].adjusted_ci_high_pct],[y-.08,y-.08],lw=1.5,color=PERSIST,zorder=3)
    ax_d.scatter(est[i],y-.08,s=40,facecolor=PERSIST,edgecolor='white',linewidth=.5,zorder=5)
# legend above D aligned with plot region
fig.add_artist(Line2D([.588,.607],[.450,.450],transform=fig.transFigure,color='#7C909B',marker='o',markerfacecolor='white',lw=1,markersize=5))
put(.613,.454,'Observed',fs=8.3,color=MUTED,va='center')
fig.add_artist(Line2D([.709,.728],[.450,.450],transform=fig.transFigure,color=PERSIST,marker='o',lw=1,markersize=5))
put(.735,.454,'Adjusted GEE',fs=8.3,color=MUTED,va='center')
put(.526,.112,f"Adjusted OR per doubling   {gee.OR_per_doubling:.3f}",fs=12,color=INK,weight='bold')
put(.526,.084,f"95% CI {gee.CI_low:.3f}–{gee.CI_high:.3f}  ·  {int(gee.n_cities):,} cities  ·  {int(gee.n_records):,} at-risk city-years",fs=8.5,color=MUTED)

rule(.050)
put(.055,.032,'A: 2024 persistent-city history.  B: annual transitions.  C: 2024 high-city durations.  D: next-year exits; city-cluster bootstrap and GEE-adjusted intervals.',fs=8,color=MUTED)

OUT=R.parents[1]/'outputs/fig2';OUT.mkdir(parents=True,exist_ok=True)
outpdf=OUT/'Fig2_redesigned.pdf';outpng=OUT/'Fig2_redesigned.png'
fig.savefig(outpdf,bbox_inches='tight',facecolor='white')
fig.savefig(outpng,dpi=220,bbox_inches='tight',facecolor='white')
plt.close(fig)
print(outpdf,outpng)

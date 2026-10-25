#!/usr/bin/env python3
"""Figure 1: high-effect states, multiyear persistence and conditional extensions.

Inputs:
  data/input/city_year_2001_2024.csv
  figure_packages/fig1/Fig1B_city_map_2024.csv
  figure_packages/fig1/Fig1D_scenarios_2030.csv
  basemap/

Outputs:
  outputs/fig1/Fig1_redesigned.pdf
  outputs/fig1/Fig1_redesigned.png
  outputs/fig1/Fig1C_annual_city_states.csv
  outputs/fig1/Fig1C_annual_population.csv.
"""
from pathlib import Path
import glob
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Patch
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[2]
OUTPUT=ROOT/'outputs/fig1'
OUTPUT.mkdir(parents=True,exist_ok=True)
DATA=ROOT/'data/input/city_year_2001_2024.csv'
SCEN=ROOT/'figure_packages/fig1/Fig1D_scenarios_2030.csv'
MAP_PATH=glob.glob(str(ROOT/'basemap/02*.shp'))[0]

# Calculate UAH categories and city counts from the annual analysis panel.
df=pd.read_csv(DATA).sort_values(['city_id','year']).reset_index(drop=True)
coords=pd.read_csv(ROOT/'figure_packages/fig1/Fig1B_city_map_2024.csv',usecols=['city_id','X','Y'])
assert coords.city_id.is_unique
df=df.merge(coords,on='city_id',validate='many_to_one')
threshold=float(df.loc[df.year.between(2001,2005),'UAH_mean'].quantile(0.90))
df['high']=df.UAH_mean>=threshold
# Continuous sequence with explicit per-city reset at below-threshold years.
group=(~df['high']).groupby(df['city_id']).cumsum()
df['duration']=df['high'].groupby([df['city_id'], group],sort=False).cumsum().astype(int)
df['persistent']=df.duration>=3

def bins(d):
    return ('Below threshold' if d==0 else '1–2 years' if d<3 else '3–4 years' if d<5 else '5–7 years' if d<8 else '8–10 years' if d<11 else '11+ years')
df['duration_group']=[bins(d) for d in df.duration]
annual=df.groupby('year').agg(high_cities=('high','sum'),persistent_cities=('persistent','sum'),all_cities=('city_id','size')).reset_index()
annual['short_high_cities']=annual.high_cities-annual.persistent_cities
annual['persistent_share_high_pct']=100*annual.persistent_cities/annual.high_cities
annual_pop=(df.assign(persistent_population=np.where(df.persistent,df.population,0),
                      high_population=np.where(df.high,df.population,0))
              .groupby('year').agg(total_population=('population','sum'),persistent_population=('persistent_population','sum'),high_population=('high_population','sum')).reset_index())
annual_pop['persistent_share_all_pct']=100*annual_pop.persistent_population/annual_pop.total_population
annual_pop['persistent_share_high_pct']=100*annual_pop.persistent_population/annual_pop.high_population
map2024=df[df.year==2024].copy()
map2001=df[df.year==2001].copy()
scen=pd.read_csv(SCEN)
assert len(df)==9713*24
assert annual.loc[annual.year.eq(2024),'high_cities'].iloc[0]==2127
assert annual.loc[annual.year.eq(2024),'persistent_cities'].iloc[0]==1509
assert len(map2024)==9713
assert abs(threshold-1.425855)<0.001

annual.to_csv(OUTPUT/'Fig1C_annual_city_states.csv',index=False)
annual_pop.to_csv(OUTPUT/'Fig1C_annual_population.csv',index=False)
map2024[['city_id','X','Y','UAH_mean','duration','duration_group','population']].to_csv(OUTPUT/'Fig1B_city_map_2024.csv',index=False)
scen.to_csv(OUTPUT/'Fig1D_scenarios_2030.csv',index=False)

# ---------- Design system ----------
BG='#ffffff'; INK='#23313B'; MUTED='#697983'; HAIR='#E4E9EC'; LOW='#C7D1D5'
SHORT='#EBC9AC'; PERSIST='#C65B40'; DEEP='#832D28'; PALE='#F5E2D7'
TEAL='#348F8B'; BLUE='#737AB0'; ORANGE='#C76D35'
COUNTRIES='#F4F6F6'; COAST='#ADB6BA'; GRID='#EBEFF1'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,
                     'font.weight':'regular','axes.labelcolor':INK,'text.color':INK,
                     'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':'#D9E0E3',
                     'axes.unicode_minus':False,'savefig.facecolor':BG,'pdf.fonttype':42,
                     'axes.titlepad':6})
fig=plt.figure(figsize=(16,10.5),facecolor=BG)

def htext(x,y,s,fontsize=10,weight='regular',color=INK,ha='left',va='top',**kwargs):
    return fig.text(x,y,s,fontsize=fontsize,fontweight=weight,color=color,ha=ha,va=va,**kwargs)

def section(x,y,letter,title):
    htext(x,y,letter,fontsize=12,weight='bold',color=PERSIST)
    htext(x+0.026,y,title,fontsize=12,weight='bold')

# Main editorial grid: compact explanation + dominant map; temporal history + scenario.
left_x=.055; left_w=.335; right_x=.426; right_w=.524
bot_l_x=.055; bot_l_w=.520; bot_r_x=.615; bot_r_w=.335
htext(.055,.985,'GLOBAL URBAN HEAT',fontsize=9,weight='bold',color=PERSIST)
htext(.055,.958,'Persistent heat effects are spreading across cities and populations',fontsize=17,weight='bold')
htext(.055,.919,'9,713 cities  /  2001–2024 observed  /  2030 conditional extension',fontsize=10,color=MUTED)
fig.add_artist(Line2D([.055,.95],[.900,.900],transform=fig.transFigure,color=HAIR,lw=1))
section(.055,.884,'A','What persistence means')
section(.426,.884,'B','The global geography of persistence')
section(.055,.468,'C','Historical expansion')
section(.615,.468,'D','Conditional continuation to 2030')

# ---------- A / state matrices and exemplary individual trajectory ----------
# Matrices deliberately hold annual prevalence fixed: 3 of 6 high every year.
labels=['A','B','C','D','E','F']
turn=np.zeros((6,8),dtype=int)
for t in range(8):
    turn[(np.arange(3)+(0 if t%2==0 else 3)),t]=1
cont=np.zeros((6,8),dtype=int);cont[:3,:2]=1;cont[:3,2:]=2

def draw_matrix(ax,arr,heading):
    ax.set_facecolor(BG)
    cols={0:'#E3E9EC',1:SHORT,2:PERSIST}
    for i in range(6):
        for j in range(8):
            ax.add_patch(Rectangle((j-.46,5-i-.46),.91,.91,facecolor=cols[arr[i,j]],edgecolor='white',linewidth=.85))
    ax.set_xlim(-.55,7.55);ax.set_ylim(-.64,5.6)
    ax.set_yticks(range(6));ax.set_yticklabels(labels[::-1],fontsize=8)
    ax.set_xticks([0,3,7]);ax.set_xticklabels(['1','4','8'],fontsize=8)
    ax.tick_params(length=0,pad=3)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_title(heading,loc='left',fontweight='semibold',fontsize=9,color=INK,pad=5)

ax_a1=fig.add_axes([.075,.710,.133,.125]);draw_matrix(ax_a1,turn,'Turnover')
ax_a2=fig.add_axes([.229,.710,.133,.125]);draw_matrix(ax_a2,cont,'Persistence')
htext(.219,.840,'3 high cities / year',fontsize=8,color=MUTED,ha='center')
# Matrices legend below; use swatches instead of a bulky legend frame.
for x, col, lab in [(0.071,'#E3E9EC','Below'),(.168,SHORT,'1–2 y'),(.268,PERSIST,'3+ y')]:
    fig.add_artist(Rectangle((x,.679),.015,.012,transform=fig.transFigure,color=col,lw=0))
    htext(x+.02,.685,lab,fontsize=8,color=MUTED,va='center')
# Individual city course, with synchronized categorical bar. Note all values illustrative.
ax_at=fig.add_axes([.082,.548,.278,.095])
example=np.array([1.13,1.60,1.30,1.20,1.55,1.64,1.74,1.82,1.76,1.63,1.30,1.24])
xx=np.arange(1,13)
ax_at.axhline(1.426,color='#88969C',ls=(0,(4,3)),lw=1)
ax_at.plot(xx,example,color=INK,lw=1.85,zorder=3)
ax_at.scatter(xx,example,c=INK,s=18,edgecolors='white',linewidth=.45,zorder=4)
ax_at.set_xlim(.8,12.2);ax_at.set_ylim(1.02,2.02)
ax_at.set_yticks([1.2,1.6,2.0]);ax_at.set_yticklabels(['1.2','1.6','2.0'],fontsize=7.5)
ax_at.set_xticks([1,3,5,7,9,11]);ax_at.set_xticklabels([1,3,5,7,9,11],fontsize=7.5)
ax_at.spines['top'].set_visible(False);ax_at.spines['right'].set_visible(False)
ax_at.spines['left'].set_color(HAIR);ax_at.spines['bottom'].set_color(HAIR)
ax_at.tick_params(length=2,pad=2)
htext(.082,.656,'Illustrative single-city UAH trajectory (°C)',fontsize=8,color=MUTED)
ax_at.text(12.1,1.445,'threshold',fontsize=7.5,color=MUTED,ha='right',va='bottom')
ax_at.annotate('entry',xy=(5,1.55),xytext=(5.15,1.96),fontsize=8,ha='center',color=PERSIST,arrowprops={'arrowstyle':'-','lw':.8,'color':PERSIST})
ax_at.annotate('persistent',xy=(7,1.74),xytext=(8.4,1.94),fontsize=8,ha='center',color=PERSIST,arrowprops={'arrowstyle':'-','lw':.8,'color':PERSIST})
ax_at.annotate('exit',xy=(11,1.30),xytext=(10.6,1.70),fontsize=8,ha='center',color=MUTED,arrowprops={'arrowstyle':'-','lw':.8,'color':MUTED})
for i, col in enumerate(['#E3E9EC',SHORT,'#E3E9EC','#E3E9EC',SHORT,SHORT,PERSIST,PERSIST,PERSIST,PERSIST,'#E3E9EC','#E3E9EC']):
    ax_at.add_patch(Rectangle((i+0.54,1.005),.90,.04,color=col,transform=ax_at.transData,clip_on=False,lw=0))
htext(.08,.526,'One city can enter, accumulate duration, and exit',fontsize=8.5,color=MUTED)

# ---------- B / combined 2024 map, compact baseline mini map ----------
world=gpd.read_file(MAP_PATH)
# Draw the geographical context using the study basemap.
def geo_axes(rect):
    ax=fig.add_axes(rect)
    ax.set_facecolor('#FAFBFB')
    world.plot(ax=ax,facecolor=COUNTRIES,edgecolor=COAST,linewidth=.30,zorder=0)
    ax.set_xlim(-180,180);ax.set_ylim(-55,78)
    ax.set_aspect('auto')
    ax.axis('off')
    return ax
ax_b=geo_axes([.430,.644,.512,.207])
colors={'Below threshold':LOW,'1–2 years':SHORT,'3–4 years':'#DB997E',
        '5–7 years':'#C56647','8–10 years':'#A74335','11+ years':DEEP}
# Grey cities first, colored high cities overprinted to emphasize duration.
for cls in ['Below threshold','1–2 years','3–4 years','5–7 years','8–10 years','11+ years']:
    subset=map2024[map2024.duration_group==cls]
    ax_b.scatter(subset.X,subset.Y,s=3.1 if cls=='Below threshold' else 5.8,
                 c=colors[cls],alpha=.6 if cls=='Below threshold' else .96,
                 edgecolors='none',rasterized=True,zorder=1 if cls=='Below threshold' else 3)
ax_b.text(.010,.98,'2024',transform=ax_b.transAxes,va='top',ha='left',color=INK,fontweight='bold',fontsize=11,
          bbox={'boxstyle':'square,pad=.18','facecolor':'white','edgecolor':'none','alpha':.92})
ax_b.text(.992,.98,'2,127 high-effect cities  ·  1,509 persistent',transform=ax_b.transAxes,va='top',ha='right',fontsize=9,color=INK,
          bbox={'boxstyle':'square,pad=.18','facecolor':'white','edgecolor':'none','alpha':.92})
# 2001 inset appears below, without covering the large map.
ax_bmini=geo_axes([.430,.531,.235,.090])
ax_bmini.scatter(map2001.X,map2001.Y,s=1.25,c=LOW,alpha=.67,linewidth=0,rasterized=True)
hi=map2001[map2001.high]
ax_bmini.scatter(hi.X,hi.Y,s=3.2,c='#E7A161',alpha=.95,linewidth=0,rasterized=True)
ax_bmini.text(.018,1.02,'2001 · 772 high-effect cities',transform=ax_bmini.transAxes,fontsize=8.5,color=INK,weight='semibold')
# Legend occupies leftover bottom right: unified two rows.
htext(.684,.624,'2024 consecutive high-effect duration',fontsize=8.3,color=MUTED)
leg_info=[('Below threshold',LOW),('1–2 y',SHORT),('3–4 y','#DB997E'),('5–7 y','#C56647'),('8–10 y','#A74335'),('11+ y',DEEP)]
for i,(name,color) in enumerate(leg_info):
    x=.687+(i%3)*.085;y=.597-(i//3)*.030
    fig.add_artist(Rectangle((x,y),.012,.012,transform=fig.transFigure,facecolor=color,lw=0))
    htext(x+.016,y+.006,name,fontsize=8,va='center',color=INK)
htext(.437,.516,'Every dot represents one study city; the 2020 city boundaries remain fixed through time.',fontsize=8,color=MUTED)

# horizontal divider between major rows
fig.add_artist(Line2D([.055,.950],[.489,.489],transform=fig.transFigure,color=HAIR,lw=1))

# ---------- C / historical time series unified vertically ----------
ax_c1=fig.add_axes([.082,.278,.470,.151])
x=annual.year.values
persistent=annual.persistent_cities.values
short=annual.short_high_cities.values
ax_c1.fill_between(x,0,persistent,color=PERSIST,alpha=.86,label='Persistent ≥3 y',zorder=2)
ax_c1.fill_between(x,persistent,persistent+short,color=SHORT,alpha=.9,label='High 1–2 y',zorder=2)
ax_c1.plot(x,annual.high_cities,color=INK,lw=1.65,label='All high-effect cities',zorder=3)
ax_c1.set_xlim(2001,2024.25);ax_c1.set_ylim(0,2450)
ax_c1.set_yticks([0,1000,2000]);ax_c1.set_xticks([2001,2006,2012,2018,2024]);ax_c1.set_xticklabels([])
ax_c1.set_ylabel('Number of cities',fontsize=9)
ax_c1.grid(axis='y',color=GRID,lw=.8,zorder=0)
ax_c1.spines[['top','right']].set_visible(False)
ax_c1.text(2001.25,2180,'City states',fontsize=9.7,fontweight='bold')
ax_c1.text(2024,2375,'2,127 high-effect',fontsize=8.7,ha='right',color=INK)
ax_c1.text(2024,2190,'1,509 persistent (70.9%)',fontsize=8.7,ha='right',color=PERSIST)
ax_c1.legend(loc='upper left',bbox_to_anchor=(.25,1.02),ncol=3,frameon=False,fontsize=8,
             columnspacing=.75,handlelength=1.5,handletextpad=.3)

ax_c2=fig.add_axes([.082,.099,.470,.144],sharex=ax_c1)
pp=annual_pop.copy();pp['pop_billion']=pp.persistent_population/1e9
ax_c2.fill_between(pp.year.values,np.zeros(len(pp)),pp.pop_billion.values,color='#EED8CC',alpha=.55,lw=0)
ax_c2.plot(pp.year.values,pp.pop_billion.values,color=PERSIST,lw=2.4,label='Population in persistent cities',zorder=3)
ax_c2.set_xlim(2001,2024.25);ax_c2.set_ylim(0,1.34)
ax_c2.set_yticks([0,.4,.8,1.2]);ax_c2.set_xticks([2001,2006,2012,2018,2024]);ax_c2.set_ylabel('Population (billions)',fontsize=9)
ax_c2.set_xlabel('Year',fontsize=9)
ax_c2.grid(axis='y',color=GRID,lw=.8)
ax_c2.spines[['top','right']].set_visible(False)
ax_c2.text(2001.25,1.23,'Population reach',fontsize=9.7,fontweight='bold')
# plot population percentage on right axis as a quiet dotted line, but use distinct label directly.
ax_c2r=ax_c2.twinx()
ax_c2r.plot(pp.year.values,pp.persistent_share_all_pct.values,color=TEAL,lw=1.4,ls=(0,(3,3)),label='Share of study-city population')
ax_c2r.set_ylim(0,42);ax_c2r.set_yticks([0,20,40]);ax_c2r.set_ylabel('Share of city population (%)',fontsize=9,color=TEAL)
ax_c2r.tick_params(axis='y',colors=TEAL,labelsize=8)
ax_c2r.spines[['top','left']].set_visible(False)
ax_c2r.spines['right'].set_color(HAIR)
ax_c2.text(2004,0.46,'2003  ·  0.411 bn',fontsize=8,color=PERSIST,va='bottom')
ax_c2.text(2024,.98,'1.024 bn',fontsize=9,ha='right',va='bottom',weight='bold',color=PERSIST)
ax_c2r.text(2024,33.5,'32.8%',fontsize=8.5,ha='right',va='bottom',color=TEAL)

# ---------- D / conditional state extensions ----------
ax_d=fig.add_axes([.635,.148,.292,.242])
scol={'Early':ORANGE,'Full':TEAL,'Recent':BLUE}
for s in ['Early','Full','Recent']:
    ss=scen[scen.scenario==s].sort_values('year')
    ax_d.plot(ss.year,ss.expected_persistent_cities,color=scol[s],lw=2.0,zorder=4)
    ax_d.fill_between(ss.year.values,ss.persistent_ci_low.values,ss.persistent_ci_high.values,
                      color=scol[s],alpha=.12,lw=0,zorder=2)
ss=scen[scen.scenario=='Early'].sort_values('year')
ax_d.plot(ss.year,ss.expected_high_cities,color=INK,ls='--',lw=1.6,zorder=3)
ax_d.fill_between(ss.year.values,ss.high_ci_low.values,ss.high_ci_high.values,color=INK,alpha=.08,lw=0)
ax_d.set_xlim(2024,2030.8);ax_d.set_ylim(1460,2330)
ax_d.set_xticks([2024,2026,2028,2030]);ax_d.set_yticks([1500,1750,2000,2250])
ax_d.spines[['top','right']].set_visible(False)
ax_d.grid(axis='y',color=GRID,lw=.8)
ax_d.set_ylabel('Expected number of cities',fontsize=9)
# Title above chart already explains conditional continuation; keep the plot uncluttered.
# Position scenario labels above the axes.
fig.legend(handles=[Line2D([0],[0],color=INK,lw=1.5,ls='--',label='High-effect cities (early)'),
                     Line2D([0],[0],color=ORANGE,lw=2,label='Persistent, early'),
                     Line2D([0],[0],color=TEAL,lw=2,label='Persistent, full'),
                     Line2D([0],[0],color=BLUE,lw=2,label='Persistent, recent')],
            loc='upper left',bbox_to_anchor=(.630,.439),bbox_transform=fig.transFigure,frameon=False,ncol=2,fontsize=8,handlelength=1.8,columnspacing=1)
last=scen[scen.year==2030].set_index('scenario')
# endpoint direct labels outside plotted curves, with nonoverlap based on expected level
ax_d.text(2030.06,2081,'2,081',color=INK,fontsize=8,va='center',weight='bold')
ax_d.text(2030.06,1865,'1,857 recent',color=BLUE,fontsize=8,va='center')
ax_d.text(2030.06,1813,'1,813 full',color=TEAL,fontsize=8,va='center')
ax_d.text(2030.06,1749,'1,764 early',color=ORANGE,fontsize=8,va='center')
# endpoint thesis, positioned as a clean caption below the chart rather than inside.
htext(.636,.118,'High-effect cities: −46     |     Persistent cities: +255  (early entry)',
      fontsize=8.3,color=MUTED)
htext(.636,.086,'Shading indicates 95% city-cluster bootstrap intervals.',fontsize=8,color=MUTED)

# unobtrusive footer
fig.add_artist(Line2D([.055,.95],[.057,.057],transform=fig.transFigure,color=HAIR,lw=.8))
htext(.055,.038,f'Fixed threshold: P90 of pooled 2001–2005 city-year UAH ({threshold:.3f} °C); persistent state: ≥3 consecutive high years.',fontsize=8,color=MUTED)
htext(.95,.038,'UAH threshold: pooled 2001–2005 P90; city observations: 2001–2024.',fontsize=7.5,color=MUTED,ha='right')

out=OUTPUT/'Fig1_redesigned.pdf'
fig.savefig(out,format='pdf',bbox_inches=None)
fig.savefig(OUTPUT/'Fig1_redesigned.png',dpi=180,bbox_inches=None)
print('Saved',out)
print('Numerical checks:',threshold,
      annual[annual.year==2024][['high_cities','persistent_cities']].to_dict('records'),
      annual_pop[annual_pop.year==2024][['persistent_population','persistent_share_all_pct']].to_dict('records'))

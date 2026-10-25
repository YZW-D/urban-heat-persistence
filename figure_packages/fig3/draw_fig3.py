#!/usr/bin/env python3
"""Draw Figure 3 from the population decomposition tables.
Usage: python draw_fig3.py --tables . --output .
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

ap=argparse.ArgumentParser()
ap.add_argument('--tables',type=Path,default=Path(__file__).resolve().parent)
ap.add_argument('--output',type=Path,default=Path(__file__).resolve().parent)
args=ap.parse_args()
args.output.mkdir(parents=True,exist_ok=True)

a=pd.read_csv(args.tables/'Fig3A_annual_population_decomposition.csv')
b=pd.read_csv(args.tables/'Fig3B_cumulative_population_decomposition.csv')
s=dict(zip(*[pd.read_csv(args.tables/'Fig3_summary_and_endpoint_sensitivity.csv')[k] for k in ('metric','value')]))
MILLION=1e6
INK='#23313B'; MUTED='#697983'; HAIR='#E4E9EC'; GRID='#EAF0F2'
PERSIST='#C65B40'; BLUE='#6D93B5'; CORAL='#D16B62'; TEAL='#348F8B'; PALE='#F3F7F9'; WHITE='#FFFFFF'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'font.weight':'regular',
                     'axes.labelcolor':INK,'text.color':INK,'xtick.color':MUTED,'ytick.color':MUTED,
                     'axes.edgecolor':'#D9E0E3','axes.unicode_minus':False,
                     'savefig.facecolor':WHITE,'pdf.fonttype':42,'ps.fonttype':42})
fig=plt.figure(figsize=(16,10.5),facecolor=WHITE)

def ft(x,y,msg,fs=9,color=INK,weight='normal',ha='left',va='top',**kwargs):
    return fig.text(x,y,msg,color=color,fontsize=fs,fontweight=weight,ha=ha,va=va,**kwargs)
def line(y):
    fig.add_artist(Line2D([.055,.95],[y,y],transform=fig.transFigure,color=HAIR,lw=1.1))
def title(x,y,label,txt):
    ft(x,y,label,fs=12,color=PERSIST,weight='bold');ft(x+.027,y,txt,fs=12,weight='bold')

def axis_format(ax):
    ax.spines[['top','right']].set_visible(False)
    for k in ('bottom','left'): ax.spines[k].set_color(HAIR)
    ax.tick_params(axis='both',which='both',length=3.5,color=HAIR)
    ax.grid(axis='y',color=GRID,lw=.9,zorder=0)
    ax.set_axisbelow(True)

# Headline
ft(.055,.985,'GLOBAL URBAN HEAT',fs=9,color=PERSIST,weight='bold')
ft(.055,.956,'Changing persistent-city membership drove most population growth',fs=17,weight='bold')
ft(.055,.917,'21 annual transitions  /  613.4 million more people in persistent cities  /  2003–2024',fs=10,color=MUTED)
line(.892)

# A annual events
# Small, natural language statement enhances rather than replaces evidence.
title(.055,.872,'A','Annual transitions repeatedly added and removed populations')
leg=[('Entry into persistent set',BLUE,'bar'),('Exit from persistent set',CORAL,'bar'),('Population-change component',TEAL,'point'),('Observed net change',INK,'line')]
for x,(label,col,typ) in zip([.058,.266,.490,.745],leg):
    if typ=='bar':
        fig.add_artist(Rectangle((x,.816),.014,.011,transform=fig.transFigure,facecolor=col,lw=0))
    elif typ=='point':
        fig.add_artist(Line2D([x,x+.017],[.821,.821],transform=fig.transFigure,color=col,marker='o',markersize=4,lw=1.2))
    else:
        fig.add_artist(Line2D([x,x+.017],[.821,.821],transform=fig.transFigure,color=col,ls='--',lw=1.8))
    ft(x+.022,.822,label,fs=8.5,va='center',color=MUTED)

ax=fig.add_axes([.090,.566,.844,.218])
x=a.transition_ending_year.to_numpy()
e=a.entry_population.to_numpy()/MILLION
ex=a.exit_population.to_numpy()/MILLION
p=a.population_change_component.to_numpy()/MILLION
obs=a.observed_delta.to_numpy()/MILLION
ax.bar(x,e,width=.68,color=BLUE,zorder=2)
ax.bar(x,ex,width=.68,color=CORAL,zorder=2)
ax.plot(x,obs,color=INK,lw=1.8,ls=(0,(4,3)),marker='o',ms=2.6,zorder=5)
ax.plot(x,p,color=TEAL,lw=1.4,marker='o',ms=3.4,zorder=6)
ax.axhline(0,lw=1,color=INK,zorder=3)
ax.set_xlim(2003.3,2024.7);ax.set_ylim(-59,155)
ax.set_yticks([-50,0,50,100,150]);ax.set_ylabel('Annual population contribution (millions)',fontsize=9,labelpad=9)
ax.set_xticks([2004,2007,2010,2013,2016,2019,2021,2024])
axis_format(ax)
# Max event annotations, visually tethered to their corresponding bars.
ax.annotate('2021  ·  largest entry  +133.9M',xy=(2021,e[np.where(x==2021)[0][0]]),xytext=(2015.15,142),
            fontsize=9,color=INK,weight='bold',ha='left',arrowprops={'arrowstyle':'-','lw':1,'color':MUTED})
ax.annotate('2022  ·  largest exit  −39.6M',xy=(2022,ex[np.where(x==2022)[0][0]]),xytext=(2013.25,-49.5),
            fontsize=9,color=CORAL,weight='bold',ha='left',arrowprops={'arrowstyle':'-','lw':1,'color':CORAL})
ft(.092,.535,'Transition ending year. Cities entering and exiting contribute repeatedly; population changes are shown separately.',fs=8.5,color=MUTED)
line(.504)

# B cumulative components over time
title(.055,.484,'B','Cumulative contributions reveal the dominant source of growth')
ax2=fig.add_axes([.090,.145,.576,.282])
xb=b.transition_ending_year.to_numpy()
def millions(name): return b[name].to_numpy()/MILLION
# Show all five original curves, but emphasize the two additive terms and observed total.
series=[
    ('Cumulative entry', 'entry_population', BLUE, 1.6, '-'),
    ('Cumulative exit', 'exit_population', CORAL, 1.6, '-'),
    ('Observed net increase', 'observed_delta', INK, 2.6, '-'),
    ('Net membership change', 'membership_component', PERSIST, 2.75, '-'),
    ('Population-change component', 'population_change_component', TEAL, 2.0, '-'),
]
for label,name,color,lw,ls in series:
    ax2.plot(xb,millions(name),label=label,color=color,lw=lw,ls=ls,zorder=4 if name in ('membership_component','observed_delta') else 2)
ax2.axhline(0,lw=.9,color=HAIR)
ax2.set_xlim(2003,2026.25);ax2.set_ylim(-340,840)
ax2.set_xlabel('Year',fontsize=9)
ax2.set_ylabel('Cumulative population contribution (millions)',fontsize=9,labelpad=9)
ax2.set_xticks([2003,2007,2011,2015,2019,2024]);ax2.set_yticks([-300,0,300,600,800])
axis_format(ax2)
end_text=[
 ('entry_population',BLUE,'Entry  +776.0',8),
 ('observed_delta',INK,'Total  +613.4',0),
 ('membership_component',PERSIST,'Membership  +488.5',-18),
 ('population_change_component',TEAL,'Population  +124.9',0),
 ('exit_population',CORAL,'Exit  −287.5',0),
]
for col,color,label,offset in end_text:
    ey=float(millions(col)[-1])
    ax2.plot([2024.0,2024.33],[ey,ey],color=color,lw=1.3)
    ax2.text(2024.40,ey+offset,label,color=color,fontsize=8.2,weight='bold' if col in ('membership_component','observed_delta') else 'regular',va='center',clip_on=False)

# Show the cumulative component shares beside the time-series panel.
ft(.714,.418,'SOURCE OF NET POPULATION INCREASE',fs=9,color=MUTED,weight='bold')
ft(.710,.369,'79.6%',fs=38,color=PERSIST,weight='bold')
ft(.714,.300,'Persistent-city membership changes',fs=10,color=INK,weight='bold')
# proportional single bar
fig.add_artist(Rectangle((.713,.263),.222*.7963858,.018,transform=fig.transFigure,facecolor=PERSIST,lw=0))
fig.add_artist(Rectangle((.713+.222*.7963858,.263),.222*(1-.7963858),.018,transform=fig.transFigure,facecolor=TEAL,lw=0))
ft(.713,.247,'79.6% membership',fs=8.3,color=PERSIST,weight='bold')
ft(.935,.247,'20.4%',fs=8.3,color=TEAL,weight='bold',ha='right')
ft(.714,.195,'+488.5M',fs=17,color=PERSIST,weight='bold')
ft(.842,.195,'+124.9M',fs=15,color=TEAL,weight='bold')
fig.add_artist(Line2D([.714,.935],[.157,.157],transform=fig.transFigure,color=HAIR,lw=1))
ft(.714,.145,'Total increase',fs=9,color=MUTED)
ft(.935,.145,'+613.4 million',fs=13,color=INK,weight='bold',ha='right')

line(.063)
ft(.055,.044,'Annual symmetric decomposition using 2003–2024 LandScan ambient population in fixed city boundaries.  Membership-change terms include entries and exits;',fs=8,color=MUTED)
ft(.055,.025,'Population changes within cities entering or leaving persistence are weighted symmetrically between consecutive years.',fs=8,color=MUTED)

fig.savefig(args.output/'Fig3_redesigned.pdf',bbox_inches='tight',facecolor=WHITE)
fig.savefig(args.output/'Fig3_redesigned.png',dpi=240,bbox_inches='tight',facecolor=WHITE)
plt.close(fig)
print('Saved',args.output/'Fig3_redesigned.pdf')

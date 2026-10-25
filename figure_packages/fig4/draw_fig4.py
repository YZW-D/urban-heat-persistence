#!/usr/bin/env python3
"""Draw Fig. 4: regional entry-exit classifications and pooled rates.

The supplied IPCC regions are cartographic boundaries. All statistics are
computed by grouping on the IPCC_Acronym attribute in the city-year table.
"""
from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap,Normalize
from matplotlib.cm import ScalarMappable
import matplotlib.patheffects as pe

ROOT=Path(__file__).resolve().parents[2]
T=Path(__file__).resolve().parent/'tables'
OUT=ROOT/'outputs/fig4'
COLORS={'low_low':'#dae7d2','low_high':'#d6e0ef','high_low':'#f1c38f',
        'high_high':'#e1b2ab','sparse':'#f1f1f1','none':'#ffffff'}
PATTERNS=[('low_low','Low entry / low exit'),('low_high','Low entry / high exit'),
          ('high_low','High entry / low exit'),('high_high','High entry / high exit'),
          ('sparse','<50 cities'),('none','No study cities')]

def main():
    a=pd.read_csv(T/'Fig4A_regional_transition_scatter.csv')
    b=pd.read_csv(T/'Fig4B_regional_transition_patterns.csv')
    ref=pd.read_csv(T/'Fig4_global_reference_values.csv').set_index('metric').value
    globe=(float(ref['global entry rate (%)']),float(ref['global exit rate (%)']))
    regional=a.merge(b[['region','pattern_code']],on='region',validate='one_to_one')
    basemap=ROOT/'basemap'
    regs=gpd.read_file(basemap/'IPCC-WGI-reference-regions-v4.shp').to_crs(4326)
    countries=gpd.read_file(next(basemap.glob('02*.shp'))).to_crs(4326)
    land=countries.geometry.union_all()
    clipped=regs.copy()
    clipped['geometry']=clipped.geometry.intersection(land)
    codes=regional.set_index('region').pattern_code.to_dict()
    clipped['pattern']=clipped['Acronym'].map(codes).fillna('none')
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'pdf.fonttype':42,'ps.fonttype':42,
                         'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
    fig=plt.figure(figsize=(13.6,10.2),facecolor='white')
    fig.text(.052,.965,'Fig. 4',weight='bold',fontsize=15,color='#AE583D')
    fig.text(.134,.965,'Regional contrasts in high-effect state transitions',weight='bold',fontsize=14.4,color='#263843')
    fig.text(.054,.925,'a   Regional entry–exit classification, 2001–2024',weight='bold',fontsize=12)
    ax=fig.add_axes([.055,.525,.888,.370])
    for name,color in COLORS.items():
        f=clipped[clipped.pattern.eq(name)]
        if len(f): f.plot(ax=ax,color=color,edgecolor='none',zorder=1)
    sparse=clipped[clipped.pattern.eq('sparse')]
    if len(sparse): sparse.plot(ax=ax,color='none',hatch='////',edgecolor='#A3A8AB',linewidth=.12,zorder=3)
    countries.boundary.plot(ax=ax,color='#8F9EA6',linewidth=.20,alpha=.65,zorder=2)
    regs.boundary.plot(ax=ax,color='#89979B',linewidth=.42,alpha=.70,zorder=3)
    ax.set_xlim(-178,178);ax.set_ylim(-58,80);ax.set_aspect('auto');ax.axis('off')
    for label,x,y in [('WNA',-121,46),('ENA',-80,40),('WCE',18,55),('EAS',123,38),('SEA',109,8)]:
        t=ax.text(x,y,label,ha='center',va='center',fontsize=8.3,weight='bold',color='#283A43',zorder=5)
        t.set_path_effects([pe.withStroke(linewidth=2.3,foreground='white')])
    legend=[Patch(facecolor=COLORS[key],edgecolor='#A7B0B3',hatch='////' if key=='sparse' else None,label=label)
            for key,label in PATTERNS]
    fig.legend(handles=legend,loc='upper center',bbox_to_anchor=(.5,.545),ncol=3,
               frameon=False,fontsize=9.5,columnspacing=2.8,handlelength=2.2)
    fig.add_artist(Line2D([.055,.945],[.479,.479],transform=fig.transFigure,color='#E3E8EA',linewidth=1))
    fig.text(.054,.453,'b   Regional pooled annual entry and exit rates',weight='bold',fontsize=12)
    ax=fig.add_axes([.116,.121,.680,.293])
    ax.grid(color='#E1E6E8',linewidth=.65)
    ax.set_axisbelow(True)
    ax.axvline(globe[0],ls='--',color='#8B969D',lw=1.05)
    ax.axhline(globe[1],ls='--',color='#8B969D',lw=1.05)
    regular=regional[regional.eligible_pattern.eq(True)].copy()
    sparse=regional[regional.eligible_pattern.eq(False)].copy()
    cmap=LinearSegmentedColormap.from_list('proportion',['#dceae9','#86b7aa','#347f76','#125c66'])
    norm=Normalize(vmin=0,vmax=50)
    pop=regular.persistent_population_million.clip(lower=0).to_numpy()
    marker_size=24+360*np.power(pop/300,0.75)
    ax.scatter(regular.entry_rate_pct,regular.exit_rate_pct,c=regular.persistent_city_share_pct,
               s=marker_size,cmap=cmap,norm=norm,edgecolors='white',linewidth=1.0,zorder=3)
    ax.scatter(sparse.entry_rate_pct,sparse.exit_rate_pct,s=25,edgecolors='#A5AFB3',facecolors='white',linewidth=1.1,zorder=2)
    ax.set_xlim(0,13.6);ax.set_ylim(0,45)
    ax.set_xlabel('Pooled entry rate (%)',labelpad=7);ax.set_ylabel('Pooled exit rate (%)',labelpad=7)
    for code,dx,dy in [('EAS',6,-12),('WCE',7,7),('WNA',8,7),('SEA',7,5),('ENA',8,-11)]:
        row=regional.set_index('region').loc[code]
        ax.annotate(code,(row.entry_rate_pct,row.exit_rate_pct),xytext=(dx,dy),textcoords='offset points',
                    fontsize=9,weight='bold',color='#273943',path_effects=[pe.withStroke(linewidth=2.5,foreground='white')])
    ax.text(.01,.97,f'Global entry: {globe[0]:.2f}%',transform=ax.transAxes,fontsize=8.7,va='top',color='#56666D')
    ax.text(.99,.045,f'Global exit: {globe[1]:.2f}%',transform=ax.transAxes,fontsize=8.7,ha='right',color='#56666D')
    cax=fig.add_axes([.839,.215,.018,.161])
    cb=fig.colorbar(ScalarMappable(norm=norm,cmap=cmap),cax=cax,ticks=[0,10,20,30,40,50])
    cb.ax.tick_params(labelsize=8);cb.outline.set_visible(False)
    fig.text(.824,.404,'Persistent-city',fontsize=8.4)
    fig.text(.824,.387,'share (%)',fontsize=8.4)
    fig.text(.814,.169,'Circle area shows' ,fontsize=8.1,color='#63747A')
    fig.text(.814,.148,'persistent-city population;' ,fontsize=8.1,color='#63747A')
    fig.text(.814,.127,'open: <50 cities.',fontsize=8.1,color='#63747A')
    fig.text(.055,.048,'Rates use eligible city-year denominators. Four regions with fewer than 50 cities have exit rates above the displayed axis. Region labels use IPCC_Acronym.',fontsize=8.5,color='#5C6C74')
    OUT.mkdir(parents=True,exist_ok=True)
    for extension in ('pdf','png'):
        fig.savefig(OUT/f'Fig4_regional_transitions.{extension}',dpi=250,facecolor='white')
    plt.close(fig)
    print('Saved Fig. 4 to',OUT)

if __name__=='__main__': main()

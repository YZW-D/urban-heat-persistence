#!/usr/bin/env python3
"""Draw Figure 5 using city-level IPCC region assignments and cartographic polygons.
Requires matplotlib, geopandas, shapely and numpy.
"""
from __future__ import annotations
import csv, argparse
from pathlib import Path
import geopandas as gpd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import ListedColormap
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe

DARK='#22323A';MUTED='#63747D';TEAL='#197D7B';ORANGE='#BE623F';BLUE='#5C8799'
FILL=['#F3F5F5','#D8EAE5','#B4D8CD','#7FBCB1','#3A908D','#12626B']
LABELS=['No gain','1–9','10–24','25–49','50–99','≥100']

def read_csv(p):
 with open(p,encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def setup():
 plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9.3,'axes.labelcolor':DARK,
  'text.color':DARK,'xtick.color':MUTED,'ytick.color':DARK,'axes.edgecolor':'#A9B8BD',
  'pdf.fonttype':42,'ps.fonttype':42,'axes.spines.top':False,'axes.spines.right':False,
  'savefig.facecolor':'white'})

def map_draw(ax, regs, world, summaries):
 land=world.geometry.union_all()
 clipped=regs.copy()
 clipped['geometry']=clipped.geometry.intersection(land)
 clipped=clipped.set_geometry('geometry')
 s={r['region']:r for r in summaries}
 def idx(code):
  if code not in s:return -1
  v=float(s[code]['net'])
  if v<1:return 0
  if v<10:return 1
  if v<25:return 2
  if v<50:return 3
  if v<100:return 4
  return 5
 clipped['class']=clipped['Acronym'].map(idx)
 for k,color in enumerate(FILL):
  f=clipped.loc[clipped['class']==k]
  if len(f): f.plot(ax=ax,color=color,edgecolor='none',zorder=1)
 f=clipped.loc[clipped['class']==-1]
 if len(f): f.plot(ax=ax,color='#EBECEC',edgecolor='none',zorder=1)
 world.boundary.plot(ax=ax,color='#9BACB1',linewidth=.22,alpha=.65,zorder=2)
 regs.boundary.plot(ax=ax,color='#81959C',linewidth=.44,alpha=.85,zorder=3)
 ax.set_xlim(-178,178);ax.set_ylim(-55,78);ax.set_aspect('equal',adjustable='box');ax.axis('off')
 positions={'EAS':(121,34),'WCE':(17,54),'ENA':(-83,40),'WNA':(-119,42),'SEA':(107,9),'WSB':(79,61),'MED':(13,39)}
 for code in ['EAS','WCE','ENA','WNA','SEA','WSB']:
  x,y=positions[code]
  t=ax.text(x,y,code,fontsize=8.8,color=DARK,ha='center',va='center',weight='bold',zorder=5)
  t.set_path_effects([pe.withStroke(linewidth=2.6,foreground='white')])

def panel_b(ax,summaries):
 inds={r['region']:r for r in summaries};names=['EAS','WCE','ENA','SEA','WNA','MED','WCA','NEU']
 rows=[inds[n] for n in names];yy=np.arange(len(names))
 enters=np.array([float(r['entry']) for r in rows]);exits=np.array([float(r['exit']) for r in rows]);net=enters-exits
 ax.barh(yy,enters,color=TEAL,height=.61,label='Entries',edgecolor='white',linewidth=.5)
 ax.barh(yy,-exits,color='#DC927A',height=.61,label='Exits',edgecolor='white',linewidth=.5)
 for y,n in zip(yy,net):ax.text(314,y,f'+{int(n)}',va='center',ha='right',fontsize=9,color=DARK,weight='bold')
 ax.axvline(0,color='#6B818A',lw=.85)
 ax.set_yticks(yy,names);ax.invert_yaxis();ax.set_xlim(-240,325)
 ax.set_xticks([-200,-100,0,100,200,300],['200','100','0','100','200','300'])
 ax.set_xlabel('Transition events, 2003–2024',labelpad=8)
 ax.grid(axis='x',color='#DCE3E6',linewidth=.65,zorder=0);ax.set_axisbelow(True)
 ax.tick_params(axis='y',length=0,pad=6)
 ax.spines['left'].set_visible(False);ax.spines['bottom'].set_color('#DCE3E6')
 ax.legend(handles=[Patch(color=TEAL,label='Entries'),Patch(color='#DC927A',label='Exits')],
   loc='upper center',bbox_to_anchor=(.50,1.15),ncol=2,frameon=False,fontsize=8)
 ax.text(.985,1.10,'Net',transform=ax.transAxes,ha='right',fontsize=8.3,weight='bold')

def panel_c(ax,summaries):
 inds={r['region']:r for r in summaries}; names=['EAS','SEA','SAS','WCE','WCA','ENA','WNA']
 rows=[inds[n] for n in names]; y=np.arange(len(names))
 m=np.array([float(r['membership_pop_m']) for r in rows]);d=np.array([float(r['demographic_pop_m']) for r in rows]);tt=m+d
 ax.barh(y,m,color=TEAL,height=.61,label='State membership',edgecolor='white',linewidth=.5)
 ax.barh(y,d,left=m,color='#E0A37B',height=.61,label='City population',edgecolor='white',linewidth=.5)
 for j,v in enumerate(tt):ax.text(v+3,j,f'{v:.1f}',ha='left',va='center',fontsize=8.6,weight='bold')
 ax.set_yticks(y,names);ax.invert_yaxis();ax.set_xlim(0,250);ax.set_xticks([0,50,100,150,200])
 ax.set_xlabel('Population change (millions)',labelpad=8)
 ax.grid(axis='x',color='#DCE3E6',linewidth=.65,zorder=0);ax.set_axisbelow(True)
 ax.tick_params(axis='y',length=0,pad=6)
 ax.spines['left'].set_visible(False);ax.spines['bottom'].set_color('#DCE3E6')
 ax.legend(loc='upper center',bbox_to_anchor=(.53,1.15),ncol=2,frameon=False,fontsize=7.6)

def save(fig,prefix):
 fig.savefig(str(prefix)+'.pdf',bbox_inches=None)
 fig.savefig(str(prefix)+'.png',dpi=300,bbox_inches=None)
 plt.close(fig)

def draw(root):
 setup()
 (root.parents[1]/'outputs/fig5').mkdir(parents=True,exist_ok=True)
 summaries=read_csv(root.parent/'fig4/tables/02_regional_summary_primary.csv')
 base=root.parents[1]/'basemap'
 regs=gpd.read_file(base/'IPCC-WGI-reference-regions-v4.shp').to_crs(4326)
 countries=next(base.glob('02*.shp'))
 world=gpd.read_file(countries).to_crs(4326)
 fig=plt.figure(figsize=(14.3,11.5),facecolor='white')
 fig.text(.055,.975,'GLOBAL URBAN HEAT  /  FIGURE 5',fontsize=10,color=ORANGE,weight='bold')
 fig.text(.055,.948,'Regional expansion of persistent high-effect states',fontsize=17.2,color=DARK,weight='bold')
 fig.text(.055,.925,'2003–2024  |  43 IPCC AR6 regions  |  9,713 study cities',fontsize=9.2,color=MUTED)
 fig.add_artist(Line2D([.055,.945],[.912,.912],transform=fig.transFigure,color='#DBE3E6',lw=1.2))
 fig.text(.055,.888,'A',fontsize=11.5,weight='bold',color=ORANGE)
 fig.text(.078,.888,'Net increase in persistent cities by region',fontsize=11.1,weight='bold',color=DARK)
 ax=fig.add_axes([.062,.486,.88,.39]);map_draw(ax,regs,world,summaries)
 handles=[Patch(facecolor=c,edgecolor='#B8C6CB',linewidth=.5,label=l) for c,l in zip(FILL,LABELS)]
 leg=fig.legend(handles=handles,ncol=6,frameon=False,loc='lower center',
        bbox_to_anchor=(.50,.477),fontsize=8.2,columnspacing=2.1,handlelength=1.7)
 fig.add_artist(Line2D([.055,.945],[.471,.471],transform=fig.transFigure,color='#DBE3E6',lw=1))
 fig.text(.055,.446,'B',fontsize=11.5,weight='bold',color=ORANGE)
 fig.text(.077,.446,'Turnover can offset persistent-state gains',fontsize=10.6,weight='bold')
 fig.text(.550,.446,'C',fontsize=11.5,weight='bold',color=ORANGE)
 fig.text(.573,.446,'Contributions to regional population growth',fontsize=10.6,weight='bold')
 axb=fig.add_axes([.10,.129,.365,.255]);panel_b(axb,summaries)
 axc=fig.add_axes([.585,.129,.365,.255]);panel_c(axc,summaries)
 fig.add_artist(Line2D([.055,.945],[.088,.088],transform=fig.transFigure,color='#DBE3E6',lw=1))
 fig.text(.055,.065,'GLOBAL NET CHANGE',fontsize=8.6,color=MUTED,weight='bold')
 fig.text(.055,.041,'+803 persistent cities',fontsize=11,weight='bold',color=DARK)
 fig.text(.350,.041,'+613.4M associated population',fontsize=11,weight='bold',color=DARK)
 fig.text(.713,.041,'79.6% membership component',fontsize=11,weight='bold',color=DARK)
 fig.text(.055,.015,'Population components: exact symmetric annual decomposition. Regional assignments: IPCC_Acronym; map boundaries: IPCC AR6.',fontsize=7.8,color=MUTED)
 save(fig,root.parents[1]/'outputs/fig5/Fig5_regional_accumulation')
 # Export individual panels for layout and verification.
 for key in ['a','b','c']:
  if key=='a':
   f=plt.figure(figsize=(11,5.8),facecolor='white');f.text(.04,.95,'A  Regional net expansion, 2003–2024',fontsize=13,weight='bold')
   ax=f.add_axes([.04,.19,.92,.69]);map_draw(ax,regs,world,summaries)
   f.legend(handles=handles,ncol=6,loc='lower center',bbox_to_anchor=(.5,.09),frameon=False,fontsize=9)
  elif key=='b':
   f=plt.figure(figsize=(7.7,6.3),facecolor='white');f.text(.06,.955,'B  Entry and exit of persistent states',fontsize=13,weight='bold')
   ax=f.add_axes([.13,.19,.78,.58]);panel_b(ax,summaries)
  else:
   f=plt.figure(figsize=(8.3,6.3),facecolor='white');f.text(.06,.955,'C  Regional population-change decomposition',fontsize=13,weight='bold')
   ax=f.add_axes([.14,.19,.78,.58]);panel_c(ax,summaries)
  save(f,root.parents[1]/f'outputs/fig5/Fig5_panel_{key}')
 print('Wrote Fig.5 PDFs and PNGs to',root.parents[1]/'outputs/fig5')

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default=str(Path(__file__).resolve().parent))
 draw(Path(ap.parse_args().root))

#!/usr/bin/env python3
"""Run manuscript-analysis computations, numerical checks, and figure scripts."""
import argparse
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parent

def run(*parts):
    command=[sys.executable,*(str(p) for p in parts)]
    print('+',' '.join(command),flush=True)
    subprocess.run(command,cwd=ROOT,check=True)

def verify():
    run('scripts/validate_inputs_and_results.py')
    run('scripts/verify_manuscript.py')
    run('figure_packages/fig2/verify_results.py')
    run('figure_packages/fig3/verify_fig3.py','--tables','figure_packages/fig3')

def core():
    run('figure_packages/fig2/compute_fig2_tables.py')
    run('figure_packages/fig3/compute_fig3_tables.py','--input','data/input/city_year_2001_2024.csv','--output','figure_packages/fig3')
    run('figure_packages/fig4/compute_regional_rates.py')
    run('figure_packages/fig4/scripts/compute_regional_dynamics.py')

def plot():
    run('figure_packages/fig1/draw_fig1.py')
    run('figure_packages/fig2/draw_fig2.py')
    run('figure_packages/fig3/draw_fig3.py','--tables','figure_packages/fig3','--output','outputs/fig3')
    run('figure_packages/fig4/draw_fig4.py')
    run('figure_packages/fig5/draw_fig5.py')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',default='verify',choices=['verify','recompute-core','refit-gee','scenarios','plot','reproduce'])
    opts=p.parse_args()
    if opts.mode=='verify':verify()
    elif opts.mode=='recompute-core':core();verify()
    elif opts.mode=='refit-gee':run('figure_packages/fig2/compute_gee.py');verify()
    elif opts.mode=='scenarios':run('analysis/scenario_2030.py');verify()
    elif opts.mode=='plot':plot()
    elif opts.mode=='reproduce':
        core()
        run('figure_packages/fig2/compute_gee.py')
        run('analysis/scenario_2030.py')
        verify()
        plot()
if __name__=='__main__':main()

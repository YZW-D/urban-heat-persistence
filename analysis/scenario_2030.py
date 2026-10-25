#!/usr/bin/env python3
"""Conditional annual-state propagation and stratified city bootstrap through 2030.

The state space records consecutive high-effect years, including state zero for
cities below the threshold. Entries are estimated separately for three historical
periods; duration-dependent exits use all 23 observed year-to-year transitions.
The population equivalents retain city populations as measured in 2024.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCENARIOS = ('Early', 'Full', 'Recent')
YEARS = np.arange(2024, 2031)
MAX_DURATION = 30
CLASSES = np.array([0 if d == 1 else 1 if d == 2 else 2 if d == 3 else
                    3 if d <= 5 else 4 if d <= 10 else 5
                    for d in range(1, MAX_DURATION + 1)])


def prepare_panel(path):
    df = pd.read_csv(path, usecols=['city_id', 'year', 'UAH_mean', 'population'])
    df = df.sort_values(['city_id', 'year']).reset_index(drop=True)
    if len(df) != 9713 * 24 or df[['city_id', 'year']].duplicated().any():
        raise ValueError('Incomplete or duplicated city-year panel')
    if not df.groupby('city_id').year.nunique().eq(24).all():
        raise ValueError('Every city must have 24 observations')
    threshold = df.loc[df.year.between(2001, 2005), 'UAH_mean'].quantile(.90)
    high = df.UAH_mean.ge(threshold)
    periods = (~high).groupby(df.city_id).cumsum()
    df['duration'] = high.groupby([df.city_id, periods], sort=False).cumsum().astype(int)
    df['high'] = high.astype(int)
    pop2001 = df.loc[df.year == 2001, ['city_id', 'population']]
    breaks = np.quantile(pop2001.population.to_numpy(), [.25, .5, .75])
    pop2001['stratum'] = np.searchsorted(breaks, pop2001.population.to_numpy(), side='right')
    df = df.merge(pop2001[['city_id', 'stratum']], on='city_id', validate='many_to_one')
    return df, threshold


def historical_counts(df):
    cities = np.sort(df.city_id.unique())
    index = pd.Series(np.arange(len(cities)), index=cities)
    risk = df[df.year < 2024].copy()
    risk['next_high'] = df.groupby('city_id').high.shift(-1).loc[risk.index].astype(int)
    city = index.loc[risk.city_id].to_numpy(dtype=int)
    ncity = len(cities)
    entry_at_risk = np.zeros((ncity, 3), dtype=int)
    entry_events = np.zeros((ncity, 3), dtype=int)
    eligible = risk.high.eq(0).to_numpy()
    time_conditions = [(risk.year.between(2001, 2011)).to_numpy(),
                       np.ones(len(risk), dtype=bool),
                       (risk.year.between(2013, 2023)).to_numpy()]
    for j, period in enumerate(time_conditions):
        loc = eligible & period
        np.add.at(entry_at_risk[:, j], city[loc], 1)
        np.add.at(entry_events[:, j], city[loc], risk.loc[loc, 'next_high'].to_numpy())
    duration = risk.duration.to_numpy(dtype=int)
    active = duration > 0
    class_id = np.where(duration == 1, 0, np.where(duration == 2, 1,
               np.where(duration == 3, 2, np.where(duration <= 5, 3,
               np.where(duration <= 10, 4, 5)))))
    exit_at_risk = np.zeros((ncity, 6), dtype=int)
    exit_events = np.zeros((ncity, 6), dtype=int)
    np.add.at(exit_at_risk, (city[active], class_id[active]), 1)
    np.add.at(exit_events, (city[active], class_id[active]),
              1 - risk.loc[active, 'next_high'].to_numpy())
    city_groups = df.loc[df.year == 2024, ['city_id', 'stratum']]
    city_groups = city_groups.set_index('city_id').loc[cities, 'stratum'].to_numpy(dtype=int)
    current = df.loc[df.year == 2024].set_index('city_id').loc[cities]
    initial = np.zeros((2, 4, MAX_DURATION + 1))
    for stratum in range(4):
        group = current.loc[current.stratum.eq(stratum)]
        initial[0, stratum] = np.bincount(group.duration, minlength=MAX_DURATION + 1)
        initial[1, stratum] = np.bincount(group.duration, weights=group.population,
                                        minlength=MAX_DURATION + 1)
    assert initial[0].sum() == ncity
    return city_groups, entry_at_risk, entry_events, exit_at_risk, exit_events, initial


def estimate_rates(groups, en_risk, en_events, ex_risk, ex_events, samples=None):
    ent = np.empty((3, 4))
    ext = np.empty((4, 6))
    for s in range(4):
        ids = np.flatnonzero(groups == s) if samples is None else samples[s]
        den = en_risk[ids].sum(axis=0)
        num = en_events[ids].sum(axis=0)
        if np.any(den == 0):
            raise ValueError('No eligible entry transitions within a stratum')
        ent[:, s] = num / den
        den_exit = ex_risk[ids].sum(axis=0)
        num_exit = ex_events[ids].sum(axis=0)
        if np.any(den_exit == 0):
            raise ValueError('No eligible exit transitions within a duration class')
        ext[s] = num_exit / den_exit
    return ent, ext


def propagate(initial, entry_rates, exit_rates):
    """Return seven annual arrays: high count, persistent count, and population totals."""
    state = initial.copy()
    committed = initial[0].copy()
    committed[:, 0] = 0
    result = np.zeros((7, 5))
    exits = exit_rates[:, CLASSES]
    for i in range(7):
        high = state[:, :, 1:].sum(axis=(1, 2))
        persistent = state[:, :, 3:].sum(axis=(1, 2))
        committed_n = committed[:, 3:].sum()
        result[i] = [high[0], persistent[0], persistent[1], high[1], committed_n]
        if i == 6:
            break
        next_state = np.zeros_like(state)
        next_state[:, :, 0] = state[:, :, 0] * (1 - entry_rates[None, :]) + \
                              (state[:, :, 1:] * exits[None, :, :]).sum(axis=2)
        next_state[:, :, 1] = state[:, :, 0] * entry_rates[None, :]
        next_state[:, :, 2:] = state[:, :, 1:-1] * (1 - exits[None, :, :-1])
        next_committed = np.zeros_like(committed)
        next_committed[:, 2:] = committed[:, 1:-1] * (1 - exits[:, :-1])
        state, committed = next_state, next_committed
    return result


def scenario_table(initial, rates, exits):
    records = {}
    for j, name in enumerate(SCENARIOS):
        records[name] = propagate(initial, rates[j], exits)
    return records


def run(n_boot, seed, output, skip_bootstrap=False):
    df, threshold = prepare_panel(ROOT / 'data/input/city_year_2001_2024.csv')
    groups, en_risk, en_event, ex_risk, ex_event, initial = historical_counts(df)
    entries, exits = estimate_rates(groups, en_risk, en_event, ex_risk, ex_event)
    base = scenario_table(initial, entries, exits)
    boot = {name: [] for name in SCENARIOS}
    if not skip_bootstrap:
        ids_by_group = [np.flatnonzero(groups == s) for s in range(4)]
        rng = np.random.default_rng(seed)
        for b in range(n_boot):
            samples = [rng.choice(ids, size=len(ids), replace=True) for ids in ids_by_group]
            be, bx = estimate_rates(groups, en_risk, en_event, ex_risk, ex_event, samples)
            for key, series in scenario_table(initial, be, bx).items():
                boot[key].append(series)
            if (b + 1) % 300 == 0:
                print(f'Bootstrap replicates: {b+1}/{n_boot}', flush=True)
        for key in SCENARIOS:
            boot[key] = np.asarray(boot[key])
    allrows = []
    for key in SCENARIOS:
        for i, year in enumerate(YEARS):
            high, persistent, pop_persistent, pop_high, committed = base[key][i]
            values = {'year': int(year), 'scenario': key,
                'expected_high_cities': high, 'expected_persistent_cities': persistent,
                'persistent_share_high_pct': 100*persistent/high,
                'fixed_2024_persistent_population': pop_persistent,
                'fixed_2024_high_effect_population': pop_high,
                'expected_committed_persistent_cities': committed}
            if not skip_bootstrap:
                v = boot[key][:, i, :]
                for col, arr in [('high', v[:, 0]), ('persistent', v[:, 1]),
                                 ('population', v[:, 2]), ('committed', v[:, 4]),
                                 ('persistent_share', 100*v[:, 1]/v[:, 0])]:
                    low, hi = np.quantile(arr, [.025, .975])
                    values[f'{col}_ci_low'] = low
                    values[f'{col}_ci_high'] = hi
            allrows.append(values)
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(allrows).to_csv(output, index=False, float_format='%.12f')
    check = pd.read_csv(ROOT / 'figure_packages/fig1/Fig1D_scenarios_2030.csv')
    reproduced = pd.DataFrame(allrows).merge(check, on=['year', 'scenario'], suffixes=('', '_reference'))
    for column in ('expected_high_cities', 'expected_persistent_cities',
                   'fixed_2024_persistent_population'):
        err = np.max(np.abs(reproduced[column]-reproduced[f'{column}_reference']))
        assert err < 0.0001, (column, err)
    cm = base['Early'][-1, 4]
    assert abs(cm - 1489.11518656365) < .001
    print(f'PASS: P90={threshold:.9f}; 2030 committed persistent cities={cm:.3f}')
    for name in SCENARIOS:
        print(name, '2030 persistent cities:', base[name][-1,1])
    print('Saved:', output)


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description='Recompute conditional 2030 extensions')
    ap.add_argument('--bootstrap', type=int, default=1500)
    ap.add_argument('--seed', type=int, default=20261020)
    ap.add_argument('--skip-bootstrap', action='store_true')
    ap.add_argument('--output', type=Path, default=ROOT / 'outputs/scenarios/Fig1D_recomputed.csv')
    options = ap.parse_args()
    run(options.bootstrap, options.seed, options.output, options.skip_bootstrap)

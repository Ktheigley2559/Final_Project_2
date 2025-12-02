#!/usr/bin/env python3
"""Generate `players.geojson` from `combined_table.db` using the SQL in `queries.sql`.

This script:
- reads the SQL query from `queries.sql` (first statement)
- executes it against `combined_table.db`
- loads `college_raw.csv` to find lat/long for each player's college
- writes `players.geojson` with a Feature per player that has geometry = college lon/lat

Run: python3 generate_players_geojson.py
"""
import sqlite3
import json
from pathlib import Path
import pandas as pd
import re

ROOT = Path(__file__).resolve().parent
DB = ROOT / 'combined_table.db'
SQL_FILE = ROOT / 'queries.sql'
COLLEGE_RAW = ROOT / 'college_raw.csv'
OUT = ROOT / 'players.geojson'


def read_sql_query(path):
    txt = path.read_text(encoding='utf-8')
    # take first statement
    parts = re.split(r";\s*\n", txt)
    return parts[0]


def load_college_coords(college_csv_path):
    df = pd.read_csv(college_csv_path, dtype=str, encoding='latin1', on_bad_lines='skip')
    # normalize name
    df['Name_norm'] = df['Name'].str.lower().str.strip()
    # ensure lat/long numeric
    df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
    df['long'] = pd.to_numeric(df['long'], errors='coerce')
    # drop rows without coords
    df = df[df['lat'].notna() & df['long'].notna()]
    return df


def find_coords_for_college(name, colleges_df):
    if not name or pd.isna(name):
        return None
    key = name.lower().strip()
    # exact substring match first
    match = colleges_df[colleges_df['Name_norm'].str.contains(re.escape(key))]
    if match.empty:
        # try token overlap
        tokens = set(re.findall(r"\w+", key))
        best = None
        best_score = 0
        for _, row in colleges_df.iterrows():
            tokens2 = set(re.findall(r"\w+", row['Name_norm']))
            score = len(tokens & tokens2)
            if score > best_score:
                best_score = score
                best = row
        if best is not None and best_score > 0:
            return float(best['long']), float(best['lat'])
        return None
    # use first match
    r = match.iloc[0]
    return float(r['long']), float(r['lat'])


def main():
    if not DB.exists():
        print('combined_table.db not found; run csv_to_sqlite.py first')
        return
    if not SQL_FILE.exists():
        print('queries.sql not found; create one with desired SELECT statement')
        return
    if not COLLEGE_RAW.exists():
        print('college_raw.csv not found; required to map colleges to coordinates')
        return

    sql = read_sql_query(SQL_FILE)
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    rows = cur.execute(sql).fetchall()
    cols = [d[0] for d in cur.description]
    conn.close()

    colleges_df = load_college_coords(COLLEGE_RAW)
    # Aggregate rows by player name to deduplicate and merge positions/statuses
    players = {}

    def status_rank(s):
        if not s or s is None:
            return 0
        s2 = str(s).strip().lower()
        # higher is better
        if s2 == 'player':
            return 3
        if s2 == 'free agent':
            return 2
        if s2 == 'draft':
            return 1
        return 0

    unique_colleges = set()
    for row in rows:
        rec = dict(zip(cols, row))
        name = rec.get('name') or rec.get('Name') or rec.get('player')
        if not name:
            continue
        unique_colleges.add((rec.get('college') or '').strip())
        key = str(name).strip().lower()
        college = rec.get('college')
        coords = find_coords_for_college(college, colleges_df)
        if not coords:
            # record missing coords for debugging and skip
            missing = rec.get('college') or '<no-college>'
            print(f"Skipping '{name}': no coords found for college '{missing}'")
            continue
        lon, lat = coords
        pos = (rec.get('position') or '').strip()
        status = (rec.get('team_status') or '').strip()

        entry = players.get(key)
        if not entry:
            players[key] = {
                'name': name,
                'positions': set([pos]) if pos else set(),
                'team_status': status,
                'status_rank': status_rank(status),
                'college': college,
                'college_address': rec.get('college_address'),
                'city': rec.get('city'),
                'state': rec.get('state'),
                'coords': (lon, lat)
            }
        else:
            # merge position
            if pos:
                entry['positions'].add(pos)
            # choose better status if present
            r = status_rank(status)
            if r > entry.get('status_rank', 0):
                # prefer record with higher status (Player > Free Agent > Draft)
                entry['team_status'] = status
                entry['status_rank'] = r
                entry['college'] = college
                entry['college_address'] = rec.get('college_address')
                entry['city'] = rec.get('city')
                entry['state'] = rec.get('state')
                entry['coords'] = (lon, lat)

    features = []
    for entry in players.values():
        lon, lat = entry['coords']
        props = {
            'name': entry['name'],
            'position': '/'.join(sorted([p for p in entry['positions'] if p])),
            'college': entry.get('college'),
            'college_address': entry.get('college_address'),
            'city': entry.get('city'),
            'state': entry.get('state'),
            'team_status': entry.get('team_status')
        }
        feat = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': props
        }
        features.append(feat)

    geo = {'type': 'FeatureCollection', 'features': features}
    OUT.write_text(json.dumps(geo), encoding='utf-8')
    print(f'Wrote {OUT} with {len(features)} features')
    # report colleges available vs. missing
    print(f'Tried to map {len(unique_colleges)} unique college names from query')


if __name__ == '__main__':
    main()

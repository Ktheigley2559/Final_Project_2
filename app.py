from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import pandas as pd
import json
import os

HERE = os.path.dirname(__file__)
DB_PATH = os.path.join(HERE, 'combined_table.db')
COLLEGE_CSV = os.path.join(HERE, 'college_raw.csv')
QUERIES_SQL = os.path.join(HERE, 'queries.sql')

app = Flask(__name__, static_folder='static', static_url_path='')


def read_query():
    with open(QUERIES_SQL, 'r', encoding='utf-8') as f:
        raw = f.read()
    # Use the first statement (before first semicolon) if multiple
    stmt = raw.strip()
    if ';' in stmt:
        stmt = stmt.split(';', 1)[0]
    return stmt


def query_db(sql):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(sql)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def load_colleges():
    # load databayou colleges CSV (expected to contain lat/lon columns)
    if not os.path.exists(COLLEGE_CSV):
        return pd.DataFrame()
    try:
        df = pd.read_csv(COLLEGE_CSV, encoding='utf-8')
    except Exception:
        df = pd.read_csv(COLLEGE_CSV, encoding='latin1')
    # normalize column names
    cols = {c.lower(): c for c in df.columns}
    # find lat/lon heuristically
    lat_col = None
    lon_col = None
    for k in cols:
        if 'lat' in k:
            lat_col = cols[k]
        if 'lon' in k or 'lng' in k or 'long' in k:
            lon_col = cols[k]
    # ensure name column
    name_col = cols.get('name') or cols.get('college') or list(df.columns)[0]
    df = df.rename(columns={name_col: 'name'})
    if lat_col:
        df = df.rename(columns={lat_col: 'lat'})
    if lon_col:
        df = df.rename(columns={lon_col: 'lon'})
    return df


def match_college_coords(college_name, colleges_df):
    if colleges_df is None or colleges_df.empty:
        return None
    key = str(college_name).lower().strip()
    # exact match
    m = colleges_df[colleges_df['name'].str.lower().str.strip() == key]
    if not m.empty and 'lat' in m.columns and 'lon' in m.columns:
        row = m.iloc[0]
        return (float(row['lon']), float(row['lat']))
    # substring match
    m = colleges_df[colleges_df['name'].str.lower().str.contains(key, na=False)]
    if not m.empty and 'lat' in m.columns and 'lon' in m.columns:
        row = m.iloc[0]
        return (float(row['lon']), float(row['lat']))
    # token overlap
    tokens = [t for t in key.replace(',', ' ').split() if len(t) > 2]
    if tokens:
        def score_name(n):
            ln = str(n).lower()
            return sum(1 for t in tokens if t in ln)
        scores = colleges_df['name'].apply(score_name)
        best = scores.idxmax()
        if scores.loc[best] > 0 and 'lat' in colleges_df.columns and 'lon' in colleges_df.columns:
            row = colleges_df.loc[best]
            try:
                return (float(row['lon']), float(row['lat']))
            except Exception:
                return None
    return None


@app.route('/api/players')
def api_players():
    q = request.args.get('q', '').strip().lower()
    sql = read_query()
    rows = query_db(sql)
    # in-memory filter by q if provided
    if q:
        def keep(r):
            for k in ('name', 'college', 'position', 'team_status'):
                if r.get(k) and q in str(r.get(k)).lower():
                    return True
            return False
        rows = [r for r in rows if keep(r)]

    colleges_df = load_colleges()
    features = []
    for r in rows:
        coords = match_college_coords(r.get('college'), colleges_df)
        if not coords:
            # skip entries without coordinates
            continue
        lon, lat = coords
        feat = {
            'type': 'Feature',
            'geometry': {'type': 'Point', 'coordinates': [lon, lat]},
            'properties': r
        }
        features.append(feat)
    fc = {'type': 'FeatureCollection', 'features': features}
    return jsonify(fc)


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)

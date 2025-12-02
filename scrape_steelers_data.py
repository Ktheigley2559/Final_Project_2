#!/usr/bin/env python3
"""Scrape local copies of the three pages and databayou CSV to produce
CSV outputs: draft_picks.csv, free_agents.csv, current_roster.csv,
colleges.csv, and combined_table.csv (players merged with college info).

Assumes the following files are present in repo root:
- raw_wikipedia.html
- raw_steelers.html
- college_raw.csv

Run: python3 scrape_steelers_data.py
"""
import csv
import re
from pathlib import Path
from bs4 import BeautifulSoup
import pandas as pd

ROOT = Path(__file__).resolve().parent


def normalize_name(n):
    if not n:
        return n
    n = re.sub(r"\s+III$|\s+II$|\s+Jr\.?$|\s+Sr\.?$", "", n, flags=re.I)
    n = re.sub(r"\s+\(.+\)", "", n)
    return re.sub(r"\s+", " ", n).strip()


def parse_wikipedia_draft_and_freeagents(wiki_html_path):
    html = wiki_html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    # Draft table
    draft_rows = []
    draft_table = None
    for table in soup.find_all("table", class_="wikitable"):
        cap = table.find("caption")
        if cap and "draft selections" in cap.get_text().lower():
            draft_table = table
            break
    if draft_table:
        for tr in draft_table.find_all("tr")[1:]:
            # Heuristic: find anchors in the row and identify which is player / position / college
            anchors = tr.find_all('a')
            player = position = college = ''
            if anchors:
                # try to pick the player anchor: prefer anchors whose href doesn't reference seasons or teams
                player_anchor = None
                for a in anchors:
                    href = a.get('href','')
                    txt = a.get_text(strip=True)
                    if not href or href.startswith('#'):
                        continue
                    if any(sub in href for sub in ['/season', 'season', '2025_', '2024_']):
                        continue
                    # skip obvious position links
                    if txt.lower() in ('qb','rb','wr','te','dt','de','ol','lb','s','cb','k','p'):
                        continue
                    # likely a player name if it contains a space or has mixed case
                    # likely a player name if it contains a space or is longer than 2 characters
                    if ' ' in txt or len(txt) > 2:
                        player_anchor = a
                        break
                if player_anchor:
                    player = player_anchor.get_text(strip=True)
                    # position: look for an anchor after the player_anchor that is a position
                    try:
                        ai = anchors.index(player_anchor)
                        # scan following anchors for a position-like anchor
                        for a in anchors[ai+1:ai+4]:
                            t = a.get_text(strip=True)
                            if t and (len(t) <= 3 or 'defensive' in t.lower() or 'quarterback' in t.lower()):
                                position = t
                                break
                        # college: pick next anchor that seems like a school (may include 'football team' pages)
                        for a in anchors[ai+1:ai+6]:
                            t = a.get_text(strip=True)
                            href = a.get('href','')
                            if 'football_team' in href or len(t) > 2 and t[0].isupper():
                                # avoid team season pages
                                if 'season' in href:
                                    continue
                                college = t
                                break
                    except ValueError:
                        pass
            if player:
                draft_rows.append({"name": normalize_name(player), "position": position, "college": college})

    # Undrafted free agents table (caption contains 'undrafted free agents' or 'undrafted')
    free_rows = []
    for table in soup.find_all("table", class_="wikitable"):
        cap = table.find("caption")
        if cap and "undrafted free agents" in cap.get_text().lower():
            for tr in table.find_all("tr")[1:]:
                tds = tr.find_all("td")
                if len(tds) >= 3:
                    player = tds[0].get_text(strip=True)
                    position = tds[1].get_text(strip=True)
                    college = tds[2].get_text(strip=True)
                    free_rows.append({"name": normalize_name(player), "position": position, "college": college})
            break

    return draft_rows, free_rows


def parse_wikipedia_roster(wiki_html_path):
    # Wikipedia roster is organized as a template with headings for position groups
    html = wiki_html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    roster = []
    # find the 'Current roster' heading
    h = soup.find(id="Current_roster")
    if not h:
        # fallback: find h2 with text Current roster
        for h2 in soup.find_all("h2"):
            if "Current roster" in h2.get_text():
                h = h2
                break
    if not h:
        return roster

    # The roster template following the heading contains multiple <ul> blocks grouped by position headers
    # The roster is usually contained in a following <table class="toccolours">; find next table after heading
    tbl = h.find_next('table')
    if not tbl:
        return roster
    # For each table cell, extract group header (<b> tag) and the following <ul>
    pos_map = {
        'Quarterbacks': 'QB', 'Running': 'RB', 'Wide': 'WR', 'Tight': 'TE',
        'Offensive': 'OL', 'Defensive': 'DL', 'Linebackers': 'LB', 'Linebacker': 'LB',
        'Linebacker': 'LB', 'Defensive_line': 'DL', 'Special': 'ST'
    }
    for td in tbl.find_all('td'):
        # find header in td
        header = td.find(['b', 'p'])
        current_pos = None
        if header:
            txt = header.get_text()
            m = re.search(r"\((QB|RB|WR|TE|OL|DL|LB|S|CB|K|P|LS)\)", txt)
            if m:
                current_pos = m.group(1)
            else:
                # fallback to the header word (e.g., 'Quarterbacks')
                words = re.findall(r"[A-Za-z]+", txt)
                if words:
                    current_pos = words[0]
        # find any ul lists in this td
        for ul in td.find_all('ul'):
            for li in ul.find_all('li'):
                a = li.find('a')
                if not a:
                    continue
                href = a.get('href','')
                txt = a.get_text(strip=True)
                # filter out non-player links
                if not href.startswith('/wiki/'):
                    continue
                if any(ignore in txt for ignore in ['Roster','Depth chart','Transactions','Practice']):
                    continue
                # reasonable player name should be longer than 2 chars or contain a space
                if len(txt) <= 2 and ' ' not in txt:
                    continue
                player = txt
                abbr = li.find('abbr')
                pos = abbr.get_text(strip=True) if abbr else current_pos
                # normalize position if it's a verbose header
                if isinstance(pos, str):
                    # map common header words to abbreviations
                    for k,v in pos_map.items():
                        if k.lower() in str(pos).lower():
                            pos = v
                            break
                roster.append({"name": normalize_name(player), "position": pos})
    return roster


def parse_steelers_roster(steelers_html_path):
    html = steelers_html_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")
    mapping = {}
    # Find the roster table by class 'd3-o-table' and header 'College'
    table = soup.find('table', class_=lambda c: c and 'd3-o-table' in c)
    if not table:
        return mapping
    rows = table.find('tbody').find_all('tr')
    for tr in rows:
        name_tag = tr.find('span', class_='nfl-o-roster__player-name')
        if not name_tag:
            continue
        name = name_tag.get_text(strip=True)
        tds = tr.find_all('td')
        # last td contains college (per inspection)
        college = ''
        if tds:
            college = tds[-1].get_text(strip=True)
        mapping[normalize_name(name)] = college
    return mapping


def load_databayou_colleges(college_csv_path):
    # read the CSV as provided by databayou (college_raw.csv)
    # databayou CSV contains characters that may not be UTF-8; read with latin1 to be forgiving
    df = pd.read_csv(college_csv_path, dtype=str, encoding='latin1', on_bad_lines='skip')
    # normalize column names: Name, ADDR, CITY, State
    df = df.rename(columns={c: c.strip() for c in df.columns})
    # Keep only requested columns
    cols = [c for c in ['Name', 'ADDR', 'CITY', 'State'] if c in df.columns]
    out = df[cols].copy()
    out = out.fillna('')
    return out


def write_csv_rows(path, rows, fieldnames):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def match_college(player_college, colleges_df):
    if not player_college or player_college.strip() == '':
        return None
    needle = player_college.lower()
    # exact substring match on Name
    for _, row in colleges_df.iterrows():
        name = str(row['Name']).lower()
        if needle in name or name in needle:
            return row.to_dict()
    # try token match
    needle_tokens = set(re.findall(r"\w+", needle))
    best = None
    best_score = 0
    for _, row in colleges_df.iterrows():
        name = str(row['Name']).lower()
        tokens = set(re.findall(r"\w+", name))
        score = len(needle_tokens & tokens)
        if score > best_score:
            best_score = score
            best = row.to_dict()
    if best_score > 0:
        return best
    return None


def main():
    wiki = ROOT / 'raw_wikipedia.html'
    steelers = ROOT / 'raw_steelers.html'
    college_csv = ROOT / 'college_raw.csv'

    draft_rows, free_rows = parse_wikipedia_draft_and_freeagents(wiki)
    roster_rows = parse_wikipedia_roster(wiki)
    steelers_map = parse_steelers_roster(steelers)
    colleges_df = load_databayou_colleges(college_csv)

    # enrich roster rows with college by matching to steelers.com mapping when possible
    for r in roster_rows:
        key = normalize_name(r['name'])
        college = steelers_map.get(key, '')
        if not college:
            # try fuzzy match on last name
            for k,v in steelers_map.items():
                if k.split()[-1].lower() == key.split()[-1].lower():
                    college = v
                    break
        r['college'] = college

    # assign team_status and source_url
    draft_out = []
    for r in draft_rows:
        r_out = {'name': r['name'], 'position': r['position'], 'college': r['college'], 'team_status': 'Draft', 'source_url': 'https://en.wikipedia.org/wiki/2025_Pittsburgh_Steelers_season'}
        draft_out.append(r_out)

    free_out = []
    for r in free_rows:
        r_out = {'name': r['name'], 'position': r['position'], 'college': r['college'], 'team_status': 'Free Agent', 'source_url': 'https://en.wikipedia.org/wiki/2025_Pittsburgh_Steelers_season'}
        free_out.append(r_out)

    roster_out = []
    for r in roster_rows:
        r_out = {'name': r['name'], 'position': r.get('position',''), 'college': r.get('college',''), 'team_status': 'Player', 'source_url': 'https://en.wikipedia.org/wiki/2025_Pittsburgh_Steelers_season'}
        roster_out.append(r_out)

    # Write individual CSVs
    csv_fields = ['name','position','college','team_status','source_url']
    write_csv_rows(ROOT / 'draft_picks.csv', draft_out, csv_fields)
    write_csv_rows(ROOT / 'free_agents.csv', free_out, csv_fields)
    write_csv_rows(ROOT / 'current_roster.csv', roster_out, csv_fields)

    # colleges.csv: include Name, ADDR, CITY, State, and source_url
    colleges_df_out = colleges_df.copy()
    colleges_df_out['source_url'] = 'https://databayou.com/usofa/colleges.html'
    colleges_df_out = colleges_df_out.rename(columns={'Name':'name','ADDR':'address','CITY':'city','State':'state'})
    colleges_df_out.to_csv(ROOT / 'colleges.csv', index=False)

    # combined_table.csv: merge players with college details, but only for colleges referenced by players
    players_df = pd.DataFrame(draft_out + free_out + roster_out)
    players_df['college_key'] = players_df['college'].fillna('').str.lower().str.strip()

    combined_rows = []
    for _, prow in players_df.iterrows():
        college_text = prow['college']
        matched = match_college(college_text, colleges_df)
        if matched:
            combined = {
                'name': prow['name'],
                'position': prow['position'],
                'college': college_text,
                'college_address': matched.get('ADDR',''),
                'city': matched.get('CITY',''),
                'state': matched.get('State',''),
                'team_status': prow['team_status'],
                'player_source': prow['source_url'],
                'college_source': 'https://databayou.com/usofa/colleges.html'
            }
            combined_rows.append(combined)

    if combined_rows:
        df_comb = pd.DataFrame(combined_rows)
        df_comb.to_csv(ROOT / 'combined_table.csv', index=False)
    else:
        # write empty combined with headers
        pd.DataFrame(columns=['name','position','college','college_address','city','state','team_status','player_source','college_source']).to_csv(ROOT / 'combined_table.csv', index=False)

    print('Wrote: draft_picks.csv, free_agents.csv, current_roster.csv, colleges.csv, combined_table.csv')


if __name__ == '__main__':
    main()

# NFL Player/Roster Data Column Reference Guide

This dataset contains 37 columns of NFL player and roster information for the 2024 season. Below is a comprehensive guide to each column and what it represents.

## Basic Player Information

| Column Name | Description |
|-------------|-------------|
| season | The NFL season year (2024) |
| player_name | Full name of the player |
| first_name | Player's first name |
| last_name | Player's last name |
| football_name | Name commonly used on jerseys/broadcasts |
| birth_date | Player's date of birth |
| age | Player's age during the season |

## Team and Position Information

| Column Name | Description |
|-------------|-------------|
| team | Three-letter abbreviation for player's team |
| position | Player's primary position (QB, RB, WR, etc.) |
| depth_chart_position | Position on the official depth chart |
| ngs_position | Next Gen Stats position classification |
| jersey_number | Player's jersey number |

## Player Status and Availability

| Column Name | Description |
|-------------|-------------|
| status | Current roster status (Active, IR, etc.) |
| status_description_abbr | Abbreviated status description |
| week | Week number for status (if status changes during season) |
| game_type | Type of game for status tracking (REG, POST) |

## Physical Characteristics

| Column Name | Description |
|-------------|-------------|
| height | Player's height (typically in feet-inches format) |
| weight | Player's weight in pounds |
| college | College or university the player attended |

## Experience and Career Information

| Column Name | Description |
|-------------|-------------|
| years_exp | Number of years of NFL experience |
| entry_year | Year player first entered the NFL |
| rookie_year | Year player was considered a rookie |
| draft_club | Team that originally drafted the player |
| draft_number | Overall draft position (1-262 for 7 rounds) |

## Unique Player Identifiers

| Column Name | Description |
|-------------|-------------|
| player_id | Primary unique identifier for the player |
| espn_id | ESPN's unique player identifier |
| sportradar_id | SportRadar's unique player identifier |
| yahoo_id | Yahoo Sports unique player identifier |
| rotowire_id | RotoWire's unique player identifier |
| pff_id | Pro Football Focus unique player identifier |
| pfr_id | Pro Football Reference unique player identifier |
| fantasy_data_id | FantasyData.com unique player identifier |
| sleeper_id | Sleeper fantasy platform unique identifier |
| esb_id | Elite Sports Bureau unique identifier |
| gsis_it_id | NFL's Game Statistics & Information System identifier |
| smart_id | Smart ID system identifier |

## Media and Visual Assets

| Column Name | Description |
|-------------|-------------|
| headshot_url | URL link to player's official headshot photo |

---

## Understanding Player Positions

### Offensive Positions
- **QB** - Quarterback
- **RB** - Running Back
- **FB** - Fullback
- **WR** - Wide Receiver
- **TE** - Tight End
- **C** - Center
- **G** - Guard
- **T** - Tackle
- **OL** - Generic Offensive Line
- **OT** - Offensive Tackle
- **OG** - Offensive Guard

### Defensive Positions
- **DE** - Defensive End
- **DT** - Defensive Tackle
- **NT** - Nose Tackle
- **DL** - Generic Defensive Line
- **LB** - Linebacker
- **ILB** - Inside Linebacker
- **OLB** - Outside Linebacker
- **MLB** - Middle Linebacker
- **CB** - Cornerback
- **S** - Safety
- **FS** - Free Safety
- **SS** - Strong Safety
- **DB** - Generic Defensive Back

### Special Teams Positions
- **K** - Kicker
- **P** - Punter
- **LS** - Long Snapper

## Understanding Player Status Codes

### Common Status Types
- **ACT** - Active (available to play)
- **IR** - Injured Reserve (out for season/extended period)
- **PUP** - Physically Unable to Perform list
- **NFI** - Non-Football Injury list
- **SUS** - Suspended
- **RET** - Retired
- **UFA** - Unrestricted Free Agent
- **RFA** - Restricted Free Agent
- **EXE** - Exempt list
- **RES** - Reserve list
- **CUT** - Released from team
- **TRADE** - Traded to another team

## Draft Information

### Draft Rounds and Picks
- **Rounds 1-7**: Each round has 32 picks (one per team)
- **Overall Pick Numbers**: 1-262 total picks in a full draft
- **Round 1**: Picks 1-32
- **Round 2**: Picks 33-64
- **Round 3**: Picks 65-96
- **Round 4**: Picks 97-128
- **Round 5**: Picks 129-160
- **Round 6**: Picks 161-192
- **Round 7**: Picks 193-224+ (compensatory picks can extend this)

### Undrafted Players
- Players not selected in the draft will have `NA` or blank values for `draft_club` and `draft_number`
- These players signed as Undrafted Free Agents (UDFA)

## Experience Levels

### Years of Experience
- **0**: Rookie season
- **1-3**: Early career players
- **4-7**: Mid-career veterans
- **8+**: Veteran players
- **10+**: Long-term veterans

## Using Player IDs

### Primary Identifiers
- **player_id**: Use this as the main identifier for joining with play-by-play data
- **gsis_it_id**: NFL's official identifier, often used in official statistics

### External Platform IDs
- **espn_id**, **yahoo_id**: Useful for integrating with fantasy sports platforms
- **pff_id**: For connecting with Pro Football Focus advanced analytics
- **pfr_id**: For linking with Pro Football Reference historical data
- **sleeper_id**: For fantasy football applications using Sleeper platform

## Notes for Using This Data

1. **Position Flexibility**: Some players may be listed with multiple positions or have position changes during the season.

2. **Roster Changes**: Player status can change weekly due to injuries, trades, signings, and releases.

3. **Depth Chart**: The `depth_chart_position` may differ from `position` and indicates where the player stands in the team's depth chart.

4. **Missing Data**: Some fields may be empty (NA) for certain players, especially undrafted players or players with incomplete records.

5. **Team Abbreviations**: Use standard NFL 3-letter team codes (same as in play-by-play data).

6. **Joining with Play-by-Play**: Use `player_id` to join this roster data with the play-by-play data for comprehensive player analysis.

7. **Physical Measurements**: Height and weight data is typically from NFL Combine or team measurements.

8. **College Information**: Includes major universities and smaller colleges, as well as international players.

## Common Use Cases

- **Roster Analysis**: Track team composition and depth at each position
- **Experience Analysis**: Analyze team age and experience levels
- **Draft Analysis**: Study draft pick performance and value
- **Physical Traits**: Correlate player size with performance metrics
- **College Pipeline**: Analyze which colleges produce the most NFL talent
- **Fantasy Sports**: Player identification and metadata for fantasy applications
- **Contract/Salary Analysis**: When combined with contract data
- **Injury Tracking**: Monitor player availability throughout the season

This roster dataset is perfect for analyzing team construction, player demographics, and creating comprehensive player profiles when combined with the play-by-play performance data!

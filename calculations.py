"""
calculations.py
---------------
All the maths of the project. NumPy is used to get totals, averages,
median, standard deviation and counts from lists of numbers.
"""

import numpy as np

# TUPLE: every key that a summary dictionary will contain
SUMMARY_KEYS = ("played", "wins", "draws", "losses", "gf", "ga", "gd", "points",
                "win_pct", "clean_sheets", "avg_gf", "median_gf", "std_gf",
                "avg_xg", "avg_xga", "avg_poss", "total_xg", "total_xga",
                "shot_accuracy")


def empty_summary():
    """A summary full of zeros (used when there are no matches)."""
    summary = {}
    for key in SUMMARY_KEYS:
        summary[key] = 0
    return summary


def team_summary(matches):
    """Take a list of Match objects of ONE team and return a dictionary of statistics."""
    if len(matches) == 0:
        return empty_summary()

    # Put each column of numbers into a NumPy array
    goals_for = np.array([m.gf for m in matches])
    goals_against = np.array([m.ga for m in matches])
    xg = np.array([m.xg for m in matches])
    xga = np.array([m.xga for m in matches])
    possession = np.array([m.poss for m in matches])
    shots = np.array([m.sh for m in matches])
    on_target = np.array([m.sot for m in matches])

    played = len(matches)
    wins = draws = losses = points = 0
    for m in matches:
        if m.result == "W":
            wins += 1
        elif m.result == "D":
            draws += 1
        else:
            losses += 1
        points += m.points()

    total_shots = int(np.sum(shots))
    if total_shots > 0:
        shot_accuracy = float(np.sum(on_target)) / total_shots * 100
    else:
        shot_accuracy = 0

    summary = {
        "played": played,
        "wins": wins,
        "draws": draws,
        "losses": losses,
        "gf": int(np.sum(goals_for)),
        "ga": int(np.sum(goals_against)),
        "gd": int(np.sum(goals_for) - np.sum(goals_against)),
        "points": points,
        "win_pct": round(wins / played * 100, 1),
        "clean_sheets": int(np.sum(goals_against == 0)),   # matches with 0 goals conceded
        "avg_gf": round(float(np.mean(goals_for)), 2),
        "median_gf": float(np.median(goals_for)),
        "std_gf": round(float(np.std(goals_for)), 2),
        "avg_xg": round(float(np.mean(xg)), 2),
        "avg_xga": round(float(np.mean(xga)), 2),
        "avg_poss": round(float(np.mean(possession)), 1),
        "total_xg": round(float(np.sum(xg)), 1),
        "total_xga": round(float(np.sum(xga)), 1),
        "shot_accuracy": round(shot_accuracy, 1),
    }
    return summary


def last_results(matches, count=5):
    """Return the last few results ('W','D','L'), oldest first."""
    ordered = sorted(matches, key=get_date)
    recent = ordered[-count:]
    results = []
    for m in recent:
        results.append(m.result)
    return results


def table_sort_key(row):
    """Sort rule for the league table: points, then goal difference, then goals scored."""
    return (row["points"], row["gd"], row["gf"])


def league_table(matches):
    """Take the matches of one season (all teams) and return table rows, best team first."""
    groups = {}                       # DICTIONARY: team name -> list of its matches
    for m in matches:
        if m.team not in groups:
            groups[m.team] = []
        groups[m.team].append(m)

    rows = []
    for team in groups:
        row = team_summary(groups[team])
        row["team"] = team
        rows.append(row)

    rows.sort(key=table_sort_key, reverse=True)
    return rows


def head_to_head(matches, team_a, team_b):
    """Compare two teams using the matches of team_a played against team_b."""
    meetings = []
    for m in matches:
        if m.team == team_a and m.opponent == team_b:
            meetings.append(m)
    meetings.sort(key=get_date)

    a_wins = draws = b_wins = a_goals = b_goals = 0
    for m in meetings:
        if m.result == "W":
            a_wins += 1
        elif m.result == "D":
            draws += 1
        else:
            b_wins += 1
        a_goals += m.gf
        b_goals += m.ga

    return {"meetings": meetings, "a_wins": a_wins, "draws": draws,
            "b_wins": b_wins, "a_goals": a_goals, "b_goals": b_goals}


def get_date(match):
    return match.date

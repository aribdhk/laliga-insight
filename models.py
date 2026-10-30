"""
models.py
---------
Two classes live here:
  * Match        -> ONE match, seen from ONE team's point of view (data model class)
  * MatchManager -> keeps ALL matches, and does add / update / delete / filter / save / load
"""

import csv

# ---- TUPLES: fixed values that never change ----
VENUES = ("Home", "Away")
RESULTS = ("W", "D", "L")
CSV_COLUMNS = ("match_id", "season", "matchweek", "date", "venue", "team",
               "opponent", "gf", "ga", "result", "xg", "xga", "poss", "sh", "sot")


class Match:
    """One row of data: how one team played one match."""

    def __init__(self, match_id, season, matchweek, date, venue, team, opponent,
                 gf, ga, xg, xga, poss, sh, sot):
        self.match_id = match_id    # e.g. "M00001"
        self.season = season        # start year, 2024 means season 2024/25
        self.matchweek = matchweek  # 1 to 38
        self.date = date            # text like "2024-08-18"
        self.venue = venue          # "Home" or "Away"
        self.team = team            # the team we are looking at
        self.opponent = opponent
        self.gf = gf                # goals for
        self.ga = ga                # goals against
        self.xg = xg                # expected goals (quality of chances created)
        self.xga = xga              # expected goals against
        self.poss = poss            # possession %
        self.sh = sh                # shots
        self.sot = sot              # shots on target
        self.result = self.work_out_result()   # always calculated, never typed in

    def work_out_result(self):
        """Return 'W', 'D' or 'L' from the score."""
        if self.gf > self.ga:
            return "W"
        elif self.gf < self.ga:
            return "L"
        else:
            return "D"

    def points(self):
        """Win = 3 points, draw = 1, loss = 0."""
        if self.result == "W":
            return 3
        elif self.result == "D":
            return 1
        return 0

    def goal_difference(self):
        return self.gf - self.ga

    def key(self):
        """A team can only play one match per date, so (team, date) must be unique."""
        return (self.team, self.date)

    def to_dict(self):
        """Turn the object into a dictionary so the csv module can write it."""
        row = {}
        for column in CSV_COLUMNS:
            row[column] = getattr(self, column)
        return row

    def __str__(self):
        return f"{self.date}  {self.team} {self.gf}-{self.ga} {self.opponent} ({self.venue})"


def row_to_match(row):
    """Convert one CSV row (a dictionary of text) into a Match object.
    Raises ValueError / KeyError if the row is broken."""
    return Match(
        match_id=row["match_id"].strip(),
        season=int(row["season"]),
        matchweek=int(row["matchweek"]),
        date=row["date"].strip(),
        venue=row["venue"].strip(),
        team=row["team"].strip(),
        opponent=row["opponent"].strip(),
        gf=int(row["gf"]),
        ga=int(row["ga"]),
        xg=float(row["xg"]),
        xga=float(row["xga"]),
        poss=int(row["poss"]),
        sh=int(row["sh"]),
        sot=int(row["sot"]),
    )


class MatchManager:
    """Keeps the list of matches and everything we can do with it."""

    def __init__(self):
        self.matches = []        # LIST of Match objects
        self.used_ids = set()    # SET of match ids        -> stops duplicate ids
        self.used_keys = set()   # SET of (team, date)     -> stops duplicate matches

    # ------------------------------------------------------------ files
    def load_from_csv(self, filename):
        """Read matches from a CSV file.
        Returns (True/False, message). It never crashes on a bad file."""
        new_matches = []
        new_ids = set()
        new_keys = set()
        skipped = 0

        try:
            with open(filename, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        match = row_to_match(row)
                    except (ValueError, KeyError, TypeError, AttributeError):
                        skipped += 1          # malformed row -> skip it
                        continue
                    if match.match_id in new_ids or match.key() in new_keys:
                        skipped += 1          # duplicate -> skip it
                        continue
                    new_matches.append(match)
                    new_ids.add(match.match_id)
                    new_keys.add(match.key())
        except FileNotFoundError:
            return False, f"File not found: {filename}"
        except (OSError, UnicodeDecodeError, csv.Error) as error:
            return False, f"Could not read the file: {error}"

        if len(new_matches) == 0:
            return False, "The file is empty or has no valid match rows."

        # Only replace the current data once we know the new file is good
        self.matches = new_matches
        self.used_ids = new_ids
        self.used_keys = new_keys
        return True, f"Loaded {len(new_matches)} matches ({skipped} bad rows skipped)."

    def save_to_csv(self, filename):
        """Write all matches to a CSV file. Returns (True/False, message)."""
        try:
            with open(filename, "w", newline="", encoding="utf-8") as file:
                writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
                writer.writeheader()
                for match in self.matches:
                    writer.writerow(match.to_dict())
        except OSError as error:
            return False, f"Could not save the file: {error}"
        return True, f"Saved {len(self.matches)} matches."

    # ------------------------------------------------------------ add / find / update / delete
    def next_id(self):
        """Make a new unused id like 'M04701'."""
        number = len(self.matches) + 1
        while f"M{number:05d}" in self.used_ids:
            number += 1
        return f"M{number:05d}"

    def add_match(self, match):
        if match.match_id in self.used_ids:
            raise ValueError("This match id already exists.")
        if match.key() in self.used_keys:
            raise ValueError(f"{match.team} already has a match on {match.date}.")
        self.matches.append(match)
        self.used_ids.add(match.match_id)
        self.used_keys.add(match.key())

    def find_by_id(self, match_id):
        """Return the Match with this id, or None if it does not exist."""
        for match in self.matches:
            if match.match_id == match_id:
                return match
        return None

    def update_match(self, match_id, new_match):
        old_match = self.find_by_id(match_id)
        if old_match is None:
            raise ValueError("Match not found.")
        # the new (team, date) may only clash with OTHER matches, not with itself
        if new_match.key() != old_match.key() and new_match.key() in self.used_keys:
            raise ValueError(f"{new_match.team} already has a match on {new_match.date}.")
        position = self.matches.index(old_match)
        self.matches[position] = new_match
        self.used_keys.discard(old_match.key())
        self.used_keys.add(new_match.key())

    def delete_match(self, match_id):
        match = self.find_by_id(match_id)
        if match is None:
            raise ValueError("Match not found.")
        self.matches.remove(match)
        self.used_ids.discard(match.match_id)
        self.used_keys.discard(match.key())

    # ------------------------------------------------------------ lists for the screens
    def get_teams(self):
        """Sorted list of unique team names (a set removes the repeats)."""
        names = set()
        for match in self.matches:
            names.add(match.team)
        return sorted(names)

    def get_seasons(self):
        """Unique seasons, newest first."""
        seasons = set()
        for match in self.matches:
            seasons.add(match.season)
        return sorted(seasons, reverse=True)

    def filter_matches(self, team="All", season="All", venue="All", opponent_text=""):
        """Return the matches that pass every filter, ordered by date."""
        found = []
        search = opponent_text.strip().lower()
        for match in self.matches:
            if team != "All" and match.team != team:
                continue
            if season != "All" and str(match.season) != str(season):
                continue
            if venue != "All" and match.venue != venue:
                continue
            if search != "" and search not in match.opponent.lower():
                continue
            found.append(match)
        found.sort(key=get_date)
        return found


def get_date(match):
    """Helper used for sorting matches by date."""
    return match.date

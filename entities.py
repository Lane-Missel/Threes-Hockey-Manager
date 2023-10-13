"""
Lane Missel

General objects for the application.
"""

from dataclasses import dataclass, field
from enum import Enum
from itertools import combinations
from random import randint
from typing import Dict, List, Tuple

class Position(Enum):
    goaltender = 0
    defender = 1
    forward = 2

class GameTypes(Enum):
    regular = 0
    postseason = 1
    exhibition = 2

@dataclass
class Person:
    """An object representing a person in the game."""
    identifier: int
    first: str
    last: str
    region_id: int
    age: int
    special: str

    @property
    def name(self):
        return "{} {}".format(self.first, self.last)

@dataclass(frozen=True)
class Contract:
    """An object with contract information"""
    salary: int
    type_id: int

@dataclass
class Record:
    """An object for tracking team/goalie records."""
    wins: int = 0
    losses: int = 0
    ties: int = 0

@dataclass
class Statistics:
    """An object for tracking general player statistics."""
    goals: int = 0
    assists: int = 0
    shots: int = 0
    games_played: int = 0
    seconds_played: int = 0
    plus: int = 0
    minus: int = 0

    @property
    def points(self):
        return self.goals + self.assists

    @property
    def plus_minus(self):
        return self.plus - self.minus

    @classmethod
    def randomized(self):
        return Statistics(randint(0,30), randint(0, 30), randint(0, 90), randint(10, 30), 0, randint(0, 60), randint(0, 60))

@dataclass
class GoaltenderStatistics(Statistics):
    """An object fro tracking goaltending statistics."""
    goals_against: int = 0
    shots_against: int = 0
    record: Record = Record()

@dataclass(frozen=True)
class StatisticalRecordKey:
    """An object for indexing statistics"""
    year: int
    team: int = None
    type: int = None

    def has_year(self, year: int):
        return year == self.year

@dataclass
class StatisticalRecords:
    """An object for managing statistics objects."""
    records: dict = field(default_factory=dict)

    @property
    def keys(self):
        return set(self.records.keys())

    @property
    def active_years(self):
        years = set()
        for key in self.keys:
            years.add(key.year)
        return years

    def add_record(self, key: StatisticalRecordKey, stat: Statistics):
        assert key not in self.keys, "Record Clash"
        assert type(stat) is Statistics, "stat isn't child of Statistics."

        self.records[key] = stat

    def get_record(self, key: StatisticalRecordKey):
        # Check that record exists.
        if key in self.keys:
            return self.records[key]

        # Record not found.
        return None

    def replace_record(self, key: StatisticalRecordKey, stat: Statistics):
        assert key in self.keys, "Key not found"
        self.records[key] = stat

    def add_to_record(self, key: StatisticalRecordKey, stat: Statistics):
        """Return sTrue if the record already exists and a sum has been taken, else False."""
        if key in self.keys:
            self.records[key] += stat
            return True

        self.add_record(key, stat)
        return False

    def get_record_by_year(self, year: int, seperate_by_team = False) -> dict:
        keys = []

        # get keys with specified year.
        for key in self.keys:
            if key.has_year(year):
                keys.append(key)

        # No record
        if len(keys) == 0:
            return Statistics()

        # On eteam
        if len(keys) == 1:
            return self.records[keys[0]]

        # multiple records:
        if seperate_by_team:
            records = {}
            for key in keys:
                team = key.year

                if team in records.keys():
                    records[team] += self.get_record(key)
                    continue

                records[team] = self.get_record(key)
            return records

        # Amalgamate statistics:
        stats = Statistics()
        for key in keys:
            stats += self.get_record(key)
        return stats            

@dataclass
class ForAgainst:
    _for: int = 0
    _againts: int = 0

@dataclass
class TeamStatistics:
    """An object for tracking a teams statistics."""
    record: Record = Record()
    goals: ForAgainst = ForAgainst()
    shots: ForAgainst = ForAgainst()
    possession: ForAgainst = ForAgainst()
    games: int = 0

    @property
    def wins(self):
        return self.record.wins

    @property
    def losses(self):
        return self.record.losses

    @property
    def ties(self):
        return self.record.ties

    def points(self, per_win, per_tie):
        return per_win * self.wins + per_tie * self.ties

@dataclass
class Player(Person):
    """A player in the game."""
    position_id: int
    potential: int
    longevity: int
    fitness: int
    passing: int
    contracts: Dict[int, Contract]
    statistics: StatisticalRecords()
    rights: dict

    def get_statistics(self, year=None, team=None):
        # get lastest year.
        if year == None and len(self.statistics.keys) > 0:
            year = max(self.statistics.active_years)

        # check if year has a statistic
        if year not in self.statistics.active_years:
            return Statistics()

        # return statistic of year.
        return self.statistics.get_record_by_year(year)

    @property
    def active_years(self) -> list:
        return sorted(self.statistics.active_years)

    def get_condition(self) -> str:
        """Return string description of a players condition."""
        if self.fitness >= 90:
            return "A"
        if self.fitness >= 80:
            return "B"
        if self.fitness >= 70:
            return "C"
        if self.fitness >= 60:
            return "D"
        return "F"

@dataclass
class Skater(Player):
    """A player that plays out."""
    shooting: int = 0
    defending: int = 0

    def _calculate_grade(self, val1, val2):
        total = val1 + val2
        if total > 160:
            return 'A'
        if total > 120:
            return 'B'
        if total > 100:
            return 'C'
        if total > 80:
            return 'D'
        return 'F'

    @property
    def overall(self):
        return int((self.shooting + self.passing + self.defending) / 3)

    @property
    def offensive_grade(self) -> str:
        return self._calculate_grade(self.shooting, self.passing)

    @property
    def defensive_grade(self) -> str:
        return self._calculate_grade(self.passing, self.defending)

@dataclass
class Goaltender(Player):
    """A goaltender."""
    stopping: int = 0

    @property
    def overall(self):
        return int(self.stopping * 0.8 + self.passing * 0.2)

@dataclass
class Spending:
    """An object for tracking team spending."""
    start: int
    income: int
    expenses: int
    
    @property
    def balance(self):
        return self.start + self.income - self.expenses

@dataclass
class Roster:
    """A teams roster."""
    active: set
    reserves: set
 
    def __len__(self):
        return len(self.active)

    def add_player_by_id(self, id: int) -> bool:
        if id in self.active or self.reserves:
            return False
        
        self.active.add(id)
        return True

    def add_player_by_object(self, player: Player) -> bool:
        return self.add_player_by_id(player.identifier)

    def get_active(self):
        return set(self.active)

    def get_reserves(self):
        return set(self.reserves)

    def set_roster(self, interable):
        for identifier in interable:
            self.reserves.add(identifier)

@dataclass
class Line:
    forward: int = None
    flex: int = None
    defender: int = None

@dataclass
class Lineup:
    first: Line = Line()
    second: Line = Line()
    goaltender: int = None
    backup: int = None
    bias: float = 0.5

@dataclass
class Organization:
    identifier: int
    name: str
    location: str
    abbreviation: str
    colors: str
    roster: Roster
    statistics: Dict[int, TeamStatistics] = field(default_factory=dict)
    spending: Dict[int, Spending] = field(default_factory=dict)
    lineup: Lineup = Lineup()

    @property
    def players(self) -> list:
        """
        Returns id of all players owned by organizations.
        """
        return set.union(self.roster.get_reserves(), self.roster.get_active())

    @property
    def active(self):
        return self.roster.get_active()

    def set_roster(self, iterator):
        self.roster.set_roster(iterator)

@dataclass
class Game:
    home: int
    away: int
    score: List[int] = field(default_factory=list([0,0]))

@dataclass
class Schedule:
    preseason: List[Game] = field(default_factory=list)
    regular: List[Game] = field(default_factory=list)
    playoff: List[Game] = field(default_factory=list)

@dataclass
class League:
    identifier: int
    name: int
    abreviation: int
    teams: List[int]
    games: Dict[int, Schedule]

    def get_teams(self, teams: Dict[int, Organization]):
        to_return = []
        for team_id in self.teams:
            to_return.append(teams.get(team_id))

        return to_return

    def keys(self):
        return self.teams

    def create_schedule(self, size: int, year: int):
        simple = list(combinations(self.teams, 2)).shuffle()
        schedule = []
        
        # Ensure each team plays on seperate weeks.
        for i in len(simple) / 2:
            combo1 = simple[i*2]
            combo2 = simple[i*2 + 1]
            if combo1[0] in combo2 or combo1[1] in combo2:
                # swap
                pass
            




if __name__ == '__main__':
    league = League(0, "League", "LG", [1, 2, 3, 4], {})
    print(league.create_schedule(1, 2022))
    
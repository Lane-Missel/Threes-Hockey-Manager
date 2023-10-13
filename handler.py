from dataclasses import dataclass, field
from typing import Dict

from entities import League, Player, Organization, Roster

@dataclass
class Regions:
    regions: Dict[int, tuple] = field(default_factory=dict)# [key, (name,abr,relativepopulation)]

    def get(self, key):
        if key in self.keys():
            return self.regions[key]
        else:
            raise KeyError

    @property
    def population(self):
        total = 0
        for key in self.regions.keys():
            total += self.regions[key][2]
        return total

    @property
    def keys(self):
        return set(self.regions.keys())

    @classmethod
    def load_from_csv(cls, path: str):
        with open(path, 'r') as csvfile:
            lines = csvfile.read().split('\n')

        regions = {}

        for line in lines:
            data = line.split(',')
            regions[int(data[0])] = tuple([data[1], data[2], int(data[3])])

        return Regions(regions)

@dataclass
class Players:
    players: Dict[int, Player] = field(default_factory=dict)

    @classmethod
    def load_from_exec(string: str) -> bool:
        """Loads a Players object from an excecutable python string."""
        try:
            players = exec(string)
        except Exception as error:
            return None

        return Players(players)

    @classmethod
    def init_from_csv(cls, path: str):
        """Loads a Players object from a csv file with default attributes."""
        with open(path, 'r') as csvfile:
            lines = csvfile.readlines()

        organizations = {}

        for line in lines:
            data = line.strip().split('\n')
            organizations[data[0]] = Organization(data[0], data[2], data[1], data[3], data[4])

@dataclass
class Organizations:
    """Loads an Organizations object from an excecutable python string."""
    organizations: Dict[int, Organization] = field(default_factory=dict)

    @classmethod
    def load_from_exec(cls, string: str):
        try:
            organizations = exec(string)
        except Exception:
            return None

        return Organizations(organizations)

    @classmethod
    def load_from_csv(cls, path: str):
        with open(path, 'r') as csvfile:
            lines = csvfile.read().split('\n')

        organizations = {}

        for line in lines:
            data = line.split(",")
            x = set()
            y = set()
            roster = Roster(x, y)
            organizations[int(data[0])] = Organization(int(data[0]), data[2], data[1], data[3], data[4], roster, None)
 
        return Organizations(organizations)

    def ids(self):
        return self.organizations.keys()

    def get(self, team_id):
        if team_id in self.ids():
            return self.organizations[team_id]
        print("{} not in {}".format(team_id, self.ids()))

@dataclass
class Leagues:
    """Loads a Leagues objet from an excecuatable pthon string."""
    leagues: Dict[int, League] = field(default_factory=dict)

    @classmethod
    def load_from_exec(cls, string:str):
        try:
            leagues = exec(string)
        except Exception:
            return None
        
        return Leagues(leagues)

    @classmethod
    def load_from_csv(cls, path: str):
        with open(path, 'r') as csvfile:
            lines = csvfile.read().split('\n')
        leagues = {}

        for line in lines:
            data = line.split(',')
            # get teams.
            teams = []
            for team_id in data[3].split('.'):
                teams.append(int(team_id))

            leagues[int(data[0])] = League(int(data[0]), data[1], data[2], teams, {})
        return leagues

    def ids(self):
        return self.leagues.keys()

    def get(self, league_id: int):
        return self.leagues[league_id]

@dataclass
class Other:
    other: dict = field(default_factory=dict)
    year: int = 0
    year_offset: int = 2022

    @classmethod
    def load_from_exec(cls, string: str):
        """Returns Other object instantiated from a string interpreted as a python commmand."""
        try:
            other = exec(string)
        except Exception:
            return None

        return Other(other)

    @classmethod
    def new(cls):
        other = {}
        other['week'] = None
        other['games_per_team'] = {1: 4, 2: 3, 3: 2}
        return Other(other)

    def get_week(self):
        if 'week' in self.other.keys():
            value = self.other['week']
            if value == 'None' or value == None:
                return None

            return int(value)

    def started(self):
        return self.get_week() is not None

    @property
    def current_year(self):
        return self.year + self.year_offset

def load_names(path, amount: int, start: int = 0) -> list:
    names = []
    with open(path, 'r') as datfile:
        for i in range(start):
            datfile.readline()

        for i in range(amount):
            names.append(datfile.readline().strip())

    return names
                

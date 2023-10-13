"""
Lane Missel

Objects and function for managing the applications data.
"""


import os.path

from entities import *
from handler import Players, Leagues, Organizations, Regions, Other, load_names
from mechanics import create_players

class Data:
    """An object storing the applications data."""
    def __init__(self, players: dict = None, organizations: dict = None, leagues: dict = None, other: dict = None):
        self.players = players
        self.organizations = organizations
        self.leagues = leagues
        self.other = other

    def __repr__(self):
        return "Data({},{},{},{})".format(self.players, self.organizations, self.leagues, self.other)

    @classmethod
    def load_from_files(cls, players_path: str, organizations_path: str, leagues_path: str, other_path: str):
        """Returns an object instantiated with data from provided files."""
        # get excecuatable strings from data files.
        with open(players_path, 'r') as datafile:
            players_executable = datafile.read()
        with open(organizations_path, 'r') as datafile:
            organizations_executable = datafile.read()
        with open(leagues_path, 'r') as datafile:
            leagues_executable = datafile.read()
        with open(other_path, 'r') as datafile:
            other_executable = datafile.read()

        # load dictionaries from strings.
        players = Players.load_from_exec(players_executable)
        organizations = Organizations.load_from_exec(organizations_executable)
        leagues = Leagues.load_from_exec(leagues_executable)
        other = Other.load_from_exec(other_executable)

        return Data(players, organizations, leagues, other)

    @classmethod
    def create(cls):
        """Returns an object with data loaded from default files."""
        names = load_names("data/names.dat", 500)
        regions = Regions.load_from_csv("data/regions.csv")
        players = create_players(names, regions)
        organizations = Organizations.load_from_csv("data/organizations.csv")
        leagues = Leagues.load_from_csv("data/leagues.csv")
        other = Other.new()

        return Data(players, organizations, leagues, other)

    @classmethod
    def init_from_file(cls, path: str):
        """Returns an objected with data loaded from a file."""
        """Loads application from excecutable text file."""
        with open(path, "r") as datafile:
            text = datafile.read()

        exec("data = {}".format(text), globals())
        return globals()['data']

    def load_from_file(self, path: str):
        """Sets data of object from provided file."""
        temp_app = Data.init_from_file(path)
        self.players = temp_app.players
        self.organizations = temp_app.organizations
        self.leagues = temp_app.leagues

    def save_to_file(self, path: str):
        """Writes representation of pbject to file."""
        """Saves python object to excecutable text file."""
        with open(path, 'w') as savefile:
            savefile.write(repr(self))

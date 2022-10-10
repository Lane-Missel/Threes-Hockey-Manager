#from email.mime import base
from random import randint, sample
from typing import List
from math import sqrt

from handler import load_names, Regions
from entities import Skater, Goaltender, Player, Statistics, StatisticalRecords, StatisticalRecordKey
from engine import select_uniform_steps

class FreeAgency:
    def __init__(self, length: int = 10, decision_time: int = 3, offers_per_period: int = 3):
        self.length = length
        self.decision_time = decision_time
        self.offers_per_period = offers_per_period

    def get_unsigned(self):
        pass

def age_player(player: Player):
    def _ensure_bounds(value, min = 0, max = 100):
        if value < min:
            return min
        elif value > max:
            return max
        return value
    
    age = player.age
    modifier = 1

    if age < 18:
        ceiling = 5 + player.potential
    elif age < 21:
        ceiling = 2 + player.potential
    elif age < 25:
        ceiling = 1 + player.potential
    elif age < 30:
        ceiling = player.potential
    elif age < 40:
        ceiling = 5 - player.longevity
        modifier = -1
    else:
        ceiling = 10 - player.longevity
        modifier = -1

    player.passing = _ensure_bounds(player.passing + randint(0, ceiling) * modifier)

    if type(player) == Goaltender:
        if modifier < 0 and age < 45:
            ceiling = int(ceiling / 2)

        player.stopping = _ensure_bounds(player.stopping + randint(0, ceiling) * modifier)

    elif type(player) == Skater:
        player.shooting = _ensure_bounds(player.shooting + randint(0, ceiling) * modifier)
        player.defending = _ensure_bounds(player.defending + randint(0, ceiling) * modifier)
        
    player.age += 1

def create_players(names: list, regions: Regions):
    players = dict()
    region_populations = [regions.regions[x][2] for x in sorted(list(regions.keys))]
    identifier = 0

    for i in range(24):
        for _ in range(20):
            identifier += 1
            region = select_uniform_steps(region_populations) + 1
            position = select_uniform_steps([2, 3, 5])
            potential = randint(1,3)
            longevity = randint(1,3)
            first, last = names.pop(0).split()
            passing = randint(10,50)

            if position in (1,2):
                shooting = randint(10,50)
                defending = randint(10,50)
                stat = Statistics.randomized()
                players[identifier] = Skater(identifier, first, last, region, 16, "", position, potential, longevity, 100, passing, {}, StatisticalRecords({StatisticalRecordKey(2000, None, None): Statistics.randomized()}), {}, shooting, defending)       
                continue

            stopping = randint(20, 50)
            players[identifier] = Goaltender(identifier, first, last, region, 16, "", position, potential, longevity, 100, passing, {}, StatisticalRecords(), {}, stopping)

        for key in players.keys():
            player = players[key]
            age_player(player)

    return players

def generate_random_rosters(players, num_teams: int = 12, group_num: int = 4) -> list:
    goalies = [players[x] for x in players.keys() if players[x].position_id == 0]
    goalies.sort(key = lambda x: x.overall, reverse = True)
    defenders = [players[x] for x in players.keys() if players[x].position_id == 1]
    defenders.sort(key = lambda x: x.overall, reverse = True)
    forwards = [players[x] for x in players.keys() if players[x].position_id == 2]
    forwards.sort(key = lambda x: x.overall, reverse = True)

    teams = []
    for _ in range(num_teams):
        teams.append([])

    # loop through groups.
    for i in range(int(num_teams / group_num)):
        # loop through draft rounds.
        padding = i * group_num
        # Goalies
        for ii in range(2):
            order = sample([padding + x for x in range(group_num)], 4)

            for team_index in order:
                teams[team_index].append(goalies.pop(0).identifier)

        # Defenders
        for ii in range(3):
            # loop through draft rounds.
            padding = i * group_num
            for ii in range(2):
                order = sample([padding + x for x in range(group_num)], 4)

                for team_index in order:
                    teams[team_index].append(defenders.pop(0).identifier)

        # Forwards
        for ii in range(5):
            # loop through draft rounds.
            padding = i * group_num
            for ii in range(2):
                order = sample([padding + x for x in range(group_num)], 4)

                for team_index in order:
                    teams[team_index].append(forwards.pop(0).identifier)

    return teams

def get_players_age_restriction(players: List[Player], maximum: int, minimum: int = 0):
    """minimum and maximumns are inclusive."""
    eligible = []

    for player in players:
        if minimum <= player.age and player.age <= maximum:
            eligible.append(player)

    return eligible

def get_attendance(capacity: int, point_percentage: float):
    return int(sqrt(point_percentage) * capacity)

def get_revenue(attendance: int, ticket_price: float):
    return attendance * ticket_price

def calculate_ticket_price(base_price: float, increase_per_win: float, wins: int):
    return round(base_price + wins * increase_per_win, 2)

def player_performance_score(plus_minus: int, goals: int, assists: int, team_goals_for: int, league_average_goals: float):
    return round(plus_minus + (league_average_goals * goals / team_goals_for) + (goals + assists), 1)

if __name__ == '__main__':
    names = load_names("data/names.dat", 600)
    regions = Regions.load_from_csv("data/regions.csv")

    players = create_players(names, regions)

    skaters = []
    goaltenders = []
    all_p = []

    for key in players.keys():
        player = players[key]

        if type(player) == Goaltender:
            goaltenders.append(player)
        else:
            skaters.append(player)

        all_p.append(player)

    all_p.sort(key = lambda x: x.overall, reverse=True)
    #skaters.sort(key = lambda x: x.overall, reverse = True)
    #goal

    teams = generate_random_rosters(players)

    for team in teams:
        print("\n")

        overall = 0
        team.sort(key = lambda x: x.overall, reverse = True)

        for player in team:
            print("{:3} {:20} {:1}".format(player.overall, player.name, player.position_id))
            overall += player.overall

        print("Team Overall: {}".format(overall))

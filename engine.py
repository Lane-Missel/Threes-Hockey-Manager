"""
Lane Missel

The simulation engine for the application.
"""


from dataclasses import dataclass
from random import random
from typing import List


class Player:
    def __init__(self, identifier, energy, passing):
        self.identifier = identifier
        self.energy = energy
        self._passing = passing

    @property
    def passing(self):
        return self._correct_for_energy(self._passing)

    def _correct_for_energy(self, value):
        return int(value / (self.energy / 100))

class Skater(Player):
    def __init__(self, identifier, passing, shooting, defending, energy = 100):
        self.identifier = identifier
        self._passing = passing
        self._shooting = shooting
        self._defending = defending
        self.energy = energy

    @property
    def shooting(self):
        return self._correct_for_energy(self._shooting)

    @property
    def defending(self):
        return self._correct_for_energy(self._defending)

class Goaltender(Player):
    def __init__(self, identifier, passing, stopping, energy):
        self.identifier = identifier
        self._passing = passing
        self._stopping = stopping
        self.ebergy = energy

    @property
    def stopping(self):
        return self._correct_for_energy(self._stopping)

@dataclass
class GameStatistics:
    seconds_played: int = 0
    assists: int = 0

@dataclass
class SkaterGameStatistics(GameStatistics):
    shots: int = 0
    goals: int = 0
    assists: int = 0
    plus: int = 0
    minus: int = 0

@dataclass
class GoaltenderGameStatistics(GameStatistics):
    goals_against: int = 0
    shots_against: int = 0

@dataclass
class Players:
    forward: Skater = None
    flex: Skater = None
    defender: Skater = None
    goaltender: Goaltender = None

    def __iter__(self):
        self._index = 0
        return

    def __next__(self) -> Player:
        if self._index > 3:
            delattr(self, "_index")
            raise StopIteration

        self._index += 1

        return self[self._index]

    def __getitem___(self, i) -> Player:
        if i == 0:
            return self.forward
        elif i == 1:
            return self.flex
        elif i == 2:
            return self.defender
        elif i == 3:
            return self.goaltender
        else:
            raise IndexError

    @property
    def possession(self):
        return self.defending + self.passing

    @property
    def defending(self):
        defending = 0
        player: Skater

        for player in self:
            if type(player) is Goaltender:
                break
            defending += player.defending
        
        return defending

    @property
    def passing(self):
        passing = 0
        player: Skater

        for player in self:
            passing += player.passing

        return passing

    @property
    def skater_ids(self):
        """Return set of identifiers of skaters."""
        identifiers = set()
        player: Skater

        for player in self:
            if type(player) is Skater:
                identifiers.add(player.identifier)

        return identifiers

@dataclass
class Lineup:
    first: Players
    second: Players
    goaltender: Goaltender
    backup: Goaltender = None
    bias: float = 0.5

    def swap_goalie(self):
        self.goaltender, self.backup = self.backup, self.goaltender

    def get_line(self):
        if random() < self.bias:
            forward = self.first.forward
            flex = self.first.flex
            defender = self.first.flex
        else:
            forward = self.second.forward
            flex = self.second.flex
            defender = self.second.defender

        return Players(forward, flex, defender, self.goaltender)

@dataclass(frozen=True)
class Event:
    time: int
    length: int

@dataclass(frozen=True)
class Possession(Event):
    team: int

@dataclass(frozen=True)
class Shot(Possession):
    shooter: int
    goaltender: int

@dataclass(frozen=True)
class Goal(Shot):
    passer: int
    plus: set
    minus: set

@dataclass
class Score:
    home: int
    away: int
    
    @property
    def tied(self):
        return self.home == self.away

    def update(self, events: List[Event]):
        for event in events:
            if type(event) != Goal:
                continue
            if event.team == 0:
                self.home += 1
                continue
            self.away += 1

def select_uniform_steps(values: List[int]) -> int:
    reference = values[0]
    key = random() * sum(values)

    for i in range(len(values)):
        if key < reference:
            return i
        
        reference += values[i + 1]

def simulate_play(home: Players, away: Players, time: int = 0) -> Event:
    attacking: Players
    defending: Players

    # Decide which team has possession (chance to score).
    if select_uniform_steps(home.possession, away.possession) == 0:
        attacking = home
        defending = away
    else:
        attacking = away
        defending = home

    team = home == defending

    # Get the player passing the puck.
    passer_index = select_uniform_steps([attacking.forward.passing, attacking.flex.passing, attacking.defender.passing, int(attacking.goaltender.passing * 0.5)])
    passer: Player = attacking[passer_index]

    # Try passing the puck.
    if select_uniform_steps([passer.passing, defending.defending]) == 1:
        return Possession(time, 10, team)

    # Get the player shooting the puck.
    shooter_indices = [0,1,2]
    if passer_index in shooter_indices: shooter_indices.remove(passer_index)
    shooters: List[Skater] = []
    shooter_skills: List[int] = []
    for index in shooter_indices:
        player: Skater = attacking[index]
        shooters.append(player)
        shooter_skills.append(player.shooting)
    shooter_index = select_uniform_steps(shooter_skills)
    shooter: Skater = shooters[shooter_index]

    # Player takes shot.
    if select_uniform_steps([shooter, defending.goaltender.stopping + 300]) == 0:
        return Goal(time, 10, team, shooter.identifier, defending.goaltender.identifier, passer.identifier, attacking.skater_ids, defending.shooting_ids)

    return Shot(time, 10, team, shooter.identifier, defending.goaltender.identifier)

def simulate_period(home: Lineup, away: Lineup, length: int, shift_length: int, sudden_death = False):
    time = 0
    events = list()
    duration = 10

    # Simulate through the period.
    while time < length:
        home_players = home.get_line()
        away_players = away.get_line()
        events.append(simulate_play(home_players, away_players, time))
        time += duration

        # Exit if goal scored in sudden death period.
        if sudden_death and type(events[-1]) == Goal:
            break

    return events

def simulate_game(home: Lineup, away:Lineup, period_length: int, num_periods: int, shift_length: int = 10, over_time = False):
    events = {}
    score = Score()

    for period in range(num_periods):
        events[period] = simulate_period(home, away, period_length, shift_length, over_time)
        score.update(events[period])

    while over_time and score.tied:
        period += 1
        events[period] = simulate_period(home, away, period_length, shift_length, True)
        score.update(events[period])

    return events, score

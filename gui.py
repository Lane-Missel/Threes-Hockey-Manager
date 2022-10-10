import tkinter as tk
import os.path

from data import Data
from entities import *
from mechanics import generate_random_rosters

FONT = "TkFixedFont"

class Interface:
    def __init__(self, data: Data = None):
        self.data = data
        self.master = tk.Tk()
        self.master.title("Micro Threes Manager")
        self.master.minsize(500, 300)
        self.path = None
        self.history = []   # Queue
        self.history_location = 0
        # set history bar
        self.frame_history = tk.Frame(self.master)
        tk.Button(self.frame_history, text="<-", command=self.last_page).pack(side="left")
        self.title = tk.Label(self.frame_history, text='', width=30)
        self.title.pack(side="left")
        tk.Button(self.frame_history, text="->", command=self.next_page).pack(side="left")

        self.frame_history.pack()
        self.content = tk.Frame(self.master)

        # Initial save screen to window.
        self.start()

    def last_page(self):
        if self.history_location > 0:
            self.history_location -= 1
            page = self.history[self.history_location]
            page()

    def next_page(self):
        if self.history_location < len(self.history) - 1:
            self.history_location += 1
            page = self.history[self.history_location]
            page()

    def select_page(self, function):
        self.history_location += 1
        self.history = self.history[0:self.history_location]
        self.history.append(function)
        function()

    def clear(self):
        """Clears the window."""
        for widget in self.content.winfo_children():
            widget.destroy()

    def display_statistic(self, statistic):
        pass

    def display_player(self, player_id):
        """
        Opens new frame to display player history
        """
        # TODO
        # Add to page queueu

        player: Skater
        player = self.data.players[player_id]

        self.clear()
        frame_player = tk.Frame(self.content, width = 100)

        # Display basic information and achgeivments
        tk.Label(frame_player, text=player.name, font="TkFixedFont").pack(side="top", anchor="w")
        tk.Label(frame_player, text=player.age, font="TkFixedFont").pack(side="top", anchor="w")

        # Statistics Header
        frame_stat_header = tk.Frame(frame_player, width = 100)
        tk.Label(frame_stat_header, text="YEAR", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="TEAM", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="LEAGUE", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="GP", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="G", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="A", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="P", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="+/-", font="TkFixedFont").pack(side="left")
        tk.Label(frame_stat_header, text="").pack(side="left")
        frame_stat_header.pack(side="top", anchor="w")

        # Display Stats History
        for year in player.active_years:
            stat = player.get_statistics(year)
            frame_stat = tk.Frame(frame_player, width = 100)

            tk.Label(frame_stat, text=year, font="TkFixedFont").pack(side="left")
            tk.Label(frame_stat, text="TOT ", font="TkFixedFont").pack(side="left")
            tk.Label(frame_stat, text="ALL   ", font="TkFixedFont").pack(side="left")

            tk.Label(frame_stat, text="{}".format(stat.games_played), font="TkFixedFont").pack(side="left")
            tk.Label(frame_stat, text="{}".format(stat.goals), font="TkFixedFont").pack(side="left")
            tk.Label(frame_stat, text="{}".format(stat.assists), font="TkFixedFont").pack(side="left")
            tk.Label(frame_stat, text="{}".format(stat.points), font="TkFixedFont").pack(side="left")
            tk.Label(frame_stat, text="{}".format(stat.plus_minus), font="TkFixedFont").pack(side="left")

            frame_stat.pack(side="top", anchor="w")

        # Display Contract History
        frame_player.pack()

    def display_skater_frame(self, player_id):
        """
        Display's inline Skater information.
        """
        player: Skater
        player = self.data.players[player_id]

        # Display Player Grades
        frame_player = tk.Frame(self.content, width = 50)
        tk.Label(frame_player, text="{:20}".format(player.name), font="TkFixedFont", width=25).pack(side="left", anchor="w")
        tk.Label(frame_player, text=player.get_condition(), font="TkFixedFont", width=2).pack(side="left", anchor="w")
        tk.Label(frame_player, text=player.offensive_grade, font="TkFixedFont", width=2).pack(side="left", anchor="w")
        tk.Label(frame_player, text=player.defensive_grade, font="TkFixedFont", width=2).pack(side="left", anchor="w")

        # Display Player Stats
        statistic = player.get_statistics()
        tk.Label(frame_player, text=statistic.goals, font="TkFixedFont", width=2).pack(side="left", anchor="w")
        tk.Label(frame_player, text=statistic.assists, font="TkFixedFont", width=2).pack(side="left", anchor="w")
        tk.Label(frame_player, text=statistic.points, font="TkFixedFont", width=3).pack(side="left", anchor="w")

        tk.Button(frame_player, text="View", font="TkFixedFont", width=5, command=lambda x = player_id: self.select_page(lambda: self.display_player(x))).pack(side="left", anchor="w")

        frame_player.pack(side="top", anchor="w")

    def display_goalie_frame(self, goalie_id):
        """
        Display's inline Goaltender information.
        """
        goalie: Goaltender
        goalie = self.data.players[goalie_id]

        frame_goalie = tk.Frame(self.content, width = 50)
        tk.Label(frame_goalie, text=goalie.name, font="TkFixedFont", width=20).pack(side="left", anchor="w")

        frame_goalie.pack(side="top", anchor="w")

    def display_team(self, team_id):
        """
        Dipslay players statistics of selected team.
        """
        self.clear()
        team = self.data.organizations.get(team_id)
        tk.Label(self.content, text="{} {}".format(team.location, team.name)).pack()
        frame = tk.Frame(self.content)

        tk.Label(self.content, text="{:20} {:2} {:2} {:2} {:2} {:2} {:3}".format("Name","F","O","D", "G", "A", "Pts"), font="TkFixedFont").pack()

        # display players of team_frame
        goalies = []
        #players = [x for x in self.data.organizations.get(team_id).players if self.data.players.get(x).position_id == 2]
        #players.sort(key = lambda x: x.get_stat)
        for player_id in self.data.organizations.get(team_id).players:
            if self.data.players.get(player_id).position_id == 2:
                self.display_skater_frame(player_id)
            else:
                goalies.append(player_id)

        # display goalies
        tk.Label(self.content, text="{:20} {:2}".format("Name", "O"), font="TkFixedFont").pack()

        for goalie_id in goalies:
            self.display_goalie_frame(goalie_id)

        frame.pack()

    def display_league(self, league_id):
        # Update window.
        self.clear()
        frame = tk.Frame(self.content)

        league = self.data.leagues.get(league_id)
        teams = league.get_teams(self.data.organizations)

        for team in teams:
            team_frame = tk.Frame(frame)
            tk.Label(team_frame, width=40, text="{} {}".format(team.location, team.name), font="TkFixedFont").pack(side="left", anchor="w")
            tk.Button(team_frame, text="View", font="TkFixedFont", command=lambda x = team.identifier: self.select_page(lambda: self.display_team(x))).pack(side="left", anchor="w")
            team_frame.pack(side="top", anchor="w")

        frame.pack()

    def display_standings(self, league_id: int):
        pass

    def display_leaders(self, league_id: int):
        pass

    def display_league_menu(self, league_id: int):
        self.clear()
        frame = tk.Frame(self.content)

        tk.Button(frame, text="View Teams", font=FONT, command=lambda: self.select_page(lambda: self.display_league(league_id))).pack(side="top")
        tk.Button(frame, text="View Standings", font=FONT, command=lambda: self.select_page(lambda: self.display_standings(league_id))).pack(side="top")
        tk.Button(frame, text="View Leaders", font=FONT, command=lambda: self.select_page(lambda: self.display_leaders(league_id))).pack(side="top")
        frame.pack()

    def display_leagues(self):
        self.clear()
        frame = tk.Frame(self.content)
        buttons = []

        for league_id in self.data.leagues.keys():
            league = self.data.leagues[league_id]
            buttons.append(tk.Button(frame, text=league.name, font="TkFixedFont", command=lambda x = league_id: self.select_page(lambda: self.display_league_menu(x))))
            buttons[-1].pack(side="top")
        frame.pack()

    def sim_week(self):
        if self.data.other.get_week() == None:
            # Make schedule. / update year
            pass

        else:
            pass



    def edit_team(self):
        pass

    def home(self):
        """
        Initial screen the user see's after loading a saved game.
        """
        self.clear()
        frame = tk.Frame(self.content)
        tk.Button(frame, text="Simulate Week", font=FONT, command=lambda: self.select_page(self.sim_week)).pack(side="top")
        tk.Button(frame, text="View Leagues", font=FONT, command=lambda: self.select_page(self.display_leagues)).pack(side="top")
        tk.Button(frame, text="Edit Team", font=FONT, command=lambda: self.select_page(self.edit_team)).pack(side="top")
        frame.pack()

    def load(self, number: int):
        self.path = "data/save{}.dat".format(number)
        if os.path.exists(self.path):
            self.data = Data.init_from_file(self.path)
        else:
            self.data = Data.create()
            # random rosters.
            rosters = generate_random_rosters(self.data.players, 12, 6)

            # assign rosters to teams:
            for i in range(len(rosters)):
                target_organization = self.data.organizations.get(i + 1)
                target_organization.set_roster(rosters[i])
                #self.data.organizations.get(i + 1).set_roster(rosters[i])
        
        #self.display_leagues() [old title screen]
        self.select_page(self.home)

    def get_data(self):
        tk.Button(self.content, text="Save 1", command=lambda: self.load(1)).pack(side="top", anchor="n")
        tk.Button(self.content, text="Save 2", command=lambda: self.load(2)).pack(side="top", anchor="n")
        tk.Button(self.content, text="Save 3", command=lambda: self.load(3)).pack(side="top", anchor="n")
        self.content.pack()

    def save_data(self):
        with open(self.path, "w") as datafile:
            datafile.write(repr(self.data))

    def start(self):
        if self.data is None:
            self.get_data()

    def welcome(self):
        frame = tk.Frame(self.master)
        tk.Label(text = "Welcome!").pack()
        frame.pack()

    def run(self):
        self.master.mainloop()
        self.save_data()
        
if __name__ == "__main__":
    app = Interface()
    app.run()
        

        
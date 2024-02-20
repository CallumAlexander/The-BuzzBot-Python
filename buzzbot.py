import datetime
import random
import string
import numpy as np
import warnings
import utils

from DistanceMatrixAPI import DistanceMatrixInterface, LocationManager
from credentials import get_DistanceMatrix_credentials


class TransportMatrix:

    def __init__(self, location_names, modes_of_transport):
        self.num_locations = len(location_names)
        self.num_modes = len(modes_of_transport)

        self.locations = {name: index for index, name in enumerate(location_names)}
        self.modes = {mode: index for index, mode in enumerate(modes_of_transport)}

        self.matrix = np.full((self.num_locations, self.num_locations, self.num_modes), np.nan)


class Fixture:

    def __init__(self, home_: str, away_: str, start_time_, umpires_required_: int, location_: str):
        assert 0 <= umpires_required_ <= 2
        self.home = home_
        self.away = away_
        self.start_time = start_time_
        self.end_time = self.start_time + datetime.timedelta(hours=1.5)  # Length of a hockey match is 1.5 hours
        self.location = location_
        self.covering_team = ""
        self.umpires_required = umpires_required_

    def overlaps_with(self, other_fixture):
        # Return True if the two fixtures overlap
        return self.start_time < other_fixture.end_time and self.end_time > other_fixture.start_time


teams = ["1s", "2s", "3s", "4s", "5s", "6s", "7s"]
# matches = [Fixture(teams[i], teams[j]) for i in range(len(teams)) for j in range(i + 1, len(teams))]


# Random fixtures, only home assignments, purely for testing purposes
number_of_matches = 7
matches = []
playing_teams = random.sample(teams, number_of_matches)
lm = LocationManager()
for i in range(0, number_of_matches):
    team1 = playing_teams[i]
    random_opponent1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))  # Random opponent name
    random_start_time, random_end_time = 11, 18  # 8AM & 8PM
    start_hour = random.randint(random_start_time, random_end_time)
    start_time = datetime.datetime.now().replace(hour=start_hour, minute=0, second=0, microsecond=0)
    umpires_required = random.randint(0, 2)
    location = random.choice(list(lm.get_all_location_names()))
    matches.append(Fixture(team1, random_opponent1, start_time, umpires_required, location))

umpiring_count = {team: 0 for team in teams}


class BuzzBot:
    def __init__(self, matches_, teams_, umpiring_count_):
        self.matches = matches_
        self.teams = teams_
        self.umpiring_count = umpiring_count_
        self.location_manager = LocationManager()
        self.api = DistanceMatrixInterface(get_DistanceMatrix_credentials())
        self.bootstrap_api()
        self.travel_time_matrix = self.api.get_travel_time_matrix()

    def extract_location_names(self) -> [str]:
        return [m.location for m in self.matches]

    def extract_location_coordinates(self, location_names_) -> [(float, float)]:
        coords = []
        for name in location_names_:
            coord = self.location_manager.get_location(name)
            coords.append(coord)
        return coords

    def bootstrap_api(self):
        matchday_locations = self.extract_location_names()
        matchday_locations_dict = self.location_manager.return_matchday_location_subdictionary(matchday_locations)
        self.api.import_from_LocationManager(matchday_locations_dict)


    def assign_covering_teams(self) -> None:
        """
        High level function called when all fixtures are to be assigned an umpire. Each `match` instance in the list
        `matches`, the assigned umpire is updated.
        :return: None
        """
        for match in self.matches:
            if match.umpires_required == 0:
                match.covering_team = "COVERED"
                continue

            selected_team = self.find_umpiring_team(match)
            match.covering_team = selected_team
            if selected_team != "No available umpire":
                self.umpiring_count[selected_team] += match.umpires_required

    def find_umpiring_team(self, match: Fixture) -> str:
        """
        Finds the best team to cover a match based on defined criteria
        :param match: Fixture object
        :return: String name of the best team to cover a match
        """
        eligible_teams = self.get_eligible_teams(match)
        if not eligible_teams:
            return "No available umpire"
        # Greedy heuristic that takes the team with the least assignments first, then the strongest team.
        return sorted(eligible_teams, key=lambda x: self.umpiring_count[x])[0]

    def get_eligible_teams(self, match: Fixture) -> [str]:
        """
        Computes the list of teams eligible for covering a match
        :param match: Fixture object representing the match
        :return: List of strings representing the names of eligible teams
        """
        teams_playing_same_day = self.get_teams_playing_same_day(match)
        eligible_playing_teams = [team for team in teams_playing_same_day if self.is_eligible(team, match)]

        if eligible_playing_teams:
            return eligible_playing_teams
        else:
            return [team for team in self.teams if team not in teams_playing_same_day and self.is_eligible(team, match)]

    def get_teams_playing_same_day(self, match: Fixture) -> [str]:
        """
        # TODO - this could probably be independent of argument match (almost certainly)
        Computes the subset of teams playing that don't include the teams playing in the input match
        :param match: Fixture object representing the match
        :return: List of strings representing the names of teams playing
        """
        teams_playing_same_day = {m.home for m in self.matches if m != match and m.home in self.teams}
        teams_playing_same_day.update({m.away for m in self.matches if m != match and m.away in self.teams})
        return teams_playing_same_day

    def is_eligible(self, team: str, match: Fixture) -> bool:
        """

        :param team: Name as a string representing the team to check if eligible to umpire
        :param match: Fixture object representing the match to check eligibility against.
        :return: True if the team can cover umpiring, False if not
        """
        if team in [match.home, match.away]:
            return False
        for other_match in self.matches:
            if team in [other_match.home, other_match.away] and match.overlaps_with(other_match):
                return False

        for other_match in self.matches:
            if team in [other_match.home, other_match.away]:
                origin_cords = self.extract_location_coordinates([other_match.location])[0]
                dest_cords = self.extract_location_coordinates([match.location])[0]
                travel_time = self.get_travel_time(origin_cords, dest_cords)

                travel_time_delta = datetime.timedelta(minutes=travel_time)
                time_diff = abs(match.start_time - other_match.end_time)
                print(f"time diff {time_diff}, travel time delta {travel_time_delta}")
                if time_diff < travel_time_delta:
                    return False
        return True

    def get_travel_time(self, origin, destination):
        origin = ",".join([str(x) for x in origin])
        destination = ",".join(str(x) for x in destination)
        travel_time = self.travel_time_matrix.at[origin, destination]
        return travel_time // 60  # converts to minutes

    def get_total_umpires_supplied(self):
        return sum(self.umpiring_count.values())


if __name__ == "__main__":

    print(f"TheBuzzBot says, \"{utils.get_opening_tagline()}\"\n")

    # Usage
    buzzbot = BuzzBot(matches, teams, umpiring_count)
    buzzbot.assign_covering_teams()
    for match in buzzbot.matches:
        print(
            f"{match.home} vs {match.away}, PB: {match.start_time}, END: {match.end_time} @ {match.location} - Umpiring "
            f"Team: {match.covering_team} providing {match.umpires_required} umpire(s)")

    print(f"TOTAL UMPIRES SUPPLIED: {buzzbot.get_total_umpires_supplied()}")

    warnings.warn("Always doublecheck and cross reference umpiring assignments given by The Buzzbot")
    print(buzzbot.travel_time_matrix)

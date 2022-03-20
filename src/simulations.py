# -*- coding: utf-8 -*-
# 
# Intelligence Artificielle & Jeux
# Sorbonne Université
#
# Ben Kabongo
# Mars 2022
# 

import math
import numpy as np
import matplotlib.pyplot as plt
import random
import sys
import strategies
from search.grid2D import ProblemeGrid2D
from search import probleme

plt.style.use('seaborn-whitegrid')

# verbose if verbose is true
_VERBOSE = True
def verbose(*args, **kwargs):
    if _VERBOSE:
        print(*args, **kwargs)


def play(nb_lines=20,
        nb_cols=20,
        nb_players=10,
        nb_goals=5,
        players_teams=[],
        players_init_positions=[],
        goals_init_positions=[],
        wall_positions=[],
        nb_days=10, 
        dist_min=12,
        strategy_team1=strategies.RandomStrategy,
        strategy_team2=strategies.RandomStrategy):

    # teams
    team1_ids = []
    team2_ids = []
    for i, t in enumerate(players_teams):
        if t == 1:
            team1_ids.append(i)
        else:
            team2_ids.append(i)
    
    # liste des positions légales
    legals_positions = []
    for row in range(nb_lines):
        for col in range(nb_cols):
            if (row, col) not in wall_positions:
                legals_positions.append((row, col))

    # initialisation des strategies
    strategy_team1_instance = strategy_team1(1, team1_ids, nb_goals, dist_min)
    strategy_team2_instance = strategy_team2(2, team2_ids, nb_goals, dist_min)

    # jour de propagandes
    
    players_current_positions = players_init_positions
    goals_current_positions = goals_init_positions
    
    for day in range(nb_days):
        verbose(f"Jour {day}")

        # calculs des distances
        team1_positions = {}
        for i in team1_ids:
            team1_positions[i] = players_current_positions[i]
        team2_positions = {}
        for i in team2_ids:
            team2_positions[i] = players_current_positions[i]
        
        strategy_team1_instance.update_distances(team1_positions, goals_current_positions)
        strategy_team2_instance.update_distances(team2_positions, goals_current_positions)

        # génération des  des objectifs en fonction des stratégies
        goals_id_team1, distribution_team1 = strategy_team1_instance.generate()
        goals_id_team2, distribution_team2 = strategy_team2_instance.generate()

        goal_id_by_player = dict()
        goal_id_by_player.update(goals_id_team1)
        goal_id_by_player.update(goals_id_team2)
        goals = {j: goals_current_positions[i] for j, i in goal_id_by_player.items()}
        
        # votes
        votes = [0] * nb_goals
        for i in range(nb_goals):
            if distribution_team1[i] > distribution_team2[i]:
                votes[i] = 1
            elif distribution_team1[i] < distribution_team2[i]:
                votes[i] = 2

        # sauvegarde des votes et des scores du jour
        strategy_team1_instance.save_day_results(votes)
        strategy_team2_instance.save_day_results(votes)

        # Calcul de A* pour chaque joueur
        paths = {}
        for i in goals.keys():
            g = np.ones((nb_lines,nb_cols),dtype=bool)
            for w in wall_positions:
                g[w] = False
            _stdout = sys.__stdout__
            sys.stdout = None
            p = ProblemeGrid2D(players_init_positions[i], goals[i], g, 'manhattan')
            path = probleme.astar(p)
            sys.stdout = _stdout
            paths[i] = path
                    
        # changement des positions des cibles
        goals_current_positions = random.sample(legals_positions, nb_goals)

    # plot
    days = np.arange(0, nb_days+1)

    plt.title(f"Scores")
    plt.plot(days, 
            strategy_team1_instance.cumulative_score_memory, 
            label=strategy_team1_instance.name)
    plt.plot(days,
            strategy_team2_instance.cumulative_score_memory,
            label=strategy_team2_instance.name)
    plt.xlabel("Jours")
    plt.ylabel("Scores")
    plt.legend()
    plt.savefig(
        f'./out/scores/{strategy_team1_instance.name}_{strategy_team2_instance.name}_'+
        f'days_{nb_days}_dist_{("inf" if dist_min == np.inf else dist_min)}.png'
    )
    plt.clf()

    plt.title(f"Coûts des trajets")
    plt.plot(days,
            strategy_team1_instance.cumulative_coast_memory, 
            label=strategy_team1_instance.name)
    plt.plot(days,
            strategy_team2_instance.cumulative_coast_memory, 
            label=strategy_team2_instance.name)
    plt.xlabel("Jours")
    plt.ylabel("Coûts")
    plt.legend() 
    plt.savefig(
        f'./out/coasts/{strategy_team1_instance.name}_{strategy_team2_instance.name}_'+
        f'days_{nb_days}_dist_{("inf" if dist_min == np.inf else dist_min)}.png'
    )
    plt.clf()

def main():
    nb_lines = 30
    nb_cols = 30
    nb_players = 20
    nb_goals = 8
    nb_walls = int(0.2 * nb_lines * nb_cols)
    nb_days = 100
    dist_min = math.inf

    positions = random.sample(
        [(row, col) for row in range(nb_lines) for col in range(nb_cols)],
        nb_players + nb_goals + nb_walls
    )

    i, j = 0, nb_players
    players_init_positions = positions[i: j]
    i += nb_players; j += nb_goals
    goals_init_positions = positions[i: j]
    i += nb_goals
    walls_positions = positions[i:]

    players_teams = [1 for _ in range(nb_players//2)] + [2 for _ in range(nb_players//2)]

    play(
        nb_lines,
        nb_cols,
        nb_players,
        nb_goals,
        players_teams,
        players_init_positions,
        goals_init_positions,
        walls_positions,
        nb_days,
        dist_min,
        strategies.RandomStrategy,
        strategies.RandomStrategy
    )

if __name__ == '__main__':
    main()
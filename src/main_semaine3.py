# -*- coding: utf-8 -*-
# 
# Intelligence Artificielle & Jeux
# Sorbonne Université
#
# Ben Kabongo
# Mars 2022
# 

from __future__ import (absolute_import, 
                        print_function, 
                        unicode_literals)
import numpy as np
import random
import matplotlib.pyplot as plt
import sys
import pygame
import pySpriteWorld.glo
from pySpriteWorld.gameclass import Game,check_init_game_done
from pySpriteWorld.spritebuilder import SpriteBuilder
from pySpriteWorld.players import Player
from pySpriteWorld.sprite import MovingSprite
from pySpriteWorld.ontology import Ontology
from search.grid2D import ProblemeGrid2D
from search import probleme

import strategies

plt.style.use('seaborn-whitegrid')

# verbose if verbose is true
_VERBOSE = False
def verbose(*args, **kwargs):
    if _VERBOSE:
        print(*args, **kwargs)


game = Game()

def init(_boardname=None):
    global player,game
    name = _boardname if _boardname is not None else 'blottoMap'
    game = Game('./Cartes/' + name + '.json', SpriteBuilder)
    game.O = Ontology(True, 'SpriteSheet-32x32/tiny_spritesheet_ontology.csv')
    game.populate_sprite_names(game.O)
    game.fps = 5
    game.mainiteration()
    player = game.player
    

def play(nb_iter, 
        nb_days=10, 
        dist_min=12,
        strat1=strategies.RandomStrategy,
        strat2=strategies.RandomStrategy,
        strat1_args={},
        strat2_args={}
        ):
    
    verbose("Initialisation ")
    verbose(f"Nb d'itérations \t: {nb_iter}")

    init('blottoMap')
    nb_lines = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize

    verbose(f"Nb de lignes \t: {nb_lines}")
    verbose(f"Nb de colonnes \t: {nb_cols}")
        
    # joueurs
    players = [o for o in game.layers['joueur']]
    nb_players = len(players)
    verbose(f"Nombre de joueurs \t: {nb_players}")
    
    # positions initiales des joueurs
    players_init_positions = [o.get_rowcol() for o in players]
    verbose(f"Positions intiales des joueurs \t: {players_init_positions}")
    
    # teams
    players_teams = [1 if y == 9 else 2 for _, y in players_init_positions]
    team1_ids = []
    team2_ids = []
    for i, t in enumerate(players_teams):
        if t == 1:
            team1_ids.append(i)
        else:
            team2_ids.append(i)
    verbose(f"Teams des joueurs \t: {players_teams}")

    # votants
    cibles = [o for o in game.layers['ramassable']]
    goals_init_positions = [o.get_rowcol() for o in game.layers['ramassable']]
    nb_goals = len(goals_init_positions)
    verbose(f"Positions des votants \t: {goals_init_positions}")
    
    # obstacles
    wall_positions = [w.get_rowcol() for w in game.layers['obstacle']]
    verbose(f"Positions des obstacles \t: {wall_positions}")

    # liste des positions légales
    legals_positions = []
    for row in range(nb_lines):
        for col in range(nb_cols):
            if (row, col) not in wall_positions:
                legals_positions.append((row, col))

    # initialisation des strategies
    strat1_ = strat1(1, team1_ids, nb_goals, dist_min, **strat1_args)
    strat2_ = strat2(2, team2_ids, nb_goals, dist_min, **strat2_args)
    strat1_.set_adversary(strat2_)
    strat2_.set_adversary(strat1_)

    # jour de propagandes
    
    players_current_positions = players_init_positions
    goals_current_positions = goals_init_positions
    
    for _ in range(nb_days):
        
        # calculs des distances
        team1_positions = {}
        for i in team1_ids:
            team1_positions[i] = players_current_positions[i]
        team2_positions = {}
        for i in team2_ids:
            team2_positions[i] = players_current_positions[i]
        
        strat1_.update_distances(team1_positions, goals_current_positions)
        strat2_.update_distances(team2_positions, goals_current_positions)

        # génération des  des objectifs en fonction des stratégies
        goals_id_team1, distribution_team1 = strat1_.generate()
        goals_id_team2, distribution_team2 = strat2_.generate()

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
        strat1_.save_day_results(votes)
        strat2_.save_day_results(votes)

        # Calcul de A* pour chaque joueur
        paths = {}
        for i in goals.keys():
            g = np.ones((nb_lines,nb_cols),dtype=bool)
            for w in wall_positions:
                g[w] = False
            p = ProblemeGrid2D(players_init_positions[i], goals[i], g, 'manhattan')
            _stdout = sys.__stdout__
            sys.stdout = None
            path = probleme.astar(p)
            sys.stdout = _stdout
            paths[i] = path
            verbose(f"Chemin trouvé pour le joueur {i} : {path}")
                    
        # changement des positions des cibles
        goals_current_positions = random.sample(legals_positions, nb_goals)

        # mise en scène graphique
        goal_flag_by_player = {i:False for i in goals.keys()}

        for it in range(nb_iter):
            for i in goals.keys():
                if not goal_flag_by_player[i]:
                    path = paths[i]
                    row, col = path[it]
                    players_current_positions[i] = (row, col)
                    players[i].set_rowcol(row, col)
                    verbose(f"Pos {i} :({row}, {col})")
                    if (row, col) == goals[i]:
                        verbose(f"Le joueur {i} a atteint son but !")
                        goal_flag_by_player[i] = True
            
            if np.all(list(goal_flag_by_player.values())):
                break

            game.mainiteration()

        # déplacement des cibles
        for i in range(nb_goals):
            cibles[i].set_rowcol(*goals_current_positions[i])
            game.mainiteration()    

    pygame.quit()
    
    days = np.arange(0, nb_days+1)

    plt.title(f"Scores")
    plt.plot(days, 
            strat1_.cumulative_score_memory, 
            label=strat1_.name)
    plt.plot(days,
            strat2_.cumulative_score_memory,
            label=strat2_.name)
    plt.xlabel("Jours")
    plt.ylabel("Scores")
    plt.legend()
    plt.savefig(
        f'./out/scores/{strat1_.name}_{strat2_.name}_'+
        f'days_{nb_days}_dist_{("inf" if dist_min == np.inf else dist_min)}.png'
    )
    plt.clf()

    plt.title(f"Coûts des trajets")
    plt.plot(days,
            strat1_.cumulative_coast_memory, 
            label=strat1_.name)
    plt.plot(days,
            strat2_.cumulative_coast_memory, 
            label=strat2_.name)
    plt.xlabel("Jours")
    plt.ylabel("Coûts")
    plt.legend() 
    plt.savefig(
        f'./out/coasts/{strat1_.name}_{strat2_.name}_'+
        f'days_{nb_days}_dist_{("inf" if dist_min == np.inf else dist_min)}.png'
    )
    plt.clf()

    plt.title(f"Rapport Score/Coût")
    plt.plot(days,
            (np.array(strat1_.cumulative_score_memory) / 
            np.array(strat1_.cumulative_coast_memory)), 
            label=strat1_.name)
    plt.plot(days,
            (np.array(strat2_.cumulative_score_memory) / 
            np.array(strat2_.cumulative_coast_memory)), 
            label=strat2_.name)
    plt.xlabel("Jours")
    plt.ylabel("Coûts")
    plt.legend() 
    plt.savefig(
        f'./out/scores_coasts/{strat1_.name}_{strat2_.name}_'+
        f'days_{nb_days}_dist_{("inf" if dist_min == np.inf else dist_min)}.png'
    )
    plt.clf()


if __name__ == '__main__':
    play(
        int(sys.argv[1]) if len(sys.argv) == 2 else 100,
        12, 
        np.inf, 
        strategies.EpsilonStrategy, 
        strategies.EpsilonImitatorMixStrategy,
        {'eps': 0.6},
        {'eps': 0.4}
    )

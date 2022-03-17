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
        strategy_team1=strategies.RandomStrategy,
        strategy_team2=strategies.RandomStrategy):
    
    verbose("Initialisation ")
    verbose(f"Nb d'itérations \t: {nb_iter}")

    init()
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
    verbose(f"Teams des joueurs \t: {players_teams}")

    # votants
    goals_init_positions = [o.get_rowcol() for o in game.layers['ramassable']]
    nb_goals = len(goals_init_positions)
    verbose(f"Positions des votants \t: {goals_init_positions}")
    
    # obstacles
    wall_positions = [w.get_rowcol() for w in game.layers['obstacle']]
    verbose(f"Positions des obstacles \t: {wall_positions}")

    def is_legal_position(row,col):
        return (
            ((row,col) not in wall_positions) and 
            row>=0 and row<nb_lines and col>=0 and col<nb_cols
        )

    # initialisation des strategies
    strategy_team1_instance = strategy_team1(nb_players // 2, nb_goals)
    strategy_team2_instance = strategy_team2(nb_players // 2, nb_goals)

    # jour de propagandes
    
    players_current_positions = players_init_positions
    scores = np.zeros((nb_days, 2))
    
    for day in range(nb_days):

        # génération des  des objectifs en fonction des stratégies
        goals_id_team1 = strategy_team1_instance.generate()
        goals_id_team2 = strategy_team2_instance.generate()

        i1 = 0
        i2 = 0
        goal_id_by_player = []
        for t in players_teams:
            if t == 1:
                goal_id_by_player.append(goals_id_team1[i1])
                i1 += 1
            else:
                goal_id_by_player.append(goals_id_team2[i2])
                i2 += 1

        goals = [goals_init_positions[i] for i in goal_id_by_player]

        # votes
        votes = [0] * nb_goals
        for i in range(nb_goals):
            for j in range(nb_players):
                if goal_id_by_player[j] == i:
                    if players_teams[j] == 1:
                        votes[i] += 1
                    else:
                        votes[i] -= 1
        for i in range(nb_goals):
            if votes[i] > 0:
                votes[i] = 1
            elif votes[i] < 0:
                votes[i] = 2

        scores[day] = [votes.count(1), votes.count(2)]

        # Calcul de A* pour chaque joueur
        paths = []
        for i in range(nb_players):
            g = np.ones((nb_lines,nb_cols),dtype=bool)
            for w in wall_positions:
                g[w] = False
            p = ProblemeGrid2D(players_init_positions[i], goals[i], g, 'manhattan')
            __stdout = sys.__stdout__
            sys.stdout = None
            path = probleme.astar(p)
            sys.stdout = __stdout
            paths.append(path)
            verbose(f"Chemin trouvé pour le joueur {i} : {path}")
                    
        goal_flag_by_player = [False for _ in range(nb_players)]

        for it in range(nb_iter):
            for i in range(nb_players):
                if not goal_flag_by_player[i]:
                    path = paths[i]
                    row,col = path[it]
                    players_current_positions[i] = (row, col)
                    players[i].set_rowcol(row, col)
                    verbose(f"Pos {i} :({row}, {col})")
                    if (row,col) == goals[i]:
                        verbose(f"Le joueur {i} a atteint son but !")
                        goal_flag_by_player[i] = True
            
            if np.all(goal_flag_by_player):
                break

            game.mainiteration()

    pygame.quit()
    
    plt.title(f"Scores des teams")
    days = np.arange(1, nb_days+1)
    plt.plot(days, scores[:,0], label='Team 1')
    plt.plot(days, scores[:,1], label='Team 2')
    plt.legend()
    plt.show()


def main():
    nb_iter = int(sys.argv[1]) if len(sys.argv) == 2 else 100
    play(nb_iter, 10, strategies.RandomStrategy, strategies.RandomStrategy)

if __name__ == '__main__':
    main()
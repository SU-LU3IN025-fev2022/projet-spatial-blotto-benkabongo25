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
    
def main():
    iterations = 100
    if len(sys.argv) == 2:
        iterations = int(sys.argv[1])
    print("Nombre d'iterations :", iterations)

    init()
        
    nb_lines = game.spriteBuilder.rowsize
    nb_cols = game.spriteBuilder.colsize

    def legal_position(row,col):
        return (
            ((row,col) not in wall_positions) and 
            row>=0 and row<nb_lines and col>=0 and col<nb_cols
        )
       
    print("Lignes :", nb_lines, "Colonnes :", nb_cols)
    
    # joueurs
    players = [o for o in game.layers['joueur']]
    nb_players = len(players)
    print("Nombre de joueurs :", nb_players)
    
    # positions initiales des joueurs
    players_init_positions = [o.get_rowcol() for o in players]
    print("Positions intiales des joueurs :", players_init_positions)
    
    # teams
    players_teams = [1 if y == 9 else 2 for _, y in players_init_positions]
    print("Teams des joueurs :", players_teams)

    # votants
    goals_init_positions = [o.get_rowcol() for o in game.layers['ramassable']]
    nb_goals = len(goals_init_positions)
    print("Positions des votants:", goals_init_positions)
    
    # obstacles
    wall_positions = [w.get_rowcol() for w in game.layers['obstacle']]
    print("Wall states:", wall_positions)
    
    # attribution aléatoire des objectifs  
    goal_id_by_player = np.random.randint(0, nb_goals, size=nb_players)
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

    scores = [votes.count(1), votes.count(2)]

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
        print(f"Chemin trouvé pour le joueur {i} : {path}")
                
    players_current_positions = players_init_positions
    goal_flag_by_player = [False for _ in range(nb_players)]

    for it in range(iterations):
        for i in range(nb_players):
            if not goal_flag_by_player[i]:
                path = paths[i]
                row,col = path[it]
                players_current_positions[i] = (row, col)
                players[i].set_rowcol(row, col)
                print(f"Pos {i} :({row}, {col})")
                if (row,col) == goals[i]:
                    print(f"Le joueur {i} a atteint son but !")
                    goal_flag_by_player[i] = True
        
        if np.all(goal_flag_by_player):
            break

        game.mainiteration()

    print("Nombre de votes équipe 1 :", scores[0])
    print("Nombre de votes équipe 2 :", scores[1])

    pygame.quit()
    
if __name__ == '__main__':
    main()
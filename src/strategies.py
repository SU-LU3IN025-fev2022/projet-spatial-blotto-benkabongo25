# -*- coding: utf-8 -*-
# 
# Intelligence Artificielle & Jeux
# Sorbonne Université
#
# Ben Kabongo
# Mars 2022
# 

import numpy as np

class Strategy:
    '''
    Classe de base pour les stratégies des joueurs
    '''
    
    def __init__(self, nb_team_players, nb_goals):
        '''
        :param nb_team_players (int)
            nombre de joueurs de la team
        :param nb_goals (int)
            nombre de cibles possibles
        '''
        self.nb_team_players = nb_team_players
        self.nb_goals = nb_goals

    def generate(self):
        '''
        Génération des cibles pour une team de joueurs en fonction
        de la stratégie
        '''
        raise NotImplementedError


class RandomStrategy:
    '''
    Strategie aléatoire
    '''

    def __init__(self, nb_team_players, nb_goals):
        Strategy.__init__(self, nb_team_players, nb_goals)

    def generate(self):
        return np.random.randint(0, self.nb_goals, size=self.nb_team_players)

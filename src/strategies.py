# -*- coding: utf-8 -*-
# 
# Intelligence Artificielle & Jeux
# Sorbonne Université
#
# Ben Kabongo
# Mars 2022
# 

import math
import random


class Strategy:
    '''
    Classe de base pour les stratégies des joueurs
    '''
    
    def __init__(self, 
                team_id,
                players_ids,
                nb_goals, 
                dist_min=math.inf):
        '''
        :param team_id (int)
            identifiant de la team
        :param players_ids (list)
            identifiant des joueurs de la team
        :param nb_goals (int)
            nombre de cibles possibles
        :param dist_min (int)
            nombre de pas minimum entre un joueur et une cible
            au dessus de cette distance, la cible n'est pas atteignable pour
            le joueur
        '''
        self.team_id = team_id
        self.players_ids = players_ids
        self.nb_team_players = len(players_ids)
        self.nb_goals = nb_goals

        # mémoires 
        self.distrib_memory = []   # distribution
        self.vote_memory    = []   # vote
        self.score_memory   = []   # score

        # distances 
        self.dist_min = dist_min
        self.distances = {
            player_id: [-math.inf for _ in range(self.nb_goals)] 
            for player_id in self.players_ids
        }
        self.accessibles = {
            player_id: list(range(self.nb_goals))
            for player_id in self.players_ids
        }

    def _filter_accessibles(self):
        self.accessibles = {}
        for j in self.players_ids:
            accessibles = []
            for i in range(self.nb_goals):
                if self.distances[j][i] <= self.dist_min:
                    accessibles.append(i)
            self.accessibles[j] = accessibles
        
    def _generate(self, v):
        '''
        :param v (dict)
            dictionnaire des distributions
        :returns
            - v (dict)
            - r (list)
        '''
        goals = list(v.values())
        r = [goals.count(i) for i in range(self.nb_goals)]
        self.distrib_memory.append(r)
        return v, r

    def generate(self):
        '''
        Génération des cibles pour une team de joueurs en fonction
        de la stratégie
        :returns
            - v (dict): dictionnaire des indices des cibles par joueur de la team
            - r (list): liste de répartition des joueurs par cibles
                        nombre des joueurs par cible
        '''
        raise NotImplementedError

    def from_distribution(self, r):
        '''
        Génération des cibles pour chaque joueur en fonction d'une liste
        de repartition des cibles
        :param r (list)
            liste de répartition des joueurs par cibles
            nombre des joueurs par cible
        '''
        v = []
        for i in range(self.nb_goals):
            v += [i] * r[i]
        return v

    def save_day_results(self, votes):
        '''
        Sauvegarde dans les mémoires adéquates les informations des votes :
        votes par cible et le score du jour
        '''
        self.vote_memory.append(votes)
        self.score_memory.append(votes.count(self.team_id))

    def update_distances(self, team_positions_dict, goals_positions_list):
        '''
        mis à jour des distances entre les joueurs et les cibles
        :param team_positions_dict (dict)
            dictionnaire des positions des joueurs de la team
        :param goals_positions_list (list)
            liste des positions des cibles
        '''
        def manathan(p1, p2):
            x1, y1 = p1
            x2, y2 = p2
            return abs(x2-x1) + abs(y2-y1)
    
        for j in self.players_ids:
            p1 = team_positions_dict[j]
            for i in range(self.nb_goals):
                p2 = goals_positions_list[i]
                self.distances[j][i] = manathan(p1, p2)
        self._filter_accessibles()


class RandomStrategy(Strategy):
    '''
    Strategie aléatoire

    Les cibles sont allouées alétoirement
    '''

    def generate(self):
        v = {}
        for j in self.players_ids:
            if len(self.accessibles[j]) > 0:
                v[j] = random.choice(self.accessibles[j])
        return self._generate(v)        

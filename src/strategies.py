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
import random


class Strategy:
    '''
    Classe de base pour les stratégies des joueurs
    '''
    
    def __init__(self,
                name, 
                team_id,
                players_ids,
                nb_goals, 
                dist_min=math.inf):
        '''
        :param name (str)
            nom de la stratégie
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
        self.name = name
        self.team_id = team_id
        self.players_ids = players_ids
        self.nb_team_players = len(players_ids)
        self.nb_goals = nb_goals

        # mémoires 
        self.distrib_memory = []   # distribution / cible / jour
        self.vote_memory    = []   # vote / cible / jour
        self.score_memory   = []   # score / jour
        self.travel_coast_memory     = [] # coût des trajets / jour
        self.cumulative_score_memory = [0] # score cumulé
        self.cumulative_coast_memory = [0] # coût cumulé

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

    def _compute_travel_coast(self, v):
        '''
        Calcule le coût de déplacement journalier
        '''
        coast = 0
        for j, i in v.items():
            coast += self.distances[j][i]
        self.travel_coast_memory.append(coast)
        a = self.cumulative_coast_memory[-1]
        self.cumulative_coast_memory.append(a + coast)

    def _filter_accessibles(self):
        '''
        met à jour les cibles accessibles par joueur en fonction de la 
        distance minimale autorisée
        '''
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
        self._compute_travel_coast(v)
        goals = list(v.values())
        r = [goals.count(i) for i in range(self.nb_goals)]
        self.distrib_memory.append(r)
        return v, r

    def from_distribution(self, r):
        '''
        Génération des cibles pour chaque joueur en fonction d'une liste
        de repartition des cibles
        :param r (dict)
            liste de répartition des joueurs par cibles
            nombre des joueurs par cible
        '''
        v = {}
        players = list(self.players_ids)
        if self.dist_min == math.inf:
            for i in range(self.nb_goals):
                for j in range(r[i]):
                    v[players[j]] = i
                players = players[r[i]:]
        else:
            for i in range(self.nb_goals):
                c = 0
                j = 0
                n = len(players)
                while j < n and c < r[i]:
                    if i in self.accessibles[players[j]]:
                        v[players[j]] = i
                        del players[j]
                        c += 1
                        n -= 1
                    j += 1
        return v

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

    def get_accessibles_players(self):
        '''
        renvoie la liste des joueurs accessibles par cibles
        :return (dict)
        '''
        g = {}
        for i in range(self.nb_goals):
            accessibles = []
            for j in self.players_ids:
                if i in self.accessibles[j]:
                    accessibles.append(j)
            g[i] = accessibles
        return g

    def save_day_results(self, votes):
        '''
        Sauvegarde dans les mémoires adéquates les informations des votes :
        votes par cible et le score du jour
        '''
        self.vote_memory.append(votes)
        score = votes.count(self.team_id)
        self.score_memory.append(score)
        a = self.cumulative_score_memory[-1]
        self.cumulative_score_memory.append(a + score)

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

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf):
        Strategy.__init__(self, 'random', team_id, players_ids, nb_goals, dist_min)

    def generate(self):
        v = {}
        for j in self.players_ids:
            if len(self.accessibles[j]) > 0:
                v[j] = random.choice(self.accessibles[j])
        return self._generate(v)        


class StubbornStrategy(Strategy):
    '''
    Stratégie du tétu

    Les cibles sont toujours les mêmes pour les joueurs
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf, 
                distrib={}):
        '''
        :param distrib (dict)
            distribution par défaut des cibles aux joueurs
        '''
        Strategy.__init__(self, 'stubborn', team_id, players_ids, nb_goals, dist_min)

        if len(distrib) == 0:
            distrib = {i: random.randint(0, self.nb_goals-1) for i in players_ids}
        self.distrib = distrib

    def generate(self):
        v = {}
        for j, i in self.distrib.items():
            if i in self.accessibles[j]:
                v[j] = i
        return self._generate(v)


class BestAnswerStrategy(Strategy):
    '''
    Stratégie de meilleure réponse

    Meilleure réponse à la stratégie précédente de l'équipe adverse
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf):
        Strategy.__init__(self, 'best answer', team_id, players_ids, nb_goals, dist_min)

    def generate(self):
        return super().generate()

class NearStrategy(Strategy):
    '''
    Stratégie du plus proche

    A chaque joueur est attribué la cible accessible la plus proche possible
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf):
        Strategy.__init__(self, 'near', team_id, players_ids, nb_goals, dist_min)


    def generate(self):
        v = {}
        for j in self.players_ids:
            i = np.argmin(self.distances[j])
            if self.dist_min == math.inf or i in self.accessibles[j]:
                v[j] = i
        return self._generate(v)


class FarStrategy(Strategy):
    '''
    Stratégie du plus loin

    A chaque joueur est attribué la cible accesible la plus loin possible
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf):
        Strategy.__init__(self, 'far', team_id, players_ids, nb_goals, dist_min)

    def generate(self):
        v = {}
        for j in self.players_ids:
            distances = list(self.distances[j])
            if self.dist_min == math.inf:
                i = np.argmax(distances)
                v[j] = i
            else:
                while not np.all(distances == -math.inf):
                    i = np.argmax(distances)
                    if i in self.accessibles[j]:
                        v[j] = i
                        break
                    distances[i] = -math.inf
        return self._generate(v)
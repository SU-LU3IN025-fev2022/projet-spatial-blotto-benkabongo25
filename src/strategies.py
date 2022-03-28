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


def compare(r1, r2):
    '''
    compare deux stratégies et retourne la meilleure
    :param r1 (list) 
        stratégie de répartition 1
    :parm r2 (list)
        stratégie de répartition 2
    :return int, int
        le numéro et le score de la répartition gagnate
    '''
    s = np.sum(np.array(r1) > np.array(r2))
    a = s / len(r2)
    if a == .5:
        return 0, 0
    w = 1 if a > .5 else 2
    return w, int(s)
    

def generate_distrib(limit, size):
    '''
    génère une distribution dont la somme est bornée à limit
    :param limit (int)
        borne supérieure 
    :param size (int)
        taille de la distribution
    '''
    if size == 1:
        return [[i] for i in range(limit+1)]
    distribs = []
    for i in range(limit+1):
        for distrib in generate_distrib(limit-i, size-1):
            distribs.append( [i] + distrib )
    return distribs


def better_answer(r, limit):
    '''
    :param r (list)
        stratégie de répartition
    :param limit (int)
        nombre maximum de ressources (joueurs) à répartir
    :return (list)
        une stratégie de répartition bien meilleure que r
    '''
    for answer in generate_distrib(limit, len(r)):
        w, _ = compare(answer, r)
        if w == 1:
            return tuple(answer)


def all_better_answers(r, limit):
    '''
    :param r (list)
        stratégie de répartition
    :param limit (int)
        nombre maximum de ressources (joueurs) à répartir
    :return (dict)
        la liste de toutes les stratégies meilleures que r et leur score
    '''
    answers = {}
    for answer in generate_distrib(limit, len(r)):
        w, s = compare(answer, r)
        if w == 1:
            answers[tuple(answer)] = s
    return answers


def best_answer(r, limit):
    '''
    :param r (list)
        stratégie de répartition
    :param limit (int)
        nombre maximum de ressources (joueurs) à répartir
    :return (list)
        la meilleure des stratégies de répartition bien meilleures que r
    '''
    best = None
    s = 0
    for answer, score in all_better_answers(r, limit).items():
        if score > s:
            best = answer
            s = score
    return best
    

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

        # adversaire
        self.adversary_strategy = None

        # mémoires 
        self.distrib_memory = []   # distribution / cible / jour
        self.vote_memory    = []   # vote / cible / jour
        self.score_memory   = []   # score / jour
        self.travel_coast_memory     = [] # coût des trajets / jour
        self.cumulative_score_memory = [0] # score cumulé
        self.cumulative_coast_memory = [0] # coût cumulé

        # dictionnaire des stratégies jouées
        self.strat_cum_scores  = {} # somme cumulée
        self.strat_mean_scores = {} # scores moyens
        self.strat_counts      = {} # compteurs
        
        # meilleure stratégie courante
        self.current_best = []

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
            - r (tuple)
        '''
        self._compute_travel_coast(v)
        goals = list(v.values())
        r = tuple([goals.count(i) for i in range(self.nb_goals)])
        self.distrib_memory.append(r)
        return v, r

    def _generate_random_distribution(self):
        '''
        génère une distribution aléatoire
        :return list
            liste générée
        '''
        a = self.nb_team_players
        b = self.nb_goals
        return list(np.random.multinomial(a, np.ones(b)/b, size=1)[0])

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

    def set_adversary(self, adversary_strategy):
        '''
        :param adversary_strategy (Strategy) 
            stratégie adversaire
        '''
        self.adversary_strategy = adversary_strategy

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
        Strategy.__init__(self, 
                        'random', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

    def generate(self):
        v = {}
        for j in self.players_ids:
            if len(self.accessibles[j]) > 0:
                v[j] = random.choice(self.accessibles[j])
        return self._generate(v)        


class StubbornStrategy1(Strategy):
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
        Strategy.__init__(self, 
                        'stubborn_1', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

        if len(distrib) == 0:
            distrib = {
                i: random.randint(0, self.nb_goals-1) 
                for i in players_ids
            }
        self.distrib = distrib

    def generate(self):
        v = {}
        for j, i in self.distrib.items():
            if i in self.accessibles[j]:
                v[j] = i
        return self._generate(v)


class StubbornStrategy2(Strategy):
    '''
    Stratégie du tétu

    Les cibles ont toujours le même nombre de joueurs
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf, 
                r=[]):
        '''
        :param r (list)
            repartition par défaut pour les cibles
        '''
        Strategy.__init__(self, 
                        'stubborn_2', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

        if len(r) == 0:
            r = self._generate_random_distribution()
        self.r = r

    def generate(self):
        v = self.from_distribution(self.r)
        return self._generate(v)


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
        Strategy.__init__(self, 
                        'near', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

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
        Strategy.__init__(self, 
                        'far', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

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


class EpsilonStrategy(Strategy):
    '''
    Stratégie epsilon-greedy

    Avec une probabilité epsilon, la distribution choisie est aléatoire
    Avec une probabilité 1-epsilon, la distribution choisie est celle qui a 
    le maximisé le score le plus souvent
    '''

    def __init__(self,
                team_id,
                players_ids, 
                nb_goals, 
                dist_min=math.inf,
                eps=0.5
                ):
        Strategy.__init__(self, 
                        f'epsilon_{eps}', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)
        self.eps = eps

    def generate(self):
        if len(self.strat_counts) == 0 or random.random() < self.eps: # random
            v = {}
            for j in self.players_ids:
                if len(self.accessibles[j]) > 0:
                    v[j] = random.choice(self.accessibles[j])
        else: # best 
            if self.current_best == []:
                self.current_best = self._generate_random_distribution()
            v = self.from_distribution(self.current_best)
        return self._generate(v)             

    def save_day_results(self, votes):
        super().save_day_results(votes)
        
        r = self.distrib_memory[-1]
        s = self.score_memory[-1]
        if r not in self.strat_counts:
            self.strat_cum_scores[r] = 0
            self.strat_counts[r] = 0
        self.strat_cum_scores[r] += s
        self.strat_counts[r] += 1
        
        r_max = []
        max_mean = 0
        for r in self.strat_counts:
            mean = self.strat_cum_scores[r] / self.strat_counts[r]
            if mean > max_mean:
                max_mean = mean
                r_max = r
            self.strat_mean_scores[r] = mean
        self.current_best = list(r_max)


class AdversaryImitatorStrategy(Strategy):
    '''
    Stratégie de l'imitateur

    Joue un coup identique que au coup précédent
    '''

    def __init__(self,
                team_id,
                players_ids, 
                nb_goals, 
                dist_min=math.inf):
        Strategy.__init__(
            self, 
            'imitator', 
            team_id, 
            players_ids, 
            nb_goals, 
            dist_min
        )

    def generate(self):
        i = self.team_id
        if len(self.adversary_strategy.distrib_memory) < i:
            r = self._generate_random_distribution()
        else:
            r = self.adversary_strategy.distrib_memory[-i]
        return self._generate(self.from_distribution(r))


class EpsilonImitatorStrategy(Strategy):
    '''
    Stratégie epsilon-greedy

    Avec une probabilité epsilon, la distribution choisie est aléatoire
    Avec une probabilité 1-epsilon, la distribution choisie est celle qui a 
    le maximisé le score le plus souvent en fonction des coups de l'adversaire
    '''

    def __init__(self,
                team_id,
                players_ids, 
                nb_goals, 
                dist_min=math.inf,
                eps=0.5
                ):
        Strategy.__init__(
            self, 
            f'epsilon_imitator_{eps}', 
            team_id, 
            players_ids, 
            nb_goals, 
            dist_min
        )
        self.eps = eps

    def generate(self):
        if len(self.strat_counts) > 0 and random.random() > self.eps: # best
            if self.current_best == []:
                self.current_best = self._generate_random_distribution()
            v = self.from_distribution(self.current_best)
        else: # random
            v = {}
            for j in self.players_ids:
                if len(self.accessibles[j]) > 0:
                    v[j] = random.choice(self.accessibles[j])
        return self._generate(v)             

    def save_day_results(self, votes):
        super().save_day_results(votes)
        
        i = self.team_id
        if len(self.adversary_strategy.score_memory) < i:
            return
        
        r = self.adversary_strategy.distrib_memory[-i]
        s = self.adversary_strategy.score_memory[-i]
        if r not in self.strat_counts:
            self.strat_cum_scores[r] = 0
            self.strat_counts[r] = 0
        self.strat_cum_scores[r] += s
        self.strat_counts[r] += 1
        
        r_max = []
        max_mean = 0
        for r in self.strat_counts:
            mean = self.strat_cum_scores[r] / self.strat_counts[r]
            if mean > max_mean:
                max_mean = mean
                r_max = r
            self.strat_mean_scores[r] = mean
        self.current_best = list(r_max)


class EpsilonImitatorMixStrategy(Strategy):
    '''
    Stratégie épislon-greedy

    Avec une probabilité epsilon, la distribution choisie est aléatoire
    Avec une probabilité 1-epsilon, la distribution choisie est celle qui a 
    maximisé le score le plus souvent en fonction tous les coups, ceux de 
    l'adversaire compris
    '''

    def __init__(self,
                team_id,
                players_ids, 
                nb_goals, 
                dist_min=math.inf,
                eps=0.5
                ):
        Strategy.__init__(
            self, 
            f'epsilon_imitator_mix_{eps}', 
            team_id, 
            players_ids, 
            nb_goals, 
            dist_min
        )
        self.eps = eps

    def generate(self):
        if len(self.strat_counts) == 0 or random.random() < self.eps: # random
            v = {}
            for j in self.players_ids:
                if len(self.accessibles[j]) > 0:
                    v[j] = random.choice(self.accessibles[j])
        else: # best 
            if self.current_best == []:
                self.current_best = self._generate_random_distribution()
            v = self.from_distribution(self.current_best)
        return self._generate(v)             

    def save_day_results(self, votes):
        super().save_day_results(votes)
        
        r = self.distrib_memory[-1]
        s = self.score_memory[-1]
        if r not in self.strat_counts:
            self.strat_cum_scores[r] = 0
            self.strat_counts[r] = 0
        self.strat_cum_scores[r] += s
        self.strat_counts[r] += 1
        
        i = self.team_id
        if len(self.adversary_strategy.score_memory) >= i:
            r = self.adversary_strategy.distrib_memory[-i]
            s = self.adversary_strategy.score_memory[-i]
            if r not in self.strat_counts:
                self.strat_cum_scores[r] = 0
                self.strat_counts[r] = 0
            self.strat_cum_scores[r] += s
            self.strat_counts[r] += 1

        r_max = []
        max_mean = 0
        for r in self.strat_counts:
            mean = self.strat_cum_scores[r] / self.strat_counts[r]
            if mean > max_mean:
                max_mean = mean
                r_max = r
            self.strat_mean_scores[r] = mean
        self.current_best = list(r_max)


class BetterAnswerLastAdversaryStrategy(Strategy):
    '''
    Stratégie de meilleure réponse version 1

    Rend une meilleure réponse à la stratégie précédente de l'équipe adverse
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf,
                ):
        Strategy.__init__(self,
                        'better_answer_last_adversary', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

    def generate(self):
        i = self.team_id
        if len(self.adversary_strategy.distrib_memory) < i:
            r = self._generate_random_distribution()
        else:
            r = self.adversary_strategy.distrib_memory[-i]
        best = better_answer(r, self.nb_team_players)
        if best is None:
            best = []
        return self._generate(self.from_distribution(best))    


class BestAnswerLastAdversaryStrategy(Strategy):
    '''
    Stratégie de meilleure réponse

    Rend la meilleure réponse à la stratégie précédente de l'équipe adverse
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf
                ):
        Strategy.__init__(self,
                        'best_answer_last_adversary', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

    def generate(self):
        i = self.team_id
        if len(self.adversary_strategy.distrib_memory) < i:
            r = self._generate_random_distribution()
        else:
            r = self.adversary_strategy.distrib_memory[-i]
        best = best_answer(r, self.nb_team_players)
        if best is None:
            best = []
        return self._generate(self.from_distribution(best))    


class BestAnswerAdversaryStrategy(Strategy):
    '''
    Stratégie de meilleure réponse

    Rend la meilleure réponse à la meilleure stratégie de l'équipe adverse
    '''

    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf,
                ):
        Strategy.__init__(self,
                        'best_answer_adversary', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

    def generate(self):
        if self.current_best == []:
            self.current_best = self._generate_random_distribution()
        best = best_answer(self.current_best, self.nb_team_players)
        if best is None:
            best = self.current_best
        return self._generate(self.from_distribution(best))   

    def save_day_results(self, votes):
        super().save_day_results(votes)

        i = self.team_id
        if len(self.adversary_strategy.score_memory) >= i:
            r = self.adversary_strategy.distrib_memory[-i]
            s = self.adversary_strategy.score_memory[-i]
            if r not in self.strat_counts:
                self.strat_cum_scores[r] = 0
                self.strat_counts[r] = 0
            self.strat_cum_scores[r] += s
            self.strat_counts[r] += 1

        r_max = []
        max_mean = 0
        for r in self.strat_counts:
            mean = self.strat_cum_scores[r] / self.strat_counts[r]
            if mean > max_mean:
                max_mean = mean
                r_max = r
            self.strat_mean_scores[r] = mean
        self.current_best = list(r_max)


class FicticiousPlayStrategy(Strategy):
    '''
    Ficticious play
    '''
    
    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf,
                ):
        Strategy.__init__(self,
                        'ficticious_play', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)

        self.strategy_set = generate_distrib(self.nb_team_players, self.nb_goals)
        self.adversary_strategy_counts = {}
        self.adversary_strategy_probas = {}

    def generate(self):
        if len(self.adversary_strategy_counts) == 0:
            r = self._generate_random_distribution()
            return self._generate(self.from_distribution(r))
        best = []
        score_max = -1
        for r in self.strategy_set:
            score = 0
            for ra, p in self.adversary_strategy_probas.items():
                s = np.sum(np.array(r) > np.array(ra))
                score += s * p
            if score > score_max:
                score_max = score
                best = r
        return self._generate(self.from_distribution(best))

    def save_day_results(self, votes):
        super().save_day_results(votes)

        i = self.team_id
        if len(self.adversary_strategy.distrib_memory) >= i:
            r = self.adversary_strategy.distrib_memory[-i]
            if r not in self.adversary_strategy_counts:
                self.adversary_strategy_counts[r] = 0
            self.adversary_strategy_counts[r] += 1

        n = len(self.distrib_memory)
        for r in self.adversary_strategy_counts:
            self.adversary_strategy_probas[r] = self.adversary_strategy_counts[r] / n


class ExpertStochasticStrategy(Strategy):
    '''
    Stratégie du stochastique expert
    '''
    
    def __init__(self, 
                team_id, 
                players_ids, 
                nb_goals, 
                dist_min=math.inf):
        Strategy.__init__(self,
                        'stochastic_expert', 
                        team_id, 
                        players_ids, 
                        nb_goals, 
                        dist_min)
        self.strategies = [
            FicticiousPlayStrategy(team_id,players_ids, nb_goals, dist_min),
            BestAnswerAdversaryStrategy(team_id,players_ids, nb_goals, dist_min),
            EpsilonStrategy(team_id,players_ids, nb_goals, dist_min),
            RandomStrategy(team_id, players_ids, nb_goals, dist_min),
            NearStrategy(team_id,players_ids, nb_goals, dist_min),  
        ]
        self.p = [.3, .2, .2, .2, .1]

    def generate(self):
        strats_ids = list(range(len(self.strategies)))
        i = np.random.choice(strats_ids, p=self.p)
        v, r = self.strategies[i].generate()
        for j in strats_ids:
            if j != i:
                self.strategies[j]._generate(v)
        return self._generate(v)

    def save_day_results(self, votes):
        super().save_day_results(votes)
        for strat in self.strategies:
            strat.save_day_results(votes)    

    def set_adversary(self, adversary_strategy):
        super().set_adversary(adversary_strategy)
        for strat in self.strategies:
            strat.set_adversary(adversary_strategy)

    def update_distances(self, team_positions_dict, goals_positions_list):
        super().update_distances(team_positions_dict, goals_positions_list)
        for strat in self.strategies:
            strat.update_distances(team_positions_dict, goals_positions_list)

import botbowl
from botbowl.core import Action, Agent, ActionType, OutcomeType
import numpy as np
from copy import deepcopy
import random
import time
import sys
import math
from botbowl.core.procedure import *

class Node:
    def __init__(self, action=None, parent=None):
        self.parent = parent
        self.children = []
        self.action = action
        self.evaluations = []

    def num_visits(self):
        return len(self.evaluations)

    def visit(self, score):
        self.evaluations.append(score)

    def score(self):
        return np.average(self.evaluations)


class SearchBot(botbowl.Agent):

    def __init__(self, name, seed=None):
        super().__init__(name)
        self.my_team = None
        self.rnd = np.random.RandomState(seed)
        self.action = None
        self.parent = None
        self.records = dict()
        self.choices = [ActionType.START_MOVE, ActionType.START_BLOCK, ActionType.START_BLITZ]
        self.rewards_opp = {
            OutcomeType.TOUCHDOWN: -1.50,
            OutcomeType.SUCCESSFUL_CATCH: -0.20,
            OutcomeType.INTERCEPTION: -0.20,
            OutcomeType.SUCCESSFUL_PICKUP: -0.20,
            OutcomeType.ACCURATE_PASS: -0.10,
            OutcomeType.INACCURATE_PASS: 0.10,
            OutcomeType.FUMBLE: 0.10,
            OutcomeType.KNOCKED_DOWN: 0.20,
            OutcomeType.KNOCKED_OUT: 0.20,
            OutcomeType.CASUALTY: 0.50,
        }
        self.rewards_own = {
            OutcomeType.TOUCHDOWN: 1.5,
            OutcomeType.SUCCESSFUL_CATCH: 0.2,
            OutcomeType.INTERCEPTION: 0.20,
            OutcomeType.SUCCESSFUL_PICKUP: 0.20,
            OutcomeType.ACCURATE_PASS: 0.10,
            OutcomeType.INACCURATE_PASS: -0.10,
            OutcomeType.FUMBLE: -0.10,
            OutcomeType.KNOCKED_DOWN: -0.20,
            OutcomeType.KNOCKED_OUT: -0.20,
            OutcomeType.CASUALTY: -0.50,
        }
        self.ball_progression_reward = 0.5
        self.last_report_idx = 0
        self.last_ball_x = None
        self.last_ball_team = None
        self.pos_len = 1
        self.reps = 25
        self.off_formation = [
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "m", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "x", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "S"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "x"],
            ["-", "-", "-", "-", "-", "s", "-", "-", "-", "0", "-", "-", "S"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "x"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "S"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "x", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "m", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"]
        ]

        self.def_formation = [
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "x", "-", "b", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "x", "-", "S", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "0"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "0"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "0"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "x", "-", "S", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "x", "-", "b", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"]
        ]
        self.off_formation = Formation("Wedge offense", self.off_formation)
        self.def_formation = Formation("Zone defense", self.def_formation)
        self.setup_actions = []
        self.ends = 0

    def new_game(self, game, team):
        self.my_team = team
        self.opp_team = game.get_opp_team(team)

    def UCB_policy(self, node):
        best_score = -sys.maxsize
        best_sub_node = None
        # C = 1 / math.sqrt(2.0)
        C = 2
        for sub_node in node.children:
            left = sub_node.score()
            right = math.sqrt(math.log(node.num_visits()) / sub_node.num_visits())
            score = left + C * right
            if score > best_score:
                best_sub_node = sub_node
                best_score = score
        return best_sub_node

    def coin_toss_flip(self, game):
        """
        Select heads/tails and/or kick/receive
        """
        return Action(ActionType.TAILS)
        # return Action(ActionType.HEADS)

    def coin_toss_kick_receive(self, game):
        """
        Select heads/tails and/or kick/receive
        """
        return Action(ActionType.RECEIVE)
        # return Action(ActionType.KICK)

    def perfect_defense(self, game):
        return Action(ActionType.END_SETUP)

    def setup(self, game):
        """
        Use either a Wedge offensive formation or zone defensive formation.
        """
        # Update teams
        self.my_team = game.get_team_by_id(self.my_team.team_id)
        self.opp_team = game.get_opp_team(self.my_team)

        if self.setup_actions:
            action = self.setup_actions.pop(0)
            return action
        else:
            if game.get_receiving_team() == self.my_team:
                self.setup_actions = self.off_formation.actions(game, self.my_team)
                self.setup_actions.append(Action(ActionType.END_SETUP))
            else:
                self.setup_actions = self.def_formation.actions(game, self.my_team)
                self.setup_actions.append(Action(ActionType.END_SETUP))
            action = self.setup_actions.pop(0)
            return action

    def place_ball(self, game):
        """
        Place the ball when kicking.
        """
        left_center = Square(7, 8)
        right_center = Square(20, 8)
        if game.is_team_side(left_center, self.opp_team):
            return Action(ActionType.PLACE_BALL, position=left_center)
        return Action(ActionType.PLACE_BALL, position=right_center)

    def touchback(self, game):
        """
        Select player to give the ball to.
        """
        p = None
        for player in game.get_players_on_pitch(self.my_team, up=True):
            if Skill.BLOCK in player.get_skills():
                return Action(ActionType.SELECT_PLAYER, player=player)
            p = player
        return Action(ActionType.SELECT_PLAYER, player=p)



    def act(self, game):
        game_copy = deepcopy(game)
        game_copy.enable_forward_model()
        game_copy.home_agent.human = True
        game_copy.away_agent.human = True

        root_step = game_copy.get_step()
        own_team = game_copy.active_team
        opp_team = game_copy.get_opp_team(own_team)
        root_node = Node(action=self.action, parent=self.parent)

        proc = game.get_procedure()
        print("proc:",proc)
        if isinstance(proc, CoinTossFlip):
            return self.coin_toss_flip(game)
        elif isinstance(proc, CoinTossKickReceive):
            return self.coin_toss_kick_receive(game)
        elif isinstance(proc, Setup):
            if proc.reorganize:
                return self.perfect_defense(game)
            else:
                return self.setup(game)
        elif isinstance(proc, PlaceBall):
            return self.place_ball(game)
        elif isinstance(proc, Touchback):
            return self.touchback(game)
        elif isinstance(proc, Turn):
            if root_node.action in self.records:
                root_node.children = self.records[root_node.action]
                best_node = self.UCB_policy(root_node)
            else:
                for action_choice in game_copy.get_available_actions():
                    if action_choice.action_type == botbowl.ActionType.PLACE_PLAYER:
                        continue

                    if len(action_choice.players)>0:
                        ball_pos1 = game_copy.get_ball_position()
                        # print("ball_pos1:",ball_pos1)
                        if ball_pos1 is None:
                            for player in action_choice.players:
                                root_node.children.append(
                                    Node(Action(action_choice.action_type, player=player), parent=root_node))
                        else:
                            pos_tmp = []
                            for player in action_choice.players:
                                pos_tmp.append(
                                    math.sqrt((player.position.x - ball_pos1.x) ** 2 + (
                                            player.position.y - ball_pos1.y) ** 2))
                            if len(pos_tmp) > 0:
                                pos_tmp = np.array(pos_tmp)
                                pos_index = np.argmin(pos_tmp)
                                players = np.array(action_choice.players)
                                player = players[pos_index]
                                # print("1:", Action(action_choice.action_type, player=player))
                                root_node.children.append(
                                    Node(Action(action_choice.action_type, player=player), parent=root_node))

                self.records[root_node.action] = root_node.children
                for j in range(len(root_node.children)):
                    game_copy.step(root_node.children[j].action)
                    times = 0
                    evaluate_score = 0
                    while not game_copy.state.game_over and len(game_copy.state.available_actions) > 0:
                        if times > self.reps:
                            break
                        while True:
                            action_choice = self.rnd.choice(game_copy.state.available_actions)
                            if action_choice.action_type != botbowl.ActionType.PLACE_PLAYER:
                                break
                        position = self.rnd.choice(action_choice.positions) if len(
                            action_choice.positions) > 0 else None
                        player = self.rnd.choice(action_choice.players) if len(action_choice.players) > 0 else None
                        action = botbowl.Action(action_choice.action_type, position=position, player=player)

                        game_copy.step(action)
                        evaluate_score += self._evaluate(game_copy)
                        # print(str(times) + ":", evaluate_score)
                        times += 1
                    root_node.children[j].visit(evaluate_score)
                    node_parent = root_node.children[j].parent
                    while True:
                        node_parent.visit(evaluate_score)
                        if node_parent.action is None:
                            break
                        else:
                            node_parent = node_parent.parent
                    # print(f"{root_node.children[j].action.action_type}: {root_node.children[j].score()}")
                    game_copy.revert(root_step)
                best_node = self.UCB_policy(root_node)
        elif isinstance(proc, MoveAction) or isinstance(proc, BlockAction) or isinstance(proc, PassAction) or isinstance(proc, HandoffAction) or isinstance(proc, BlitzAction) or isinstance(proc, FoulAction) or isinstance(proc, ThrowBombAction) or isinstance(proc, Push) or isinstance(proc, FollowUp):
            if root_node.action in self.records:
                root_node.children = self.records[root_node.action]
                best_node = self.UCB_policy(root_node)
            else:
                for action_choice in game_copy.get_available_actions():
                    if action_choice.action_type == botbowl.ActionType.PLACE_PLAYER:
                        continue

                    if len(action_choice.positions) > 0:
                        ball_pos1 = game_copy.get_ball_position()
                        ball_carrier = game_copy.get_ball_carrier()
                        if ball_carrier is None or (ball_carrier is not None and ball_carrier.team is opp_team):
                            pos_tmp = []
                            for position in action_choice.positions:
                                pos_tmp.append(
                                    math.sqrt((position.x - ball_pos1.x) ** 2 + (
                                            position.y - ball_pos1.y) ** 2))
                            if len(pos_tmp) > 0:
                                pos_tmp = np.array(pos_tmp)
                                pos_index = np.argmin(pos_tmp)
                                positions = np.array(action_choice.positions)
                                position1 = positions[pos_index]
                                # print("1:", Action(action_choice.action_type, position=position1))
                                root_node.children.append(
                                    Node(Action(action_choice.action_type, position=position1), parent=root_node))
                            else:
                                for position in action_choice.positions:
                                    root_node.children.append(
                                        Node(Action(action_choice.action_type, position=position), parent=root_node))
                        else:
                            ball_carrier = game_copy.get_ball_carrier()
                            # print("ball_carrier:", ball_carrier)
                            if ball_carrier is not None and ball_carrier.team is own_team:
                                tmp1 = []
                                for position in action_choice.positions:
                                    tmp1.append(abs(self.ends - position.x))
                                indexs = np.argmin(np.array(tmp1))
                                positions = np.array(action_choice.positions)
                                position1 = positions[indexs]
                                # print("2:", Action(action_choice.action_type, player=position1))
                                root_node.children.append(
                                    Node(Action(action_choice.action_type, position=position1), parent=root_node))
                            else:
                                for position in action_choice.positions:
                                    root_node.children.append(
                                        Node(Action(action_choice.action_type, position=position), parent=root_node))


                self.records[root_node.action] = root_node.children
                for j in range(len(root_node.children)):
                    print(root_node.children[j].action)
                    game_copy.step(root_node.children[j].action)
                    times = 0
                    evaluate_score = 0
                    while not game_copy.state.game_over and len(game_copy.state.available_actions) > 0:
                        if times > self.reps:
                            break
                        while True:
                            action_choice = self.rnd.choice(game_copy.state.available_actions)
                            if action_choice.action_type != botbowl.ActionType.PLACE_PLAYER:
                                break
                        position = self.rnd.choice(action_choice.positions) if len(
                            action_choice.positions) > 0 else None
                        player = self.rnd.choice(action_choice.players) if len(action_choice.players) > 0 else None
                        action = botbowl.Action(action_choice.action_type, position=position, player=player)

                        game_copy.step(action)
                        evaluate_score += self._evaluate(game_copy)
                        # print(str(times) + ":", evaluate_score)
                        times += 1
                    root_node.children[j].visit(evaluate_score)
                    node_parent = root_node.children[j].parent
                    while True:
                        node_parent.visit(evaluate_score)
                        if node_parent.action is None:
                            break
                        else:
                            node_parent = node_parent.parent
                    # print(f"{root_node.children[j].action.action_type}: {root_node.children[j].score()}")
                    game_copy.revert(root_step)
                best_node = self.UCB_policy(root_node)
        else:
            if root_node.action in self.records:
                root_node.children = self.records[root_node.action]
                best_node = self.UCB_policy(root_node)
            else:
                for action_choice in game_copy.get_available_actions():
                    print("3:",Action(action_choice.action_type))
                    if action_choice.action_type == botbowl.ActionType.PLACE_PLAYER:
                        continue
                    if len(action_choice.players) == len(action_choice.positions) == 0:
                        root_node.children.append(Node(Action(action_choice.action_type), parent=root_node))

                self.records[root_node.action] = root_node.children
                if len(root_node.children)==1:
                    best_node = root_node.children[0]
                else:
                    for j in range(len(root_node.children)):
                        game_copy.step(root_node.children[j].action)
                        times = 0
                        evaluate_score = 0
                        while not game_copy.state.game_over and len(game_copy.state.available_actions) > 0:
                            if times > self.reps:
                                break
                            while True:
                                action_choice = self.rnd.choice(game_copy.state.available_actions)
                                if action_choice.action_type != botbowl.ActionType.PLACE_PLAYER:
                                    break
                            position = self.rnd.choice(action_choice.positions) if len(
                                action_choice.positions) > 0 else None
                            player = self.rnd.choice(action_choice.players) if len(action_choice.players) > 0 else None
                            action = botbowl.Action(action_choice.action_type, position=position, player=player)

                            game_copy.step(action)
                            evaluate_score += self._evaluate(game_copy)
                            # print(str(times) + ":", evaluate_score)
                            times += 1
                        root_node.children[j].visit(evaluate_score)
                        node_parent = root_node.children[j].parent
                        while True:
                            node_parent.visit(evaluate_score)
                            if node_parent.action is None:
                                break
                            else:
                                node_parent = node_parent.parent
                        # print(f"{root_node.children[j].action.action_type}: {root_node.children[j].score()}")
                        game_copy.revert(root_step)
                    best_node = self.UCB_policy(root_node)
        self.action = best_node.action
        self.parent = best_node.parent
        print("action:", best_node.action)
        return best_node.action


    def _evaluate(self, game):
        if len(game.state.reports) < self.last_report_idx:
            self.last_report_idx = 0

        r = random.uniform(0, 0.1)
        own_team = game.active_team
        opp_team = game.get_opp_team(own_team)

        for outcome in game.state.reports[self.last_report_idx:]:
            team = None
            if outcome.player is not None:
                team = outcome.player.team
            elif outcome.team is not None:
                team = outcome.team

            if team == own_team and outcome.outcome_type in self.rewards_own:
                r += self.rewards_own[outcome.outcome_type]
            if team == opp_team and outcome.outcome_type in self.rewards_opp:
                r += self.rewards_opp[outcome.outcome_type]
        self.last_report_idx = len(game.state.reports)

        ball_carrier = game.get_ball_carrier()
        ball_pos1 = game.get_ball_position()
        if ball_carrier is not None:
            if self.last_ball_team is own_team and ball_carrier.team is own_team:
                ball_progress = self.last_ball_x - ball_carrier.position.x
                end_dis = abs(self.ends - ball_pos1.x)
                end_dis = int(1/end_dis)
                if own_team is game.state.away_team:
                    ball_progress *= -1  # End zone at max x coordinate
                    end_dis *= -1
                r += self.ball_progression_reward * ball_progress
                r += end_dis

            self.last_ball_team = ball_carrier.team
            self.last_ball_x = ball_carrier.position.x
        else:
            self.last_ball_team = None
            self.last_ball_x = None
        print("score: ", r)
        return r

    def end_game(self, game):
        """
        Called when a game ends.
        """
        winner = game.get_winning_team()
        print("Casualties: ", game.num_casualties())
        if winner is None:
            print("It's a draw")
        elif winner == self.my_team:
            print("I ({}) won".format(self.name))
            print(self.my_team.state.score, "-", self.opp_team.state.score)
        else:
            print("I ({}) lost".format(self.name))
            print(self.my_team.state.score, "-", self.opp_team.state.score)


# Register the bot to the framework
botbowl.register_bot('search-bot', SearchBot)

def main():
    # Load configurations, rules, arena and teams
    config = botbowl.load_config("bot-bowl")
    config.competition_mode = False
    config.pathfinding_enabled = True
    ruleset = botbowl.load_rule_set(config.ruleset, all_rules=False)  # We don't need all the rules
    arena = botbowl.load_arena(config.arena)
    home = botbowl.load_team_by_filename("human", ruleset)
    away = botbowl.load_team_by_filename("human", ruleset)

    num_games = 5
    wins = 0
    tds = 0
    sums = 0
    for i in range(num_games):
        home_agent = botbowl.make_bot('search-bot')
        home_agent.name = "MCTS Bot"
        away_agent = botbowl.make_bot('random')
        away_agent.name = "Random Bot"
        config.debug_mode = False
        game = botbowl.Game(i, home, away, home_agent, away_agent, config, arena=arena, ruleset=ruleset)
        game.config.fast_mode = True

        print("Starting game", (i + 1))
        start = time.time()
        game.init()
        end = time.time()
        print("last time:", end - start)
        sums = sums + (end - start)

        wins += 1 if game.get_winning_team() is game.state.home_team else 0
        tds += game.state.home_team.state.score
    print("average time:", float(sums / num_games))
    print(f"won {wins}/{num_games}")
    print(f"Own TDs per game={tds / num_games}")


if __name__ == "__main__":
    main()

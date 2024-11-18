from hanabi import *
import agent
import random
import util

def format_hint(h):
    if h == HINT_COLOR:
        return "color"
    return "rank"

class ImprovedOuterAgent(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.hints = {}
        self.pnr = pnr
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        # Initialize hints for cards not tracked
        for player, hand in enumerate(hands):
            for card_index, _ in enumerate(hand):
                if (player, card_index) not in self.hints:
                    self.hints[(player, card_index)] = set()

        # Track hints for teammate cards
        known = [""] * 5
        for h in self.hints:
            pnr, card_index = h
            if pnr != nr:
                known[card_index] = str(list(map(format_hint, self.hints[h])))
        self.explanation = [["hints received:"] + known]

        my_knowledge = knowledge[nr]

        # Discard useless cards
        for i, k in enumerate(my_knowledge):
            if util.is_useless(k, board):
                return Action(DISCARD, card_index=i)

        # Playable cards
        for i, k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)

        # Potential discards
        potential_discards = []
        for i, k in enumerate(my_knowledge):
            if util.is_useless(k, board):  # Discard useless cards
                potential_discards.append(i)

        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))

        # Hinting teammates' playable cards
        playables = []
        for player, hand in enumerate(hands):
            if player != nr:
                for card_index, card in enumerate(hand):
                    if card.is_playable(board):
                        playables.append((player, card_index))

        playables.sort(key=lambda which: -hands[which[0]][which[1]].rank)  # Sort descending by rank
        while playables and hints > 0:
            player, card_index = playables[0]
            hinttype = [HINT_COLOR, HINT_RANK]
            for h in self.hints[(player, card_index)]:
                if h in hinttype:
                    hinttype.remove(h)

            if hinttype:
                t = random.choice(hinttype)
                if t == HINT_RANK:
                    for i, card in enumerate(hands[player]):
                        if card.rank == hands[player][card_index].rank:
                            self.hints[(player, i)].add(HINT_RANK)
                    return Action(HINT_RANK, player=player, rank=hands[player][card_index].rank)
                elif t == HINT_COLOR:
                    for i, card in enumerate(hands[player]):
                        if card.color == hands[player][card_index].color:
                            self.hints[(player, i)].add(HINT_COLOR)
                    return Action(HINT_COLOR, player=player, color=hands[player][card_index].color)

            playables = playables[1:]

        # Fallback: Check for unhinted 5 cards in teammates' hands
        if hints > 0:
            for player, hand in enumerate(hands):
                if player != nr:
                    for card_index, card in enumerate(hand):
                        if card.rank == 5 and HINT_RANK not in self.hints[(player, card_index)]:
                            # Hint the 5 if not already hinted
                            self.hints[(player, card_index)].add(HINT_RANK)
                            return Action(HINT_RANK, player=player, rank=5)

        # Fallback discard (if no valid plays, hints, or guaranteed discards)
        return Action(DISCARD, card_index=0)


    def inform(self, action, player):
        if action.type in [PLAY, DISCARD]:
            if (player,action.card_index) in self.hints:
                self.hints[(player,action.card_index)] = set()
            for i in range(5):
                if (player,action.card_index+i+1) in self.hints:
                    self.hints[(player,action.card_index+i)] = self.hints[(player,action.card_index+i+1)]
                    self.hints[(player,action.card_index+i+1)] = set()

agent.register("impouter", "Improved Outer Agent", ImprovedOuterAgent)
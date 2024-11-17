from hanabi import *
import agent
import random
import util

PLAY_CLUE = 0
SAVE_CLUE = 1


# Format hint taken from osawa script
def format_hint(h):
    if h == HINT_COLOR:
        return "color"
    return "rank"

class MyAgent(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.colorHintsToProcess = {}
        self.rankHintsToProcess = {}
        self.hints = {}
        self.pnr = pnr
        self.explanation = []
        self.hand = None
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        
        for player,hand in enumerate(hands):
            for card_index in range(5):
                if (player,card_index) not in self.hints:
                    self.hints[(player,card_index)] = set()
            if (player) not in self.colorHintsToProcess:
                self.colorHintsToProcess[(player)] = ""
            if (player) not in self.rankHintsToProcess:
                self.rankHintsToProcess[(player)] = ""

        my_knowledge = knowledge[nr]


        # Process color hints
        for h, c in self.colorHintsToProcess.items():
            for i in range(5):
                if(util.has_property(util.has_color(c), my_knowledge[i])):
                    print("Card " + str(i) + " is color " + str(c))
                    self.hints[(h,i)].add(format_hint(HINT_COLOR))
                    # known[i] += format_hint(HINT_COLOR)
            self.colorHintsToProcess[h] = ""

        # Process rank hints
        for h, r in self.rankHintsToProcess.items():
            for i in range(5):
                if(util.has_property(util.has_rank(r), my_knowledge[i])):
                    print("Card " + str(i) + "is rank " + str(r))
                    self.hints[(h,i)].add(format_hint(HINT_RANK))
                    # known[i] += format_hint(HINT_RANK)
            self.rankHintsToProcess[h] = ""
        
        # Known hints about myself
        known = [""]*5

        for card_index in range(5):
            for hint in self.hints[(self.pnr, card_index)]:
                print("card number" + str(card_index) + " " + str(hint))
                known[card_index] += str(hint)

        # Get current chop card (-1 means played does not have a chop card)
        for i in range(4, -1, -1):
            if known[i] == "":
                print("chop card found")
                known[i] += "chop"
                chop = i
                break

        # Get next player's chop
        nextPlayerChop = -1
        for i in range(4, -1, -1):
            if len(self.hints[(self.pnr + 1 % len(hands)), i]) == 0:
                nextPlayerChop = i
                break


        self.explanation = [["next player's chop card = " + str(nextPlayerChop + 1) + "| hints known: "] + known]
        # Check for playable cards while keeping track of useless cards in the case that we don't find any playable ones
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
        
        # Try to give a hint
        if hints > 0:
            for player,hand in enumerate(hands):
                if player != nr:
                    for card_index,card in enumerate(hand):
                        if card.is_playable(board):                              
                            if random.random() < 0.5:
                                return Action(HINT_COLOR, player=player, color=card.color)
                            return Action(HINT_RANK, player=player, rank=card.rank)

        # If we could not play a card and have found a useless card, discard the rightmost useless card
        if chop:
            return Action(DISCARD, card_index=chop)
        

        # HINTS:
        # PLAY CLUE: assume all "play clues" are delayed play clues (meaning don't play them immediately)

        # Otherwise just choose a random action (for now)
        return random.choice(valid_actions)
    
    
    def inform(self, action, player):
        debug = "self = " + str(self.pnr) + " player's turn = " + str(player) + " targeted player = " + str(action.player)
        if action.type == PLAY:
            debug+=" Play "
        elif action.type == DISCARD:
            debug+=" Discard "
        elif action.type == HINT_COLOR:
            debug+=" Hint Color "
        else:
            debug+=" Hint Rank "

        print(debug + " | card ind: " + str(action.card_index) + " | color: " + str(action.color) + " | rank: " + str(action.rank))
        # If we play or discard, move our explanation accordingly
        if action.type in [PLAY, DISCARD]:
            if (player,action.card_index) in self.hints:
                self.hints[(player,action.card_index)] = set()
            for i in range(5):
                if (player,action.card_index+i+1) in self.hints:
                    self.hints[(player,action.card_index+i)] = self.hints[(player,action.card_index+i+1)]
                    self.hints[(player,action.card_index+i+1)] = set()
        # If we get a hint, update knowledge accordingly       
        elif action.type == HINT_COLOR:
            self.colorHintsToProcess[action.player] = action.color
        elif action.type == HINT_RANK:
            self.rankHintsToProcess[action.player] = action.rank
                   

agent.register("mine", "Benjamin and Mark's Agent", MyAgent)
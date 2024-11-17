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
        self.hints = {}
        self.pnr = pnr
        self.explanation = []
        self.hand = None
        self.color_hint = None
        self.rank_hint = None
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        
        my_knowledge = knowledge[nr]
        known = [""]*5


        if self.color_hint != None:
            print("GOT COLOR HINT")
            for i in range(5):
                if(util.has_property(util.has_color(self.color_hint), my_knowledge[i])):
                    print("Card " + str(i) + " is color " + str(self.color_hint))
                    known[i] += format_hint(HINT_COLOR)
            self.color_hint = None

        if self.rank_hint != None:
            print("GOT RANK HINT")
            for i in range(5):
                if(util.has_property(util.has_rank(self.rank_hint), my_knowledge[i])):
                    print("Card " + str(i) + "is rank " + str(self.rank_hint))
                    known[i] += format_hint(HINT_RANK)
            self.rank_hint = None
        
        
        # Get current chop card (-1 means played does not have a chop card)
        for i in range(4, -1, -1):
            if known[i] == "":
                print("chop card found")
                known[i] += "chop"
                break


        self.explanation = [["hints known:"] + known]
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

        # # If we could not play a card and have found a useless card, discard the rightmost useless card
        # if chop:
        #     # print(str(max(potential_discards)) + str(potential_discards))
        #     return Action(DISCARD, card_index=max(potential_discards))
        

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
        # We only care about the hints that WE got
        if action.player != self.pnr:
            return
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
            self.color_hint = action.color
        elif action.type == HINT_RANK:
            self.rank_hint = action.rank
                   

agent.register("mine", "Benjamin and Mark's Agent", MyAgent)
from hanabi import *
import agent
import random
import util

class MyAgent(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.explanation = []
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
        my_knowledge = knowledge[nr]
        known = [""]*5
        potential_discards = []

        # Get current chop card (-1 means played does not have a chop card)
        chop_card = my_knowledge[0]
        self.explanation = [["chop_card:" + str(chop_card)] + known]

        # Check for playable cards while keeping track of useless cards in the case that we don't find any playable ones
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
            if util.is_useless(k, board):    
                potential_discards.append(i)
        
        # If we could not play a card and have found a useless card, discard a useless card
        if potential_discards:
            return Action(DISCARD, card_index=random.choice(potential_discards))


        # HINTS:
        # PLAY CLUE: assume all "play clues" are delayed play clues (meaning don't play them immediately)

        # Otherwise just choose a random action (for now)
        return random.choice(valid_actions)


agent.register("mine", "Benjamin and Mark's Agent", MyAgent)
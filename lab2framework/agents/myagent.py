from hanabi import *
import agent
import random
import util

PLAY_CLUE = 8
SAVE_CLUE = 9


# Format hint taken from osawa script
def format_hint(h):
    if h == HINT_COLOR:
        return "color"
    elif h == PLAY_CLUE:
        return "play clue"
    elif h == SAVE_CLUE:
        return "save clue"
    return "rank"

# Check if a card needs to be saved
def needs_save(card, board, trash, played):
    # Save all 5's
    if card.rank == 5:
        return True
    
    # If we have not played a 2 of that color yet, save a 2
    if card.rank == 2 and board[card.color].rank < 2:
        return True 

    # Check if card is a "critical card"
    if card.rank == 1:
        count = 3
    else:
        count = 2

    count -= trash.count((card.color, card.rank)) + played.count((card.color, card.rank))

    # If there are no remaining cards of this color and rank, return true
    if count == 0:
        return True

    # If none are true, then we don't need to save
    return False


class MyAgent(agent.Agent):
    def __init__(self, name, pnr):
        self.name = name
        self.colorHintsToProcess = {}
        self.rankHintsToProcess = {}
        self.hints = {}
        self.pnr = pnr
        self.explanation = []
        self.hand = None
        self.hintsSetup = False
    def get_action(self, nr, hands, knowledge, trash, played, board, valid_actions, hints, hits, cards_left):
            
        for player,hand in enumerate(hands):
            for card_index in range(5):
                if (player,card_index) not in self.hints:
                    print("missing hints")
                    self.hints[(player,card_index)] = set()
            if (player) not in self.colorHintsToProcess:
                self.colorHintsToProcess[(player)] = ""
            if (player) not in self.rankHintsToProcess:
                self.rankHintsToProcess[(player)] = ""

        my_knowledge = knowledge[nr]

        # Get chop before processing hint
        chop = -1
        for i in range(4, -1, -1):
            if len(self.hints[((self.pnr + 1) % len(hands)), i]) == 0:
                chop = i
                break

        # Process color hints
        for h, c in self.colorHintsToProcess.items():
            for i in range(5):
                if(util.has_property(util.has_color(c), my_knowledge[i])):
                    if len(self.hints[(h,i)]) == 0:
                        self.hints[(h,i)].add(format_hint(HINT_COLOR))
                        print("Add hint to player " + str(h) + " card " + str(i))
                        if i == chop:
                            self.hints[(h,i)].add(format_hint(SAVE_CLUE))
                        else:
                            self.hints[(h,i)].add(format_hint(PLAY_CLUE))
            self.colorHintsToProcess[h] = ""

        # Process rank hints
        for h, r in self.rankHintsToProcess.items():
            for i in range(len(hands[h])):
                if(util.has_property(util.has_rank(r), my_knowledge[i])):
                    self.hints[(h,i)].add(format_hint(HINT_RANK))
                    print("Add hint to player " + str(h) + " card " + str(i))
                    if len(self.hints[(h,i)]) == 0:
                        if i == chop:
                            self.hints[(h,i)].add(format_hint(SAVE_CLUE))
                        else:
                            self.hints[(h,i)].add(format_hint(PLAY_CLUE))
            self.rankHintsToProcess[h] = ""
        
        # Known hints about myself
        known = [""]*5

        for card_index in range(5):
            for hint in self.hints[(self.pnr, card_index)]:
                known[card_index] += str(hint) + ", "

        # Get current chop card (-1 means played does not have a chop card)
        chop = -1
        for i in range(4, -1, -1):
            if known[i] == "":
                known[i] += "chop"
                chop = i
                break

        # Get next player's chop
        nextPlayerChop = -1
        playerNo = (self.pnr + 1 ) % len(hands)
        
        for i in range(len(hands[playerNo]) - 1, -1, -1):

            for s in self.hints[(playerNo, i)]:
                print("card index: " + str(i) + " hint: " + str(s))

            if len(self.hints[(playerNo, i)]) == 0:
                print("current player " + str(self.pnr) + " checking chop of player " + str(playerNo) + " chop card: " + str(i))
                nextPlayerChop = i
                break


        self.explanation = [["next player's chop card = " + str(nextPlayerChop + 1) + "| hints known: "] + known]
       
       
        # See if we can give any play clues
        if hints > 0:
            for player,hand in enumerate(hands):
                if player != nr:
                    for card_index,card in enumerate(hand):
                        if card.is_playable(board):                              
                            if random.random() < 0.5:
                                return Action(HINT_COLOR, player=player, color=card.color)
                            return Action(HINT_RANK, player=player, rank=card.rank)

        #See if we need to give any save clues
        if hints > 0:
            for player,hand in enumerate(hands):
                # skip ourself
                if player == self.pnr:
                    continue
                # Find chop of next player
                tnextPlayerChop = -1
                for i in range(len(hand) - 1, -1, -1):
                    # for s in self.hints[player, i]:
                    #     print("card index: " + str(i) + " hints seen " + str(s))
                    if len(self.hints[player, i]) == 0:
                        tnextPlayerChop = i
                        break

                # If next player doesn't have a chop, skip this player
                if tnextPlayerChop == -1:
                    print("no chop found")
                    continue

                # If they do have a chop, check if chop needs to be saved
                card = hand[tnextPlayerChop]
                if needs_save(card, board, trash, played):
                    #print("CHOP INDEX SAVE " + str(tnextPlayerChop) + " Player No. " + str(player) + str(self.pnr) + " Hand " + str(hand) + " hints: " + str(self.hints[(player,i)]))
                    if random.random() < 0.5:
                        return Action(HINT_COLOR, player=player, color=card.color)
                    return Action(HINT_RANK, player=player, rank=card.rank)
 

        # Play any playable cards
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)
                          
        # Try to play a play clue

        # If we could not play a card and cannot give any helpful clues, discard the chop
        if chop != -1:
            return Action(DISCARD, card_index=chop)
        
        # If we do not have a chop, then play the card that has the highest probability of being playable

        # Play a save clue

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
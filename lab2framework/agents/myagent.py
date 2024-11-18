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
        return "play"
    elif h == SAVE_CLUE:
        return "save"
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

        # Set up hint lists and dictionaries
        for player,hand in enumerate(hands):
            for card_index in range(5):
                if (player,card_index) not in self.hints:
                    #print("missing hints")
                    self.hints[(player,card_index)] = set()
            if (player) not in self.colorHintsToProcess:
                self.colorHintsToProcess[(player)] = ""
            if (player) not in self.rankHintsToProcess:
                self.rankHintsToProcess[(player)] = ""

        # for i in hands[1]:
        #     print("Player 1 Card " + str(i))
        
        # for h, r in self.rankHintsToProcess.items():
        #     print("Rank hint to process || Player = " + str(h) + " Rank = " + str(r)) 
        
        # for h, c in self.colorHintsToProcess.items():
        #     print("Color hint to process || Player = " + str(h) + " Color = " + str(c)) 

        my_knowledge = knowledge[nr]

        


        # Process color hints
        for h, c in self.colorHintsToProcess.items():
            # Get the chop of the player before processing hint
            chop = -1
            for i in range(4, -1, -1):
                if len(self.hints[(h, i)]) == 0:
                    chop = i
                    break
            for i in range(5):
                if(c == ""):
                    continue
                #print("Color hint to process || Player = " + str(h) + " Color = " + str(c)) 
                if(util.has_property(util.has_color(c), knowledge[h][i])):
                    if len(self.hints[(h,i)]) == 0:
                        #print("Add hint to player " + str(h) + " card " + str(i) + " chop card " + str(chop))
                        if i == chop:
                            self.hints[(h,i)].add(format_hint(SAVE_CLUE))
                        else:
                            self.hints[(h,i)].add(format_hint(PLAY_CLUE))
                        self.hints[(h,i)].add(format_hint(HINT_COLOR))
            self.colorHintsToProcess[h] = ""

        # Process rank hints
        for h, r in self.rankHintsToProcess.items():
            for i in range(5):
                if(r == ""):
                    continue
                #print("Rank hint to process || Player = " + str(h) + " Rank = " + str(r)) 
                if(util.has_property(util.has_rank(r), knowledge[h][i])):
                    #print("Add hint to player " + str(h) + " card " + str(i) + " chop card " + str(chop))
                    if len(self.hints[(h,i)]) == 0:
                        if i == chop:
                            self.hints[(h,i)].add(format_hint(SAVE_CLUE))
                        else:
                            self.hints[(h,i)].add(format_hint(PLAY_CLUE))
                    self.hints[(h,i)].add(format_hint(HINT_RANK))
            self.rankHintsToProcess[h] = ""

        # for player, index in self.hints:
        #     print("Player " + str(player) + " index " + str(index) + " " + str(self.hints[player, index]))
        
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
        playerNo = (self.pnr + 1 )% len(hands)
        
        for i in range(4, -1, -1):
            if len(self.hints[(playerNo, i)]) == 0:
                nextPlayerChop = i
                break


        self.explanation = [["next player's chop card = " + str(nextPlayerChop + 1) + "| hints known: "] + known]
       
       
        # See if we can give any play clues
        if hints > 0:
            for player,hand in enumerate(hands):
                if player != nr:
                    for card_index,card in enumerate(hand):
                        if card.is_playable(board) and len(self.hints[(player, card_index)]) == 0:  
                            hintcolor = False
                            if random.random() < 0.5:
                                hintcolor = True
                            if hintcolor and ("color" not in self.hints[(player, card_index)]):
                                #print("Play Clue " + str(self.hints[(player, card_index)]))
                                return Action(HINT_COLOR, player=player, color=card.color)
                            elif hintcolor and"rank" not in self.hints[(player, card_index)]:
                                return Action(HINT_RANK, player=player, rank=card.rank)    
                            if not hintcolor and ("rank" not in self.hints[(player, card_index)]):
                                #print("Play Clue " + str(self.hints[(player, card_index)]))
                                return Action(HINT_RANK, player=player, rank=card.rank)
                            elif not hintcolor and "rank" not in self.hints[(player, card_index)]:
                                return Action(HINT_RANK, player=player, rank=card.rank)       


        #See if we need to give any save clues
        if hints > 0:
            for player,hand in enumerate(hands):
                # skip ourself
                if player == self.pnr:
                    continue
                # Find chop of next player
                #print("Trying Save Clue")
                tnextPlayerChop = -1
                for i in range(len(hands[player]) - 1, -1, -1):
                    # for s in self.hints[(player, i)]:
                    #     print("player " + str(player) + " card index: " + str(i) + " hint: " + str(s))

                    if len(self.hints[(player, i)]) == 0:
                        #print("current player " + str(self.pnr) + " checking chop of player " + str(player) + " chop card: " + str(i))
                        tnextPlayerChop = i
                        break

                # If next player doesn't have a chop, skip this player
                if tnextPlayerChop == -1:
                    #print("no chop found")
                    continue

                # If they do have a chop, check if chop needs to be saved
                card = hand[tnextPlayerChop]
                #print("Check Save clue")
                if needs_save(card, board, trash, played):
                    #print("CHOP INDEX SAVE " + str(tnextPlayerChop) + " Player No. " + str(player) + str(self.pnr) + " Hand " + str(hand) + " hints: " + str(self.hints[(player,i)]))
                    hintcolor = False
                    if random.random() < 0.5:
                        hintcolor = True
                    if hintcolor and ("color" not in self.hints[(player, card_index)]):
                        #print("Play Clue " + str(self.hints[(player, card_index)]))
                        return Action(HINT_COLOR, player=player, color=card.color)
                    elif hintcolor and"rank" not in self.hints[(player, card_index)]:
                        return Action(HINT_RANK, player=player, rank=card.rank)    
                    
                    if not hintcolor and ("rank" not in self.hints[(player, card_index)]):
                        #print("Play Clue " + str(self.hints[(player, card_index)]))
                        return Action(HINT_RANK, player=player, rank=card.rank)
                    elif not hintcolor and "rank" not in self.hints[(player, card_index)]:
                        return Action(HINT_RANK, player=player, rank=card.rank)    
 

        # Play any playable cards
        for i,k in enumerate(my_knowledge):
            if util.is_playable(k, board):
                return Action(PLAY, card_index=i)

        # Try to play a play clue if we have extra hits to spare
        #print("hits " + str(hits))
        best_card = -1
        max_probability = 0
        if hits > 0:
            for player, index in self.hints:
                if player == self.pnr:
                    if "play" in self.hints[(player, index)]:
                        # prob = util.probability(util.playable(board), my_knowledge[index])
                        # if prob > max_probability:
                        #     max_probability = prob
                        #     best_card = index
                        #print("Play off of a play clue " + str(best_card) + " prob " + str(max_probability))
                        return Action(PLAY, card_index=index)
            # if best_card != -1:
            #     print("Play off of a play clue " + str(best_card) + " prob " + str(max_probability))
            #     return Action(PLAY, card_index=best_card)
            
        # If there is a card that has no chance of being playable, discard that card
        for i,k in enumerate(my_knowledge):
            if util.is_useless(k, board):
                #print("CARD IS NOT PLAYABLE" + str(i))
                return Action(DISCARD, card_index=i)

        # If we could not play a card and cannot give any helpful clues, discard the chop 
        if chop != -1:
            #print("Discarding Chop")
            return Action(DISCARD, card_index=chop)
        
        best_card = -1
        max_probability = 0
        if hits > 0:
            for player, index in self.hints:
                if player == self.pnr:
                    if  "save" in self.hints[(player, index)] or "play" in self.hints[(player, index)]:
                        #print("TEST2")
                        prob = util.probability(util.playable(board), my_knowledge[index])
                        #print("Prob" + str(prob))
                        if prob > max_probability:
                            max_probability = prob
                            best_card = index
            if best_card != -1:
                #print("Play off of a save clue " + str(best_card) + " prob " + str(max_probability))
                return Action(PLAY, card_index=best_card)
            

        
        # If we do not have a chop, then play the card that has the highest probability of being playable

        # HINTS:
        # PLAY CLUE: assume all "play clues" are delayed play clues (meaning don't play them immediately)

        # Otherwise just choose a random action (for now)
        #print("random choice")
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

        #print(debug + " | card ind: " + str(action.card_index) + " | color: " + str(action.color) + " | rank: " + str(action.rank))
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
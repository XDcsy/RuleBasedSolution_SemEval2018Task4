# The script for entity linking based on coreference chains
# results are stored in var named "result"

# TRAIN_DATA_PATH = "dat/friends.train.scene_delim.conll"
# TEST_DATA_PATH_NOKEY = "dat/friends.test.scene_delim.conll.nokey"
# TEST_DATA_PATH_KEY = "dat/friends.test.scene_delim.conll"

# path to coref results or gold test data
# if inputting coref results, one file should only contain one scene/episode
COREF_DATA_PATH = "dat/friends.test.scene_delim.conll"

##############################################################################
def vote(words, speaker, weight, pos, characterid , index):
                recognized = False
                # get the text of the mention
                mention = words[index]
                mention = mention.lower()
                if mention in {"i", "me", "my", "mine", "myself"}:
                    # get the speaker of the mention
                    speaker = speaker[index].replace("_", " ")
                    # look for the speaker id
                    if speaker in character_dict:
                        referto = character_dict[speaker]
                        recognized = True
                        return referto
                if mention in {"you", "your", "yours", "ya", "yourself"}:
                    # look for the previous speaker id
                    # keep going back until a different speaker
                    i = index
                    while (i > 0):
                        i = i - 1
                        if words[i] == "#EOS#" and speaker[i-1] != speaker[i+1]:
                            break
                    # no previous speaker
                    if i == 0:
                        return 386
                    else:
                        previous_speaker = speaker[i-1].replace("_", " ")
                    if previous_speaker in character_dict:
                        referto = character_dict[previous_speaker]
                        recognized = True
                        return referto
                # search the name directly
                # if mention in name_list and _pos[x][index] == 1:
                # also match some NN can improve the result
                # but need to manully exclude some ambiguous NN like "guy"
                if mention in name_list and mention != "guy":
                    referto = id_list[name_list.index(mention)]
                    recognized = True
                    return referto
                if recognized == False:
                    return 386

def most_common(lst):
    # unknown does not vote
    new_lst = [value for value in lst if value != 386]
    if len(new_lst) > 0:
        return max(set(lst), key=lst.count)
    else:
        return 386
   
    
    
###############################################################################


# load coreference chain data
# or load gold test data
f = open(COREF_DATA_PATH)
test_lines = f.readlines()
f.close()

_words = []
_speaker = []
_weight = []
_pos = []
_characterid = []

# start to load one scene or episode
for line in test_lines:
    line_s = line.split()
    if "#begin document" in line:
        # prepare some temp varibles
        # to store the content of current sceen or episode
        words_tmp = []
        speaker_tmp = []
        pos_tmp = []
        weight_tmp = []
        characterid_tmp = []
    elif "#end document" in line:
        # append their content when meet end of sceen or episode
        _words.append(words_tmp)
        _speaker.append(speaker_tmp)
        _pos.append(pos_tmp)
        _weight.append(weight_tmp)
        _characterid.append(characterid_tmp)
    else:
        # there should be 12 annatators in a valid line
        if len(line_s) == 12:
            words_tmp.append(line_s[3].lower())
            speaker_tmp.append(line_s[9])
            
            # read pos
            # 1:nnp, 2: prp & prp$, 3:nn, 4: other tags, 5: end of sentence
            if line_s[4].lower() == "nnp":
                pos_tmp.append(1)
            elif line_s[4].lower() in {"prp", "prp$"}:
                pos_tmp.append(2)
            elif line_s[4].lower() == "nn":
                pos_tmp.append(3)
            else:
                pos_tmp.append(4)
                
            # for mentions that is longer than one word
            # only record the last word of the mention for simplicity
            if ")" in line_s[11]:
                id_ = line_s[11].replace("-","")
                id_ = id_.replace("(","").replace(")","")
                characterid_tmp.append(int(id_))
                # also record the weight
                weight_tmp.append(1)
            else:
                characterid_tmp.append(0)
                weight_tmp.append(0)

        # otherwise it should be a blank line
        # suggesting a split of sentence
        else:
            words_tmp.append("#EOS#") # end of sentence
            speaker_tmp.append("#EOS#")
            pos_tmp.append(5)
            characterid_tmp.append(0)
            weight_tmp.append(0)
    
if __name__ == "__main__":
    id_list = []
    name_list = []
    character_dict = {}
    result = ""
    
    # read character library
    with open("data/friends_entity_map_modified.txt", "r") as f:
        text = f.read()
        splited_text = text.split('\n')
        for l in splited_text:
            splited_line = l.split()
            if len(splited_line) > 0:
                # avoid empty line
                character_id = splited_line[0]
                character_name = []
                original_name = []
                for i in range(1, len(splited_line)):
                    original_name.append(splited_line[i])
                    id_list.append(character_id)
                    name_list.append(splited_line[i].lower())
                    character_name.append(splited_line[i])
                full_name = ' '.join(original_name)
                character_dict[full_name] = character_id

    t_character_dict = inv_map = {v: k for k, v in character_dict.items()}


    # start entity linking
    for x in range(0, len(_words)):
        # find the chains of the result
        chains = set(_characterid[x])
        for chain_number in chains:
            # ignore the words without corefrence labels
            if chain_number == 0:
                continue
            # index list of all the chain members
            index_list_of_members = [i for i,val in enumerate(_characterid[x]) if val == chain_number]
            # each member votes for a mention
            # a list to store all the votes
            all_votes = []
            for member_index in index_list_of_members:
                all_votes.append(vote(_words[x], _speaker[x], _weight[x], _pos[x], _characterid[x], member_index))
            winning_character = most_common(all_votes)
            # use _weights[] to record the winpos
            for member_index in index_list_of_members:
                _weight[x][member_index] = winning_character
    
    # output
    for x in range(0, len(_words)):
        for result_lable in _weight[x]:
            if result_lable != 0:
                result += str(result_lable) + "\n"
            
print(result)




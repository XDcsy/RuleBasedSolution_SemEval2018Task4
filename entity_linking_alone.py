# The script for performing entity linking alone
# results are stored in var named "output"

# set these paths for loading the dataset
# this script can run without loading gold test data
# note there is some commented code for error analysis
# when doing error analysis uncomment them and load gold test data instead
# TRAIN_DATA_PATH = "dat/friends.train.scene_delim.conll"
TEST_DATA_PATH_NOKEY = "dat/friends.test.scene_delim.conll.nokey"
# TEST_DATA_PATH_KEY = "dat/friends.test.scene_delim.conll"

# use a modefied charactor library to produce best result
# where the mentions are ranked by its frequency
CHARACTER_LIBRARY_PATH = "dat/friends_entity_map_modified.txt"

# read character library
id_list = []
name_list = []
character_dict = {}

f = open(CHARACTER_LIBRARY_PATH)
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
f.close()

# load test data ( no key )
f = open(TEST_DATA_PATH_NOKEY)
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
            
            
# start entity linking
t_character_dict = inv_map = {v: k for k, v in character_dict.items()}
found_el = 0
corrcet_el = 0
all_el = 0
incorrect = ""
output = ""
log = ""

# this set and the cluster F1 below etc. are not necessary for entitying linking
# they are just used for error analysis
set_major_speakers = {'Ross Geller', 'Joey Tribbiani', 'Chandler Bing', 'Monica Geller', 'Phoebe Buffay', 'Rachel Green', 'Carol Willick', 'Mindy', 'Barry'}

for x in range(0, len(_words)):
        set_text_speakers = set([speaker.replace("_", " ") for speaker in _speaker[x]])
        set_found_speakers = set()
        # set_found_major_speakers = set()
        set_major_exsist = set()
        major_exsist_count = 0
        major_correct_count = 0
        for index in range(0, len(_words[x])):
            found_correct = False
            # record the previous speaker
            if index == 0:
                previous_speaker = "None"
            if _words[x][index] == "#EOS#":
                # when the speaker in the last sentence is difference from the current one
                if index + 1 < len(_words[x]) and _speaker[x][index-1] != _speaker[x][index+1]:
                    previous_speaker = _speaker[x][index-1].replace("_", " ")
            # when it is a mention
            recognized = False
            if _weight[x][index] != 0:
                all_el += 1
                # get the text of the mention
                mention = _words[x][index]
                mention = mention.lower()
                # add the mention to the exsist set
                if _characterid[x][index] in {335, 183, 59, 248, 292, 306, 51, 242, 29}:
                    set_major_exsist.add(t_character_dict[str(_characterid[x][index])])
                    major_exsist_count += 1
                if mention in {"i", "me", "my", "mine", "myself"}:
                    # get the speaker of the mention
                    speaker = _speaker[x][index].replace("_", " ")
                    # look for the speaker id
                    if speaker in character_dict:
                        referto = character_dict[speaker]
                        found_el += 1
                        output += referto + "\n"
                        recognized = True
                        set_found_speakers.add(speaker)
                    # check correctness
                    if int(referto) == _characterid[x][index]:
                        corrcet_el += 1
                        found_correct = True
                        if speaker in set_major_exsist:
                            major_correct_count += 1
                if mention in {"you", "your", "yours", "ya", "yourself"}:
                    # look for the previous speaker id
                    if previous_speaker in character_dict:
                        referto = character_dict[previous_speaker]
                        found_el += 1
                        output += referto + "\n"
                        recognized = True
                        set_found_speakers.add(previous_speaker)
                    # check correctness
                    if int(referto) == _characterid[x][index]:
                        corrcet_el += 1
                        found_correct = True
                        if previous_speaker in set_major_exsist:
                            major_correct_count += 1
#        ##### error analysis
#                    else:
#                        print("error in episode or scene", x)
#                        print(t_character_dict[str(_characterid[x][index])]+ ' is linked to '+ t_character_dict[referto])
#                        log += "error in episode " + str(x) + "  " + t_character_dict[str(_characterid[x][index])]+ ' is linked to '+ t_character_dict[referto] + '\n'
#                        log += "words nearby:" + _words[x][index-2] + " " + _words[x][index-1] + " " + _words[x][index] + " " + _words[x][index+1] + " " + _words[x][index+2] + "\n"
                # search the name directly
                if mention in name_list and _pos[x][index] == 1:
                    referto = id_list[name_list.index(mention)]
                    found_el += 1
                    output += referto + "\n"
                    recognized = True
                    set_found_speakers.add(t_character_dict[referto])
                    if int(referto) == _characterid[x][index]:
                        corrcet_el += 1
                        found_correct = True
                        if t_character_dict[referto] in set_major_exsist:
                            major_correct_count += 1
        ##### error analize
#                    else:
#                        print("error in episode", data_test_with_key.index(scene))
#                        print(t_character_dict[str(scene[3][index])]+ ' is linked to '+ t_character_dict[referto])
                if recognized == False:
                    output += "386" + "\n" # 386 is UNKNOWN
        # incorrect mentions
#                if found_correct == False:
#                    incorrect = incorrect + t_character_dict[str(scene[3][index])]+"\n"
        
        # missing mentions
        #print("missing mentions")
        #print(set_text_speakers - (set_text_speakers&set_found_speakers))
        
        #####
        
        # cluster f1
        # len(set) - 1 to discard the sentence split
        # print('all clusters', len(set_text_speakers)-1, 'found clusters', len(set_found_speakers), 'correct clusters', len(set_text_speakers&set_found_speakers))

        # major accuracy
        #print('total mentions of major charactors ', major_exsist_count, 'correctly labeled mentions', major_correct_count)

print(output)
print('all mentions ', all_el, ', found mentions after el ', found_el, ', correct mentions after el ', corrcet_el)
if corrcet_el == 0:
    print('###')
    print('error analysis need to load gold test data')
    print('if correct mentions shows 0, check if gold test data is loaded')

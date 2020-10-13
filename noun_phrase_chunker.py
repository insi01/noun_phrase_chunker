import nltk
from nltk.stem import WordNetLemmatizer

# as input you just have to create a tab-separated text file with the WOS identifier (UT) and in the next
# column the title and abstract of the publication (these only separated by a space character)
ut_text_list = []
with open('path/to/file/with_UT_TitleAbstract.txt') as f:
    for line in f:
        ut_text_list.append([line.strip().split('\t')[0], line.strip().split('\t')[1]])

patterns = """
           NP: {<JJ><NN|NNP|NNS|NNPS>}
               {<NN|NNP|NNS|NNPS><NN|NNP|NNS|NNPS>}
               {<NN|NNP|NNS|NNPS>}
           """

NPChunker = nltk.RegexpParser(patterns)

def prepare_text(txt):
    txt = ' '.join([word if word.isupper() is False else word.lower() for word in txt.split(' ')])
    tokenized_sentence = nltk.sent_tokenize(txt)
    tokenized_words = [nltk.word_tokenize(sentence) for sentence in tokenized_sentence]

    tagged_words = [nltk.pos_tag(word) for word in tokenized_words] 
    word_tree = [NPChunker.parse(word) for word in tagged_words]  
    return word_tree


def return_a_list_of_NPs(sentences):
    nps = []  
    for sent in sentences:
        tree = NPChunker.parse(sent)
        for subtree in tree.subtrees():
            if subtree.label() == 'NP':
                t = subtree
                words = [item[0] for item in t.leaves()]
                tags = [item[1] for item in t.leaves()]
                if 'CC' in tags:
                    cc_pos = tags.index('CC')
                    for i in range(0,cc_pos):
                        nps.append(words[i] + ' ' + words[-1])
                    if words[cc_pos+1] != words[-1]:
                        nps.append(words[cc_pos+1] + ' ' + words[-1])
                    else:
                        nps.append(words[-1])
                else:
                    t = ' '.join(word for word, tag in t.leaves())
                    nps.append(t)
    return nps

def strip_leadingspecialchars(word):
    start_id = 0
    for k in range(0, len(word)):
        if word[k].isalpha():
            return start_id
        else:
            start_id += 1

def strip_endingspecialchars(word):
    end_id = 0
    for k in range(0, len(word)):
        if word[-1 - k].isalpha():
            return end_id
        else:
            end_id -= 1

wordnet_lemmatizer = WordNetLemmatizer()

def writeOutput():
    with open('outputpath/to/UT_extractednounphrases.txt', 'w') as f:
        for item in ut_text_list:
            txt = item[1]
            ut = item[0]
            sentences = prepare_text(txt)
            wordlist = return_a_list_of_NPs(sentences)
            lemmawordlist = []
            for word in wordlist:
                if 'elsevier' in word.lower() or 'copyright' in word.lower():
                    pass
                else:
                    hasAlpha = 0
                    for k in range(0, len(word)):
                         if word[k].isalpha() == True:
                             hasAlpha = 1
                    if hasAlpha == 0:
                        word = ''
                    else:    # strip leading and ending non alphanumeric characters
                        start_id = strip_leadingspecialchars(word)
                        end_id = strip_endingspecialchars(word)
                    if end_id == 0:
                        word = word[start_id:]
                    else: word = word[start_id:end_id]
                    if len(word.strip()) > 2:
                       lemmawordlist.append(word.lower().strip())

            lemmawordlist = set(lemmawordlist)
            f.write(ut + '\t' + ','.join(lemmawordlist) + '\n')

writeOutput()

'''
grammars.py - "Grammar transform" functions
'''
import io
import random

def randomize(value, bound):
    '''
    Returns a a random value+/- bound
    :param value:
    :param bound:
    '''
    return random.randrange((value - bound),(value + bound))

def headline(data, **options):
    '''
    Returns string with each word capitalized
    :param data:
    '''
    return " ".join([str(x).lower().capitalize() for x in data])

def sentence(data, **options):
    '''
    Returns string with first word capitalized and punctuation added.
    :param data:
    '''
    
    last_comma = 0
    last_semic = 0
    
    output = []
    for i in range(len(data)):
        comma_freq = randomize(options.get("comma_freq", 7), 2)
        semic_freq = randomize(options.get("semiq_freq", 15), 2) 

        word = str(data[i]).lower()
        if i == 0:
            word = word.capitalize()
        
        
        if (last_comma + comma_freq) < i:
            word = word + ","

        if (last_semic + semic_freq) < i:
            word = word + ";"
            
        output.append(word)
    
    return " ".join(output) + ". "
        
def body(data, **options):
    '''
    Returns string of sentences with paragraphs
    :param data:
    '''
    output = io.StringIO()
    output.write("\t")

    para_len     = randomize(options.get("para_len", 5), 2)
    pos          = 0
    sentences    = 0
    
    while True:
        # Slice out a sentence worth of data and transform it to a sentence.
        sentence_len = randomize(options.get("sentence_len", 10), 2)
        sliced = data[pos:(pos+sentence_len)]
        if len(sliced) > 0:
            output.write(sentence(sliced, **options))
            sentences = sentences + 1
            pos       = pos + sentence_len
            if sentences >= para_len:
                output.write("\n\n\t")
                para_len = randomize(options.get("para_len", 5), 2)
        else:
            break
    
    text_body = output.getvalue().rstrip() + "\n\n"
    output.close()
    return text_body

def json_list(data, **options):
    '''
    Returns a list suitable for use in JSON/BSON
    :param data:
    '''
    return [str(x).lower() for x in data]
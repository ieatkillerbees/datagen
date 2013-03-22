'''
dictionaries.py

Data dictionaries
'''
import os
import random
import sys

class Dictionary(object):
    '''
    Dictionary base class. Dictionaries generate data
    '''
    datafile = None        # Input file
    words    = []        # Collection of dictionary entries

    def __init__(self, datafile=None):
        '''
        Initializes the dictionary with an optional datafile.
        :param datafile:
        '''
        if datafile != None:
            self.datafile = datafile

        sys.stdout.write("* Loading %s..." % self.__class__.__name__)
        sys.stdout.flush()

        self.words = self.load()

        sys.stdout.write("done! Loaded %d bytes\n" % sys.getsizeof(self.words))
        sys.stdout.flush()
                

    def load(self):
        '''
        Return a list of words.
        '''
        raise Exception("Not implemented")

    def generate_data(self, size=0, **options):
        '''
        Generates a collection of random data. 
        :param size:            Amount of data to return, depending on class 
                                context. Can be an int or range.
        '''
        # Calculate the size. If a sequence, take the first two elements as 
        # the lower and upper bounds of a range, and select a random element
        # therein.
        try:
            size = int(random.randrange(size[0], size[1]))
        except TypeError:
            try: 
                size = int(size)
            except TypeError:
                raise
            
        # Generate a list of random selections from the the word list.
        return [random.choice(self.words) for x in range(size)]
        
        
class NamesDictionary(Dictionary):
    '''
    Dictionary to generate random names.
    '''
    datafile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "data/randomNames.csv"))

    def load(self):
        '''
        Load the data from the file. The data is csv and will be returned as a 
        list of dictionaries.
        '''
        words = []
        try:
            with open(self.datafile, "r") as fp:
                for line in fp.readlines():
                    if not line:
                        continue
                    line = line.strip().split(",")
                    entry = {}
                    entry["first_name"] = line[0]
                    entry["last_name"] = line[1]
                    entry["middle_init"] = line[2]
                    entry["full_name"] = line[3]
                    words.append(entry)
        except Exception as exc:
            raise Exception("Names dictionary file '%s' does not exist or could\
                             not be opened: %s" % (self.datafile, str(exc)))
        else:
            return words

    def generate_data(self, size=0, **options):
        '''
        Options should contain a kwarg 'subfield' that maps to a key in a
        name dictionary (first_name, last_name, middle_init_, full_name)
        :param data:
        :param field_type:
        '''
        try:
            size = int(random.randrange(size[0], size[1]))
        except TypeError:
            try: 
                size = int(size)
            except TypeError:
                raise
            
        # Generate a list of random selections from the the word list.
        data     = [random.choice(self.words) for x in range(size)]
        
        subfield = options.get("subfield", "full_name")
        
        if subfield not in ["first_name", "last_name", 
                            "middle_init", "full_name"]:
            raise Exception("Invalid subfield specified.")
        
        return [name.get(subfield, " ") for name in data]

class WordsDictionary(Dictionary):
    '''
    Dictionary of English words
    '''
    datafile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "data/en-words.txt"))

    def load(self):
        '''
        Load the data file.
        '''
        words = [] 
        try:
            with open(self.datafile) as fp:
                for word in fp.readlines():
                    if not word:
                        continue
                    words.append(word.strip())
        except Exception as exc:
            raise Exception("Words dictionary file '%s' does not exist or could\
                             not be opened: %s" % (self.datafile, str(exc)))
        else:
            return words

class LipsumDictionary(Dictionary):
    '''
    Dictionary of lorem ipsum words.
    '''
    datafile = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                            "data/lorem.txt"))

    def load(self):
        '''
        Load the file.
        '''
        words = []
        try:
            with open(self.datafile) as fp:
                text = fp.read().replace("\n", " ")
                words = text.split(" ")
        except Exception as exc:
            raise Exception("Lipsum dictionary file '%s' does not exist or\
                             could not be opened: %s" % (self.datafile, 
                                                         str(exc)))
        else:
            return words
        
class NumbersDictionary(Dictionary):
    '''
    Dictionary for generating pseudorandom numbers
    '''
    
    types = {
         "us-telno": ((3,3,4), "+1({0}){1}-{2}"),
         "us-ssn":   ((3,2,4), "{0}-{1}-{2}")
    }
    
    def load(self):
        '''
        Does nothing
        '''
        return 
        
    def generate_data(self, size=0, **options):
        '''
        Generates a random number 
        :param size:            Amount of data to return, depending on class
        context. Can be an int or range.
        '''
        # Calculate the size. If a sequence, take the first two elements as 
        # the lower and upper bounds of a range, and select a random element
        # therein.
        try:
            size = int(random.randrange(size[0], size[1]))
        except TypeError:
            try: 
                size = int(size)
            except TypeError:
                raise
            
        if options["field_type"] not in self.types:
            transform = None
        else:
            transform = self.types[options["field_type"]]
            
        if not transform:
            return "".join([str(random.randrange(1, 9)) for x in range(size)])
        
        numbers    = []
        numstrings = []
        for number in range(size):
            for count in transform[0]:
                numbers.append("".join([str(random.randrange(1, 9)) for x in
                                         range(count)]))
            numstrings.append(transform[1].format(*numbers))
        if len(numstrings) == 1:
            return str(numstrings[0])
        else:
            return numstrings
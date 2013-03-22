'''
output_methods.py

Output handlers
'''

class OutputInterface(object):
    '''
    Base output handler. Does nothing.
    '''
    def clear(self):
        '''
        Does nothing.
        '''
        raise NotImplementedError
    
    def write(self):
        '''
        Does nothing.
        '''
        raise NotImplementedError
    
class MongoInterface(OutputInterface):
    '''
    Mongo handler, writes out to a preconfigured mongo instance.
    '''
    options = {}
    def __init__(self, mongo, dbname, **options):
        '''
        Creates a mongo output interface.
        :param mongo:
        :param dbname:
        '''
        self.output = mongo
        self.dbname = dbname
        self.options.update(options)
        
    def clear(self):
        '''
        Drop the database
        '''
        return self.output.drop_database(self.dbname)

    def write(self, collection, document):
        '''
        Persist a document to output.
        :param collection:
        :param document:
        '''
        db = getattr(self.output, self.dbname)
        return db[collection].insert(document)
    
class StdoutInterface(OutputInterface):
    '''
    Output interface for stdout. Used for testing templates.
    '''
    def __init__(self, *args, **kwargs):
        pass

    def clear(self):
        pass
    
    def write(self, collection, document):
        '''
        Writes the document to stdout and returns a random ID string.
        :param collection:
        :param document:
        '''
        import uuid
        print(document)
        return uuid.uuid4().hex

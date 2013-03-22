'''
generator.py

Random data generator.
'''
from bson.dbref import DBRef
import base64
import cgi
import random
import re
from datagen import grammars


class Generator(object):
    '''
    Generator takes a template and output instance and generates a bunch of
    data.
    '''
    
    dbs     = {}    # Container of word dictionary objects
    ids     = {}    # List of generated dbrefs/IDs
    output  = None  # output interface
    dbname  = None  # output database name
    options  = {}    # Config dictionary

    def __init__(self, template, output, pbar, **options):
        self.template = template
        self.output   = output
        self.pbar     = pbar
        self.options.update(options)
        
        self.dbs["words"]   = options["words"]
        self.dbs["names"]   = options["names"]
        self.dbs["lipsum"]  = options["lipsum"]
        self.dbs["numbers"] = options["numbers"]

    def run(self):
        '''
        Run a data generation process.
        '''
        
        if not self.options["preserve_database"]:
            self.output.clear()
        
        # Loop through the collection definitions in the template list.
        for collection in self.template:
            name = collection["collection_name"]
            count = int(collection["count"])
            self.generate_collection(name, count, collection["fields"])

    def generate_collection(self, name, count, fields):
        '''
        Generate a output collection containing generated documents.
        :param name:
        :param count:
        :param fields:
        '''
        print("\n>>> Building '%s' collection, %d documents to build." % 
              (name, count))
        self.ids[name] = []

        # Configure a progress indicator.
        if self.options["use_pbar"]:
            pbar = self.pbar(name, count)
            pbar.start()

        # Produce as many documents as requested
        for i in range(count):
            # Generate the document and save the dbref
            document = self.generate_document(fields)
            doc_id   = self.output.write(name, document)
            self.ids[name].append(doc_id)
            if self.options["use_pbar"]:
                pbar.update(i + 1)

        if self.options["use_pbar"]:
            pbar.finish()
        print(">>> Completed '%s' collection." % name)

    def generate_document(self, fields):
        '''
        Generate a document based on the supplied field definitions.
        :param fields:
        '''
        document = {}        # prepare an empty dictionary
        
        # Loop through the fields
        for field in fields:
            # If the field does not specify a gen, it's not going to be
            # random.
            if "generator" not in field:
                # If the field type starts with "ref:", we need to build a 
                # reference to a related collection. The name of the colletion
                # should come after the ":"
                if field["type"].startswith("ref:"):
                    # Split out the related collection name
                    ref_coll = field["type"].split(":")[1]
                    
                    # If we don't have any ids with that collection name, it's
                    # possible the user input a bad name, or tried to refer to 
                    # a collection before defining it. Raise an exception.
                    if ref_coll not in self.ids:
                        raise Exception("Field with name '%s' requests \
                                         reference to collection '%s' which \
                                         does not exist. Make sure that any \
                                         collection referred to is defined \
                                         before the request." % (field["name"], 
                                                                 ref_coll))
                        

                    # Otherwise, pick a random id from the list and build a 
                    # reference.
                    document[field["name"]] = DBRef(ref_coll, 
                                                    random.choice(
                                                          self.ids[ref_coll]), 
                                                    self.dbname) 

            
            # If a gen is specified, we'll call it to get our data.
            else:
                try:
                    gen = self.dbs[field["generator"]]
                except KeyError:
                    raise Exception("Invalid generator '%s' specified" %  
                                    field["generator"])
                else:
                    data = gen.generate_data(
                        size=(field.get("size", 0)), 
                        field_type=field.get("type", "words")
                    )
                    data = self.apply_grammar(field, data)
                    data = self.apply_encoding(data)
                    document[field["name"]] = data 
        return document
    
    def apply_encoding(self, data):
        '''
        Return the input data encoded with the appropriate encoding.
        :param data:
        '''
        if type(data) != str:
            return [self.apply_encoding(item) for item in data]
        
        if self.options["encoding"] == "html":
            # convert paragraph breaks
            data = re.sub("\n\n", "<\p>", data)
            data = re.sub("\t+", "<p>", data)
            return cgi.escape(data).encode('utf-8', 
                                           'xmlcharrefreplace').decode("ascii")
        elif self.options["encoding"] == "base64":
            return base64.b64encode(data.encode("ascii")).decode("ascii")
        elif self.options["encoding"] == "ascii":
            return data.encode("ascii").decode("ascii")
        else:                           # default: utf-8
            return data.encode("utf-8").decode("utf-8")
    
    def apply_grammar(self, field, data):
        '''
        Apply a grammar function to the input data.
        :param field:
        :param data:
        '''
        
        if field.get("generator", None) == "numbers":
            return data 
        
        if "type" not in field:
            return " ".join(data)

        if field["type"] == "body":
            return grammars.body(data)
        elif field["type"] == "headline":
            return grammars.headline(data)
        elif field["type"] == "list":
            return grammars.json_list(data)
        else:
            return " ".join(data)

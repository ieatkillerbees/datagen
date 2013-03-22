"""
datagen.py 

Generate randomish data to fill up a sad, empty mongo database.
"""
import argparse
import json
import os
import progressbar
import pymongo
import sys
import time

from datagen.output_methods import MongoInterface, StdoutInterface
from datagen import dictionaries
from datagen import generator

__author__  = "Samantha Quinones"
__email__   = "squinones@politico.com"
__version__ = "0.9"
__status__  = "Development"
__sample__  = os.path.abspath(os.path.join(os.path.dirname(__file__),"../templates/template.json"))

def parse_args():
    '''
    Set up cmdline argument parser. 
    '''
    parser = argparse.ArgumentParser(description="Generate dummy data in a mongo collection.")
    parser.add_argument("-n", "--no-progress", action="store_true", default=False,
                        help="Do not display progress.")
    parser.add_argument("-e", "--encoding", type=str, choices=["html", "base64", "ascii", "utf-8"], default="utf-8",
                        help="Output encoding.")
    parser.add_argument("-t", "--test-output", action="store_true", default=False,
                        help="Do not write to database. Instead, parse template and display output to stdout.")
    parser.add_argument("--hostname", type=str, default="localhost",
                        help="Hostname with a MongoDB instance. Default: localhost")
    parser.add_argument("--port", type=int, default=27017,
                        help="Post hosting the MongoDB instance. Default: 27017")
    parser.add_argument("-d", "--dbname", type=str, default="datagen",
                        help="Database name to use. Default: datagen")
    parser.add_argument("-p", "--preserve-database", action="store_true", default=False,
                        help="Do NOT overwrite existing databases (appends new records)")
    parser.add_argument("--create-sample", action="store_true", default=False,
                        help="Write a sample template file to stdout and exit.")
    parser.add_argument("template", nargs="?",
                        type=argparse.FileType('r'),
                        help="A file containing a JSON template to generate documents.")
    return parser.parse_args()


def load_template(template_file):
    ''' 
    Attempts to open a JSON template file and load it in to a dictionary
    '''
    
    # Get an open file handle
#    try:
#        fp = open(template_file, "r")
#    except:
#        raise Exception("JSON template file '%s' does not exist or could not be opened." % template_file)

    # Attempt to read and parse the file
    try:
        template = json.load(template_file)
    except Exception as exc:
        raise Exception("JSON template could not be parsed: %s" % str(exc))

    return template

def create_pbar(name, count):
    '''
    Create a progress bar object
    :param name:
    :param count:
    '''
    pbar = progressbar.ProgressBar(widgets=[
            ">>> ['%s'] Generated " % name,
            progressbar.FormatLabel(" %(value)d documents "),
            "of %d (" % count,
            progressbar.Percentage(),
            ")"],
            maxval=count)
    return pbar

def load_mongo(hostname, port, dbname):
    '''
    Create a pymongo client
    :param hostname:
    :param port:
    '''
    try:
        client = pymongo.MongoClient(hostname, port)
    except Exception as exc:
        raise Exception("Failed to connect to Mongo instance: %s" % str(exc))
    else: 
        return MongoInterface(client, dbname)

def print_sample_template():
    '''
    Print the contents of template.json to stdout
    '''
    try:
        with open(__sample__, "r") as fp:
            print(fp.read())
    except OSError:
        raise Exception("Failed to open sample template!")
    
def main(args):
    '''
    Main method. Generate dependencies for the generator and initiate the run.
    :param args:
    '''
    
    if args.create_sample:
        print_sample_template()
        return
    
    if not args.template:
        raise Exception("You must supply a template file.")
    
    print("datagen.py - Version %s\n" % __version__)
    
    sys.stdout.write("* Loading template...")
    sys.stdout.flush()
    template = load_template(args.template)
    sys.stdout.write("done!\n")
    sys.stdout.flush()
    
    if args.test_output:
        output = StdoutInterface() 
    else:
        output = load_mongo(args.hostname, args.port, args.dbname)

    gen_config = {
        "use_pbar": not args.no_progress,
        "encoding": args.encoding,
        "preserve_database": args.preserve_database,
        "names":  dictionaries.NamesDictionary(),
        "words":  dictionaries.WordsDictionary(),
        "lipsum": dictionaries.LipsumDictionary(),
    }
    gen = generator.Generator(template, output, create_pbar, **gen_config)

    # Print a message that we're starting the generation and trap the time.
    print("\nStarting data generation.")
    s_time = time.time()
    
    gen.run()
    
    print("\nData generation complete in %f seconds" % (float(time.time()) - float(s_time)))

def start():
    try:
        main(parse_args())
    except KeyboardInterrupt:
        sys.stdout.flush()
        print("\nCancelled!\n")
        sys.exit(0)
    except Exception as exc:
        print(str(exc))
        sys.exit(-1)
    else:
        sys.exit(0)

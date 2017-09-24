#
# AutoWINdexer.py
# Author: Wayne "ViridianForge" Manselle
# Version 0.1
#
# Changelog:
# 0.1 - 08/05/17 -- Initial Creation
# 0.2 - 09/06/17 -- Noting that I got this working for scraping new releases, etc and the whole album tear apart
#
#
# The AutoWINdexer is a script whose purpose is to scrape multiple musical services and
# collect data on the Genres of music that Chiptunes = WIN gives a shit about.
#
# Why? Because Wayne and Ryn have been doing this shit by hand for way too fucking long.
#
# Tons of credit to 59Naga at Github for their coffeescript BC scraper that Wayne read
# over to figure out how to do this in Python.
#
# Requirements:

import json
import argparse
import logging
import csv
from lib import bc

def run_scrape(site, stype, sterm, output, depth=None):
    '''
    Generic main method
    Purpose is to select the specific mode of operation using
    input and then run a scrape in that fashion

    Parameters
    __________
    stype - String describing the specific type of search being done
    sterms - List of strings describing tags or terms to be used in the search
    urls - List of URLs to be searched on
    outputs - List of Files to output to
    depth - Level of recursion if set
    '''
    #Initialize Defaults
    if depth is None:
        depth=0

    #Logger here Eventually
    #TODO - Switch from IfEl ladder to catch all
    #Explore Tag relationships
    logging.debug(stype)
    if stype=='tags':
        logging.info('Hunting Related Tags')
        collatedTags = bc.bc_get_related_tags([site],[sterms])
        logging.info('Output Tag Data')
        with open(outputs,'w') as tagfile:
            for tag in collatedTags:
                tagfile.write(tag + '\n')
    #Collect Album Data
    elif stype=='albums':
        logging.info('Hunting Album Data')
        logging.debug(depth)
        collatedAlbums = bc.bc_get_genre([site],[sterms],'pop',[],depth)
        huntResult = {}
        logging.info('Collecting Output Data')
        for alb in collatedAlbums:
            huntResult[alb] = bc.bc_get_album(alb, ['tracks','artist','release','tags'])
        logging.info('Search returned ' + str(len(collatedAlbums)) + ' unique albums.')
        logging.info('Outputting Results')
        with open(outputs, 'w') as outfile:
            json.dump(huntResult, outfile)
        logging.info('Results saved to ' + outputs)
    #Collect Artist Discog Data
    elif stype=='discog':
        logging.info('Hunting Artist Discography')
        collatedDiscog = bc.bc_get_discog([site])
        logging.info('Outputting Discog Data')
        with open(outputs, 'w') as outfile:
            for disc in collatedDiscog:
                outfile.write(disc + '\n')
    else:
        logging.debug('Search Style ' + style + ' is not a valid style.')

    logging.info('Done.')

    return 0

def bulk_proc(args):
    """
    Function that processes a bulk scrape command.
    
    args - the args passed from the calling parser.
    Looking for file or string. These are mutually exclusive args
    so its either one or the other.
    """
    scrapeQueue = []
    if args.file:
        with open(args.file, 'rb') as f:
            reader = csv.reader(f)
            scrapeQueue = list(reader)
    elif args.string:
        for line in args.string.split('|'):
            scrapeQueue.append(line.split(','))
    else:
        print("Bulk processing requires either a file or string containing scrapes to run.")
        logging.exception('No valid arguments passed to bulk processer.')

    for scrape in scrapeQueue:
        #Test for valid input
        if valid_scrape(scrape):
            run_scrape(scrape)
    return 0

def man_proc(args):
    if valid_scrape([args.url, args.type, args.query, args.file, args.depth]):
        run_scrape(args.url, args.type, args.query, args.file, args.depth)
    else:
        print('Invalid arguments passed to manual scrape processor.')
        logging.exception('Invalid arguments passed to manual scrape processor.')

    return 0

def valid_scrape(scrape_spec):
    valid = False

    return validity

if __name__ == '__main__':
    #Run input grabbing only if someone's running the CLI
    #Starter version, very discrete, limited options and control
    parser = argparse.ArgumentParser()
    #Log can stand alone
    parser.add_argument('-l','--log', help='Whether output should be logged to a file', action="store_true")
    #Subparser for Bulk Processing Arguments
    subparsers = parser.add_subparsers(title='Scrape Specification modes', description='How to call specific modes of scraping', help='Subcommand')
    bulk_parser = subparsers.add_parser('bulk', help='Mass Scrape Setup')
    bulk_group = bulk_parser.add_mutually_exclusive_group()
    bulk_group.add_argument('-f','--file', type=str, help='CSV File containing a list of scrapes to run')
    bulk_group.add_argument('-s','--string', type=str, help='String of Bulk Scrapes to Run')
    bulk_parser.set_default(func=bulk_proc)
    #TODO - Figure out how to make this specification of a search mutually exclusive to the above group
    #Subparser for Manual Settings
    manual_parser = subparsers.add_parser('manual', help='Direct Scrape Setup')
    manual_parser.add_argument('url', type=str, help='The URL to scrape.')
    manual_parser.add_argument('-t','--type', type=str, help='The type of scrape to run.')
    manual_parser.add_argument('-q','--query', type=str, help='The query to pass to the scrape.')
    manual_parser.add_argument('-f','--file', type=str, help='The filename to write to.')
    manual_parser.add_argument('-d','--depth', type=int, choices=[0,1,2], help='Number of recursive scans to run for a recursive scrape.')
    manual_parser.set_defaults(func=man_proc)
    args=parser.parse_args()

    #Activate Logging if Noted
    if args.log:
        logging.basicConfig(filename=args.log, filemode='w', level=logging.INFO)
    
    args.func(args)

    #if args.bulkScrape:
    #    try:
    #        with open(args.searchFile) as inFile:
    #            for line in inFile:
    #                scrapeDefs = line.split(',')
    #                scrapeSite = scrapeTerms[0]
    #                scrapeType = searchTerms[1]
    #                scrapeTerms = searchTerms[2].split(' ')
    #                outFile = searchTerms[3]
    #                runScrape(scrapeSite, scrapeType, scrapeTerms, outFile)
    #    except:
    #        #TODO flesh out common exceptions and give decent feedback
    #        logging.exception("An invalid thing happened.")

    #Args parsed, run scan
    #if args.scrapeSite and args.scrapeType and args.scrapeTerm and args.outFile:
    #    runScrape(args.scrapeSite, args.scrapeType, args.scrapeTerm, args.outFile, args.depth)
    #else:
    #    logging.exception("Invalid parameters passed.")


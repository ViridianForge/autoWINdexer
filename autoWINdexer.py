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
from lib import bc

#Static Variables

def runScrape(site, stype, sterm, output, depth=None):
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
        collatedTags = bc.bc_get_related_tags([site],[],[sterms])
        logging.info('Output Tag Data')
        with open(outputs,'w') as tagfile:
            for tag in collatedTags:
                tagfile.write(tag + '\n')
    #Collect Album Data
    elif stype=='albums':
        logging.info('Hunting Album Data')
        logging.debug(depth)
        collatedAlbums = bc.bc_get_genre([site],[],[sterms],depth)
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

if __name__ == '__main__':
    #Run input grabbing only if someone's running the CLI
    #Starter version, very discrete, limited options and control
    parser = argparse.ArgumentParser()
    parser.add_argument('--scrapeSite', help='The scan to be run.')
    parser.add_argument('--scrapeType', help='The term to scan for.')
    parser.add_argument('--scrapeTerm', help='The URL to scan')
    parser.add_argument('--outFile', help='The filename to write to.')
    parser.add_argument('--bulkScrape', help='A csv file containing searches to run')
    parser.add_argument('--depth', help='How deep to recurse for recursive scans')
    parser.add_argument('--log', help='Whether output should be logged to a file')
    args=parser.parse_args()

    #Activate Logging if Noted
    if args.log:
        logging.basicConfig(filename=args.log, filemode='w', level=logging.INFO)
    
    if args.bulkScrape:
        try:
            with open(args.searchFile) as inFile:
                for line in inFile:
                    scrapeDefs = line.split(',')
                    scrapeSite = scrapeTerms[0]
                    scrapeType = searchTerms[1]
                    scrapeTerms = searchTerms[2].split(' ')
                    outFile = searchTerms[3]
                    runScrape(scrapeSite, scrapeType, scrapeTerms, outFile)
        except:
            #TODO flesh out common exceptions and give decent feedback
            logging.exception("An invalid thing happened.")

    #Args parsed, run scan
    if args.scrapeSite and args.scrapeType and args.scrapeTerm and args.outFile:
        runScrape(args.scrapeSite, args.scrapeType, args.scrapeTerm, args.outFile, args.depth)
    else
        logging.exception("Invalid parameters passed.")


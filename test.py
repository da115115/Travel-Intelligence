#!/usr/bin/env python

# A simple example of how to use python using the travel-intelligence web api.
# Requirements: 
#   python (tested on 2.7)
#   requests library (see http://docs.python-requests.org/en/latest/)
#   matplotlib

import requests
import json

from pylab import *

########## Load countries.dat ########
country2code = {}
with open('countries.dat', 'r') as cfile:
    for line in cfile:
        name = line[ 0:48].strip()
        code = line[48:50]
        country2code[name] = code

########## Load airports.dat ########
# Maybe use csv module?
airport2country = {}
with open('airports.dat', 'r') as afile:
    # missing = set()
    for line in afile:
        cells = [x.strip('"').strip() for x in line.split(',')]
        country = cells[3].upper()
        # if country not in country2code:
        #     missing.add(country)
        airport2country[cells[4]] = country

    # for c in missing:
    #    print c


class TIWebAPI(object):
    """
    Initialize a connection to the server and perform different queries
    """
    def __init__(self, 
                 url      = 'https://demo.travel-intelligence.com/api/v1',
                 email    = 'demo@travel-intelligence.com', 
                 password = "demo"):
        """
        By default connect to demo server and get an authorization token
        """

        data = '{"session":{"email":"%s", "password":"%s"}}' % (email, password)
        headers = {
            'Content-Type': 'application/json',
            'Accept'      : 'application/json' 
            }
        r = requests.post(url + '/session', data=data, headers=headers)        

        self.url = url
        self.authToken = json.loads(r.text)['session']['auth_token']
        
    def search_travel_hits(self, market, month, origin=None, destination=None, weekends=None):
        """
        See https://github.com/travel-intelligence/travel-intelligence.github.io/blob/master/_posts/2013-11-19-search-travel-hits.md
        """
        headers = {
            'Accept'       : 'application/json',
            'Authorization': 'Token %s' % self.authToken
            }
        payload = {
            'market': market,
            'month' : month,            
        }

        if origin != None:
            payload['origin'] = origin
        if destination != None:
            payload['destination'] = destination
        if weekends != None:
            payload['weekends'] = weekends

        r = requests.get(self.url + '/search_travel_hits',
                         headers = headers,
                         params  = payload)
        return r.json()

    def search_look_hits(self):
        # TODO
        pass

    def search_hit_evolutions(self):
        # TODO
        pass

    def search_hit_variations(self):
        # TODO
        pass

    def booking_agency_total(self):
        # TODO
        pass

    def booking_agency_evolution(self):
        # TODO
        pass

    def booking_agency_onds(self):
        # TODO
        pass

    def booking_agency_airlines(self):
        # TODO
        pass

    def booking_agency_countries(self):
        # TODO
        pass

def primaryMarkets(market, month):
    """
    For a given market and a given month return the top destination countries (including internal travel)
    """
    ti = TIWebAPI()

    r = ti.search_travel_hits(market, month)
    airports = r['search_travel_hits']['top_destinations']['dimension']['destination']['category']['index']
    hits = r['search_travel_hits']['top_destinations']['value']

    markets = {}
    for airport,index in airports.iteritems():
        try:
            market = country2code[airport2country[airport]]
            if not market in markets:
                markets[market] = 0
            
            markets[market] += hits[index]
            
        except:
            # TODO
            pass
        
    return markets


if __name__ == '__main__':
    pm1 = primaryMarkets('ES', '2012-01')

    # transform to percentage
    total = float(sum(pm1.values()))   
    pm2 = {}
    for k,v in pm1.iteritems():
        pm2[k] = v/total*100.0

    # order results by percentage
    market, percent = zip(*sorted(pm2.iteritems(), key=lambda x: x[1], reverse=True))

    # make a bar plot with the results
    indx = arange(len(market))
    width = 0.35

    fig = figure()
    ax = fig.add_subplot(111)
    ax.bar(indx, percent)
    ax.set_ylabel('% of travel')
    ax.set_title('Top markets for ES on 2012-01')
    ax.set_xticks(indx + width)
    ax.set_xticklabels(market)

    show()

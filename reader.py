#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from parser import Parser
from operator import attrgetter
from utils import api_get_node, api_update_node

OLSRD_LAT_LON_FILE = '/var/run/latlon.js'
API_URLS = ['http://localhost:5984/openwifimap/_design/owm-api/_rewrite', 'http://api.openwifimap.net/']
SKIP_SCRIPTS = ('luci-app-owm')

if __name__ == "__main__":
    if len(sys.argv) > 1:
        lat_lon_file = sys.argv[1]
    else:
        lat_lon_file = OLSRD_LAT_LON_FILE

    print("Trying to parse {}".format(lat_lon_file))

    p = Parser()
    links_unknown = p.parse_from_file(lat_lon_file)
    nodes = p.get_nodes()
    to_update = {}
    for api_url in API_URLS:
        to_update[api_url] = []
        print('\nFetching data')
        for hostname, node in nodes.items():
            data = api_get_node(api_url, node._id)

            if data is not None:
                if 'script' in data and data['script'] in SKIP_SCRIPTS:
                    print('*'),
                    continue
                else:
                    node.script = data['script']

            print('.'),
            to_update[api_url].append(node)

    for api_url in API_URLS:
        print('\nSaving data')
        for node in sorted(to_update[api_url], key=attrgetter('hostname')):
            print('\t* {}...\t'.format(node.hostname)),
            print('Success' if api_update_node(api_url, node) else 'Error')


    stat_nodes = (len(p.get_nodes()), len(p.get_nodes()) - len(to_update))


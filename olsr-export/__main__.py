#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from parser import Parser
from datetime import datetime, timedelta
from operator import attrgetter
from utils import api_get_node, api_update_node
from optparse import OptionParser

DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'
SKIP_SCRIPTS = ('luci-app-owm')

def logg(msg, verbose, joined=False):
    if verbose:
        if joined:
            sys.stdout.write(msg)
        else:
            print(msg)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      default='/var/run/latlon.js',
                      help="use different latlon.js file than\
                      /var/run/latlon.js", metavar="LATLON_FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print verbose status messages to stdout")
    parser.add_option("-s", "--skip",
                      action="store_true", dest="skip_self", default=True,
                      help="skip links to this node (Self-Entries)")
    parser.add_option("-a", "--apis",
                      dest="apis", default='http://api.openwifimap.net',
                      help="api servers to push the data (separated by comma)")

    (options, args) = parser.parse_args()

    print("Trying to parse {0}".format(options.filename))

    p = Parser()
    links_unknown = p.parse_from_file(options.filename, options.skip_self)
    nodes = p.get_nodes()
    to_update = {}
    apis = options.apis.split(' ')
    for api_url in apis:
        to_update[api_url] = []
        print('\nFetching data')
        for hostname, node in nodes.items():
            data = api_get_node(api_url, node._id)

            if data is not None:
                if 'script' in data and data['script'] in SKIP_SCRIPTS:
                    if 'mtime' in data:
                        date = datetime.strptime(data['mtime'], DATE_FORMAT)
                        now = datetime.now()
                        if (now - date) <= timedelta(days=7):
                            logg('*', options.verbose, True)
                            continue
                node.script = data['script']

            logg('.', options.verbose, True)
            to_update[api_url].append(node)

    for api_url in apis:
        print('\nSaving data')
        for node in sorted(to_update[api_url], key=attrgetter('hostname')):
            logg('\t* {0}...\t'.format(node.hostname), options.verbose, True)
            msg = 'Success' if api_update_node(api_url, node) else 'Error'
            logg(msg, options.verbose)

        print('\n{0}'.format(api_url))
        print('\tNodes: {0}'.format(len(p.get_nodes())))
        print('\tUpdated: {0}'.format(len(to_update[api_url])))

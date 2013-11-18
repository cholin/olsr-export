#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import json


def api_update_node(api_url, node):
    url = "%s/update_node/%s" % (api_url, node._id)
    try:
        req = urllib2.urlopen(url, json.dumps(node.as_dict()))
        if req.getcode() == 201:
            return True
    except urllib2.HTTPError as e:
        print(e)

    return False

def api_get_node(api_url, _id):
    url = '%s/db/%s' % (api_url, _id)
    try:
        oldreq = urllib2.urlopen(url)
        if oldreq.getcode() == 200:
            return json.loads(oldreq.read())
    except urllib2.HTTPError:
        pass

    return None

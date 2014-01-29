#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

class Node:
    def __init__(self, name, latlon):
        _id = name if name.endswith('.olsr') else '{0}.olsr'.format(name)
        self._id = re.sub(r'^_+', '', _id)
        self.hostname = name
        self.latlon = latlon
        self.links = []
        self.ips = []
        self.script = 'freifunk-olsrd'

    def add_ip(self, ip):
        self.ips.append(ip)

    def add_link(self, node):
        self.links.append(node)

    def as_dict(self):
        lat, lon = self.latlon
        return {
            'type' : 'node',
            'updateInterval' : 86400,
            'hostname' : self.hostname,
            'longitude' : float(lon),
            'latitude' : float(lat),
            'script' : self.script,
            'links' : [ l.as_dict() for l in self.links]
        }

    def __repr__(self):
        return 'Node({0})'.format(self.hostname)


class Link:
    def __init__(self, dst, quality):
        self.dst = dst
        self.quality = quality

    def as_dict(self):
        return {
          'id' : self.dst._id,
          'quality' : self.quality
        }

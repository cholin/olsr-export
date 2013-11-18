#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
from model import Node, Link

TAG_CLASS_ID = 'Tag'

class SelfTag:
    def __init__(self, ip, lat, lon, is_hna, hna_ip, hostname):
        self.ip = ip
        self.latlon = (lat,lon)
        self.is_hna = is_hna,
        self.hna_ip = hna_ip
        self.hostname = hostname


class NodeTag(SelfTag):
    pass


class MidTag:
    def __init__(self, ip, alias):
        self.ip = ip
        self.alias = alias


class LinkTag:
    def __init__(self, src_ip, dst_ip, lq, nlq, etx, *args):
        self.src_ip = src_ip
        self.dst_ip = dst_ip
        self.lq = lq
        self.nlq = nlq
        self.etx = etx


class PLinkTag(LinkTag):
    pass


class Parser:

    def __init__(self):
        self.tags = [SelfTag, NodeTag, MidTag, LinkTag, PLinkTag]
        self._ips = {}
        self._nodes = {}

    def get_nodes(self):
        return self._nodes

    def get_ips(self):
        return self._ips

    def parse(self, lines):
        self.lex_lines(lines.splitlines())

    def parse_from_file(self, filename):
        entries = []
        with open(filename, 'r') as f:
            lines = f.read().splitlines()
            entries = self.lex_lines(lines)
        self._parse(entries)

    def _parse(self, entries):
        for node in entries['Node'] + entries['Self']:
            n = Node(node.hostname, node.latlon)
            n.add_ip(node.ip)
            self._nodes[node.hostname] = n
            self._ips[node.ip] = n

        mids_unknown = []
        for mid in entries['Mid']:
            try:
                node = self._ips[mid.ip]
                node.add_ip(mid.alias)
                self._ips[mid.alias] = node
            except KeyError:
                mids_unknown.append(mid)

        links = entries['Link'] + entries['PLink']
        links_unknown = []
        for link in links:
            try:
                node = self._ips[link.src_ip]
                l = Link(self._ips[link.dst_ip], link.lq)
                node.add_link(l)
            except KeyError:
                links_unknown.append(link)

    def lex_lines(self, lines):
        entries = {}
        for tag in self.tags:
            entries[self._get_tag_name(tag)] = []

        for line in lines:
            tag = self.lex_line(line)
            tag_name = self._get_tag_name(tag)
            entries[tag_name].append(self.lex_line(line))

        return entries

    def lex_line(self, line):
        for tag in self.tags:
            try:
                tag_name = self._get_tag_name(tag)
                raw = self.lex_line_raw(tag_name, line)
                return tag(*raw)
            except ValueError:
                pass

        raise ValueError

    def lex_line_raw(self, tag_id, line):
        delimiter = ('{}('.format(tag_id), ');')
        if not line.startswith(delimiter[0]) or not line.endswith(delimiter[1]):
            raise ValueError

        start = len(delimiter[0])
        end = len(delimiter[1])
        unquoted = line.replace("'", '')

        return unquoted[start:-end].split(',')

    def _get_tag_name(self, tag):
        if not inspect.isclass(tag):
            tag = tag.__class__

        return tag.__name__[:-len(TAG_CLASS_ID)]

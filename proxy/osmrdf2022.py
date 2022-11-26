#!/usr/bin/env python3
# ==============================================================================
#
#          FILE:  osmrdf2022.py
#
#         USAGE:  # this is a library. Import into your code:
#                     from osmrdf2022 import *
#
#   DESCRIPTION:  ---
#
#       OPTIONS:  ---
#
#  REQUIREMENTS:  - python3
#          BUGS:  ---
#         NOTES:  ---
#       AUTHORS:  Emerson Rocha <rocha[at]ieee.org>
# COLLABORATORS:  ---
#       LICENSE:  Public Domain dedication or Zero-Clause BSD
#                 SPDX-License-Identifier: Unlicense OR 0BSD
#       VERSION:  v0.1.0
#       CREATED:  2022-11-25 19:22 UTC v1.0.0 started
#      REVISION:  ---
# ==============================================================================

from dataclasses import dataclass
import xml.etree.ElementTree as XMLElementTree


# See also: https://wiki.openstreetmap.org/wiki/Sophox#How_OSM_data_is_stored
# See also https://wiki.openstreetmap.org/wiki/Elements
RDF_TURTLE_PREFIXES = [
    'PREFIX geo: <http://www.opengis.net/ont/geosparql#>',
    'PREFIX osmnode: <https://www.openstreetmap.org/node/>',
    'PREFIX osmrel: <https://www.openstreetmap.org/relation/>',
    'PREFIX osmway: <https://www.openstreetmap.org/way/>',
    'PREFIX osmm: <https://example.org/todo-meta/>',
    'PREFIX osmt: <https://example.org/todo-tag/>',
    'PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>',
]

OSM_ELEMENT_PREFIX = {
    'node': 'osmnode:',
    'relation': 'osmrel:',
    'tag': 'osmt:',
    'way': 'osmway:'
}


class OSMApiv06Xml:
    """OSMApiv06Xml

    Not so optimized quick parser for XML files that can fit into memory
    """

    iterator: None
    xmlroot: None  # xml.etree.ElementTree.Element
    root_tag: str  # Example: osm
    root_attrib: dict
    child_1_tag: str
    child_1_attr: dict
    # @TODO for full dumps, will have 1-n child items

    def __init__(self, file_or_string: str) -> None:

        # @TODO maybe eventually implement from file (the large ones)
        # self.iterator = XMLElementTree.iterparse(
        #     source=file_or_string,
        #     events=('start', 'end')
        # )

        # self.iterator = XMLElementTree.fromstring(
        #     file_or_string,
        #     events=('start', 'end')
        # )
        root = XMLElementTree.fromstring(file_or_string)
        self.xmlroot = root
        self.root_tag = root.tag
        self.root_attrib = root.attrib

    def node(self):

        for child in self.xmlroot:
            # print('>>>>> el', child.tag, child.attrib)
            # print('>>>>> el2', dict(child.attrib))
            # # @TODO restrict here to node, way, relation, ...
            # print('>>>>> el3', OSMElement(
            #     child.tag, dict(child.attrib)).__dict__)
            return OSMElement(child.tag, dict(child.attrib))
            break
        # pass


class OSMElement:
    """OSMElement generic container for primitives

    Note: this will not do additional checks if input data is valid
    """
    _basegroup: str
    _tag: str
    id: int
    changeset: int
    timestamp: str  # maybe chage later
    user: str
    userid: str
    version: str
    visible: bool
    lat: float
    lon: float

    def __init__(self, tag: str, meta: dict):
        if not isinstance(meta, dict):
            meta = dict(meta)

        self.id = int(meta['id']) if 'id' in meta else None

        self.version = int(meta['version']) if 'version' in meta else None
        self.changeset = int(
            meta['changeset']) if 'changeset' in meta else None
        self.timestamp = meta['timestamp'] if hasattr(
            meta, 'timestamp') else None
        self.user = meta['user'] if 'user' in meta else None
        self.userid = int(meta['userid']) if 'userid' in meta else None
        self.lat = float(meta['lat']) if 'lat' in meta else None
        self.lon = float(meta['lon']) if 'lon' in meta else None

        self._tag = tag
        self._basegroup = '{0}{1}'.format(
            OSM_ELEMENT_PREFIX[tag], str(self.id))

    def to_ttl(self) -> list:
        data = []
        data.append(self._basegroup)

        if self.changeset:
            data.append(f'    osmm:changeset {self.changeset} ;')
        if self.lat and self.lon:
            data.append(
                f'    osmm:loc "Point({self.lat} {self.lon})"^^geo:wktLiteral ;')
        if self.timestamp:
            data.append(
                f'    osmm:timestamp "{self.timestamp}"^^xsd:dateTime ;')
        if self.user:
            data.append(
                f'    osmm:user "{self.user}" ;')
        if self.userid:
            data.append(
                f'    osmm:userid {self.userid} ;')
        if self.version:
            data.append(
                f'    osmm:version {self.version} ;')

        data.append('    # TODO implement the tags')
        data.append('.')
        return data


# class OSMElementNode(OSMElement):
#     def __init__(self, meta):
#         super().__init__(meta)
#         # super(OSMElement, self).__init__(meta)
#         print('oooi', self)
#         print('oooi', self.__dict__)
#         print('oooi', hasattr(self.__dict__, 'id'))
#         print('oooi', self.__dict__['id'])
#         self._basegroup = '{0}{1}'.format(
#             OSM_ELEMENT_PREFIX['node'], str(self.id))


def osmrdf_node_xml2ttl(data_xml: str):

    osmx = OSMApiv06Xml(data_xml)
    osmnode = osmx.node()

    output = []
    output.extend(RDF_TURTLE_PREFIXES)
    output.append('')

    output.extend(osmnode.to_ttl())

    output.append('')
    # DEBUG: next 2 lines will print the XML node, commented
    # comment = "# " + "\n# ".join(data_xml.split("\n"))
    # output.append(comment)

    return "\n".join(output)


def osmrdf_relation_xml2ttl(data_xml: str):

    osmx = OSMApiv06Xml(data_xml)
    osmnode = osmx.node()

    output = []
    output.extend(RDF_TURTLE_PREFIXES)
    output.append('')

    output.extend(osmnode.to_ttl())

    output.append('')
    # DEBUG: next 2 lines will print the XML node, commented
    comment = "# " + "\n# ".join(data_xml.split("\n"))
    output.append(comment)

    return "\n".join(output)


def osmrdf_way_xml2ttl(data_xml: str):

    osmx = OSMApiv06Xml(data_xml)
    osmnode = osmx.node()

    # print(osmnode)
    # print(type(osmnode))
    # print(osmnode.to_ttl())
    # print(type(osmnode.to_ttl()))

    output = []
    output.extend(RDF_TURTLE_PREFIXES)
    output.append('')

    output.extend(osmnode.to_ttl())

    output.append('')
    # DEBUG: next 2 lines will print the XML node, commented
    # comment = "# " + "\n# ".join(data_xml.split("\n"))
    # output.append(comment)

    return "\n".join(output)

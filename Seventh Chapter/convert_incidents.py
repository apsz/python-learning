#!/usr/bin/python3
# TODO: optargs parsing

import os
import sys
import datetime
import string
import gzip
import pickle
import struct
import textwrap
import xml
import xml.dom
import xml.dom.minidom
import xml.sax
from xml.etree import ElementTree
from xml.etree.ElementTree import SubElement
from xml.parsers import expat


class IncidentError(Exception): pass


GZIP_MAGIC = b'\x1F\x8B'
MAGIC = b"AIB\x00"
FORMAT_VERSION = b"\x00\x01"
NumbersStruct = struct.Struct("<Idi?")


class Incident:
    def __init__(self, report_id, date, airport, aircraft_id, aircraft_type,
                 pilot_percent_hours_on_type, pilot_total_hours, midair, narrative=''):
        assert isinstance(report_id, str) and \
                len(report_id) >= 8 and \
                all([not c in string.whitespace for c in report_id]), \
                ('report_id must contain no whitespaces '
                'and be at least 8 characters long')
        self.__report_id = report_id
        self.date = date
        self.airport = airport
        self.aircraft_id = aircraft_id
        self.pilot_percent_hours_on_type = pilot_percent_hours_on_type
        self.pilot_total_hours = pilot_total_hours
        self.midair = midair
        self.narrative = narrative

    @property
    def report_id(self):
        return self.__report_id

    @property
    def date(self):
        return self.__date

    @date.setter
    def date(self, date):
        assert isinstance(date, datetime.date), \
               'must be datetime.date type'
        self.__date = date

    @property
    def airport(self):
        return self.__airport

    @airport.setter
    def airport(self, airport):
        assert airport and isinstance(airport, str), \
               'airport cannot be empty and must be a string'
        self.__airport = airport.strip('\n')

    @property
    def aircraft_id(self):
        return self.__aircraft_id

    @aircraft_id.setter
    def aircraft_id(self, aircraft_id):
        assert  aircraft_id and isinstance(aircraft_id, str), \
                'aircraft_id cannot be empty and must be a string'
        self.__aircraft_id = aircraft_id.strip('\n')

    @property
    def aircraft_type(self):
        return self.__aircraft_type

    @aircraft_type.setter
    def aircraft_type(self, aircraft_type):
        assert  aircraft_type and isinstance(aircraft_type, str), \
                'aircraft_type cannot be empty and must be a string'
        self.__aircraft_type = aircraft_type.strip('\n')

    @property
    def pilot_percent_hours_on_type(self):
        return self.__pilot_percent_hours_on_type

    @pilot_percent_hours_on_type.setter
    def pilot_percent_hours_on_type(self, pilot_percent_hours_on_type):
        assert  0.0 <= pilot_percent_hours_on_type <= 100.0 \
                and isinstance(pilot_percent_hours_on_type, float), \
                'pilot_percent_hours_on_type must be a float between 0.0 and 100.0'
        self.__pilot_percent_hours_on_type = pilot_percent_hours_on_type

    @property
    def pilot_total_hours(self):
        return self.__pilot_total_hours

    @pilot_total_hours.setter
    def pilot_total_hours(self, pilot_total_hours):
        assert pilot_total_hours > 0 and isinstance(pilot_total_hours, int), \
                'pilot_total_hours must be an int of value > 0'
        self.__pilot_total_hours = pilot_total_hours

    @property
    def midair(self):
        return self.__midair

    @midair.setter
    def midair(self, midair):
        assert isinstance(midair, bool), 'midair must be True or False'
        self.__midair = midair

    @property
    def narrative(self):
        return self.__narrative

    @narrative.setter
    def narrative(self, narrative):
        assert  isinstance(narrative, str) and '\n' in narrative, \
                'narrative must be a multiline string'
        self.__narrative = narrative


class IncidentCollection(dict):
    def __init__(self, collection):
        if collection:
            assert all(isinstance(x, Incident) for x in collection), \
                       'collection must contain only Incident class objects'
        else:
            collection = {}
        super().__init__(collection)

    def __setitem__(self, key, value):
        assert isinstance(value, Incident), \
               'collection accepts only Incident class objects'
        assert isinstance(key, str) and \
                len(key) >= 8 and \
                len(key.split()) == 1, \
                ('key must contain no whitespaces '
                'and be at least 8 characters long')
        super().__setitem__(key, value)

    def __iter__(self):
        for report_id in sorted(super().keys()):
            yield report_id

    keys = __iter__

    def values(self):
        for report_id in self.keys():
            yield report_id

    def items(self):
        for report_id in self.keys():
            yield (report_id, self[report_id])

    def setdefault(self, k, d=None):
        assert isinstance(d, Incident), \
               'default value must be of Incident class'
        assert isinstance(k, str) and \
                len(k) >= 8 and \
                len(k.split()) == 1, \
                ('key must contain no whitespaces '
                'and be at least 8 characters long')
        super().setdefault(k, d)

    def fromkeys(iterable, value=None):
        assert isinstance(value, Incident), \
               'provided value must be of Incident class'
        for key in iterable:
            assert isinstance(key, str) and \
                   len(key) >= 8 and \
                   len(key.split()) == 1, \
                   ('key must contain no whitespaces '
                    'and be at least 8 characters long')
        super().fromkeys(iterable, value)

    def export_to_pickle(self, filename, compressed=False):
        fh = None
        try:
            if not compressed:
                fh = open(filename, 'wb')
            else:
                fh = gzip.open(filename, 'wb')
            pickle.dump(self, fh, pickle.HIGHEST_PROTOCOL)
        except (EnvironmentError, IOError, pickle.PicklingError) as save_err:
            print('{} Pickle export error: {}'.format(os.path.basename(sys.argv[0]),
                                                      save_err))
        finally:
            if fh:
                fh.close()

    def import_from_pickle(self, filename):
        fh = None
        try:
            fh = open(filename, 'rb')
            if fh.read(len(GZIP_MAGIC)) == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(filename, 'rb')
            else:
                fh.seek(0)
            self.clear()
            self.update(pickle.load(fh))
            return True
        except (EnvironmentError, IOError, pickle.UnpicklingError) as load_err:
            print('{} Pickle loading error: {}'.format(os.path.basename(sys.argv[0]),
                                                       load_err))
        finally:
            if fh:
                fh.close()

    def export_binary(self, filename, compressed=False):

        def pack_string(string):
            data = string.encode('utf-8')
            format = '<H{}s'.format(len(data))
            return struct.pack(format, len(data), data)

        fh = None
        try:
            if not compressed:
                fh = open(filename, 'wb')
            else:
                fh = gzip.open(filename, 'wb')
            fh.write(MAGIC)
            fh.write(FORMAT_VERSION)
            for incident in self.values():
                data = bytearray()
                data.extend(pack_string(incident.report_id))
                data.extend(pack_string(incident.airport))
                data.extend(pack_string(incident.aircraft_id))
                data.extend(pack_string(incident.aircraft_type))
                data.extend(pack_string(incident.narrative.strip()))
                data.extend(NumbersStruct.pack(
                                incident.date.toordinal(),
                                incident.pilot_percent_hours_on_type,
                                incident.pilot_total_hours,
                                incident.midair))
                fh.write(data)
            return True
        except (EnvironmentError, IOError) as save_err:
            print('{} Binary export error: {}'.format(os.path.basename(sys.argv[0]),
                                                      save_err))
        finally:
            if fh:
                fh.close()

    def import_binary(self, filename):

        def unpack_string(fh, eof_is_error=True):
            uint16 = struct.Struct("<H")
            length_data = fh.read(uint16.size)
            if not length_data:
                if eof_is_error:
                    raise ValueError('missing or corrupt string size')
                return None
            length = uint16.unpack(length_data)[0]
            if length == 0:
                return ""
            data = fh.read(length)
            if not data or len(data) != length:
                raise ValueError('missing or corrupt string')
            format = "<{}s".format(length)
            return struct.unpack(format, data)[0].decode('utf-8')

        fh = None
        try:
            fh = open(filename, 'rb')
            magic = fh.read(len(GZIP_MAGIC))
            if magic == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(filename, 'rb')
            else:
                fh.seek(0)
            magic = fh.read(len(MAGIC))
            if magic != MAGIC:
                raise ValueError('invalid .aib file format')
            version = fh.read(len(FORMAT_VERSION))
            if version > FORMAT_VERSION:
                raise ValueError('unrecognized .aib file version')
            self.clear()

            while True:
                report_id = unpack_string(fh, False)
                if report_id is None:
                    break
                data = {}
                data['report_id'] = report_id
                for name in ('airport', 'aircraft_id',
                             'aircraft_type', 'narrative'):
                    data[name] = unpack_string(fh)
                other_data = fh.read(NumbersStruct.size)
                numbers = NumbersStruct.unpack(other_data)
                data['date'] = datetime.date.fromordinal(numbers[0])
                data["pilot_percent_hours_on_type"] = numbers[1]
                data["pilot_total_hours"] = numbers[2]
                data["midair"] = numbers[3]
                incident = Incident(**data)
                self[incident.report_id] = incident
            return True
        except (EnvironmentError, IOError) as load_err:
            print('{} Binary import error: {}'.format(os.path.basename(sys.argv[0]),
                                                      load_err))
        finally:
            if fh:
                fh.close()

    def export_txt(self, filename):
        fh = None
        try:
            fh = open(filename, 'w')
            for incident in self.values():
                wrapper = textwrap.TextWrapper(initial_indent='    ',
                                               subsequent_indent='    ')
                narrative = wrapper.wrap(incident.narrative.strip())
                fh.write('[{0.report_id}]\n'
                         'date={0.date!s}\n'
                         'aircraft_id={0.aircraft_id}\n'
                         'aircraft_type={0.aircraft_type}\n'
                         'airport={airport}\n'
                         'pilot_percent_hours_on_type='
                         '{0.pilot_percent_hours_on_type\n'
                         'pilot_total_hours='
                         '{0.pilot_total_hours}\n'
                         'midair={0.midair:d}\n'
                         '.NARRATIVE_START.\n{narrative}\n'
                         '.NARRATIVE_END.\n\n'.format(incident, airport=
                                                      incident.airport.strip(),
                                                      narrative=narrative))
            return True
        except (EnvironmentError, IOError) as save_err:
            print('{} Text export error: {}'.format(os.path.basename(sys.argv[0]),
                                                                     save_err))
        finally:
            if fh:
                fh.close()

    def import_txt(self, filename):
        fh = None
        try:
            fh = open(filename)
            narrative = False
            self.clear()
            data = {}
            for lino, line in enumerate(fh.read(), 1):
                line = line.rstrip()
                if not narrative and not line:
                    continue
                if narrative:
                    if line == '.NARRATIVE_END.':
                        data['narrative'] = textwrap.dedent(narrative).strip()
                        if len(data) != 9:
                            raise IncidentError('missing data on line {}'.format(lino))
                        incident = Incident(**data)
                        self[incident.report_id] = incident
                        narrative = False
                        data = {}
                    else:
                        line += line + '\n'
                elif not data and (line[0] == '[' and line[-1] == ']'):
                        data['report_id'] = line[1:-1]
                elif '=' in line:
                    key, value = line.split('=')
                    if key == 'date':
                        data[key] = datetime.datetime.strptime(value,"%Y-%m-%d").date()
                    elif key == 'pilot_percent_hours_on_type':
                        data[key] = float(value)
                    elif key == 'pilot_total_hours':
                        data[key] = int(value)
                    elif key == 'midair':
                        data[key] = bool(int(value))
                elif line == '.NARRATIVE_START.':
                    narrative = ''
                else:
                    raise KeyError('parsing error on line {}'.format(lino))
        except (EnvironmentError, IOError) as load_err:
            print('{} Text import error: {}'.format(os.path.basename(sys.argv[0]),
                                                                     load_err))
        finally:
            if fh:
                fh.close()


    def export_xml_etree(self, filename):
        root = xml.etree.ElementTree.Element('incidents')
        for incident in self.values():
            element = xml.etree.ElementTree.Element('incident',
                                                    report_id=incident.report_id,
                                                    date=incident.date.isoformat(),
                                                    aircraft_id=incident.aircraft_id,
                                                    aircraft_type=incident.aircraft_type,
                                                    pilot_percent_hours_on_type=
                                                    str(incident.pilot_percent_hours_on_type),
                                                    pilot_total_hours=
                                                    str(incident.pilot_total_hours),
                                                    midair=int(incident.midair))
            airport = xml.etree.ElementTree.SubElement(element, 'airport')
            airport.text = incident.airport.strip()
            narrative = xml.etree.ElementTree.SubElement(element, 'narrative')
            narrative.text = incident.narrative.strip()
            root.append(incident)
        tree = xml.etree.ElementTree.ElementTree(root)
        try:
            tree.write(filename, 'UTF-8')
            return True
        except (EnvironmentError, IOError, IncidentError) as save_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), save_err))
            return False

    def import_xml(self, filename):
        try:
            tree = xml.etree.ElementTree.parse(filename)
        except (EnvironmentError, IOError, xml.parsers.expat.ExpatError) as load_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), load_err))
            return False

        self.clear()
        data = tree.findall('incident')
        for incident in data:
            try:
                new_inc = {}
                for attribute in ("report_id", "date", "aircraft_id",
                                  "aircraft_type",
                                  "pilot_percent_hours_on_type",
                                  "pilot_total_hours", "midair"):
                    new_inc[attribute] = incident.get(attribute)
                new_inc['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%s').date()
                new_inc['pilot_percent_hours_on_flight'] = float(new_inc['pilot_percent_hours_on_flight'])
                new_inc['pilot_total_hours'] = int(new_inc['pilot_total_hours'])
                new_inc['midair'] = bool(int(new_inc['midair']))
                narrative = incident.find('narrative')
                new_inc['narrative'] = narrative.text.strip() if narrative else ''
                airport = incident.find('airport')
                new_inc['airport'] = airport.text.strip()
                new_incident = Incident(**new_inc)
                self[new_incident.report_id] = new_incident
            except (EnvironmentError, IOError, IncidentError) as export_err:
                print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
                return False
            return True

    def export_xml_dom(self, filename):
        dom = xml.dom.minidom.getDOMImplementation()
        tree = dom.createDocument(None, 'incidents', None)
        root = tree.documentElement
        for incident in self.values():
            element = tree.createElement('incident')
            for attribute, value in (
                    ("report_id", incident.report_id),
                    ("date", incident.date.isoformat()),
                    ("aircraft_id", incident.aircraft_id),
                    ("aircraft_type", incident.aircraft_type),
                    ("pilot_percent_hours_on_type",
                     str(incident.pilot_percent_hours_on_type)),
                     ("pilot_total_hours",
                     str(incident.pilot_total_hours)),
                     ("midair", str(int(incident.midair)))):
                element.setAttribute(attribute, value)
            for name, text in (('airport', incident.airport),
                               ('narrative', incident.narrative)):
                text_element = tree.createTextNode(text)
                name_element = tree.createElement(name)
                name_element.appendChild(text_element)
                element.appendChild(name_element)
            root.appendChild(element)
        fh = None
        try:
            fh = open(filename, 'w', encoding='utf-8')
            tree.writexml(fh)
            return True
        except (IOError, EnvironmentError, xml.parsers.expat.ExpatError) as save_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), save_err))
            return False
        finally:
            if fh:
                fh.close()

    def import_xml_dom(self, filename):
        def get_text(nodes):
            text = []
            for node in nodes:
                if node.nodeType == node.TEXT_NODE:
                    text.append(node.data)
            return ''.join(text).strip()

        try:
            tree = xml.dom.minidom.parse(filename)
        except (EnvironmentError, IOError, xml.parsers.expat.ExpatError) as import_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False

        self.clear()
        for element in tree.getElementsByTagName('incident'):
            try:
                data = {}
                for attribute in ("report_id", "date", "aircraft_id",
                                  "aircraft_type",
                                  "pilot_percent_hours_on_type",
                                  "pilot_total_hours", "midair"):
                    data[attribute] = element.getAttribute(attribute)
                data["date"] = datetime.datetime.strptime(
                data["date"], "%Y-%m-%d").date()
                data["pilot_percent_hours_on_type"] = (
                float(data["pilot_percent_hours_on_type"]))
                data["pilot_total_hours"] = int(
                data["pilot_total_hours"])
                data["midair"] = bool(int(data["midair"]))
                airport = element.getElementsByTagName("airport")[0]
                data["airport"] = get_text(airport.childNodes)
                narrative = element.getElementsByTagName("narrative")[0]
                data["narrative"] = get_text(narrative.childNodes)
                incident = Incident(**data)
                self[incident.report_id] = incident
            except (ValueError, LookupError, IncidentError) as imp_err:
                print("{0}: import error: {1}".format(os.path.basename(sys.argv[0]), imp_err))
                return False
        return True

    def export_xml_manual(self, filename):
        fh = None
        try:
            fh = open(filename, 'w', encoding='utf-8')
            fh.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            fh.write('<incidents>')
            for incident in self.values():
                fh.write('incident report_id={report_id} '
                         'date={0.date!s}'
                         'aircraft_type={0.aircraft_type} '
                         'pilot_percent_hours_on_flight='
                         '"{0.pilot_percent_hours_on_flight" '
                         'pilot_total_hours="{0.pilot_total_hours}" '
                         'midair="{0.midair:d}">\n'
                         '<airport>{airport}</airport>\n'
                         '<narrative>\n{narrative}\n</narrative>\n'
                         '</incident>\n'.format(incident,
                                                report_id=xml.sax.saxutils.quoteattr(
                                                    incident.report_id),
                                                aircraft_id=xml.sax.saxutils.quoteattr(
                                                    incident.aircraft_id),
                                                aircraft_type=xml.sax.saxutils.quoteattr(
                                                    incident.aircraft_type),
                                                airport=xml.sax.saxutils.escape(incident.airport),
                                                narrative="\n".join(textwrap.wrap(
                                                    xml.sax.saxutils.escape(
                                                        incident.narrative.strip()), 70))))
            fh.write('</incidents>\n')
            return True
        except (EnvironmentError, IOError) as import_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False

    def import_xml_sax(self, filename):
        fh = None
        try:
            handler = IncidentSaxHandler(self)
            parser = xml.sax.make_parser()
            parser.setContentHandler(handler)
            parser.parse(filename)
            return True
        except (IOError, EnvironmentError, xml.sax.SAXParseError) as load_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), load_err))
            return False

class IncidentSaxHandler(xml.sax.handler.ContentHandler):
    def __init__(self, incidents):
        super().__init__()
        self.__data = {}
        self.__text = ''
        self.__incidents = incidents
        self.__incidents.clear()

    def startElement(self, name, attributes):
        if name == 'incident':
            self.__data = {}
            for key, value in attributes.items():
                if key == 'date':
                    self.__data[key] = datetime.datetime.strptime(
                                            value, '%Y-%m-%d').date()
                elif key == 'pilot_percent_hours_on_type':
                    self.__data[key] = float(value)
                elif key == 'pilot_total_hours':
                    self.__data[key] = int(value)
                elif key == 'midair':
                    self.__data[key] = bool(int(value))
                else:
                    self.__data[key] = value
        self.__text = ''

    def endElement(self, name):
        if name == 'incident':
            if len(self.__data) != 9:
                raise IncidentError('missing data')
            incident = Incident(**self.__data)
            self.__incidents[incident.report_id] = incident
        elif name in frozenset({'airport', 'narrative'}):
            self.__data[name] = self.__text.strip()
        self.__text = ''

    def characters(self, text):
        self.__text += text


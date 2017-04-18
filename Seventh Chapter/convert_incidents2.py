#!/usr/bin/python3


import os
import struct
import string
import pickle
import gzip
import datetime
import sys
import textwrap
import xml.etree.ElementTree
import xml.parsers.expat
import xml.dom.minidom



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

    def export_pickle(self, filename, compress=False):
        fh = None
        try:
            if compress:
                fh = gzip.open(filename, 'wb')
            else:
                fh = open(filename, 'wb')
            pickle.dump(self, fh, pickle.HIGHEST_PROTOCOL)
            return True
        except (IOError, EnvironmentError, pickle.PicklingError) as export_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
        finally:
            if fh:
                fh.close()

    def import_pickle(self, filename):
        fh = None
        try:
            fh = open(filename, 'rb')
            if fh.read(len(GZIP_MAGIC)) == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(filename, 'rb')
            fh.seek(0)

            self.clear()
            self.update(pickle.load(fh))
        except (IOError, EnvironmentError, pickle.UnpicklingError) as import_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False
        finally:
            if fh:
                fh.close()

    def export_binary(self, filename, compress):

        def pack_string(string):
            encoded_s = string.encode('UTF-8')
            format_s = '<H{}s'.format(len(encoded_s))
            return struct.pack(format_s, len(encoded_s), encoded_s)

        fh = None
        try:
            if compress:
                fh = gzip.open(filename, 'wb')
            else:
                fh = open(filename, 'wb')
            fh.write(MAGIC)
            fh.write(FORMAT_VERSION)

            for incident in self.values():
                data = bytearray()
                data.extend(pack_string(incident.report_id))
                data.extend(pack_string(incident.airport))
                data.extend(pack_string(incident.aircraft_id))
                data.extend(pack_string(incident.aicraft_type))
                data.extend(pack_string(incident.narrative.strip()))
                data.extend(NumbersStruct.pack(incident.date.toordinal(),
                                               incident.pilot_percent_hours_on_type,
                                               incident.pilot_total_hours,
                                               incident.midair))
                fh.write(data)
            return True
        except (IOError, EnvironmentError) as export_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
            return False
        finally:
            if fh:
                fh.close()

    def import_binary(self, filename):

        def unpack_string(fh, eof_is_error=True):
            uint16 = struct.Struct('<H')
            string_size = fh.read(uint16.size)
            if not string_size:
                if eof_is_error:
                    raise ValueError('missing or corrupt string size')
                return None
            s_len = uint16.unpack(string_size)[0]
            if s_len == 0:
                return ''
            packed_s = fh.read(string_size)
            if not packed_s or len(packed_s) != s_len:
                raise ValueError('corrupt or missing data')
            form_s = '<{}s'.format(s_len)
            return struct.unpack(form_s, packed_s)[0].decode('UTF-8')

        fh = None
        try:
            fh = open(filename, 'rb')
            if fh.read(len(GZIP_MAGIC)) == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(filename, 'rb')
            if fh.read(len(MAGIC)) != MAGIC:
                raise ValueError('{} invalid file format'.format(fh.name))
            if fh.read(len(FORMAT_VERSION)) > FORMAT_VERSION:
                raise ValueError('{} unsupported file version'.format(fh.name))
            self.clear()

            while True:
                data = {}
                report_id = unpack_string(fh, False)
                if not report_id:
                    break
                data['report_id'] = report_id
                for name in ('airport', 'aircraft_id',
                             'aircraft_type', 'narrative'):
                    data[name] = unpack_string(fh)
                other_data = fh.read(NumbersStruct.size)
                numbers = NumbersStruct.unpack(other_data)
                data['date'] = datetime.date.fromordinal(numbers[0])
                data['pilot_percent_hours_on_type'] = float(numbers[1])
                data['pilot_total_hours'] = int(numbers[2])
                data['midair'] = bool(int(numbers[3]))
                incident = Incident(**data)
                self[incident.report_id] = incident
            return True
        except (IOError, EnvironmentError) as import_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False
        finally:
            if fh:
                fh.close()

    def export_txt(self, filename):
        fh = None
        try:
            fh = open(filename, 'w')
            for incident in self.values():
                wraper = textwrap.TextWrapper(initial_indent='    ', subsequent_indent='    ')
                fh.write('[{0.report_id}]\n'
                         'date={0.date!s}\n'
                         'airport={airport}\n'
                         'aircraft_id={0.aircraft_id}\n'
                         'aircraft_type={0.aircraft_type}\n'
                         'pilot_percent_hours_on_type='
                         '{0.pilot_percent_hours_on_type}\n'
                         'pilot_total_hours='
                         '{0.pilot_total_hours}\n'
                         'midair={0.midair:s!}\n'
                         '.NARRATIVE START.\n'
                         '{narrative}\n.NARRATIVE END.\n'.format(
                                                          incident,
                                                          airport=
                                                          incident.airport.strip(),
                                                          narrative=
                                                          wraper.wrap(incident.narrative.strip())))
            return True
        except (IOError, EnvironmentError) as export_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
            return False
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
            for line_num, line in enumerate(fh.read(), 1):
                line = line.rstrip()
                if not narrative and not line:
                    continue
                if narrative:
                    if line == '.NARRATIVE END.':
                        data['narrative'] = textwrap.dedent(line).strip()
                        if len(data) != 9:
                            raise IncidentError('{}: missing data on line {}'.format(line_num,
                                                                                     fh.name))
                        incident = Incident(**data)
                        self[incident.report_id] = incident
                        narrative = False
                        data = {}
                    else:
                        line += line + '\n'
                if not data and line[0] == '[':
                    data['report_id'] = line.strip()
                elif '=' in line:
                    key, value = line.split('=')
                    if key == 'date':
                        data[key] = datetime.datetime.strptime(value, "%Y-%m-%d").date()
                    elif key == 'pilot_percent_hours_on_type':
                        data[key] = float(value)
                    elif key == 'pilot_total_hours':
                        data[key] = int(value)
                    elif key == 'midair':
                        data[key] = bool(int(value))
                    else:
                        data[key] = value
                elif line == '.NARRATIVE_START.':
                    narrative = ''
                else:
                    raise ValueError('{}: invalid data on line {}'.format(line_num,
                                                                          fh.name))
            return True
        except (IOError, EnvironmentError) as import_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False
        finally:
            if fh:
                fh.close()

    def export_xml_tree(self, filename):
        root = xml.etree.ElementTree.Element('incidents')
        for incident in self.values():
            element = xml.etree.ElementTree.Element('incident',
                                                    report_id=incident.report_id,
                                                    date=incident.date.isoformat(),
                                                    aircraft_id=incident.aircraft_id,
                                                    aicraft_type=incident.aicraft_type,
                                                    pilot_percent_hours_on_type=
                                                    str(incident.pilot_percent_hours_on_type),
                                                    pilot_total_hours=str(incident.pilot_total_hours),
                                                    midair=str(int(incident.midair)))
            airport = xml.etree.ElementTree.SubElement(element, 'airport')
            airport.text = incident.airport.strip()
            narrative = xml.etree.ElementTree.SubElement(element, 'narrative')
            narrative.text = incident.narrative.strip()
            root.append(element)
        tree = xml.etree.ElementTree.ElementTree(root)
        try:
            tree.write(filename, 'UTF-8')
            return True
        except (IOError, EnvironmentError, xml.parsers.expat.ExpatError) as export_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
            return False

    def import_xml_tree(self, filename):
        try:
            data = xml.etree.ElementTree.parse(filename)
        except (IOError, EnvironmentError, xml.parsers.expat.ExpatError) as import_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False
        self.clear()

        for elements in data.findall('incident'):
            new_inc = {}
            for incident in elements:
                try:
                    for attr in ("report_id", "date", "aircraft_id",
                                  "aircraft_type",
                                  "pilot_percent_hours_on_type",
                                  "pilot_total_hours", "midair"):
                        new_inc[attr] = incident.get(attr)
                    new_inc['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%s').date()
                    new_inc['pilot_percent_hours_on_flight'] = float(new_inc['pilot_percent_hours_on_flight'])
                    new_inc['pilot_total_hours'] = int(new_inc['pilot_total_hours'])
                    new_inc['midair'] = bool(int(new_inc['midair']))
                    narrative = incident.find('narrative')
                    new_inc['narrative'] = narrative.text.strip() if narrative else ''
                    airport = incident.find('airport')
                    new_inc['airport'] = airport.text.strip()
                    inc = Incident(**new_inc)
                    self[inc.report_id] = inc
                except (EnvironmentError, IOError, IncidentError) as import_err:
                    print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
                    return False
                return True

    def export_xml_dom(self, filename):
        xdom = xml.dom.minidom.getDOMImplementation()
        tree = xdom.createDocument(None, 'incidents', '')
        root = tree.documentElement
        for incident in self.values():
            new_inc = tree.createElement('incident')
            for attribute, value in (
                                    ("report_id", incident.report_id),
                                    ("date", incident.date.isoformat()),
                                    ("aircraft_id", incident.aircraft_id),
                                    ("aircraft_type", incident.aircraft_type),
                                    ("pilot_percent_hours_on_type",
                                     str(incident.pilot_percent_hours_on_type)),
                                    ("pilot_total_hours",
                                     str(incident.pilot_total_hours)),
                                    ("midair", str(int(incident.midair)))
                                    ):
                new_inc.setAttribute(attribute, value)
            for name, text in (('airport', incident.airport.strip()),
                               ('narrative', incident.narrative.strip())):
                elem = tree.createElement(name)
                txt = tree.createTextNode(text)
                elem.appendChild(txt)
                new_inc.appendChild(elem)
            root.append(new_inc)
        fh = None
        try:
            fh = open(filename, 'w')
            tree.writexml(fh, encoding='utf-8')
            return True
        except (IOError, EnvironmentError) as export_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), export_err))
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
            data = xml.dom.minidom.parse(filename)
            self.clear()
        except (EnvironmentError, IOError, IncidentError) as import_err:
            print('{} error: {}'.format(os.path.basename(sys.argv[0]), import_err))
            return False

        for incident in data.getElementsByTagName('incident'):
            try:
                data = {}
                for attr in ("report_id", "date", "aircraft_id",
                             "aircraft_type",
                             "pilot_percent_hours_on_type",
                             "pilot_total_hours", "midair"):
                    data[attr] = incident.getAttribute(attr)
                data['date'] = datetime.datetime.strptime(data['date'], '%Y-%m-%s').date()
                data['pilot_percent_hours_on_flight'] = float(data['pilot_percent_hours_on_flight'])
                data['pilot_total_hours'] = int(data['pilot_total_hours'])
                data['midair'] = bool(int(data['midair']))
                airport = incident.getElementsByTagName('airport')[0]
                data['airport'] = get_text(airport.childNodes)
                narrative = incident.getElementsByTagName('narrative')[0]
                data['narrative'] = get_text(narrative.childNodes)
                inc = Incident(**data)
                self[inc.report_id] = inc
            except (ValueError, LookupError, IncidentError) as imp_err:
                print("{0}: import error: {1}".format(os.path.basename(sys.argv[0]), imp_err))
                return False
        return True













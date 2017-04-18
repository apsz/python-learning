#!/usr/bin/python3
# TODO: optargs parsing

import os
import sys
import datetime
import string
import gzip
import pickle
import struct

class IncidentError(Exception): pass


GZIP_MAGIC = b'\x1F\x8B'
MAGIC = b'AIB\x00'
FORMAT_VERSION = b'\x00\x01'
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
                fh.write(GZIP_MAGIC)
            else:
                fh = open(filename, 'wb')
            pickle.dump(self, fh, pickle.HIGHEST_PROTOCOL)
        except (IOError, EnvironmentError, pickle.PicklingError) as save_err:
            raise ValueError('{} error: {}'.format(os.path.basename(sys.argv[0]),
                                                   save_err))
        finally:
            if fh:
                fh.close()

    def import_pickle(self, filename):
        fh = None
        try:
            fh = open(filename, 'rb')
            magic = fh.read(len(GZIP_MAGIC))
            if magic == GZIP_MAGIC:
                fh.close()
                fh = gzip.open(filename, 'rb')
            else:
                fh.seek(0)
            self.clear()
            self.update(pickle.load(fh))
            return True
        except (IOError, EnvironmentError, pickle.PicklingError) as load_err:
            raise ValueError('{} error: {}'.format(os.path.basename(sys.argv[0]),
                                                   load_err))
        finally:
            if fh:
                fh.close()

    def export_binary(self, filename, compress=False):

        def pack_string(string):
            data = string.encode('utf-8')
            format = '{<H{}s}'.format(len(data))
            return struct.pack(format, len(data), data)

        fh = None
        try:
            if compress:
                fh = gzip.open(filename, 'wb')
                fh.write(GZIP_MAGIC)
            else:
                fh = open(filename, 'wb')
            fh.write(MAGIC)
            fh.write(FORMAT_VERSION)
            for incident in self.values():
                data = bytearray()
                data.extend(pack_string(incident.report_id))
                data.extend(pack_string(incident.airport))
                data.extend(pack_string(incident.aircraft_id))
                data.extend(pack_string(incident.aircraft_type))
                data.extend(pack_string(incident.narrative.strip()))
                data.extend(NumbersStruct.pack(incident.date.toordinal(),
                                               incident.pilot_percent_hours_on_type,
                                               incident.pilot_total_hours,
                                               incident.midair))
                fh.write(data)
            return True
        except (IOError, EnvironmentError) as save_err:
            raise ValueError('{} error: {}'.format(os.path.basename(sys.argv[0]),
                                                   save_err))
        finally:
            if fh:
                fh.close()

    def import_binary(self, filename):

        def unpack_string(fh, eof_is_error=True):
            uint16 = struct.Struct('<H')
            data_len = fh.read(uint16.size)
            if not data_len:
                if eof_is_error:
                    raise ValueError('missing or corrupt string data')
                return None
            string_len = uint16.unpack(data_len)[0]
            if not string_len:
                return ""
            data = fh.read(string_len)
            if not data or len(data) != string_len:
                raise ValueError('corrupt data')
            format = '<{}s'.format(string_len)
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
                raise ValueError('Incorrect .aib file format')
            version = fh.read(len(FORMAT_VERSION))
            if version > FORMAT_VERSION:
                raise ValueError('Unrecognized format version')
            while True:
                report_id = unpack_string(fh, False)
                if not report_id:
                    break
                data = {}
                for name in ('airport', 'aircraft_id',
                             'aircraft_type', 'narrative'):
                    data[name] = unpack_string(fh)
                other_data = fh.read(NumbersStruct.size)
                numbers = NumbersStruct.unpack(other_data)
                data['date'] = datetime.datetime.fromordinal(numbers[0])
                data['pilot_percent_hours_on_type'] = numbers [1]
                data['pilot_total_hours'] = numbers[2]
                data['midair'] = numbers[3]
                incident = Incident(**data)
                self[incident.report_id] = incident
            return True
        except (IOError, EnvironmentError) as load_err:
            raise ValueError('{} error: {}'.format(os.path.basename(sys.argv[0]),
                                                   load_err))
        finally:
            if fh:
                fh.close()






#!/usr/bin/python3

import os
import pickle


class ImageError(Exception): pass
class CoordinatesError(ImageError): pass
class NotFileError(ImageError): pass
class SaveError(ImageError): pass
class LoadError(ImageError): pass
class ExportError(ImageError): pass


class Image:
    def __init__(self, length, height, filename='', background='#FFFFFF'):
        self.filename = filename
        self.__length = length
        self.__height = height
        self.__background_color = background
        self.__data = {}
        self.__colors = {self.__background_color}


    @property
    def length(self):
        return self.__length

    @property
    def height(self):
        return self.__height

    @property
    def background_color(self):
        return self.__background_color

    @property
    def colors(self):
        return set(self.__colors)


    def __getitem__(self, coordinates):
        assert len(coordinates) == 2, 'coordinates must be a 2-tuple'
        if not (0 <= coordinates[0] < self.__length and
                0 <= coordinates[1] < self.__height):
            raise CoordinatesError()
        return self.__data.get(tuple(coordinates), self.__background_color)

    def __setitem__(self, coordinates, color):
        assert len(coordinates) == 2, 'coordinates must be a 2-tuple'
        if not (0 <= coordinates[0] < self.__length and
                0 <= coordinates[1] < self.__height):
            raise CoordinatesError
        if color == self.__background_color:
            self.__data.pop(tuple(coordinates), None)
        else:
            self.__data[tuple(coordinates)] = color
            self.__colors.add(color)

    def __delitem__(self, coordinates):
        assert len(coordinates) == 2, 'coordinates must be a 2-tuple'
        if not (0 <= coordinates[0] < self.__length and
                0 <= coordinates[1] < self.__height):
            raise CoordinatesError
        self.__data.pop(tuple(coordinates), None)


    def save(self, filename=''):
        if not filename:
            raise NotFileError()
        else:
            self.filename = filename

        fh = None
        try:
            fh = open(filename, 'wb')
            data = [self.__length, self.__height,
                    self.__background_color, self.__colors, self.__data]
            pickle.dump(fh, data, pickle.HIGHEST_PROTOCOL)
        except (IOError, EnvironmentError, pickle.PicklingError) as save_err:
            raise SaveError(str(save_err))
        finally:
            if fh:
                fh.close()

    def load(self, filename=''):
        if not filename:
            raise NotFileError()
        else:
            self.filename = filename

        fh = None
        try:
            fh = open(filename, 'wb')
            self.__length, self.__height, \
            self.__background_color, self.__colors, self.__data = pickle.load(fh)
        except (IOError, EnvironmentError, pickle.PicklingError) as save_err:
            raise SaveError(str(save_err))
        finally:
            if fh:
                fh.close()

    def export(self, filename):
        if filename.lower().endswith('.xpm'):
            self.__export_xpm(filename)
        else:
            raise ExportError('Cannot export to file: {} is '
                              'not a supported extension.'.format(os.path.splitext(filename)[1]))

    def __export_xpm(self, filename):
        pass


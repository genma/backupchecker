# -*- coding: utf-8 -*-
# Copyright © 2009 Carl Chenet <chaica@ohmytux.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Extract information about the archive (if it is one) and expected saved files
'''Extract information about the archive (if it is one) and expected saved files'''

import logging
import os
import sys
import configparser
from configparser import ParsingError, NoSectionError, NoOptionError
from hashlib import algorithms_guaranteed

class ExpectedValues(object):
    '''Extract information about the archive (if it is one)
    and expected saved files.
    '''

    def __init__(self, __path):
        '''The constructor of the ExpectedValues class.

        __path -- the path to the description of the expected attributes of the files

        '''
        self.__bckfiles= []
        self.__arcdata = {}
        self.__main(__path)

    def __main(self, __path):
        '''Main of the ExpectedValues class'''
        try:
            with open(__path, 'r') as __file:
                self.__retrieve_data(__file)
        except (IOError, OSError) as __err:
            print(__err)
            sys.exit(1)

    def __retrieve_data(self, __file):
        '''Retrieve data from the expected files'''
        #__hashtypes = ['md5', 'sha1', 'sha224','sha256','sha384','sha512']
        __hashtypes = algorithms_guaranteed
        __config = configparser.ConfigParser()
        __config.read_file(__file)
        #########################
        # Test the archive itself
        #########################
        if __config.has_section('archive'):
            __archive = __config.items('archive')
            # Testing the size of the archive
            if 'size' in __config['archive']:
                try:
                    # Testing the items for the expected archive
                    # Testing the size of the archive
                    ### Test if the equality is required
                    if __config['archive']['size'].startswith('='):
                        self.__arcdata['equals'] = self.__convert_arg(__config['archive']['size'])
                    ### Test if bigger than is required
                    elif __config['archive']['size'].startswith('>'):
                        self.__arcdata['biggerthan'] = self.__convert_arg(__config['archive']['size'])
                    ### Test if smaller than is required
                    elif __config['archive']['size'].startswith('<'):
                        self.__arcdata['smallerthan'] = self.__convert_arg(__config['archive']['size'])
                except ValueError as __msg:
                    logging.warn(__msg)
        ##################
        # Test saved files
        ##################
        if __config.has_section('files'):
            __files = __config.items('files')
            for __fileitems in __files:
                __data = {}
                __data['path'] = __fileitems[0]
                if len(__fileitems) == 2:
                    for __item in __fileitems[1].split(' '):
                        try:
                            # Testing the items for an expected file
                            if __item == 'unexpected':
                                __data['unexpected'] = True
                            # The uid of the expected file
                            elif __item.startswith('uid:'):
                                __data['uid'] = int(__item.split(':')[-1])
                            # The gid of the expected file
                            elif __item.startswith('gid:'):
                                __data['gid'] = int(__item.split(':')[-1])
                            # The mode of the expected file
                            elif __item.startswith('mode:'):
                                __mode =__item.split(':')[-1]
                                if len(__mode) < 3 or len(__mode) > 4:
                                    logging.warn('{}: Wrong format for the mode.'.format(__data['path']))
                                else:
                                    __data['mode'] = __mode
                            # Testing the type of the file
                            elif __item.startswith('type:'):
                                __type =__item.split(':')[-1]
                                ### f for file, c for character, d for directory
                                ### s for symbolink link, b for block, o for fifo,
                                ### k for socket
                                __types = ('f','c','d','s','b','o','k')
                                if __type not in __types:
                                    logging.warn('{}: Unknown type {} for file parameter'.format(__data['path'], __type))
                                else:
                                    __data['type'] = __type
                            # Testing the size of the file
                            ### Test if the equality is required
                            elif __item.startswith('='):
                                __data['equals'] = self.__convert_arg(__item)
                            ### Test if bigger than is required
                            elif __item.startswith('>'):
                                __data['biggerthan'] = self.__convert_arg(__item)
                            ### Test if smaller than is required
                            elif __item.startswith('<'):
                                __data['smallerthan'] = self.__convert_arg(__item)
                            # Test if a hash is provided for this file
                            for __hash in __hashtypes:
                                if __item.startswith('{}{}'.format(__hash, ':')):
                                    __hashtype, __hashvalue = __item.split(':')
                                    __data['hash'] = {'hashtype':__hashtype, 'hashvalue':__hashvalue}
                        except ValueError as __msg:
                            logging.warn(__msg)
                self.__bckfiles.append(__data)

    def __convert_arg(self, __arg):
        '''Convert the given file length to bytes'''
        __res = 0
        try:
            for __value, __power in [('K', 1),('M', 2),('G', 3),('P', 4),
                                        ('E', 5),('Z', 6),('Y', 7)]:
                if __arg.endswith(__value):
                    __res = int(__arg[1:-1]) * 1024**__power
            if __res == 0:
                __res = int(__arg[1:])
        except ValueError as __msg:
            print(__msg)
            logging.warn(__msg)
            __res = 0
        finally:
            return __res

    @property
    def data(self):
        '''Return the paths of the expected files in the archive'''
        return self.__bckfiles, self.__arcdata
# -*- coding: utf-8 -*-

"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    Development Team: Brain Storm Team
"""

import random


class AcceptHeaderProvider(object):
    """ AcceptHeaderProvider class"""

    def __init__(self):
        """
        Init interface
        """

        self.__accept = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'

        self.__accept_encoding = 'gzip, deflate'

        self.__accept_language = (
            'en-US,en;q=0.9',
            'en-US,en;q=0.9,ru;q=0.8,uk;q=0.7',
            'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,uk;q=0.6',
            'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'en-GB,en;q=0.9,en-US;q=0.8'
        )

    @property
    def _accept(self):
        """
        Get 'Accept' Header
        :return: str
        """

        return self.__accept

    @property
    def _accept_encoding(self):
        """
        Get 'Accept-Encoding' Header
        :return: str
        """

        return self.__accept_encoding

    @property
    def _accept_language(self):
        """
        Get 'Accept-Language' Header
        :return: str
        """

        index = random.randrange(0, len(self.__accept_language))
        accept = self.__accept_language[index]

        return accept

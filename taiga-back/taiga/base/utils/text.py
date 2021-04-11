# -*- coding: utf-8 -*-
# Copyright (C) 2014-present Taiga Agile LLC
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


def strip_lines(text):
    """
    Given text, try remove unnecessary spaces and
    put text in one unique line.
    """
    return text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").strip()


def split_in_lines(text):
    """Split a block of text in lines removing unnecessary spaces from each line."""
    return (line for line in map(str.strip, text.split("\n")) if line)

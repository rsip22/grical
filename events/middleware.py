#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:expandtab:tabstop=4 shiftwidth=4 textwidth=79
#############################################################################
# Copyright 2009, 2010 Ivan Villanueva <ivan ät gridmind.org>, 
#                      A. Beret Mańczuk <beret@hipisi.org.pl>
#
# This file is part of GridCalendar.
#
# GridCalendar is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# GridCalendar is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the Affero GNU General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with GridCalendar. If not, see <http://www.gnu.org/licenses/>.
#############################################################################
'''
Created on 2010-07-25

@author: beret@hipisi.org.pl
'''

from gridcalendar.events.signals import user_auth_signal

class SendAuthMiddleware(object):# pylint: disable-msg=R0903
    "middleware for send auth user signal"
    def process_request(self, request):
        "send auth user signals"
        user_auth_signal.send(sender = self, user = request.user)

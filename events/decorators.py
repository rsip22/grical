#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:expandtab:tabstop=4 shiftwidth=4 textwidth=79
#############################################################################
# Copyright 2009, 2010 Iván F. Villanueva B. <ivan ät gridmind.org>,
#                      A. Beret Mańczuk <beret@hipisi.org.pl>
#
# This file is part of GridCalendar.
#
# GridCalendar is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# GridCalendar is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the Affero GNU General Public License
# for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with GridCalendar. If not, see <http://www.gnu.org/licenses/>.
#############################################################################
'''
Created on 2010-07-25

@author: beret@hipisi.org.pl
'''

from django.contrib.auth.decorators \
    import login_required as super_login_required
from gridcalendar.events.signals import user_auth_signal

def login_required(view_func):
    "decorator for login_required decorator to send auth user info"
    def func(request, *args, **kwargs):
        "fuction container to send signal after authorise"
        
        user_auth_signal.send(sender = view_func, user = request.user)
        return view_func(request, *args, **kwargs)
    return super_login_required(func)

#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set expandtab tabstop=4 shiftwidth=4 textwidth=79 foldmethod=marker:
# gpl {{{1
#############################################################################
# Copyright 2009-2016 Stefanos Kozanis <stefanos ät wikical.com>
#
# This file is part of GriCal.
#
# GriCal is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# GriCal is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the Affero GNU General Public License for more
# details.
#
# You should have received a copy of the GNU Affero General Public License
# along with GriCal. If not, see <http://www.gnu.org/licenses/>.
#############################################################################
""" Main urls definition file. """
# imports {{{1
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls import * # pylint: disable-msg=W0401,W0614,W0614
# previous pylint directive is needed because of a bug in Django:
# http://code.djangoproject.com/ticket/5350

from grical.events import views

# registrations {{{1
admin.autodiscover()

# handler404 and handler500 {{{1
handler404 = views.handler404
handler500 = views.handler500

# patterns for administrations, db and accounts {{{1
urlpatterns = patterns( '', # pylint: disable-msg=C0103
    ( r'^a/admin/doc/', include( 'django.contrib.admindocs.urls' ) ),
    #(r'^a/admin/(.*)', admin.site.root),
    ( r'^a/admin/', admin.site.urls ),
    ( r'^a/accounts/', include( 'registration.backends.default.urls' ) ),
    ( r'^a/accounts/logout/$',
        'django.contrib.auth.views.logout', {'next_page': '/'} ),
 )

# comments / feedback
# see http://docs.djangoproject.com/en/1.3/ref/contrib/comments/
urlpatterns += patterns( '',
        (r'^c/comments/', include('django_comments.urls')),
        (r'^c/feedback/', include('grical.contact_form.urls')),
 )

# h pattern for help and legal_notice {{{1
urlpatterns += patterns( '',
        url( r'^h/help/', 'grical.events.views.help_page',
            name = "help" ),
        url( r'^h/legal_notice/', 'grical.events.views.legal_notice',
            name = "legal_notice" ),
 )

# include events.urls {{{1
urlpatterns += patterns( '',
    ( r'', include( 'grical.events.urls' ) ),
 )

# see https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-development
urlpatterns += staticfiles_urlpatterns()
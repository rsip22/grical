#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:expandtab:tabstop=4 shiftwidth=4 textwidth=79
#############################################################################
# Copyright 2010 Adam Beret Manczuk <beret@hipisi.org.pl>,
# Ivan Villanueva <iv@gridmind.org>
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
# FITNESS FOR A PARTICULAR PURPOSE. See the Affero GNU Generevent.idal Public License
# for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with GridCalendar. If not, see <http://www.gnu.org/licenses/>.
#############################################################################
from base64 import decode

"""recive events from imap mailbox"""
from imaplib import IMAP4
from gridcalendar.events.models import Event
from django.conf import settings
import email, re, sys
from django.core.mail import send_mail, get_connection
from django.core.mail.message import EmailMessage
from django.utils.translation import ugettext_lazy as _
from django.core.management.base import NoArgsCommand


class Command( NoArgsCommand ):
    """ A management command which Parse mails from imap server..
    """

    help = "Parse mails from imap server"

    def __init__( self, *args, **kwargs ):
        self.M = IMAP4( settings.IMAP_SERVER )
        self.M.login( settings.IMAP_LOGIN, settings.IMAP_PASSWD )
        self.M.select()
        super( Command, self ).__init__( *args, **kwargs )

    def get_list( self ):
        typ, data = self.M.search( None, 'ALL' )
        return data[0]

    def handle_noargs( self, **options ):
        """ Executes the action. """
        self.parse()

    def parse( self ):
        '''
        parse all mails from imap mailbox
        '''
        re_charset = re.compile( r'charset=([^\s]*)', re.IGNORECASE )
        for nr in self.get_list():
            typ, data = self.M.fetch( nr, '(RFC822 UID BODY[TEXT])' )
            if data and len( data ) > 1:
                mail = email.message_from_string( data[0][1] )
                charset = False
                if 'Content-Type' in mail.keys():
                    charset = \
                        filter( lambda x: x, \
                                map( lambda x: re_charset.findall( x ), \
                                     mail['Content-Type'].split( ';' ) ) )
                if charset:
                    charset = charset[0][0]
                else:
                    charset = 'utf-8'
                text = data[1][1].decode( charset )
                event = Event.parse_text( text )
                if type( event ) == Event :
                    self.mv_mail( nr, 'saved' )
                    sys.stdout.write( 'Successfully add new event: %s\n' \
                                       % event.title )
                else:
                    errors = event
                    self.mv_mail( nr, 'errors' )
                    subject = _( 'Validation error in: %s' % \
                                 mail['Subject'].replace( '\n', ' ' ) )
                    subject = subject.replace( '\n', ' ' )
                    message = '\n'.join( map( str, errors ) )
                    sys.stderr.write( "Found errors in message %s: \n%s\n" % \
                                      ( mail['Subject'], message ) )
                    to_email = mail['From']
                    from_email = settings.DEFAULT_FROM_EMAIL
                    if subject and message and from_email:
                        mail = EmailMessage( subject, message, \
                                             from_email, ( to_email, ) )
                        msg = str( mail.message() )
                        mail.send()
                        self.M.append( 'IMAP.sent', None, None, \
                                       msg )


        if self.get_list():
            return self.parse()

    def mv_mail( self, nr, mbox_name ):
        self.M.copy( nr, "INBOX.%s" % mbox_name )
        self.M.store( nr, '+FLAGS', '\\Deleted' )
        self.M.expunge()

    def __del__( self, *args, **kwargs ):
        self.M.close()
        self.M.logout()


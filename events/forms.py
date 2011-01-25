#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vi:expandtab:tabstop=4 shiftwidth=4 textwidth=79
#############################################################################
# Copyright 2009, 2010 Ivan Villanueva <ivan ät gridmind.org>
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

""" Forms """

import re
import datetime

from django.forms import ( CharField, IntegerField, HiddenInput,
        ModelMultipleChoiceField, URLField, ModelForm, ValidationError,
        TextInput, CheckboxSelectMultiple, Form, Field )
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from gridcalendar.settings_local import DEBUG
from gridcalendar.events.models import (Event, EventUrl, EventDeadline,
        EventSession, Filter, Group, Membership)
from gridcalendar.events.utils import validate_year

def _date(string):
    """ parse a date in the format ``yyyy-mm-dd`` using
    ``gridcalendar.events.utils.valida """
    parsed_date = datetime.datetime.strptime(string, '%Y-%m-%d').date()
    validate_year( parsed_date )
    return parsed_date

def _time(string):
    """ parse a time in the format: hh:mm """
    return datetime.datetime.strptime(string, '%H:%M').time()

class DatesTimesField(Field):
    """ processes one or two dates and optionally one or two times.

    Valid formats:

    - 2010-01-25
    - 2010-01-25 2010-01-26
    - 2010-01-25 10:00
    - 2010-01-25 10:00 2010-01-26 18:00
    - 2010-01-25 10:00 11:00
    - 2010-01-25 10:00-11:00

    >>> dt = DatesTimesField()
    >>> d = dt.to_python('2010-01-25')
    >>> d = dt.to_python('2010-01-25 2010-01-26')
    >>> d = dt.to_python('2010-01-25 10:00')
    >>> d = dt.to_python('2010-01-25 10:00 2010-01-26 18:00')
    >>> d = dt.to_python('2010-01-25 10:00 11:00')
    >>> d = dt.to_python('2010-01-25 10:00-11:00')
    """
    def to_python(self, value):
        """ returns a dictionary with four values: start_date, end_date,
        start_time, end_time """
        re_d = \
            re.compile( r'^\s*(\d\d\d\d-\d\d-\d\d)\s*$', re.UNICODE )
        re_d_d = \
            re.compile(r'^\s*(\d\d\d\d-\d\d-\d\d)\s+(\d\d\d\d-\d\d-\d\d)\s*$',
                    re.UNICODE)
        re_d_t = \
            re.compile(r'^\s*(\d\d\d\d-\d\d-\d\d)\s+(\d\d:\d\d)\s*$',
                    re.UNICODE)
        re_d_t_d_t = \
            re.compile(r"""
                ^\s*(\d\d\d\d-\d\d-\d\d)
                \s+(\d\d:\d\d)
                \s+(\d\d\d\d-\d\d-\d\d)
                \s+(\d\d:\d\d)\s*$""", re.UNICODE | re.X )
        re_d_t_t = \
            re.compile(r"""
                ^\s*(\d\d\d\d-\d\d-\d\d)
                \s+(\d\d:\d\d)
                \s+(\d\d:\d\d)\s*$""", re.UNICODE | re.X )
        re_d_t_t =   re.compile( r"""
            ^\s*(\d\d\d\d-\d\d-\d\d) # beginning, optional spaces, start date
             \s+(\d\d:\d\d)          # start time after one ore more spaces
             (?:(?:\s+)|(?:\s*-\s*)) # one or more spaces, alternatively -
             (\d\d:\d\d)\s*$         # end time before optinal spaces""",
            re.UNICODE | re.X )
        try:
            matcher = re_d.match(value)
            if matcher:
                return {'start_date': _date(matcher.group(1)),}
            matcher = re_d_d.match(value)
            if matcher:
                return {'start_date': _date(matcher.group(1)),
                        'end_date': _date(matcher.group(2))}
            matcher = re_d_t.match(value)
            if matcher:
                return {'start_date': _date(matcher.group(1)),
                        'start_time': _time(matcher.group(2))}
            matcher = re_d_t_d_t.match(value)
            if matcher:
                return {'start_date': _date(matcher.group(1)),
                        'start_time': _time(matcher.group(2)),
                        'end_date': _date(matcher.group(3)),
                        'end_time': _time(matcher.group(4))}
            matcher = re_d_t_t.match(value)
            if matcher:
                return {'start_date': _date(matcher.group(1)),
                        'start_time': _time(matcher.group(2)),
                        'end_time': _time(matcher.group(3))}
        except (TypeError, ValueError), e:
            pass
        except ValidationError, e:
            # the validationError comes from utils.validate_year and the error
            # message is translated
            raise e
        raise ValidationError( _('not a valid syntax') )
        #raise ValidationError( e.message )

    def validate(self, value):
        """ checks that dates and times are in order, i.e. start before end """
        if value.has_key('end_date'):
            if value['start_date'] > value['end_date']:
                raise ValidationError( _('end date is before start date') )
        if value.has_key('end_time'):
            if value['start_time'] > value['end_time']:
                raise ValidationError( _('end time is before start time') )

def get_event_form(user):
    """returns a simplied event form with or without the public field"""
    """ returns a dictionary with four values: start_date, end_date,
    start_time, end_time """

    if user.is_authenticated():
        return SimplifiedEventForm()
    return SimplifiedEventFormAnonymous()

class FilterForm(ModelForm):
    """ ModelForm using Filter excluding `user` """
    class Meta: # pylint: disable-msg=C0111,W0232,R0903
        model = Filter
        exclude = ('user',)

class EventForm(ModelForm):
    """ ModelForm for all editable fields of Event except `public` """
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['title'].widget.attrs["size"] = 70
        self.fields['start'].widget.attrs["size"] = 10
        self.fields['end'].widget.attrs["size"] = 10
        self.fields['starttime'].widget.attrs["size"] = 5
        self.fields['endtime'].widget.attrs["size"] = 5
        self.fields['tags'].widget.attrs["size"] = 70
        self.fields['address'].widget.attrs["size"] = 70
        self.fields['description'].widget.attrs["rows"] = 20
        self.fields['description'].widget.attrs["cols"] = 70
    class Meta: # pylint: disable-msg=C0111,W0232,R0903
        model = Event
        # notes: public field cannot be edited after creation, startime and
        # endtime are processed within start and end
        exclude = ('public')
    def clean_tags(self): # pylint: disable-msg=C0111
        data = self.cleaned_data['tags']
        if re.search("[^ \-\w]", data, re.UNICODE):
            raise ValidationError(_(u"Punctuation marks are not allowed"))
        # Always return the cleaned data, whether you have changed it or not.
        return data

class SimplifiedEventForm(EventForm):
    """ ModelForm for Events with only the fields `title`, `start`, `tags`,
    `public` """
    where = CharField( max_length = 100, required = False )
    when = DatesTimesField()
    if DEBUG:
        web = URLField(verify_exists=False)
    else:
        web = URLField(verify_exists=True)
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.fields['title'].label = _(u'What')
        self.fields['where'].label = _(u'Where')
        self.fields['where'].help_text = \
                _(u'Example: Malmöer Str. 6, Berlin, DE')
        self.fields['when'].label = _(u'When')
        self.fields['when'].help_text = \
                _(u'Example: 2010-02-27 11:00-13:00')
        #self.fields['title'].widget.attrs["size"] = 42
        #self.fields['tags'].widget.attrs["size"] = 42
        #self.fields['web'].widget.attrs["size"] = 42
    class Meta:  # pylint: disable-msg=C0111,W0232,R0903
        model = Event
        fields = ('title', 'tags', 'public')

class SimplifiedEventFormAnonymous(SimplifiedEventForm):
    """ ModelForm for Events with only the fields `title`, `start`, `tags`
    """
    class Meta:  # pylint: disable-msg=C0111,W0232,R0903
        model = Event
        fields = ('title', 'tags')

class EventUrlForm(ModelForm):
    """ ModelForm for EventUrl """
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
    class Meta: # pylint: disable-msg=C0111,W0232,R0903
        model = EventUrl

class EventDeadlineForm(ModelForm):
    """ ModelForm for EventDeadline """
    class Meta: # pylint: disable-msg=C0111,W0232,R0903
        model = EventDeadline

class EventSessionForm(ModelForm):
    """ A ModelForm for an EventSession with small sizes for the widget of some
        fields. """
    # TODO: better use CSS: modify the widget to add a html css class name.
    def __init__(self, *args, **kwargs):
        super(EventSessionForm, self).__init__(*args, **kwargs)
        assert(self.fields.has_key('session_date'))
        self.fields['session_date'].widget = TextInput(attrs = {'size':10})
        assert(self.fields.has_key('session_starttime'))
        self.fields['session_starttime'].widget = TextInput(attrs = {'size':5})
        assert(self.fields.has_key('session_endtime'))
        self.fields['session_endtime'].widget = TextInput(attrs = {'size':5})
    class Meta: # pylint: disable-msg=C0111,W0232,R0903
        model = EventSession

class NewGroupForm(ModelForm):
    """ ModelForm for Group with only the fields `name` and `description` """
    class Meta:  # pylint: disable-msg=C0111,W0232,R0903
        model = Group
        fields = ('name', 'description',)

class AddEventToGroupForm(Form):
    """ Form with a overriden constructor that takes an user and an event and
    provides selectable group names in which the user is a member of and the
    event is not already in the group. """
    grouplist = ModelMultipleChoiceField(
            queryset=Group.objects.none(), widget=CheckboxSelectMultiple())
    def __init__(self, user, event, *args, **kwargs):
        super(AddEventToGroupForm, self).__init__(*args, **kwargs)
        self.fields["grouplist"].queryset = \
                Group.groups_for_add_event(user, event)
        self.fields['grouplist'].label = _(u'Groups:')

class InviteToGroupForm(Form):
    """ Form for a user name to invite to a group """
    group_id = IntegerField(widget=HiddenInput)
    # TODO: use the constrains of the model User
    username = CharField(max_length=30)
    def __init__(self, *args, **kwargs):
        super(InviteToGroupForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = _(u'Username')
    def clean(self):
        """ Cheks that the user and group exist and the user is not in the
        group already """
        # see http://docs.djangoproject.com/en/1.2/ref/forms/validation/#cleaning-and-validating-fields-that-depend-on-each-other
        cleaned_data = self.cleaned_data
        group_id = cleaned_data.get("group_id")
        username = cleaned_data.get("username")
        if group_id and username:
            # no errors found so far
            try:
                group = Group.objects.get( id = group_id )
                user = User.objects.get( username = username )
                if Membership.objects.filter(
                        user = user, group = group).exists():
                    msg = _( u"This user is already in the group" )
                    self._errors['username'] = self.error_class([msg])
                    del cleaned_data['username']
            except Group.DoesNotExist:
                msg = _( u"The group doesn't exist" )
                self._errors['group_id'] = self.error_class([msg])
                del cleaned_data['group_id']
            except User.DoesNotExist:
                msg = _( u"The user doesn't exist" )
                self._errors['username'] = self.error_class([msg])
                del cleaned_data['username']
        return cleaned_data
    # TODO: accept also an email and create an account with the username as
    # email and a random generated password sent by email to the user
    # (encrypted if possible)

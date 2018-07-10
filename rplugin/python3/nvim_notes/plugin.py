# pylint: disable=missing-docstring
from functools import wraps

import neovim

from nvim_notes.helpers.markdown_helpers import sort_markdown_events
from nvim_notes.utils.constants import FILE_TYPE_WILDCARD, ISO_FORMAT
from nvim_notes.utils.make_markdown_file import make_todays_diary
from nvim_notes.utils.make_schedule import set_schedule_from_events_list
from nvim_notes.utils.nvim_google_cal_class import SimpleNvimGoogleCal
from nvim_notes.utils.parse_markdown import (combine_events,
                                             parse_markdown_file_for_events,
                                             remove_events_not_from_today)
from nvim_notes.utils.plugin_options import PluginOptions


def if_active(function):
    """if_active

    A decorator for a function, such that it is only run when
    nvim_notes is ready.

    Taken from numirias/semshi
    """
    @wraps(function)
    def wrapper(self):
        if not self.options.active:
            return
        function(self)
    return wrapper


@neovim.plugin
class NotesPlugin(object):

    def __init__(self, nvim):
        self._nvim = nvim
        self._options = None
        self._gcal_service = None

    @neovim.autocmd('BufEnter', pattern=FILE_TYPE_WILDCARD, sync=True)
    def event_buf_enter(self):
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(
                self._nvim,
                self._options
            )

    @neovim.command('MakeDiary')
    # @if_active
    def make_diary(self):

        # TODO: Remove this, since it shouldn't be needed due to the autocmds.
        if self._options is None:
            self._options = PluginOptions(self._nvim)
            self._gcal_service = SimpleNvimGoogleCal(
                self._nvim,
                self._options
            )

        make_todays_diary(
            self._nvim,
            self._options,
            self._gcal_service
        )

    @neovim.command('UploadCalendar')
    def upload_to_calendar(self):
        markdown_events = parse_markdown_file_for_events(
            self._nvim,
            ISO_FORMAT
        )

        self._gcal_service.upload_to_calendar(markdown_events)
        remove_events_not_from_today(self._nvim)

    @neovim.command('GrabCalendar')
    def grab_from_calendar(self):
        markdown_events = parse_markdown_file_for_events(
            self._nvim,
            ISO_FORMAT
        )
        cal_events = self._gcal_service.get_events_for_today()

        combined_events = combine_events(
            markdown_events,
            cal_events
        )
        set_schedule_from_events_list(self._nvim, combined_events, False)
        self.sort_calendar()

    @neovim.command('UpdateCalendar')
    def update_calendar(self):
        self.upload_to_calendar()
        self.grab_from_calendar()

    @neovim.command('SortCalendar')
    def sort_calendar(self):
        sort_markdown_events(self._nvim)
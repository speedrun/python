from collections import namedtuple

SuiteItem = \
    namedtuple('SuiteItem', ['type', 'location', 'details', 'size', 'scope', 'tags', 'deps'])
SuiteItem.__new__.__defaults__ = (None,) * len(SuiteItem._fields)

ReportItem = \
    namedtuple('ReportItem', ['type', 'location', 'status', 'error', 'started_at', 'finished_at', 'worker_id', 'process_id'])
ReportItem.__new__.__defaults__ = (None,) * len(ReportItem._fields)

Schedule = \
    namedtuple('Schedule', ['items'])

ScheduleItem = \
    namedtuple('ScheduleItem', ['file'])

Location = \
    namedtuple('Location', ['file', 'module', 'cls', 'func', 'line'])
Location.__new__.__defaults__ = (None,) * len(Location._fields)

Tag = \
    namedtuple('Tag', ['group', 'singleton'])
Tag.__new__.__defaults__ = (None,) * len(Tag._fields)

Failure = \
    namedtuple('Failure', ['type', 'message'])
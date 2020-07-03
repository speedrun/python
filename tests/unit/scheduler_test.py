from datetime import datetime

import pytest

from testandconquer.client import MessageType
from testandconquer.model import Location, Report, Schedule, SuiteItem
from testandconquer.scheduler import Scheduler

from unittest import mock
from tests.mock.client import MockClient
from tests.mock.settings import MockSettings
from tests import error_messages


def test_reply_to_config_message():
    class MockSerializer:
        @staticmethod
        def serialize_config(settings):
            return settings

    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, [], client=client, serializer=MockSerializer)

    scheduler.on_server_message(MessageType.Config.value, None)

    assert client.received == [
        (MessageType.Config, settings),
    ]

    scheduler.stop()


def test_reply_to_schedule_message():
    class MockSerializer:
        @staticmethod
        def deserialize_schedule(payload):
            return Schedule(payload['id'], payload['items'])

    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, [], client=client, serializer=MockSerializer)

    payload = [{'id': 'ID', 'items': [['A'], ['B']]}]
    scheduler.on_server_message(MessageType.Schedules.value, payload)

    assert scheduler.next() == Schedule('ID', [['A'], ['B']])

    scheduler.stop()


def test_reply_to_suite_message():
    class MockSerializer:
        @staticmethod
        def serialize_suite(suite_items):
            return suite_items

    settings = MockSettings({})
    client = MockClient(settings)
    suite_items = [SuiteItem('test', Location('tests/IT/stub/stub_A.py', 'stub_A', 'TestClass', 'test_A', 1))]
    scheduler = Scheduler(settings, suite_items, client=client, serializer=MockSerializer)

    scheduler.on_server_message(MessageType.Suite.value, None)

    assert client.received == [
        (MessageType.Suite, suite_items),
    ]

    scheduler.stop()


def test_reply_to_done_message():
    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, [], client=client)
    assert scheduler.more is True

    scheduler.on_server_message(MessageType.Done.value, None)

    assert scheduler.more is False

    scheduler.stop()


@mock.patch('testandconquer.util.datetime')
def test_reply_to_error_message(datetime_mock, caplog, event_loop):
    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, [], client=client)

    with pytest.raises(SystemExit):
        datetime_mock.utcnow = mock.Mock(return_value=datetime(2000, 1, 1))
        event_loop.run_until_complete(scheduler.on_server_message(MessageType.Error.value, {
            'title': 'title',
            'body': 'body',
            'meta': {
                'Name': 'Value',
            },
        }))

    assert error_messages(caplog) == [
        '\n'
        '\n'
        '    '
        '================================================================================\n'
        '\n'
        '    [ERROR] [CONQUER] title\n'
        '\n'
        '    body\n'
        '\n'
        '    [Name = Value]\n'
        '    [Timestamp = 2000-01-01T00:00:00]\n'
        '\n'
        '    '
        '================================================================================\n'
        '\n',
    ]


def test_report():
    class MockSerializer:
        @staticmethod
        def serialize_report(report):
            return report

    settings = MockSettings({})
    client = MockClient(settings)
    scheduler = Scheduler(settings, [], client=client, serializer=MockSerializer)

    scheduler.start()
    report = Report('ID', '<items>', None, None, None)
    scheduler.report(report)

    scheduler.stop()  # flushes reports

    assert client.received == [
        (MessageType.Ack, {'schedule_id': 'ID', 'status': 'success'}),
        (MessageType.Report, report),
    ]

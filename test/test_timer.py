import logging
import time

import pytest

import timer

logger = logging.getLogger(f'{__name__}')
logger.setLevel('DEBUG')


def test_timer_a_non_named_timer(caplog, capfd):
    timer.Timer.timers = {}
    my_timer = timer.Timer(logger=logger.info, silent=False)
    my_timer.start()
    time.sleep(0.01)
    my_timer.stop()

    assert my_timer.name is None
    assert my_timer.silent == False
    assert len(my_timer.timers) == 0


def test_timer_as_instance(caplog, capfd):
    timer.Timer.timers = {}
    my_timer = timer.Timer(name='test_timer', logger=logger.info, silent=False)
    my_timer.start()
    time.sleep(0.01)
    my_timer.stop()

    assert len(caplog.records) > 0

    assert caplog.records[0].levelname == 'INFO'

    assert 'Time taken: 0.01 seconds' in caplog.records[0].message

    out, err = capfd.readouterr()

    assert out == 'Time taken: 0.01 seconds\n'

    # assert len(my_timer.timers) == 1
    assert 'test_timer' in my_timer.timers.keys()
    assert my_timer.name == 'test_timer'


def test_timer_as_instance_error_when_start_already_running_timer(caplog, capfd):
    timer.Timer.timers = {}
    my_timer = timer.Timer(name='test_timer', logger=logger.info, silent=False)
    my_timer.start()
    time.sleep(0.01)
    with pytest.raises(timer.TimerError) as exc:
        my_timer.start()

    assert isinstance(exc.type, type(timer.TimerError))


def test_timer_as_instance_error_when_stop_a_non_running_timer(caplog, capfd):
    timer.Timer.timers = {}
    my_timer = timer.Timer(name='test_timer', logger=logger.info, silent=False)
    with pytest.raises(timer.TimerError) as exc:
        my_timer.stop()

    assert isinstance(exc.type, type(timer.TimerError))


def test_timer_context_manager(caplog, capfd):
    timer.Timer.timers = {}
    with timer.Timer(name='test_timer', logger=logger.info, silent=False):
        time.sleep(.01)

    assert len(caplog.records) > 0

    assert caplog.records[0].levelname == 'INFO'

    assert 'Time taken: 0.01 seconds' in caplog.records[0].message

    out, err = capfd.readouterr()

    assert out == 'Time taken: 0.01 seconds\n'


def test_timer_contect_manager_no_logger(caplog, capfd):
    timer.Timer.timers = {}
    with timer.Timer(name='test_timer', silent=False):
        time.sleep(.01)

    assert len(caplog.records) == 0

    out, err = capfd.readouterr()

    assert out == 'Time taken: 0.01 seconds\n'


def test_timer_contect_manager_silent_mode(caplog, capfd):
    timer.Timer.timers = {}
    with timer.Timer(name='test_timer', logger=logger.info, silent=True):
        time.sleep(.01)

    assert len(caplog.records) > 0

    assert caplog.records[0].levelname == 'INFO'

    assert 'Time taken: 0.01 seconds' in caplog.records[0].message

    out, err = capfd.readouterr()

    assert out == ''


def test_timer_as_decorator(caplog, capfd):
    timer.Timer.timers = {}

    @timer.Timer(name='test_timer', logger=logger.info, silent=False)
    def sleep_for_a_time():
        time.sleep(.01)

    sleep_for_a_time()

    assert len(caplog.records) > 0

    assert caplog.records[0].levelname == 'INFO'

    assert 'Time taken: 0.01 seconds' in caplog.records[0].message

    out, err = capfd.readouterr()

    assert out == 'Time taken: 0.01 seconds\n'






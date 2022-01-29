import calendar
import time
from src.actionlog.actionlog import update_summary


def test_update_summary(DDBT):
    timestamp = calendar.timegm(time.gmtime())
    result, status = update_summary("+16072152471", "pushups", 10, timestamp)
    assert status
    assert result["sum_total"] == 10

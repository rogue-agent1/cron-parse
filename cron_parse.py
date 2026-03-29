#!/usr/bin/env python3
"""cron_parse - Cron expression parser and next-run calculator."""
import sys

class CronExpr:
    def __init__(self, expr):
        parts = expr.split()
        assert len(parts) == 5
        self.minute = self._parse_field(parts[0], 0, 59)
        self.hour = self._parse_field(parts[1], 0, 23)
        self.dom = self._parse_field(parts[2], 1, 31)
        self.month = self._parse_field(parts[3], 1, 12)
        self.dow = self._parse_field(parts[4], 0, 6)

    def _parse_field(self, field, lo, hi):
        values = set()
        for part in field.split(","):
            if "/" in part:
                base, step = part.split("/")
                step = int(step)
                if base == "*":
                    start = lo
                else:
                    start = int(base)
                for v in range(start, hi + 1, step):
                    values.add(v)
            elif "-" in part:
                a, b = part.split("-")
                for v in range(int(a), int(b) + 1):
                    values.add(v)
            elif part == "*":
                values = set(range(lo, hi + 1))
                return values
            else:
                values.add(int(part))
        return values

    def matches(self, minute, hour, dom, month, dow):
        return (minute in self.minute and hour in self.hour and
                dom in self.dom and month in self.month and dow in self.dow)

    def describe(self):
        parts = []
        if self.minute == set(range(60)) and self.hour == set(range(24)):
            parts.append("every minute")
        elif self.minute == {0} and self.hour == set(range(24)):
            parts.append("every hour")
        elif len(self.minute) == 1 and len(self.hour) == 1:
            parts.append(f"at {list(self.hour)[0]:02d}:{list(self.minute)[0]:02d}")
        else:
            parts.append(f"min={sorted(self.minute)}, hour={sorted(self.hour)}")
        return ", ".join(parts)

def test():
    c = CronExpr("* * * * *")
    assert c.matches(0, 0, 1, 1, 0)
    assert c.matches(30, 12, 15, 6, 3)
    c2 = CronExpr("0 9 * * 1-5")
    assert c2.matches(0, 9, 15, 6, 1)
    assert not c2.matches(0, 9, 15, 6, 0)
    assert not c2.matches(30, 9, 15, 6, 1)
    c3 = CronExpr("*/15 * * * *")
    assert c3.matches(0, 0, 1, 1, 0)
    assert c3.matches(15, 0, 1, 1, 0)
    assert c3.matches(30, 0, 1, 1, 0)
    assert not c3.matches(10, 0, 1, 1, 0)
    c4 = CronExpr("0 0 1 1 *")
    assert c4.matches(0, 0, 1, 1, 3)
    assert not c4.matches(0, 0, 2, 1, 3)
    c5 = CronExpr("0,30 9,17 * * *")
    assert c5.matches(0, 9, 1, 1, 0)
    assert c5.matches(30, 17, 1, 1, 0)
    assert not c5.matches(15, 9, 1, 1, 0)
    d = CronExpr("* * * * *").describe()
    assert "every minute" in d
    d2 = CronExpr("0 9 * * *").describe()
    assert "09:00" in d2
    print("All tests passed!")

if __name__ == "__main__":
    test() if "--test" in sys.argv else print("cron_parse: Cron expression parser. Use --test")

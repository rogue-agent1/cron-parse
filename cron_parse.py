#!/usr/bin/env python3
"""Cron expression parser and next-run calculator."""
import sys
from datetime import datetime, timedelta

class CronExpr:
    def __init__(self, expr):
        parts = expr.split()
        assert len(parts) == 5, "Need 5 fields: min hour dom month dow"
        self.fields = [self._parse(p, r) for p, r in zip(parts, [(0,59),(0,23),(1,31),(1,12),(0,6)])]
    def _parse(self, field, rng):
        lo, hi = rng
        if field == "*": return set(range(lo, hi+1))
        result = set()
        for part in field.split(","):
            if "/" in part:
                base, step = part.split("/")
                start = lo if base == "*" else int(base)
                result.update(range(start, hi+1, int(step)))
            elif "-" in part:
                a, b = part.split("-")
                result.update(range(int(a), int(b)+1))
            else:
                result.add(int(part))
        return result
    def matches(self, dt):
        return (dt.minute in self.fields[0] and dt.hour in self.fields[1] and
                dt.day in self.fields[2] and dt.month in self.fields[3] and
                dt.weekday() in {(d-1)%7 for d in self.fields[4]} | ({6} if 0 in self.fields[4] else set()))
    def next_run(self, after=None, limit=525960):
        dt = (after or datetime.now()).replace(second=0, microsecond=0) + timedelta(minutes=1)
        for _ in range(limit):
            dow_set = set()
            for d in self.fields[4]:
                dow_set.add((d - 1) % 7 if d > 0 else 6)
            if (dt.minute in self.fields[0] and dt.hour in self.fields[1] and
                dt.day in self.fields[2] and dt.month in self.fields[3] and
                dt.weekday() in dow_set):
                return dt
            dt += timedelta(minutes=1)
        return None

def describe(expr):
    parts = expr.split()
    descs = []
    labels = ["minute", "hour", "day", "month", "weekday"]
    for p, l in zip(parts, labels):
        if p != "*": descs.append(f"{l}={p}")
    return "Every " + ", ".join(descs) if descs else "Every minute"

def test():
    c = CronExpr("*/5 * * * *")
    assert 0 in c.fields[0] and 5 in c.fields[0] and 3 not in c.fields[0]
    c2 = CronExpr("0 9 * * 1-5")
    dt = datetime(2026, 3, 30, 9, 0)  # Monday
    nxt = c2.next_run(datetime(2026, 3, 29, 10, 0))  # Saturday
    assert nxt is not None and nxt.weekday() < 5 and nxt.hour == 9
    assert describe("0 9 * * *") == "Every minute=0, hour=9"
    c3 = CronExpr("30 8,12 * * *")
    assert 8 in c3.fields[1] and 12 in c3.fields[1]
    print("  cron_parse: ALL TESTS PASSED")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test": test()
    else:
        expr = sys.argv[2] if len(sys.argv) > 2 else "*/5 * * * *"
        print(f"Next: {CronExpr(expr).next_run()}")

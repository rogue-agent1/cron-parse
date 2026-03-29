#!/usr/bin/env python3
"""Cron expression parser and next-run calculator."""
import sys, time
from datetime import datetime, timedelta

def parse_field(field, min_val, max_val):
    values = set()
    for part in field.split(","):
        if "/" in part:
            range_part, step = part.split("/"); step = int(step)
            if range_part == "*": start, end = min_val, max_val
            elif "-" in range_part:
                s, e = range_part.split("-"); start, end = int(s), int(e)
            else: start, end = int(range_part), max_val
            values.update(range(start, end + 1, step))
        elif "-" in part:
            s, e = part.split("-"); values.update(range(int(s), int(e) + 1))
        elif part == "*": values.update(range(min_val, max_val + 1))
        else: values.add(int(part))
    return sorted(values)

def parse_cron(expr):
    parts = expr.split()
    if len(parts) != 5: raise ValueError("Need 5 fields: min hour dom month dow")
    return {
        "minute": parse_field(parts[0], 0, 59),
        "hour": parse_field(parts[1], 0, 23),
        "dom": parse_field(parts[2], 1, 31),
        "month": parse_field(parts[3], 1, 12),
        "dow": parse_field(parts[4], 0, 6),
    }

def next_run(expr, after=None):
    cron = parse_cron(expr)
    dt = after or datetime.now()
    dt = dt.replace(second=0, microsecond=0) + timedelta(minutes=1)
    for _ in range(525600):  # max 1 year
        if (dt.minute in cron["minute"] and dt.hour in cron["hour"] and
            dt.day in cron["dom"] and dt.month in cron["month"] and
            dt.weekday() in [d % 7 for d in cron["dow"]]):
            return dt
        dt += timedelta(minutes=1)
    return None

def describe(expr):
    parts = expr.split()
    descs = []
    if parts[0] == "0" and parts[1] != "*": descs.append(f"at {parts[1]}:00")
    elif parts[0] == "*" and parts[1] == "*": descs.append("every minute")
    elif parts[0].startswith("*/"):
        descs.append(f"every {parts[0][2:]} minutes")
    return " ".join(descs) if descs else expr

def main():
    if len(sys.argv) < 2: print("Usage: cron_parse.py <demo|test>"); return
    if sys.argv[1] == "test":
        c = parse_cron("*/5 * * * *")
        assert c["minute"] == [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55]
        assert c["hour"] == list(range(24))
        c2 = parse_cron("0 9 * * 1-5")
        assert c2["minute"] == [0]; assert c2["hour"] == [9]
        assert c2["dow"] == [1, 2, 3, 4, 5]
        c3 = parse_cron("30 */2 * * *")
        assert c3["minute"] == [30]; assert c3["hour"] == [0,2,4,6,8,10,12,14,16,18,20,22]
        c4 = parse_cron("0 0 1,15 * *")
        assert c4["dom"] == [1, 15]
        after = datetime(2024, 1, 1, 0, 0, 0)
        nr = next_run("0 9 * * *", after)
        assert nr.hour == 9 and nr.minute == 0
        try: parse_cron("bad"); assert False
        except ValueError: pass
        print("All tests passed!")
    else:
        expr = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "*/15 * * * *"
        print(f"Parsed: {parse_cron(expr)}")
        print(f"Next: {next_run(expr)}")

if __name__ == "__main__": main()

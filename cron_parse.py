#!/usr/bin/env python3
"""Cron expression parser. Zero dependencies."""

class CronExpr:
    def __init__(self, expr):
        parts = expr.strip().split()
        if len(parts) != 5: raise ValueError(f"Need 5 fields, got {len(parts)}")
        self.minute = self._parse_field(parts[0], 0, 59)
        self.hour = self._parse_field(parts[1], 0, 23)
        self.dom = self._parse_field(parts[2], 1, 31)
        self.month = self._parse_field(parts[3], 1, 12)
        self.dow = self._parse_field(parts[4], 0, 6)

    def _parse_field(self, field, mn, mx):
        values = set()
        for part in field.split(","):
            if "/" in part:
                rng, step = part.split("/"); step = int(step)
                if rng == "*": start, end = mn, mx
                elif "-" in rng: start, end = [int(x) for x in rng.split("-")]
                else: start = int(rng); end = mx
                values.update(range(start, end+1, step))
            elif "-" in part:
                start, end = [int(x) for x in part.split("-")]
                values.update(range(start, end+1))
            elif part == "*":
                values.update(range(mn, mx+1))
            else:
                values.add(int(part))
        return values

    def matches(self, minute, hour, day, month, weekday):
        return (minute in self.minute and hour in self.hour and
                day in self.dom and month in self.month and weekday in self.dow)

    def describe(self):
        parts = []
        if self.minute == set(range(60)) and self.hour == set(range(24)):
            parts.append("Every minute")
        elif self.minute == {0} and self.hour == set(range(24)):
            parts.append("Every hour")
        elif len(self.minute) == 1 and len(self.hour) == 1:
            parts.append(f"At {list(self.hour)[0]:02d}:{list(self.minute)[0]:02d}")
        else:
            parts.append(f"Minutes: {sorted(self.minute)}")
            parts.append(f"Hours: {sorted(self.hour)}")
        return ", ".join(parts)

def parse_cron(expr): return CronExpr(expr)

if __name__ == "__main__":
    c = parse_cron("*/5 * * * *")
    print(c.describe())
    print(f"Matches 15:05? {c.matches(5, 15, 1, 1, 0)}")

from cron_parse import CronExpr, parse_cron
c = parse_cron("*/5 * * * *")
assert c.matches(0, 0, 1, 1, 0)
assert c.matches(5, 12, 15, 6, 3)
assert not c.matches(3, 0, 1, 1, 0)
c2 = parse_cron("0 9 * * 1-5")
assert c2.matches(0, 9, 1, 1, 1)  # Monday 9am
assert not c2.matches(0, 9, 1, 1, 0)  # Sunday
assert not c2.matches(30, 9, 1, 1, 1)  # 9:30
c3 = parse_cron("30 8 1 * *")
assert c3.matches(30, 8, 1, 3, 0)
assert "08:30" in c3.describe()
c4 = parse_cron("0,30 * * * *")
assert c4.matches(0, 5, 1, 1, 0) and c4.matches(30, 5, 1, 1, 0)
assert not c4.matches(15, 5, 1, 1, 0)
print("cron_parse tests passed")

# EW Bot — Daily Candle Rejection Confidence Booster

A specification for a new high-probability signal in the Elliott Wave bot. The
goal is to catch more valid trades and add confidence when a setup zone gets a
genuine rejection confirmed by a bearish daily candle.

This document is implementation-agnostic (pseudocode + rules) so it can be
dropped into whatever language/platform the bot runs on.

---

## 1. The idea in plain terms

When price trades **into** an EW setup zone and then gets **rejected** (it pumps
or dumps into the zone and reverses), and that rejection is confirmed by a
**bearish daily candle** (shooting star or bearish pin bar), the trade is a
**high-probability setup**. The bot should:

1. Flag the setup as high probability.
2. Boost its confidence score.
3. Send a Telegram notification.

The hard requirement: **price must have entered the zone first.** A bearish
daily candle on its own means nothing for this rule. The zone has to have been
touched before the candle counts as a rejection signal.

---

## 2. Definitions

| Term | Meaning |
|------|---------|
| **Setup zone** | The price band the bot has already defined for the EW setup (e.g. a fib resistance cluster, wave-4 / wave-B reaction area). Has a `zone_low` and `zone_high`. |
| **Zone entry** | A daily candle whose range overlaps the zone: `candle.high >= zone_low AND candle.low <= zone_high`. This must happen *before or on* the rejection candle. |
| **Rejection** | Price moved into the zone and reversed away from it within the daily candle, leaving a wick/tail pointing into the zone. |
| **Bearish daily candle** | A shooting star or bearish pin bar on the **daily** timeframe (see §4). Can close inside OR outside the zone — both count. |

---

## 3. Signal logic (pseudocode)

```python
def check_daily_rejection_signal(setup, daily_candles):
    """
    setup        : the active EW setup with zone_low, zone_high, confidence
    daily_candles: list of completed daily candles, oldest -> newest
    Returns an updated setup (flagged + boosted) and whether to notify.
    """
    zone_low, zone_high = setup.zone_low, setup.zone_high

    # --- Pre-condition: price must have ENTERED the zone at some point ---
    entered_zone = False
    entry_index  = None
    for i, c in enumerate(daily_candles):
        if c.high >= zone_low and c.low <= zone_high:
            entered_zone = True
            entry_index  = i
            break

    if not entered_zone:
        return setup, False   # zone never touched -> no signal, ever

    # --- Look at the most recent completed daily candle for a rejection ---
    last = daily_candles[-1]

    # The rejection candle must be at/after the first zone entry.
    if (len(daily_candles) - 1) < entry_index:
        return setup, False

    # Did this candle interact with the zone (pump/dump into it)?
    touched_zone = last.high >= zone_low and last.low <= zone_high

    # Allow a rejection that wicks into the zone even if the body closed back
    # outside it (in or outside the zone both count, per the rule).
    wicked_into_zone = last.high >= zone_low   # for a resistance/short zone

    if not (touched_zone or wicked_into_zone):
        return setup, False

    # --- Is the daily candle bearish (shooting star / bearish pin bar)? ---
    if not is_bearish_rejection_candle(last):
        return setup, False

    # --- All conditions met: high-probability setup ---
    setup.high_probability = True
    setup.confidence       = min(100, setup.confidence + CONFIDENCE_BOOST)
    setup.signal_reason    = "Daily candle rejection at zone"

    return setup, True   # True -> send Telegram notification
```

`CONFIDENCE_BOOST` is a tunable constant — suggested starting value **+20**
(clamped so confidence never exceeds 100). Tune to taste.

---

## 4. Detecting a bearish rejection candle (daily)

Both patterns share the same idea: a long upper wick showing price was pushed up
(into the zone) and rejected, with a small body near the low.

```python
def is_bearish_rejection_candle(c):
    body        = abs(c.close - c.open)
    full_range  = c.high - c.low
    if full_range == 0:
        return False

    upper_wick  = c.high - max(c.open, c.close)
    lower_wick  = min(c.open, c.close) - c.low

    # Shooting star / bearish pin bar criteria:
    #  - long upper wick (at least ~2x the body)
    #  - small body sitting in the lower third of the range
    #  - short lower wick
    long_upper_wick = upper_wick >= 2 * body
    small_body      = body <= 0.35 * full_range
    body_in_lower   = max(c.open, c.close) <= c.low + 0.5 * full_range
    short_lower     = lower_wick <= body  # not a hammer

    return long_upper_wick and small_body and body_in_lower and short_lower
```

Notes / tuning:
- Ratios (2x wick, 0.35 body, lower-third body) are the standard pin-bar/shooting-star
  thresholds. Loosen them if the bot is missing valid rejections; tighten them if
  it's firing on noise.
- For a **bullish** (long) setup zone — i.e. a support/wave reaction you'd buy —
  flip the logic: look for a **hammer / bullish pin bar** (long *lower* wick,
  body in upper third) and check `wicked_into_zone = last.low <= zone_high`.
  The current spec is written for a **bearish/short resistance zone**, matching
  the BTC short setups you've been posting.

---

## 5. Avoiding duplicate signals

Fire the notification **once per rejection candle**, not on every bot tick.

```python
if notify and setup.last_signal_candle_time != last.open_time:
    send_telegram_rejection_alert(setup, last)
    setup.last_signal_candle_time = last.open_time
```

Store `last_signal_candle_time` on the setup so a restart or repeated evaluation
of the same daily candle doesn't re-alert.

---

## 6. Telegram notification

Sent the moment a qualifying daily rejection is confirmed.

**Message format:**

```
⚠️ DAILY CANDLE REJECTION — {symbol}

A daily candle has rejected {into/out of} the zone.

Zone: {zone_low} – {zone_high}
Daily candle: {shooting star / bearish pin bar}
Close: {close}  ({inside / outside} the zone)

This setup is now flagged HIGH PROBABILITY.
Confidence: {old_score} → {new_score}
```

- `{into/out of}`: "into" if the candle closed inside the zone, "out of" if the
  wick rejected and the body closed back outside it.
- Send via the existing Telegram bot token + chat ID the EW bot already uses.

```python
def send_telegram_rejection_alert(setup, candle):
    inside = setup.zone_low <= candle.close <= setup.zone_high
    direction = "into" if inside else "out of"
    place     = "inside" if inside else "outside"
    text = (
        f"⚠️ DAILY CANDLE REJECTION — {setup.symbol}\n\n"
        f"A daily candle has rejected {direction} the zone.\n\n"
        f"Zone: {setup.zone_low} – {setup.zone_high}\n"
        f"Daily candle: {candle.pattern_name}\n"
        f"Close: {candle.close}  ({place} the zone)\n\n"
        f"This setup is now flagged HIGH PROBABILITY.\n"
        f"Confidence: {setup.confidence - CONFIDENCE_BOOST} -> {setup.confidence}"
    )
    telegram_send(text)
```

---

## 7. Where this hooks into the bot

1. **On each new completed daily candle** (not intrabar — wait for the daily
   close so the wick/body are final), run `check_daily_rejection_signal` for
   every active setup that has a defined zone.
2. If it returns `notify == True`, update the stored setup (flag + new
   confidence) and send the Telegram alert (respecting the dedupe in §5).
3. The boosted confidence score then feeds your existing trade-ranking/entry
   logic as normal.

**Key timing point:** evaluate on the **daily candle close**. A shooting star
isn't a shooting star until the day closes — checking mid-day will produce false
signals that vanish by the close.

---

## 8. Summary of the rule

> IF price has entered the setup zone at some point,
> AND the latest completed daily candle is a bearish shooting star / pin bar
> that wicked into the zone (closing inside OR outside it),
> THEN flag the setup high-probability, boost confidence (+20, capped at 100),
> and send a Telegram rejection alert.

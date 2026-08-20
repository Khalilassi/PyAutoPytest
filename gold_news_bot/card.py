"""The PNG card.

Text on the image is English and numbers only: matplotlib does not shape or
reorder Arabic, so Arabic here would render as disconnected, backwards letters.
The Arabic goes in the Telegram caption instead, where it renders properly.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Sequence

import matplotlib

matplotlib.use("Agg")  # no display on a CI runner

import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402

import indicators  # noqa: E402
from analysis import Snapshot, Ticket  # noqa: E402
from indicators import Candle  # noqa: E402
from localtime import format_datetime, to_local  # noqa: E402

BG = "#11151c"
FG = "#e8eaed"
MUTED = "#96a0b5"
GRID = "#222836"
UP = "#26a071"
DOWN = "#d1495b"
ACCENT = "#e0b341"

SIDE_COLORS = {"BUY": UP, "SELL": DOWN, "WAIT": MUTED}


def render_card(
    candles: Sequence[Candle],
    snapshot: Snapshot,
    ticket: Ticket | None,
    out_path: Path,
    rules: dict,
    age_minutes_value: int,
) -> Path:
    """Draw one instrument card and save it as a PNG."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    window = list(candles[-120:])

    figure = plt.figure(figsize=(9, 5), dpi=140, facecolor=BG)
    grid = figure.add_gridspec(1, 2, width_ratios=[2.1, 1], wspace=0.22)
    chart = figure.add_subplot(grid[0, 0], facecolor=BG)
    panel = figure.add_subplot(grid[0, 1], facecolor=BG)

    _draw_chart(chart, list(candles), len(window), snapshot, ticket, rules)
    _draw_panel(panel, snapshot, ticket, age_minutes_value)

    figure.suptitle(
        f"{snapshot.name}   {snapshot.price(snapshot.last)}   "
        f"({snapshot.change_pct:+.2f}%)",
        color=FG,
        fontsize=15,
        fontweight="bold",
        x=0.06,
        y=0.965,
        ha="left",
    )
    figure.savefig(out_path, facecolor=BG, bbox_inches="tight", pad_inches=0.25)
    plt.close(figure)
    return out_path


def _draw_chart(axis, candles: list[Candle], visible: int, snapshot: Snapshot, ticket: Ticket | None, rules: dict) -> None:
    # EMAs are computed over the full history, then cropped to the visible window —
    # otherwise a 200-period EMA never appears on a 120-candle chart.
    times = [to_local(c.when) for c in candles[-visible:]]

    axis.plot(times, [c.close for c in candles[-visible:]], color=FG, linewidth=1.6, zorder=3)

    all_closes = [c.close for c in candles]
    for period, color in ((rules.get("fast_ema", 50), ACCENT), (rules.get("slow_ema", 200), "#5c7cfa")):
        series = indicators.ema_series(all_closes, period)[-visible:]
        points = [(t, v) for t, v in zip(times, series) if v is not None]
        if points:
            axis.plot(
                [p[0] for p in points],
                [p[1] for p in points],
                color=color,
                linewidth=1.1,
                alpha=0.9,
                label=f"EMA{period}",
                zorder=2,
            )

    if ticket:
        for level, color, label in (
            (ticket.entry, FG, "entry"),
            (ticket.stop, DOWN, "SL"),
            (ticket.target, UP, "TP"),
        ):
            axis.axhline(level, color=color, linewidth=0.9, linestyle="--", alpha=0.75, zorder=1)
            axis.annotate(
                f"{label} {snapshot.price(level)}",
                xy=(1.0, level),
                xycoords=("axes fraction", "data"),
                xytext=(-4, 3),
                textcoords="offset points",
                color=color,
                fontsize=7.5,
                ha="right",
                bbox=dict(facecolor=BG, edgecolor="none", alpha=0.85, pad=1.4),
            )

    axis.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    axis.tick_params(colors=MUTED, labelsize=8)
    axis.grid(color=GRID, linewidth=0.6)
    for spine in axis.spines.values():
        spine.set_color(GRID)
    legend = axis.legend(loc="upper left", fontsize=7.5, frameon=False)
    for text in legend.get_texts():
        text.set_color(MUTED)


def _draw_panel(axis, snapshot: Snapshot, ticket: Ticket | None, age_minutes_value: int) -> None:
    axis.axis("off")

    side = ticket.side if ticket else "WAIT"
    axis.text(0, 1.0, side, color=SIDE_COLORS[side], fontsize=22, fontweight="bold", va="top")
    axis.text(
        0,
        0.9,
        f"trend {snapshot.trend}",
        color=MUTED,
        fontsize=9,
        va="top",
    )

    rows = [
        ("RSI", f"{snapshot.rsi:.1f}" if snapshot.rsi is not None else "—"),
        ("EMA fast", snapshot.price(snapshot.ema_fast)),
        ("EMA slow", snapshot.price(snapshot.ema_slow)),
        ("MACD hist", f"{snapshot.macd_hist:+.4f}" if snapshot.macd_hist is not None else "—"),
        ("ATR", snapshot.price(snapshot.atr)),
        ("swing high", snapshot.price(snapshot.swing_high)),
        ("swing low", snapshot.price(snapshot.swing_low)),
    ]
    if ticket:
        rows += [
            ("", ""),
            ("entry", snapshot.price(ticket.entry)),
            ("stop", snapshot.price(ticket.stop)),
            ("target", snapshot.price(ticket.target)),
            ("lot", f"{ticket.lot:g}"),
            ("risk", f"${ticket.risk_amount:g}"),
        ]

    y = 0.79
    for label, value in rows:
        if label:
            axis.text(0, y, label, color=MUTED, fontsize=8.5, va="top")
            axis.text(1, y, value, color=FG, fontsize=8.5, va="top", ha="right")
        y -= 0.062

    axis.text(
        0,
        max(y - 0.02, -0.08),
        f"candle {format_datetime(snapshot.candle_time)} Riyadh\n"
        f"age {age_minutes_value} min",
        color=MUTED,
        fontsize=7.5,
        va="top",
    )

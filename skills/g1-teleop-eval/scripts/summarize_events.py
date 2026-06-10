#!/usr/bin/env python3
"""Summarize a timestamped teleoperation JSONL event log."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Run directory or samples.jsonl path")
    parser.add_argument("--output", help="Markdown report path. Defaults to stdout.")
    parser.add_argument("--teleop-fsm", type=int, default=505)
    return parser.parse_args()


def resolve_samples(path: Path) -> Path:
    if path.is_dir():
        return path / "samples.jsonl"
    return path


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return rows


def ns_to_s(ns: int | float | None) -> float | None:
    if ns is None:
        return None
    return float(ns) / 1e9


def duration_s(rows: list[dict]) -> float:
    values = [r.get("mono_ns") for r in rows if r.get("mono_ns") is not None]
    if len(values) < 2:
        return 0.0
    return (max(values) - min(values)) / 1e9


def rate(rows: list[dict], total_s: float) -> float:
    return len(rows) / total_s if total_s > 0 else 0.0


def intervals(rows: list[dict], key: str = "mono_ns") -> list[float]:
    values = sorted(r[key] for r in rows if r.get(key) is not None)
    return [(b - a) / 1e9 for a, b in zip(values, values[1:]) if b >= a]


def percentile(values: list[float], p: float) -> float | None:
    values = sorted(v for v in values if math.isfinite(v))
    if not values:
        return None
    idx = (len(values) - 1) * p / 100.0
    lo = math.floor(idx)
    hi = math.ceil(idx)
    if lo == hi:
        return values[int(idx)]
    return values[lo] * (hi - idx) + values[hi] * (idx - lo)


def fmt_seconds(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:.4f}s"


def teleop_segments(rows: list[dict], teleop_fsm: int) -> list[tuple[int, int]]:
    switches = [
        r for r in rows
        if r.get("event") == "fsm_switch" and r.get("mono_ns") is not None
    ]
    switches.sort(key=lambda r: r["mono_ns"])
    segments: list[tuple[int, int]] = []
    start: int | None = None
    for row in switches:
        old_fsm = row.get("old_fsm")
        new_fsm = row.get("new_fsm")
        if old_fsm != teleop_fsm and new_fsm == teleop_fsm:
            start = int(row["mono_ns"])
        elif start is not None and old_fsm == teleop_fsm and new_fsm != teleop_fsm:
            segments.append((start, int(row["mono_ns"])))
            start = None
    return segments


def make_report(path: Path, rows: list[dict], teleop_fsm: int) -> str:
    total_s = duration_s(rows)
    counts = Counter(r.get("event", "unknown") for r in rows)
    lines: list[str] = []
    lines.append("# Teleop Event Summary")
    lines.append("")
    lines.append(f"- Source: `{path}`")
    lines.append(f"- Events: `{len(rows)}`")
    lines.append(f"- Duration: `{total_s:.3f}s`")
    lines.append("")
    lines.append("## Event Counts")
    lines.append("")
    for event, count in counts.most_common():
        lines.append(f"- `{event}`: `{count}`")

    key_events = [
        "pico_tracking",
        "pico_body_valid",
        "pose_sample",
        "dds_publish",
        "robot_lowstate",
        "buttons",
    ]
    lines.append("")
    lines.append("## Rates")
    lines.append("")
    for event in key_events:
        event_rows = [r for r in rows if r.get("event") == event]
        if event_rows:
            ints = intervals(event_rows)
            lines.append(
                f"- `{event}`: `{rate(event_rows, total_s):.2f} Hz`, "
                f"interval p95={fmt_seconds(percentile(ints, 95))}, "
                f"max={fmt_seconds(max(ints) if ints else None)}"
            )

    lines.append("")
    lines.append("## Teleop Segments")
    lines.append("")
    segments = teleop_segments(rows, teleop_fsm)
    if not segments:
        lines.append("- No complete teleop FSM segment found.")
    for idx, (start, end) in enumerate(segments, start=1):
        seg_rows = [r for r in rows if r.get("mono_ns") is not None and start <= r["mono_ns"] <= end]
        seg_s = (end - start) / 1e9
        lines.append(f"### Segment {idx}")
        lines.append(f"- Duration: `{seg_s:.3f}s`")
        for event in key_events:
            event_rows = [r for r in seg_rows if r.get("event") == event]
            if event_rows:
                lines.append(f"- `{event}` rate: `{rate(event_rows, seg_s):.2f} Hz`")
        spike_count = sum(1 for r in seg_rows if r.get("event") == "command_spike")
        outlier_count = sum(1 for r in seg_rows if r.get("event") == "pose_outlier_suppressed")
        lines.append(f"- `command_spike`: `{spike_count}`")
        lines.append(f"- `pose_outlier_suppressed`: `{outlier_count}`")
        lines.append("")

    lines.append("## Interpretation Notes")
    lines.append("")
    lines.append("- High publish rate does not prove robot execution quality without robot feedback.")
    lines.append("- Whole-run averages can hide mode-specific problems; inspect teleop segments.")
    lines.append("- Spike, outlier, pause/resume, and mode-transition windows should be reviewed before training use.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    path = resolve_samples(Path(args.input))
    rows = load_jsonl(path)
    report = make_report(path, rows, args.teleop_fsm)
    if args.output:
        Path(args.output).write_text(report, encoding="utf-8")
    else:
        print(report, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

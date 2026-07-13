#!/usr/bin/env python3
"""Generic JSONL analyzer for layered robot teleoperation lag experiments."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from collections import Counter
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", help="Directory containing samples.jsonl")
    parser.add_argument("--config", required=True, help="Analyzer mapping JSON")
    parser.add_argument("--output", default=None, help="Default: RUN_DIR/generic_lag_report.md")
    parser.add_argument("--segment", type=int, default=None, help="1-based complete active-mode segment")
    return parser.parse_args()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_jsonl(path: Path):
    rows = []
    malformed = 0
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            malformed += 1
    return rows, malformed


def event_names(value):
    if value is None:
        return set()
    if isinstance(value, str):
        return {value}
    return {str(v) for v in value}


def finite(values):
    out = []
    for value in values:
        if value is None:
            continue
        number = float(value)
        if math.isfinite(number):
            out.append(number)
    return out


def percentile(values, fraction):
    xs = sorted(finite(values))
    if not xs:
        return None
    index = (len(xs) - 1) * fraction
    lo = math.floor(index)
    hi = math.ceil(index)
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - index) + xs[hi] * (index - lo)


def stat(values):
    xs = finite(values)
    if not xs:
        return None
    return {
        "n": len(xs),
        "mean": statistics.fmean(xs),
        "p50": percentile(xs, 0.50),
        "p95": percentile(xs, 0.95),
        "p99": percentile(xs, 0.99),
        "max": max(xs),
    }


def fmt(value, unit="ms"):
    if value is None:
        return "n/a"
    return (
        f"n={value['n']}, mean={value['mean']:.3f}{unit}, "
        f"p50={value['p50']:.3f}{unit}, p95={value['p95']:.3f}{unit}, "
        f"p99={value['p99']:.3f}{unit}, max={value['max']:.3f}{unit}"
    )


def row_time(row, time_field):
    value = row.get(time_field, row.get("mono_ns"))
    return int(value) if value is not None else None


def ordered(rows, time_field):
    return sorted((r for r in rows if row_time(r, time_field) is not None), key=lambda r: row_time(r, time_field))


def intervals_ms(rows, time_field):
    rows = ordered(rows, time_field)
    return [
        (row_time(b, time_field) - row_time(a, time_field)) / 1e6
        for a, b in zip(rows, rows[1:])
        if row_time(b, time_field) >= row_time(a, time_field)
    ]


def complete_segments(rows, config):
    events = config["events"]
    fields = config["fields"]
    switch_name = events.get("mode_switch")
    active_mode = config.get("active_mode")
    time_field = fields["event_time_ns"]
    if not switch_name or active_mode is None:
        return []
    switches = ordered([r for r in rows if r.get("event") == switch_name], time_field)
    segments = []
    start = None
    for row in switches:
        old_mode = row.get(fields["old_mode"])
        new_mode = row.get(fields["new_mode"])
        if new_mode == active_mode and old_mode != active_mode:
            start = row
        elif start is not None and old_mode == active_mode and new_mode != active_mode:
            segments.append((row_time(start, time_field), row_time(row, time_field)))
            start = None
    return segments


def main():
    args = parse_args()
    run_dir = Path(args.run_dir)
    config = load_json(Path(args.config))
    rows, malformed = load_jsonl(run_dir / "samples.jsonl")
    events = config["events"]
    fields = config["fields"]
    time_field = fields["event_time_ns"]

    segments = complete_segments(rows, config)
    selected_name = "full_run"
    if segments:
        segment_index = args.segment or 1
        if segment_index < 1 or segment_index > len(segments):
            raise SystemExit(f"--segment must be between 1 and {len(segments)}")
        start_ns, end_ns = segments[segment_index - 1]
        selected = [r for r in rows if row_time(r, time_field) is not None and start_ns <= row_time(r, time_field) <= end_ns]
        selected_name = f"active_segment_{segment_index}"
    else:
        selected = rows
        times = [row_time(r, time_field) for r in rows if row_time(r, time_field) is not None]
        start_ns = min(times) if times else 0
        end_ns = max(times) if times else 0

    duration_s = (end_ns - start_ns) / 1e9 if end_ns > start_ns else 0.0
    input_rows = [r for r in selected if r.get("event") in event_names(events.get("input"))]
    output_rows = [r for r in selected if r.get("event") in event_names(events.get("output"))]
    publish_rows = [r for r in selected if r.get("event") in event_names(events.get("publish"))]
    lag_rows = [r for r in selected if r.get("event") in event_names(events.get("lag"))]
    marker_rows = [r for r in selected if r.get("event") in event_names(events.get("marker"))]
    pause_rows = [r for r in selected if r.get("event") in event_names(events.get("pause"))]

    frame_field = fields.get("frame_id")
    frame_ids = [int(r[frame_field]) for r in ordered(publish_rows, time_field) if frame_field and r.get(frame_field) is not None]
    frame_gaps = [b - a for a, b in zip(frame_ids, frame_ids[1:])]
    frame_gap_counts = Counter(frame_gaps)

    def duration_stat(field):
        if not field:
            return None
        return stat([r.get(field) / 1e6 for r in output_rows if r.get(field) is not None])

    recorder_dropped = 0
    summary_names = event_names(events.get("recorder_summary"))
    dropped_field = fields.get("recorder_dropped")
    if dropped_field:
        recorder_dropped = sum(int(r.get(dropped_field, 0)) for r in rows if r.get("event") in summary_names)

    cycle_budget = float(config.get("cycle_budget_ms", 0.0))
    processing = duration_stat(fields.get("processing_ns"))
    conclusions = []
    if not lag_rows:
        conclusions.append("No configured lag/backlog event occurred in the selected interval.")
    if not marker_rows:
        conclusions.append("No operator-perceived lag marker occurred in the selected interval.")
    if frame_gaps and set(frame_gaps) == {1}:
        conclusions.append("Publish frame identifiers were continuous with no observed sequence loss.")
    if processing and cycle_budget > 0 and processing["p99"] < cycle_budget:
        conclusions.append("Processing p99 remained below the configured cycle budget.")
    if pause_rows:
        conclusions.append("Pause/resume events are present; analyze continuous intervals separately from pause boundaries.")
    if not conclusions:
        conclusions.append("Evidence is mixed; inspect raw lag, marker, rate, and frame-gap events together.")

    lines = [
        "# Generic Robot Teleoperation Lag Report",
        "",
        "## Scope",
        "",
        f"- selection: `{selected_name}`",
        f"- duration: {duration_s:.3f} s",
        f"- complete active-mode segments found: {len(segments)}",
        f"- malformed JSONL lines skipped: {malformed}",
        f"- recorder events dropped: {recorder_dropped}",
        "",
        "## Event counts",
        "",
        f"- input: {len(input_rows)}",
        f"- output: {len(output_rows)}",
        f"- publish: {len(publish_rows)}",
        f"- lag/backlog: {len(lag_rows)}",
        f"- operator markers: {len(marker_rows)}",
        f"- pause/resume: {len(pause_rows)}",
        "",
        "## Rates and intervals",
        "",
        f"- input rate: {len(input_rows) / duration_s:.3f} Hz" if duration_s else "- input rate: n/a",
        f"- output rate: {len(output_rows) / duration_s:.3f} Hz" if duration_s else "- output rate: n/a",
        f"- publish rate: {len(publish_rows) / duration_s:.3f} Hz" if duration_s else "- publish rate: n/a",
        f"- input interval: {fmt(stat(intervals_ms(input_rows, time_field)))}",
        f"- output interval: {fmt(stat(intervals_ms(output_rows, time_field)))}",
        f"- publish interval: {fmt(stat(intervals_ms(publish_rows, time_field)))}",
        "",
        "## Processing",
        "",
        f"- processing: {fmt(processing)}",
        f"- compute: {fmt(duration_stat(fields.get('compute_ns')))}",
        f"- conversion: {fmt(duration_stat(fields.get('conversion_ns')))}",
        f"- configured cycle budget: {cycle_budget:.3f} ms",
        "",
        "## Publish continuity",
        "",
        f"- first frame id: {frame_ids[0] if frame_ids else 'n/a'}",
        f"- last frame id: {frame_ids[-1] if frame_ids else 'n/a'}",
        f"- frame-gap counts: `{dict(frame_gap_counts)}`",
        "",
        "## Interpretation",
        "",
    ]
    lines.extend(f"- {item}" for item in conclusions)
    lines += [
        "",
        "## Evidence boundary",
        "",
        "- This report classifies the configured events only.",
        "- Absence of internal backlog does not prove zero command-to-motion latency.",
        "- Absolute end-to-end latency requires synchronized robot feedback or external observation.",
        "",
    ]

    output = Path(args.output) if args.output else run_dir / "generic_lag_report.md"
    output.write_text("\n".join(lines), encoding="utf-8")
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

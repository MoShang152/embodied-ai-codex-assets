#!/usr/bin/env python3
"""Classify teleoperation JSONL event logs into bad windows and segment grades."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Run directory or samples.jsonl path")
    parser.add_argument("--output-dir", help="Output directory. Defaults to <run_dir>/qc_outputs")
    parser.add_argument("--teleop-fsm", type=int, default=505)
    parser.add_argument("--gap-threshold-s", type=float, default=0.08)
    parser.add_argument("--gap-window-s", type=float, default=0.5)
    parser.add_argument("--spike-window-s", type=float, default=1.0)
    parser.add_argument("--outlier-window-s", type=float, default=0.5)
    parser.add_argument("--fsm-window-s", type=float, default=2.0)
    parser.add_argument("--resume-window-s", type=float, default=1.0)
    return parser.parse_args()


def resolve_samples(path: Path) -> Path:
    if path.is_dir():
        return path / "samples.jsonl"
    return path


def default_output_dir(input_path: Path, samples_path: Path) -> Path:
    if input_path.is_dir():
        return input_path / "qc_outputs"
    return samples_path.parent / "qc_outputs"


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


def ns_to_s(ns: int | float) -> float:
    return float(ns) / 1e9


def add_window(windows: list[dict], center_ns: int, before_s: float, after_s: float, reason: str) -> None:
    windows.append({
        "start_s": max(0.0, ns_to_s(center_ns) - before_s),
        "end_s": ns_to_s(center_ns) + after_s,
        "reason": reason,
    })


def merge_windows(windows: list[dict]) -> list[dict]:
    if not windows:
        return []
    windows = sorted(windows, key=lambda w: (w["start_s"], w["end_s"]))
    merged = [dict(windows[0])]
    for window in windows[1:]:
        last = merged[-1]
        if window["start_s"] <= last["end_s"]:
            last["end_s"] = max(last["end_s"], window["end_s"])
            reasons = set(last["reason"].split("; "))
            reasons.add(window["reason"])
            last["reason"] = "; ".join(sorted(reasons))
        else:
            merged.append(dict(window))
    return merged


def teleop_segments(rows: list[dict], teleop_fsm: int) -> list[dict]:
    switches = [
        r for r in rows
        if r.get("event") == "fsm_switch" and r.get("mono_ns") is not None
    ]
    switches.sort(key=lambda r: r["mono_ns"])
    segments: list[dict] = []
    start: dict | None = None
    for row in switches:
        if row.get("old_fsm") != teleop_fsm and row.get("new_fsm") == teleop_fsm:
            start = row
        elif start is not None and row.get("old_fsm") == teleop_fsm and row.get("new_fsm") != teleop_fsm:
            segments.append({
                "index": len(segments) + 1,
                "start_ns": int(start["mono_ns"]),
                "end_ns": int(row["mono_ns"]),
            })
            start = None
    if not segments:
        timed = [r["mono_ns"] for r in rows if r.get("mono_ns") is not None]
        if timed:
            segments.append({"index": 1, "start_ns": min(timed), "end_ns": max(timed)})
    return segments


def rows_in(rows: list[dict], start_ns: int, end_ns: int) -> list[dict]:
    return [
        r for r in rows
        if r.get("mono_ns") is not None and start_ns <= r["mono_ns"] <= end_ns
    ]


def grade_segment(seg_rows: list[dict], long_gaps: int) -> tuple[str, str]:
    counts = Counter(r.get("event", "unknown") for r in seg_rows)
    spikes = counts.get("command_spike", 0)
    outliers = counts.get("pose_outlier_suppressed", 0)
    invalid = counts.get("pico_body_invalid", 0)
    emergency = counts.get("emergency_stop", 0)
    manual = counts.get("manual_intervention", 0)
    coordinate = counts.get("coordinate_error", 0) + counts.get("wrong_frame", 0)

    if emergency or coordinate:
        return "F", "dangerous or semantically wrong event present"
    if spikes >= 3 or long_gaps >= 10 or invalid >= 20:
        return "D", "severe repeated timing/input/command issue"
    if spikes or outliers >= 3 or manual:
        return "C", "abnormal event requires human review"
    if outliers or long_gaps or invalid:
        return "B", "minor issue, clip or label before training"
    return "A", "clean candidate if task result and robot feedback are acceptable"


def build_bad_windows(rows: list[dict], args: argparse.Namespace) -> list[dict]:
    windows: list[dict] = []
    pose_rows = sorted(
        [r for r in rows if r.get("event") == "pose_sample" and r.get("mono_ns") is not None],
        key=lambda r: r["mono_ns"],
    )
    for prev, cur in zip(pose_rows, pose_rows[1:]):
        gap_s = (cur["mono_ns"] - prev["mono_ns"]) / 1e9
        if gap_s > args.gap_threshold_s:
            center = int((prev["mono_ns"] + cur["mono_ns"]) / 2)
            add_window(windows, center, args.gap_window_s, args.gap_window_s, f"pose_gap>{args.gap_threshold_s:.3f}s")

    for row in rows:
        event = row.get("event")
        mono_ns = row.get("mono_ns")
        if mono_ns is None:
            continue
        mono_ns = int(mono_ns)
        if event == "command_spike":
            add_window(windows, mono_ns, args.spike_window_s, args.spike_window_s, "command_spike")
        elif event == "pose_outlier_suppressed":
            add_window(windows, mono_ns, args.outlier_window_s, args.outlier_window_s, "pose_outlier_suppressed")
        elif event == "fsm_switch":
            add_window(windows, mono_ns, args.fsm_window_s, args.fsm_window_s, "fsm_switch")
        elif event == "stream_pause":
            add_window(windows, mono_ns, 0.2, args.resume_window_s, "stream_pause")
        elif event == "stream_resume":
            add_window(windows, mono_ns, 0.2, args.resume_window_s, "stream_resume")
        elif event in {"emergency_stop", "manual_intervention", "support_frame_intervention"}:
            add_window(windows, mono_ns, 2.0, 2.0, event)
    return merge_windows(windows)


def make_report(samples: Path, rows: list[dict], segments: list[dict], qualities: list[dict], bad_windows: list[dict]) -> str:
    counts = Counter(r.get("event", "unknown") for r in rows)
    lines: list[str] = []
    lines.append("# Teleop Data QC Report")
    lines.append("")
    lines.append(f"- Source: `{samples}`")
    lines.append(f"- Events: `{len(rows)}`")
    lines.append(f"- Segments: `{len(segments)}`")
    lines.append(f"- Bad windows: `{len(bad_windows)}`")
    lines.append("")
    lines.append("## Event Counts")
    lines.append("")
    for event, count in counts.most_common():
        lines.append(f"- `{event}`: `{count}`")
    lines.append("")
    lines.append("## Segment Grades")
    lines.append("")
    lines.append("| Segment | Grade | Duration s | Reason |")
    lines.append("|---:|---|---:|---|")
    for item in qualities:
        lines.append(
            f"| {item['segment']} | {item['grade']} | {item['duration_s']:.3f} | {item['reason']} |"
        )
    lines.append("")
    lines.append("## Bad Windows")
    lines.append("")
    if not bad_windows:
        lines.append("- None detected by the configured rules.")
    else:
        lines.append("| Start s | End s | Reason |")
        lines.append("|---:|---:|---|")
        for window in bad_windows:
            lines.append(f"| {window['start_s']:.3f} | {window['end_s']:.3f} | {window['reason']} |")
    lines.append("")
    lines.append("## Training Use")
    lines.append("")
    lines.append("- A: use as main training candidate if task labels and robot feedback are sufficient.")
    lines.append("- B: clip or label bad windows before use.")
    lines.append("- C: hold for human review.")
    lines.append("- D: use only for failure analysis.")
    lines.append("- F: forbidden for training.")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    samples = resolve_samples(input_path)
    output_dir = Path(args.output_dir) if args.output_dir else default_output_dir(input_path, samples)
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = load_jsonl(samples)
    segments = teleop_segments(rows, args.teleop_fsm)
    bad_windows = build_bad_windows(rows, args)

    qualities: list[dict] = []
    for segment in segments:
        seg_rows = rows_in(rows, segment["start_ns"], segment["end_ns"])
        pose_rows = sorted(
            [r for r in seg_rows if r.get("event") == "pose_sample" and r.get("mono_ns") is not None],
            key=lambda r: r["mono_ns"],
        )
        long_gaps = 0
        for prev, cur in zip(pose_rows, pose_rows[1:]):
            if (cur["mono_ns"] - prev["mono_ns"]) / 1e9 > args.gap_threshold_s:
                long_gaps += 1
        grade, reason = grade_segment(seg_rows, long_gaps)
        qualities.append({
            "segment": segment["index"],
            "start_s": ns_to_s(segment["start_ns"]),
            "end_s": ns_to_s(segment["end_ns"]),
            "duration_s": (segment["end_ns"] - segment["start_ns"]) / 1e9,
            "grade": grade,
            "reason": reason,
        })

    (output_dir / "bad_windows.json").write_text(json.dumps(bad_windows, indent=2), encoding="utf-8")
    with (output_dir / "segment_quality.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["segment", "start_s", "end_s", "duration_s", "grade", "reason"])
        writer.writeheader()
        writer.writerows(qualities)
    report = make_report(samples, rows, segments, qualities, bad_windows)
    (output_dir / "data_qc_report.md").write_text(report, encoding="utf-8")
    print(f"Wrote {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

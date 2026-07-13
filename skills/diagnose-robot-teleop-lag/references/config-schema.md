# Generic analyzer configuration

Copy `config.example.json` and map the current project's event and field names.

## Top-level keys

```json
{
  "events": {},
  "fields": {},
  "active_mode": 505,
  "cycle_budget_ms": 20.0
}
```

## Event mapping

- `input`: raw or accepted input sample event.
- `output`: converted pose, policy output, or scheduled command event.
- `publish`: middleware publish event.
- `lag`: list of backlog/resync/drop event names.
- `marker`: operator-perceived lag marker.
- `pause`: list of pause/resume event names.
- `mode_switch`: mode or FSM transition event.
- `recorder_summary`: event containing recorder drop count.

Unused event names may be `null` or an empty list.

## Field mapping

- `event_time_ns`: monotonic event timestamp.
- `source_time_ns`: device/source timestamp.
- `frame_id`: publish sequence identifier.
- `processing_ns`, `compute_ns`, `conversion_ns`: optional duration fields.
- `old_mode`, `new_mode`: mode-switch fields.
- `recorder_dropped`: recorder drop field.

## Segment selection

If `active_mode` and mode-switch events are available, analyze complete enter/exit segments. Otherwise analyze the full file and state that mode isolation was unavailable.

## Units

Event and duration fields are nanoseconds. Convert source timestamps before using this script if the project stores another unit.

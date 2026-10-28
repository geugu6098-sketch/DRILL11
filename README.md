# LEC12 Character Controller

A Pico2D character-controller exercise with IDLE, SLEEP, RUN, and AUTORUN
states.

## Controls

- Left/Right: run in the selected direction; release both keys to stop.
- Space: wake up from SLEEP.
- A: start AUTORUN while IDLE. AUTORUN moves faster, appears larger, and
  reverses direction at either screen edge. Pressing a direction key cancels
  AUTORUN and continues in that direction with RUN.
- Escape: quit.

## State diagram

```mermaid
stateDiagram-v2
    [*] --> IDLE
    IDLE --> SLEEP: 5 seconds
    SLEEP --> IDLE: Space
    IDLE --> RUN: Direction key
    SLEEP --> RUN: Direction key
    RUN --> IDLE: All direction keys released
    IDLE --> AUTORUN: A
    AUTORUN --> AUTORUN: Screen edge / reverse direction
    AUTORUN --> RUN: Direction key / cancel
```

## Tests

Run the controller tests with:

```powershell
python -m unittest discover -s tests
```

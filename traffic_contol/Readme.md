# Traffic Light Controller Using Verilog HDL

## Overview

This project implements a digital traffic light controller using **Verilog HDL**. The controller uses a Finite State Machine (FSM) and a counter to sequence four sets of traffic-light outputs through six states.

The project demonstrates fundamental digital design concepts, including sequential logic, state transitions, counter-based timing, output decoding, asynchronous reset, and testbench-based simulation.

## Features

- **Six-state FSM:** Implements six traffic-control states (S1–S6) in a repeating sequence.
- **Counter-based timing:** Controls the duration of each state using a 4-bit counter.
- **Four output groups:** Controls the signals for M1, M2, MT, and S.
- **Asynchronous reset:** Resets the FSM to its initial state when reset is asserted.
- **Simulation testbench:** Generates a clock, applies reset, and runs the design for a specified simulation duration.

## Architecture

The design consists of two primary modules:

| Module | Description |
|---|---|
| `Traffic_Light_Controller.v` | Implements the FSM, counter, and traffic-light output logic. |
| `Traffic_Light_Controller_TB.v` | Provides clock and reset inputs for simulation and connects the design under test (DUT). |

### Block Diagram

```text
             +----------------------+
 clk ------->|                      |
 rst ------->|  Traffic Light       |
             |  Controller          |
             |                      |
             |  +----------------+  |
             |  | Finite State   |  |
             |  | Machine (FSM)  |  |
             |  +-------+--------+  |
             |          ^           |
             |  +-------+--------+  |
             |  | Timing Counter |  |
             |  +----------------+  |
             +----------+-----------+
                        |
             +----------+-----------+
             |          |           |
          light_M1   light_M2   light_MT
                        |
                     light_S
```

## State Machine

The controller cycles through six states in the following order:

```text
       +----+
       | S1 |
       +--+-+
          |
          v
       +----+
       | S2 |
       +--+-+
          |
          v
       +----+
       | S3 |
       +--+-+
          |
          v
       +----+
       | S4 |
       +--+-+
          |
          v
       +----+
       | S5 |
       +--+-+
          |
          v
       +----+
       | S6 |
       +--+-+
          |
          +-----------> S1
```

### State Duration Parameters

| State | Counter Limit | Next State |
|---|---:|---|
| S1 | 7 | S2 |
| S2 | 2 | S3 |
| S3 | 5 | S4 |
| S4 | 2 | S5 |
| S5 | 3 | S6 |
| S6 | 2 | S1 |

**Note:** Each state starts with the counter at zero and transitions when `count` reaches its configured limit. Consequently, a state with a limit of `N` occupies `N + 1` clock cycles. The parameters represent clock cycles, not inherently real-world seconds.

## Output Encoding

Each traffic-light output is a 3-bit signal.

| Output Code | Meaning |
|---|---|
| `3'b001` | Green |
| `3'b010` | Yellow |
| `3'b100` | Red |
| `3'b000` | All lights off (default output state) |

### State-to-Output Mapping

| State | M1 | M2 | MT | S |
|---|---|---|---|---|
| S1 | Green | Green | Red | Red |
| S2 | Green | Yellow | Red | Red |
| S3 | Green | Red | Green | Red |
| S4 | Yellow | Red | Yellow | Red |
| S5 | Red | Red | Red | Green |
| S6 | Red | Red | Red | Yellow |

*The output mappings above reflect the current RTL implementation. They are not a validated real-world traffic-safety sequence.*

## Technologies and Tools

- **Hardware Description Language:** Verilog HDL
- **Simulation:** Vivado Simulator or Icarus Verilog
- **Waveform Analysis:** Vivado Waveform Viewer or GTKWave
- **Design Concepts:** FSMs, counters, sequential logic, combinational logic, asynchronous reset



## Reset and Timing Behavior

The controller uses a rising-edge-triggered clock and an active-high asynchronous reset.

- When reset is asserted, the FSM returns to S1 and the counter resets to zero.
- When reset is deasserted, the controller advances through the states on subsequent rising clock edges.
- The testbench uses a `1 ns` time unit and a `1 ps` time precision.
- The clock period in the supplied testbench is 1 second of simulation time.

The simulated clock period is a testbench setting. Actual hardware timing depends on the target clock source and the timing constraints used during implementation.

## Future Improvements

- Synthesize the RTL and analyze area, timing, and logic utilization.
- Explore FPGA implementation and physical LED-based demonstration.


## Disclaimer

This is an educational digital-design project. The output sequence has not been validated for deployment at a real traffic intersection. A production controller would require a verified intersection-specific signal plan, conflict prevention, fail-safe behavior, and appropriate safety validation.

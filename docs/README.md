# Documentation

| Page | Contents |
|------|----------|
| [scout-cli.md](scout-cli.md) | The `scout` helper command — build, sim, demo, base, and arm from one CLI |
| [architecture.md](architecture.md) | How the workspace is organized and how the pieces fit together |
| [simulation.md](simulation.md) | Running and configuring the Gazebo simulation |
| [base-control.md](base-control.md) | Driving the Scout Mini base (topics, CLI, Python API) |
| [arm-control.md](arm-control.md) | Controlling the Piper arm and gripper (controllers, CLI, Python API) |
| [hardware.md](hardware.md) | Real-robot bringup plan and current status |
| [troubleshooting.md](troubleshooting.md) | Common problems and fixes |

For installation and a first run, start with the [top-level README](../README.md).

Day-to-day, use the `scout` helper script at the repo root (`scout help`
lists every command) — it wraps the build, simulation, demo, and the base/arm
CLIs, sourcing ROS and the workspace overlay automatically. See
[scout-cli.md](scout-cli.md) for the full reference.

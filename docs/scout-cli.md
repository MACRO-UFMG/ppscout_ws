# The `scout` CLI

`scout` is a bash helper script at the repo root that wraps every common
workspace task — building, launching the simulation, driving the base, and
moving the arm. Every command sources `/opt/ros/jazzy/setup.bash` and the
workspace overlay (`install/setup.bash`) automatically, so you never need to
source anything by hand.

It works from any directory: the script resolves its own location (even
through symlinks) and always operates on the workspace it lives in.

## Installation

The script is committed at the repo root, so `./scout <command>` works
immediately after cloning. To use it from anywhere:

```bash
./scout link    # symlinks 'scout' and 'arm' into ~/.local/bin
```

`arm` is the same script under a different name — invoking it as `arm`
behaves exactly like `scout arm`, so `arm home` moves the arm home.

If `~/.local/bin` is not on your `PATH`, `scout link` warns you and prints
the line to add to your shell profile.

## Commands

Run `scout help` for the always-up-to-date list.

### Setup & build

| Command | What it does |
|---------|--------------|
| `scout deps` | Installs all system dependencies: apt packages (ROS desktop, ros-gz, ros2-control, teleop, colcon, rosdep) and initialises/updates rosdep. Run once per machine. |
| `scout build [args]` | Full build: `rosdep install` over `src/`, then `colcon build --symlink-install`. Extra args are forwarded to colcon, e.g. `scout build --packages-select ppscout_control`. |
| `scout clean` | Deletes `build/`, `install/`, and `log/`. |
| `scout rebuild` | `clean` followed by `build` — a guaranteed from-zero rebuild. |
| `scout link` | Symlinks `scout` and `arm` into `~/.local/bin`. |

### Simulation

| Command | What it does |
|---------|--------------|
| `scout sim [args]` | Launches Gazebo, RViz, the ROS↔Gazebo bridge, and the arm controllers (`ppscout_bringup sim.launch.py`). Launch args pass through, e.g. `scout sim rviz:=false spawn_z:=0.20`. |
| `scout view` | Model viewer only — `display.launch.py`, no physics. |
| `scout demo [args]` | End-to-end demo: arm poses, gripper, and a 1 m driven square. Accepts the demo's flags, e.g. `scout demo --skip-drive --side 0.5`. |

### Base

| Command | What it does |
|---------|--------------|
| `scout drive [args]` | Timed velocity command, then stop. E.g. `scout drive --linear 0.3 --duration 2` or `scout drive --angular 0.5 --duration 3`. |
| `scout teleop` | Keyboard teleop via `teleop_twist_keyboard` (installed by `scout deps`). |
| `scout stop` | Publishes a single zero `Twist` to `/cmd_vel` — a quick way to halt the base. |

### Arm & gripper

| Command | What it does |
|---------|--------------|
| `scout arm <pose>` | Moves to a named pose: `home`, `ready`, or `reach`. `arm home` is the short form. |
| `scout arm -- j1 j2 j3 j4 j5 j6` | Moves to explicit joint positions in radians. `--time <s>` sets the trajectory duration. |
| `scout grip open\|close\|<m>` | Opens/closes the gripper or sets a position in meters (0.0 = open, 0.1 = closed). `gripper` also works. |

### Pull requests

`main` is a protected branch: it takes one approving review to merge, force-pushes and
deletions are blocked, and review threads must be resolved. These commands wrap the
[GitHub CLI](https://cli.github.com) (`gh auth login` once per machine) so the whole
branch → PR → merge loop stays in `scout`.

| Command | What it does |
|---------|--------------|
| `scout pr branch <name>` | Fetches `main` and starts `<name>` off `origin/main`. Refuses to run with uncommitted changes. |
| `scout pr new [title]` | Pushes the current branch (setting upstream) and opens a PR against `main`. Without a title, the PR is filled in from the branch's commits. Refuses to run on `main`. |
| `scout pr list` | Open PRs on the repo. |
| `scout pr view [n]` | Shows a PR — defaults to the one for the current branch. |
| `scout pr checkout <n>` | Checks out PR `<n>` locally for review or testing. |
| `scout pr merge [n]` | Squash-merges, deletes the branch, then returns you to an updated `main`. |
| `scout pr status` | What's waiting on your review, and what of yours is waiting on someone else's. |

```bash
scout pr branch fix/arm-limits
# ...edit, commit...
scout pr new "Clamp joint 3 to its mechanical limit"
scout pr merge          # after the review lands
```

Note that GitHub does not let you approve your own pull request, so a PR you opened
needs a review from another collaborator. Repo admins can still merge without one —
admin enforcement is deliberately left off so nobody gets locked out of a hotfix.

### Diagnostics

| Command | What it does |
|---------|--------------|
| `scout status` | Health check: workspace built?, Gazebo running?, key topics (`/cmd_vel`, `/odom`, `/joint_states`) present?, arm controller loaded? |
| `scout topics` | `ros2 topic list` with the workspace sourced. |
| `scout shell` | Opens a bash shell with ROS and the workspace already sourced (prompt prefixed with `(scout)`). Handy for ad-hoc `ros2` commands. |
| `scout help` | The full command list. |

## Typical session

```bash
# first time on a machine
./scout deps
./scout build
./scout link

# every day after
scout sim                                # terminal 1
scout status                             # terminal 2 — check everything is up
scout demo
arm ready
scout grip close
scout drive --linear 0.3 --duration 2
arm home
```

## Notes

- The scripts assume ROS 2 Jazzy at `/opt/ros/jazzy`. Set `ROS_DISTRO` before
  running to point at a different distro.
- Commands that need the workspace (`sim`, `arm`, `drive`, ...) fail with a
  clear message if it hasn't been built yet — run `scout build` first.
- The underlying raw ROS 2 commands are documented in
  [base-control.md](base-control.md), [arm-control.md](arm-control.md), and
  [simulation.md](simulation.md).

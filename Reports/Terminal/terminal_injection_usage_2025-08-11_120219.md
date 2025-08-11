# Terminal Injection — Usage Cheatsheet and Notes (2025-08-11)

## Quick start
- Start listener in target terminal (foreground, safest):
  ```bash
  TTY=$(readlink /proc/$$/fd/1)
  python shadeos_term_listener.py --fifo /tmp/shadeos_cmd.fifo \
    --cwd /home/luciedefraiteur/ShadeOS_Agents --tty "$TTY" \
    --echo --log /tmp/shadeos_listener.log --print-ready
  ```
- Send a command from another shell (auto-discovers FIFO):
  ```bash
  python shadeos_term_exec.py --cmd "echo '[PING]' && date"
  ```

## New safety: duplicate listener purge
- On startup, the listener now auto-kills duplicate `shadeos_term_listener.py` processes of the same user bound to the same FIFO. This prevents multiple readers competing on the FIFO (which caused commands to "disappear").
- A message like `[info] Purged N duplicate listener(s) for FIFO /tmp/shadeos_cmd.fifo` may appear once.

## Debugging visibility
- Listener mirrors output to the target TTY and can tee to a log (foreground example above). Check logs:
  ```bash
  tail -f /tmp/shadeos_listener.log
  ```
- The injector can pass full commands including cd/PYTHONPATH:
  ```bash
  python shadeos_term_exec.py --cmd "cd /home/luciedefraiteur/ShadeOS_Agents && PYTHONPATH=/home/luciedefraiteur/ShadeOS_Agents:$PYTHONPATH python Core/Agents/V10/tests/debug_scope_runner.py"
  ```

## Known good pings
```bash
python shadeos_term_exec.py --cmd "echo '[PING1]' && pwd && date"
python shadeos_term_exec.py --cmd "echo '[PING2]' && uname -a"
python shadeos_term_exec.py --cmd "printf '[PING3]\\n' && python -V"
```

## Notes
- Keep a single listener per FIFO. The new purge helps, but avoid manual multiple daemon starts.
- Foreground mode is recommended for development; daemon is available via `shadeos_start_listener.py` when needed.

!!! tip "How to restart your assistant"
    OVOS is not one program — it's several separate services (the listener, ovos-core,
    ovos-audio, the messagebus, and more) that need to pick up a config change together. How you
    restart them depends on how OVOS was installed:

    - **systemd install** (the `ovos-installer` or a RaspOVOS image): restart the whole stack with
      one command —
      ```bash
      systemctl --user restart ovos.service
      ```
      `ovos.service` is a `--user` target unit that the other services (`ovos-messagebus.service`,
      `ovos-listener.service`, `ovos-audio.service`, `ovos-skills.service`, `ovos-phal.service`,
      and — if installed — `ovos-gui.service`/`ovos-shell.service`) declare as `PartOf=`, so
      restarting it cascades to all of them. Restarting a single service instead (e.g. only the
      listener after a wake-word change) works the same way: `systemctl --user restart
      ovos-listener.service`.
    - **Docker/container install**: restart the equivalent service(s) in your compose file, e.g.
      ```bash
      docker compose restart <service-name>
      ```
      (or `docker compose restart` with no name to restart everything).
    - **Manual/development run**: stop the running `ovos-core` process (Ctrl-C) and start it again.

#!/bin/bash
# 星藏家 headless launcher: session bus + unlocked keyring (safeStorage) + electron
export DISPLAY=:99
if [ -z "$DBUS_SESSION_BUS_ADDRESS" ]; then
  if [ -S /run/user/0/bus ]; then
    export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/0/bus
  else
    eval "$(dbus-launch --sh-syntax)"
  fi
fi
echo -n "" | gnome-keyring-daemon --unlock --components=secrets >/dev/null 2>&1
eval "$(gnome-keyring-daemon --start --components=secrets 2>/dev/null)"
export GNOME_KEYRING_CONTROL
cd /opt/star-owner
export XDG_CURRENT_DESKTOP=GNOME
exec ./node_modules/.bin/electron . --no-sandbox --remote-debugging-port=13337 --password-store=gnome-libsecret

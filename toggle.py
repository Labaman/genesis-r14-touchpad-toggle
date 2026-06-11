import fcntl
import os
import sys
from pathlib import Path
import dbus
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)


def load_conf(path='/etc/touchpad-toggle.conf'):
    conf = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                k, _, v = line.partition('=')
                conf[k.strip()] = v.strip()
    return conf


def get_active_session():
    system_bus = dbus.SystemBus()
    seat_props = dbus.Interface(
        system_bus.get_object('org.freedesktop.login1', '/org/freedesktop/login1/seat/seat0'),
        'org.freedesktop.DBus.Properties',
    )
    _, session_path = seat_props.Get('org.freedesktop.login1.Seat', 'ActiveSession')
    session_props = dbus.Interface(
        system_bus.get_object('org.freedesktop.login1', session_path),
        'org.freedesktop.DBus.Properties',
    )
    uid, _ = session_props.Get('org.freedesktop.login1.Session', 'User')
    uid = int(uid)
    if uid == 0:
        raise RuntimeError('active session belongs to root; no user session bus available')
    desktop = str(session_props.Get('org.freedesktop.login1.Session', 'Desktop'))
    return uid, desktop


def session_bus(uid):
    os.seteuid(uid)
    try:
        return dbus.bus.BusConnection(f'unix:path=/run/user/{uid}/bus', mainloop=DBusGMainLoop())
    finally:
        os.seteuid(0)


def find_touchpad():
    for p in Path('/sys/class/input').glob('*/name'):
        try:
            if 'touchpad' in p.read_text().lower():
                return p.parent.name
        except OSError:
            pass
    return None


def toggle_non_kde(bus):
    inp = find_touchpad()
    if not inp:
        print('touchpad-toggle: no touchpad input device found', file=sys.stderr)
        return

    inhibit_path = Path(f'/sys/class/input/{inp}/inhibited')
    inhibited = inhibit_path.read_text().strip() == '1'
    inhibit_path.write_text('0' if inhibited else '1')

    icon  = 'input-touchpad-symbolic'  if inhibited else 'touchpad-disabled-symbolic'
    label = 'Touchpad enabled'         if inhibited else 'Touchpad disabled'

    try:
        notif = bus.get_object('org.freedesktop.Notifications', '/org/freedesktop/Notifications')
        dbus.Interface(notif, 'org.freedesktop.Notifications').Notify(
            'touchpad', dbus.UInt32(0), icon, 'Touchpad', label,
            dbus.Array([], signature='s'),
            dbus.Dictionary({'urgency': dbus.Byte(1)}, signature='sv'),
            dbus.Int32(2000),
            timeout=2000,
        )
    except dbus.DBusException as e:
        print(f'touchpad-toggle: notification failed: {e}', file=sys.stderr)


def toggle_kde(bus):
    accel = bus.get_object('org.kde.kglobalaccel', '/component/org_kde_touchpadshortcuts_desktop')
    dbus.Interface(accel, 'org.kde.kglobalaccel.Component').invokeShortcut(
        'ToggleTouchpad', timeout=2000,
    )


def do_toggle():
    lock = open('/var/lock/touchpad-toggle.lock', 'w')
    try:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        uid, desktop = get_active_session()
        bus = session_bus(uid)
        if desktop.lower() in ('kde', 'plasma'):
            toggle_kde(bus)
        else:
            toggle_non_kde(bus)
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN)
        lock.close()

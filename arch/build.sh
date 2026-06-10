#!/bin/bash
cp ../touchpad-toggle ../touchpad-key-listener ../toggle.py ../touchpad-toggle.service ../touchpad-toggle.conf .
makepkg --nodeps "$@"
rm -f touchpad-toggle touchpad-key-listener toggle.py touchpad-toggle.service touchpad-toggle.conf

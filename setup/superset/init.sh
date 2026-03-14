#!/bin/sh

init_step() {
	echo
	echo "[Init Step] $1"
	echo
}

init_step "Updating DB..."
superset db upgrade

init_step "Done upgrading DB."

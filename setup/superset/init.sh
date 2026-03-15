#!/bin/sh

init_step() {
	echo
	echo "[Init Step] $1"
	echo
}

init_step "Creating admin user"
superset fab create-admin \
	--username "$SUPERSET_ADMIN_USERNAME" \
	--firstname "$SUPERSET_ADMIN_FIRSTNAME" \
	--lastname "$SUPERSET_ADMIN_LASTNAME" \
	--email "$SUPERSET_ADMIN_EMAIL" \
	--password "$SUPERSET_ADMIN_PASSWORD"

init_step "Upgrading DB"
superset db upgrade

init_step "Initializing"
superset init

init_step "Initialization done."

#!/usr/bin/env bash
#
# Post-install Setup configuration
#
# Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
#
# Tasks performed:
# - If a config file is not provided, create and install one from template
# - Install the bash-completion file
# - Install the executable(s)
#
###############################################################################

set -Eeuo pipefail  # exit on any error
trap '>&2 echo "error: line $LINENO, status $?: $BASH_COMMAND"' ERR

#------------------------------------------------------------------------------

DESCRIPTION='Setup Configuration'

mydir=$(dirname "$(readlink -f "$0")")
setuplib="${mydir}/setuplib"
if [[ -r "$setuplib" ]]; then
	# shellcheck source=setuplib
	source "$setuplib"
else
	echo "Setup library not found: $setuplib" >&2; exit 1;
fi

#------------------------------------------------------------------------------

execdir=$BIN_HOME  # TODO: add SETUP_PREFIX to allow system-wide install
bashcompdir=${BASH_COMPLETION_USER_DIR:-"${DATA_HOME}/bash-completion/completions"}

#------------------------------------------------------------------------------

show_settings() {
	if ! ((SETUP_VERBOSE)); then return; fi
	set | grep '^SETUP_' | sort || :
}

#------------------------------------------------------------------------------

if [[ ! -f "$SETEN_CONFIG" ]]; then
	install --mode 600 -DT -- "$mydir"/seten.template.conf "$SETEN_CONFIG"
fi

if ((SETUP_INTERACTIVE)); then
	while true; do
		editor "$SETEN_CONFIG"
		# shellcheck source=seten.template.conf
		source "$SETEN_CONFIG"
		show_settings
		if confirm "Proceed with those settings?"; then break; fi
	done
else
	# shellcheck source=seten.template.conf
	source "$SETEN_CONFIG"
fi

install -- "$mydir"/setup "${execdir}/${SETUP_SLUG}"

mkdir -p -- "$bashcompdir"
awk -v SETUP_SLUG="$SETUP_SLUG" -v SETUP_DIR="$SETUP_DIR" '{
	sub("@@SETUP_SLUG@@", $SETUP_SLUG)
	sub("@@SETUP_DIR@@",  $SETUP_DIR)
	print
}' "$mydir"/setup.bash-completion.in > "${bashcompdir}/${SETUP_SLUG}"

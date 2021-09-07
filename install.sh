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
# - Install extra packages
#
###############################################################################

DESCRIPTION='Setup Configuration'

mydir=$(dirname "$(readlink -f "$0")")
setuplib=${SETUP_LIB_PATH:-"$mydir"/setuplib}
if [[ -r "$setuplib" ]]; then
	# shellcheck source=setuplib
	source "$setuplib"
else
	echo "Setup library not found: $setuplib" >&2; exit 1;
fi

#------------------------------------------------------------------------------

execdir=$BIN_HOME  # TODO: add SETUP_PREFIX to allow system-wide install
bashcompdir=${BASH_COMPLETION_USER_DIR:-"${DATA_HOME}/bash-completion/completions"}

execfile=$execdir/$SETUP_SLUG
bashcompfile=$bashcompdir/$SETUP_SLUG

#------------------------------------------------------------------------------

show_settings() {
	if ! ((SETUP_VERBOSE)); then return; fi
	message "Settings from environment and parsed from config file:"
	set | grep -E '^SET(UP|EN)_' | sort || :
}

#------------------------------------------------------------------------------

if [[ ! -f "$SETEN_CONFIG" ]]; then
	message "Install config file: ${SETEN_CONFIG}"
	install --mode 600 -DT -- "$mydir"/seten.template.conf "$SETEN_CONFIG"
fi

if ((SETUP_INTERACTIVE)); then
	while true; do
		editor "$SETEN_CONFIG"
		# shellcheck source=setuplib
		source "$setuplib"
		show_settings
		if confirm "Proceed with those settings?"; then break; fi
	done
else
	# shellcheck source=setuplib
	source "$setuplib"
fi

# SETUP_DIR is intentionally set to $mydir here and (indirectly) in setuplib
# Hardcode it in seten.sh.in and seten.bash-completion.in
# Only bootstrap.sh read it from config file.

message "Install main executable: ${execfile}"
mkdir -p -- "$execdir"
awk \
	-v SETUP_DIR="$(printf '%q' "$mydir")"  \
	'{
		sub("@@SETUP_DIR@@", SETUP_DIR)
		print
	}' \
	"$mydir"/seten.sh.in > "$execfile"
chmod +x -- "$execfile"

message "Install bash completion: ${bashcompfile}"
mkdir -p -- "$bashcompdir"
awk \
	-v SETUP_DIR="$( printf '%q' "$mydir")"      \
	-v SETUP_SLUG="$(printf '%q' "$SETUP_SLUG")" \
	'{
		sub("@@SETUP_SLUG@@", SETUP_SLUG)
		sub("@@SETUP_DIR@@",  SETUP_DIR)
		print
	}' \
	"$mydir"/seten.bash-completion.in > "$bashcompfile"

message "Install extra packages"
install_package "${SETUP_PACKAGES[@]}"

if [[ "$PATH" =~ (^|:)"$execdir"(:|$) ]]; then
	message "Done! Use the command '${SETUP_SLUG}' to run setup scripts"
else
	message "Done! Add '${execdir}' to your \$PATH to enable " \
		"the command '${SETUP_SLUG}' to run setup scripts"
	echo "PATH=\$PATH:${execdir}"
fi

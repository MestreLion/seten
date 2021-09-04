#!/usr/bin/env bash
#
# Bootstrap initial setup infrastructure
#
# Copyright (C) 2021 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
# License: GPLv3 or later, at your choice. See <http://www.gnu.org/licenses/gpl>
#
# Tasks performed:
# - Install git from distribution repositories
# - Clone project git repository, by default from Github
# - Force-update the local git repository
# - Run the installer `install.sh`
#
# Instructions:
# - Copy any pre-made configuration file to ~/.config/seten/seten.conf
#     Can also select a custom file by either setting SETEN_CONFIG environmental
#     variable or passing an argument to the command below
# - Copy in terminal:
#
# bash <(wget -qO- https://github.com/MestreLion/seten/raw/main/bootstrap.sh)
#
###############################################################################

set -Eeuo pipefail  # exit on any error
trap '>&2 echo "error: line $LINENO, status $?: $BASH_COMMAND"' ERR

#------------------------------------------------------------------------------
# Factory defaults, most copied from setuplib since boostrap can't source it
# Keep both files in sync, specially regarding SETEN_CONFIG and SETUP_SLUG!

# Handy XDG vars with their defaults
CONFIG_HOME=${XDG_CONFIG_HOME:-"$HOME/.config"}
DATA_HOME=${XDG_DATA_HOME:-"$HOME/.local/share"}

# Config file factory default path, intentionally not affected by SETUP_SLUG
defaultconf="${CONFIG_HOME}/seten/seten.conf"
export SETEN_CONFIG=${1:-${SETEN_CONFIG:-${defaultconf}}}
include-config() {
	local config
	for config in "$@"; do
		if [[ -d "$config" ]]; then
			include-config "$config"/*{.conf,/}
		fi

		if ! [[ -f "$config" && -r "$config" ]]; then
			continue
		fi

		pushd "$(dirname "$config")"
		# shellcheck source=seten.template.conf
		source "$config"
		popd
	done
}
include-config "$SETEN_CONFIG"

# All settings below can be changed in the config file
slug=${SETUP_SLUG:-}; slug=${slug##*/}; slug=${slug:-'seten'}
verbose=${SETUP_VERBOSE:-1}

# Bootstrap-only settings
repo=${SETUP_REPO:-"https://github.com/MestreLion/seten.git"}
dir=${SETUP_DIR:-"${DATA_HOME}/${slug}"}

#------------------------------------------------------------------------------

for arg in "$@"; do if [[ "$arg" == '-h' || "$arg" == '--help' ]]; then
	echo "Bootstrap Seten setup"
	echo "Install git, clone or update local repository, run installer"
	echo "See $repo for details"
	echo "Usage: bootstrap.sh [CONFIG_FILE]"
	exit
fi; done

#------------------------------------------------------------------------------

if ((verbose)) && [[ "${1:-}" && "$SETEN_CONFIG" != "$defaultconf" ]]; then
	echo "*** IMPORTANT NOTE ***"
	echo "You specified a custom path for the configuration file."
	echo "Make sure the following is added to your ~/.profile or similar:"
	echo
	echo "export SETEN_CONFIG=$(printf '%q' "$SETEN_CONFIG")"
	echo
	read -rp "Press ENTER to continue..."
fi

if ! type git &>/dev/null; then
	apt install -y git
fi

if [[ -d "$dir" ]]; then
	git -C "$dir" fetch
	git -C "$dir" checkout --force main
	git -C "$dir" reset --hard origin/main
else
	git clone -- "$repo" "$dir"
fi

exec "$dir"/install.sh

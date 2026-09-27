#!/bin/bash
# Unknown Horizons launcher — TuningFork maintenance build.
# No installation needed: just run this file.
set -u
HERE="$(dirname "$(readlink -f "$0")")"
cd "$HERE"

# The bundled engine is built for Python 3.12.
PY=""
for cand in python3.12 python3; do
	if command -v "$cand" >/dev/null 2>&1; then
		if [ "$("$cand" -c 'import sys; print("%u.%u" % sys.version_info[:2])')" = "3.12" ]; then
			PY="$cand"
			break
		fi
	fi
done
if [ -z "$PY" ]; then
	echo "Unknown Horizons needs Python 3.12, which does not seem to be installed."
	echo "On Debian/Ubuntu:  sudo apt install python3.12"
	exit 1
fi
if ! "$PY" -c "import yaml" 2>/dev/null; then
	echo "Unknown Horizons needs PyYAML, which does not seem to be installed."
	echo "On Debian/Ubuntu:  sudo apt install python3-yaml"
	exit 1
fi

export PYTHONPATH="$HERE${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="$HERE/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

if ! "$PY" -c "from fife import fife" 2>/dev/null; then
	echo "Could not load the bundled game engine."
	echo "Your system may be missing SDL2, OpenGL or OpenAL libraries."
	echo "On Debian/Ubuntu:  sudo apt install libsdl2-2.0-0 libopenal1"
	exit 1
fi

exec "$PY" run_uh.py "$@"

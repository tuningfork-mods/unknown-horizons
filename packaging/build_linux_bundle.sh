#!/bin/bash
# Builds the TuningFork Unknown Horizons Linux bundle:
# a portable tarball with the game, the prebuilt FIFE engine and a launcher.
# Usage: packaging/build_linux_bundle.sh [output-dir]
set -e
REPO="$(cd "$(dirname "$0")/.." && pwd)"
OUT="${1:-$REPO/dist}"
STAGE="$OUT/stage/unknown-horizons-linux"

echo "Staging bundle in $STAGE"
rm -rf "$OUT/stage"
mkdir -p "$STAGE/lib"

# game
cp "$REPO/run_uh.py" "$STAGE/"
cp -r "$REPO/horizons" "$STAGE/"
cp -r "$REPO/content" "$STAGE/"
cp "$REPO/packaging/UnknownHorizons.sh" "$STAGE/UnknownHorizons.sh"
cp "$REPO/packaging/README.txt" "$STAGE/README.txt"
chmod +x "$STAGE/UnknownHorizons.sh"

# vendored FIFE engine (built 0.4.2, python3.12)
# FIFE_DIR may point at the engine/python/fife source tree plus compiled _fife.so/_fifechan.so
FIFE_SRC="${FIFE_DIR:-/usr/lib/python3/dist-packages/fife}"
if [ -d "$FIFE_SRC" ] && [ ! -f "$FIFE_SRC/_fife.so" ] && [ -n "$FIFE_BUILD_DIR" ]; then
  mkdir -p /tmp/uh_fife_pkg/fife
  cp -r "$FIFE_SRC"/. /tmp/uh_fife_pkg/fife/
  cp "$FIFE_BUILD_DIR"/_fife.so "$FIFE_BUILD_DIR"/_fifechan.so "$FIFE_BUILD_DIR"/fife.py "$FIFE_BUILD_DIR"/fifechan.py /tmp/uh_fife_pkg/fife/
  FIFE_SRC=/tmp/uh_fife_pkg/fife
fi
cp -r "$FIFE_SRC" "$STAGE/fife"

# vendored fifechan libs (not present on player machines)
FIFECHAN_SEARCH="${FIFECHAN_LIB_DIR:-} /lib /usr/lib/x86_64-linux-gnu /usr/lib"
for d in $FIFECHAN_SEARCH; do
	for f in "$d"/libfifechan*.so*; do
		[ -e "$f" ] && cp -P "$f" "$STAGE/lib/"
	done
done
if ! ls "$STAGE/lib"/libfifechan*.so* >/dev/null 2>&1; then
	echo "ERROR: no fifechan libraries found" >&2
	exit 1
fi

# compiled translations (content/lang/<lang>/LC_MESSAGES/unknown-horizons.mo)
python3 - "$REPO" "$STAGE/content/lang" <<'EOF'
import os, sys
sys.path.insert(0, sys.argv[1])
from horizons.ext import polib
repo, langdir = sys.argv[1], sys.argv[2]
count = 0
for name in os.listdir(os.path.join(repo, 'po', 'uh')):
	if not name.endswith('.po'):
		continue
	lang = name[:-3]
	out = os.path.join(langdir, lang, 'LC_MESSAGES')
	os.makedirs(out, exist_ok=True)
	po = polib.pofile(os.path.join(repo, 'po', 'uh', name))
	po.save_as_mofile(os.path.join(out, 'unknown-horizons.mo'))
	count += 1
print('compiled %d translation catalogs' % count)
EOF

# cleanup
find "$STAGE" -name "__pycache__" -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$STAGE" -name "*.pyc" -delete

echo "Creating tarball"
mkdir -p "$OUT"
cd "$OUT/stage"
tar czf "$OUT/unknown-horizons-linux-x86_64.tar.gz" unknown-horizons-linux
echo "Wrote $OUT/unknown-horizons-linux-x86_64.tar.gz"
du -h "$OUT/unknown-horizons-linux-x86_64.tar.gz"

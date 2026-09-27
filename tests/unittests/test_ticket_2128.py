# ###################################################
# Copyright (C) 2026 The Unknown Horizons Team
# team@unknown-horizons.org
# This file is part of Unknown Horizons.
#
# Unknown Horizons is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# ###################################################

import os
from pathlib import Path

import pytest

import horizons.globals
from horizons.i18n import voice
from horizons.i18n.voice import get_speech_file


@pytest.fixture(autouse=True)
def repo_root(monkeypatch):
	"""Voice paths are relative to the game directory."""
	monkeypatch.chdir(Path(__file__).resolve().parent.parent.parent)


class FakeFife:
	def __init__(self, locale):
		self._locale = locale

	def get_locale(self):
		return self._locale


@pytest.fixture
def set_locale(monkeypatch):
	def _set(locale):
		monkeypatch.setattr(horizons.globals, 'fife', FakeFife(locale))
	return _set


def voice_dir(lang):
	return os.path.join('content', 'audio', 'voice', lang, '0', 'new_world')


def test_2128_plays_correct_voice_file_for_event(set_locale):
	"""The dynamic lookup resolves the right file for the event and language.

	https://github.com/unknown-horizons/unknown-horizons/issues/2128
	"""
	set_locale('de')
	path = get_speech_file('NEW_WORLD')
	assert path is not None
	assert path.startswith(voice_dir('de'))
	assert path.endswith('.ogg')
	assert os.path.isfile(path)


def test_2128_random_variation_stays_in_category(set_locale):
	"""Random variation selection never leaves the event's directory."""
	set_locale('en')
	for _ in range(20):
		path = get_speech_file('NEW_WORLD')
		assert path.startswith(voice_dir('en'))
		assert os.path.isfile(path)


def test_2128_falls_back_to_english_for_missing_language(set_locale):
	"""Languages without recordings fall back to the english voice files."""
	set_locale('it')  # no italian recordings exist
	path = get_speech_file('NEW_WORLD')
	assert path is not None
	assert path.startswith(voice_dir('en'))
	assert os.path.isfile(path)


def test_2128_fallback_preserves_variation_and_speaker(set_locale):
	"""The english fallback keeps the requested variation, not variation 0."""
	set_locale('it')
	path = get_speech_file('NEW_WORLD', variation_id=2, speaker_id=0)
	assert path == os.path.join(voice_dir('en'), '2.ogg')


def test_2128_unknown_category_returns_none(set_locale, capsys):
	"""Events without a voice category resolve to no sound file."""
	set_locale('en')
	assert get_speech_file('AUTOSAVE') is None
	# ... quietly: the lookup must not spam stdout during normal gameplay
	assert 'speech category' not in capsys.readouterr().out


def test_2128_eval_category_name_uses_logging_not_print(capsys, caplog):
	assert voice.eval_category_name('BOGUS') is None
	assert 'speech category' not in capsys.readouterr().out

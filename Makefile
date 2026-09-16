PREFIX ?= /usr/local
DESTDIR ?=
PYTHON ?= python3
APPDIR = $(DESTDIR)$(PREFIX)/share/tty-terminal

.PHONY: all check install
all: assets/tty-console.ttf

assets/tty-console.ttf: build_font.py assets/font_8x16.c assets/unicode-map.json
	$(PYTHON) build_font.py $@

check: all
	$(PYTHON) -m unittest discover -s tests -v
	desktop-file-validate data/tty-terminal.desktop

install: all
	install -d "$(APPDIR)/assets" "$(DESTDIR)$(PREFIX)/bin"
	install -m644 tty_terminal.py config.py VERSION config.example.toml "$(APPDIR)/"
	install -m644 assets/tty-console.ttf assets/FONT-LICENSE.txt "$(APPDIR)/assets/"
	printf '%s\n' '#!/bin/sh' 'exec /usr/bin/env python3 "$(PREFIX)/share/tty-terminal/tty_terminal.py" "$$@"' > "$(DESTDIR)$(PREFIX)/bin/tty-terminal"
	chmod 755 "$(DESTDIR)$(PREFIX)/bin/tty-terminal"
	install -Dm644 data/tty-terminal.desktop "$(DESTDIR)$(PREFIX)/share/applications/tty-terminal.desktop"
	install -Dm644 packaging/tty-terminal.svg "$(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/tty-terminal.svg"
	install -Dm644 LICENSE "$(DESTDIR)$(PREFIX)/share/licenses/tty-terminal/LICENSE"
	install -Dm644 assets/FONT-LICENSE.txt "$(DESTDIR)$(PREFIX)/share/licenses/tty-terminal/FONT-LICENSE.txt"
	install -Dm644 THIRD_PARTY.md "$(DESTDIR)$(PREFIX)/share/licenses/tty-terminal/THIRD_PARTY.md"
	install -Dm644 README.md "$(DESTDIR)$(PREFIX)/share/doc/tty-terminal/README.md"
	install -Dm644 docs/screenshot.png "$(DESTDIR)$(PREFIX)/share/doc/tty-terminal/docs/screenshot.png"

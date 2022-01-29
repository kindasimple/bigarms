include ../Make.defs

objects = $(wildcard *.in)
outputs := $(objects:.in=.txt)

all: $(outputs)

venv:
	python -m venv venv
	$(ACTIVATE) pip install pip-tools

%.txt: %.in
	$(ACTIVATE) pip-compile -v --output-file $@ $<

clean: check
	- rm *.txt

.PHONY: all check clean
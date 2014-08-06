TOP=$(shell pwd)
export PYTHONPATH:=$(TOP)/..:$(PYTHONPATH)

# the basename of the python binary. This complicated expression is needed
# since the newest python binary on our development host "aragon" is named
# "python2.5":
PYTHON:=$(shell python -V 2>&1 | ( grep -q " 2\.[5678]" && echo python || ( python2.5 -V >/dev/null 2>&1 && echo "python2.5" || echo python )))

# use the following definition to create code coverage information with the
# "coverage" tool:
# PYTHON=coverage run -p

.PRECIOUS: %.out

# set this only to "yes" in order to create the 
# test[n].ok files. These files are later compared to
# the test[n].out files.
# In order for the tests to really test pyexpander, 
# the variable MUST BE set to "no".
CREATE_TESTS=no

tests= $(sort $(basename $(wildcard *.ok)))

test_tst= $(addsuffix .tst, $(tests))


all: pure_module_test $(test_tst)

test:
	@echo $(tests)

realclean: clean
	rm -rf tmp-*

# do not remove tmp-010.. since it takes relatively long to create:

almostclean: clean
	rm -rf `ls -d tmp-* | grep -v tmp-010`

clean:
	rm -f $(addsuffix .out, $(tests)) 
	rm -rf *.tmp
	rm -rf *.bak
	rm -f deps

pure_module_test:
ifeq ($(PYTHON),python)
	# utils doctest fails with python2.5:
	$(PYTHON) ../sumo/Config.py
	$(PYTHON) ../sumo/JSON.py
	$(PYTHON) ../sumo/lock.py
	$(PYTHON) ../sumo/makefile_scan.py
	$(PYTHON) ../sumo/system.py
	$(PYTHON) ../sumo/utils.py
	$(PYTHON) ../sumo/ModuleSpec.py
	$(PYTHON) ../sumo/Databases.py
else
	@echo "skipping testing sumo/utils.py"
endif
	$(PYTHON) ../bin/sumo-scan --test
	$(PYTHON) ../bin/sumo-db --test
	$(PYTHON) ../bin/sumo-build --test

include deps

deps:
	for f in *.sh; do ./$$f deps; done > $@

x:
	echo $(test_tst)

%.out: %.sh 
	sh ./$< $(PYTHON) > $@

ifeq "$(CREATE_TESTS)" "yes"
%.ok: %.out
	cp $< $@
endif

%.tst: %.sh %.out %.ok
	diff $(wordlist 2, 3, $+) 


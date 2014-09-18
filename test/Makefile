TOP=$(shell pwd)

# extend PYTHONPATH in order to find Sumo modules:
export PYTHONPATH:=$(TOP)/..:$(PYTHONPATH)

# the basename of the python binary. This complicated expression is needed
# since the newest python binary on our development host "aragon" is named
# "python2.5":
PYTHON:=$(shell python -V 2>&1 | ( grep -q " 2\.[5678]" && echo python || ( python2.5 -V >/dev/null 2>&1 && echo "python2.5" || echo python )))

.PRECIOUS: %.out

# set this only to "yes" in order to create the 
# test[n].ok files. These files are later compared to
# the test[n].out files.
# In order for the shell_tests to really test pyexpander, 
# the variable MUST BE set to "no".
CREATE_TESTS=no

# a list of generic shell script based shell_tests is generated from all *.ok files:
shell_tests= $(sort $(basename $(wildcard *.ok)))

# *.sh are the shell scripts:
shell_tests_sh= $(addsuffix .tst, $(shell_tests))

# *.tst are pseudo files:
shell_tests_tst= $(addsuffix .tst, $(shell_tests))

all: target_module_tests target_script_tests target_shell_tests

help:
	@echo "make targets:"
	@echo "    all : perform all tests"
	@echo "    almostclean: clean test directories except test 010"
	@echo "    clean: clean test directories"
	@echo "    distclean: remove also created source repos"



# sample repositories must be generated:
data/repos/stamp: data/src/stamp
	@echo "creating sample repositories..."
	$(MAKE) -C $(@D)

# sample sources must be unpacked:
data/src/stamp:
	@echo "unpacking sample sources..."
	$(MAKE) -C $(@D)


distclean: clean
	@echo "cleanup repo directory..."
	make -C data/repos clean
	@echo "cleanup src directory..."
	make -C data/src clean

clean: shallowclean
	rm -rf tmp-*

# do not remove tmp-010.. since it takes relatively long to create:

almostclean: shallowclean
	rm -rf `ls -d tmp-* | grep -v tmp-010`

shallowclean:
	rm -f *.out
	rm -rf *.tmp
	rm -rf *.bak

target_module_tests: $(module_tests_tst)

target_script_tests: $(script_tests_tst)

target_shell_tests: data/repos/stamp $(shell_tests_tst)

module_tests= $(basename $(shell grep -l doctest ../sumo/*.py))
module_tests_tst= $(addsuffix .tst, $(module_tests))

script_tests= $(basename $(shell ls ../bin))
script_tests_tst= $(addsuffix .tst, $(script_tests))

# static pattern rule to test python modules:
$(module_tests_tst): %.tst: ../sumo/%.py
	$(PYTHON) $<

# static pattern rule to test scripts:
$(script_tests_tst): %.tst: ../bin/%
	$(PYTHON) $< --test

include deps

deps:
	for f in $(shell_tests_sh); do ./$$f deps; done > $@

# how to generate an out file:
%.out: %.sh 
	sh ./$< $(PYTHON) > $@

ifeq "$(CREATE_TESTS)" "yes"
%.ok: %.out
	cp $< $@
endif

# how to perform a shell test:
$(shell_tests_tst): %.tst: %.sh %.out %.ok
	diff $(wordlist 2, 3, $+) 

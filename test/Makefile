#
# test1.in : simply macro replacement

TOP=$(shell pwd)
export PYTHONPATH:=$(TOP)/..:$(PYTHONPATH)

# the basename of the python binary. This complicated expression is needed
# since the newest python binary on our development host "aragon" is named
# "python2.5":
PYTHON:=$(shell python -V 2>&1 | ( grep -q " 2\.[5678]" && echo python || ( python2.5 -V >/dev/null 2>&1 && echo "python2.5" || echo python )))

.PRECIOUS: %.out

# set this only to "yes" in order to create the 
# test[n].ok files. These files are later compared to
# the test[n].out files.
# In order for the tests to really test pyexpander, 
# the variable MUST BE set to "no".
CREATE_TESTS=no

testlist= $(sort $(basename $(wildcard *.ok)))


all: pure_module_test $(addsuffix .tst, $(testlist))

test:
	@echo $(testlist)

realclean: clean
	rm -rf tmp-*

almostclean: clean
	rm -rf tmp-test08 tmp-test1*

clean:
	rm -f $(addsuffix .out, $(testlist)) 
	rm -rf *.tmp
	rm -rf *.bak

pure_module_test:
ifeq ($(PYTHON),python)
	$(PYTHON) ../sumo/utils.py
else
	@echo "skipping testing sumo/utils.py"
endif
	$(PYTHON) ../bin/sumo-scan --test
	$(PYTHON) ../bin/sumo-db --test
	$(PYTHON) ../bin/sumo-build --test

ok: $(addsuffix .ok, $(testlist))

%.out: %.sh 
	sh ./$< $(PYTHON) > $@

ifeq "$(CREATE_TESTS)" "yes"
%.ok: %.out
	cp $< $@
endif

%.tst: %.sh %.out %.ok
	diff $(wordlist 2, 3, $+) 

test09.tst: test09.sh test09.out test09.ok test08.out
	diff $(wordlist 2, 3, $+) 

test10.tst: test10.sh test10.out test10.ok test08.out
	diff $(wordlist 2, 3, $+) 

test11.tst: test11.sh test11.out test11.ok test10.out test08.out test04.out
	diff $(wordlist 2, 3, $+) 

test12.tst: test12.sh test12.out test12.ok test11.out
	diff $(wordlist 2, 3, $+) 

test13.tst: test13.sh test13.out test13.ok test11.out
	diff $(wordlist 2, 3, $+) 

test14.tst: test14.sh test14.out test14.ok test11.out
	diff $(wordlist 2, 3, $+) 

test15.tst: test15.sh test15.out test15.ok test11.out
	diff $(wordlist 2, 3, $+) 

test16.tst: test16.sh test16.out test16.ok test11.out
	diff $(wordlist 2, 3, $+) 


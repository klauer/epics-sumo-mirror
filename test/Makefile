################################################################
# DISABLE BUILT-IN RULES
#
.SUFFIXES:
	MAKEFLAGS += -r

TOP:=$(shell pwd)

# set PYTHON only if it is not yet defined:
ifeq (,$(PYTHON))
	PYTHON=python3
endif

export PYTHONPATH:=$(TOP)/..:$(PYTHONPATH)

BINDIR:=$(TOP)/../bin
LIBDIR:=$(TOP)/../sumolib

.PRECIOUS: %.out

# set this only to "yes" in order to create the 
# test[n].ok files. These files are later compared to
# the test[n].out files.
# In order for the shell_tests to really test pyexpander, 
# the variable MUST BE set to "no".
CREATE_TESTS=no

# The list of tests and their order is taken from file "TESTS":
shell_tests:= $(shell grep -v '^ *\#' TESTS | xargs )

# *.sh are the shell scripts:
shell_tests_sh:= $(addsuffix .sh, $(shell_tests))

# *.tst are pseudo files:
shell_tests_tst:= $(addsuffix .tst, $(shell_tests))

all: target_module_tests target_script_tests target_shell_tests

help:
	@echo "make targets:"
	@echo "    all : perform all tests"
	@echo "    clean: clean test directories"
	@echo "    distclean: remove also created source repos"



# sample epics support dir must be generated
data/epics/stamp: data/repos/stamp
	@echo
	@echo "================================================="
	@echo "creating sample support dir..."
	$(MAKE) -C $(@D)

# sample repositories must be generated:
data/repos/stamp: data/src/stamp
	@echo
	@echo "================================================="
	@echo "creating sample repositories..."
	$(MAKE) -C $(@D)

# sample sources must be unpacked:
data/src/stamp:
	@echo
	@echo "================================================="
	@echo "unpacking sample sources..."
	$(MAKE) -C $(@D)

distclean: clean
	@echo "cleanup epics directory..."
	make -C data/epics clean
	@echo "cleanup repo directory..."
	make -C data/repos clean
	@echo "cleanup src directory..."
	make -C data/src clean

clean: shallowclean
	for d in tmp-*; do \
	    echo "DELETING $$d..."; \
	    rm -rf $$d 2>/dev/null; \
	    if [ $$? -ne 0 ]; then \
	        echo chmod -R u+w $$d; \
	        chmod -R u+w $$d; \
	        rm -rf $$d; \
	    fi; \
	done
	rm -rf *.tst
	rm -rf *.out
	rm -rf *.tmp
	rm -rf *.bak

# clean only files for a single test
%.clean: 
	if [ -d tmp-$* ]; then \
	    chmod -R u+w tmp-$*; \
	fi
	rm -rf $*.tst
	rm -rf $*.out
	rm -rf $*.tmp
	rm -rf $*.bak
	rm -rf tmp-$*


# do not remove tmp-010.. since it takes relatively long to create:

shallowclean:
	rm -f *.out
	rm -rf *.tmp
	rm -rf *.bak


module_tests:= $(notdir $(basename $(shell grep -l doctest $(LIBDIR)/*.py)))
module_tests_tst= $(addsuffix .tst, $(module_tests))

script_tests:= $(sort $(notdir $(basename $(shell ls $(BINDIR)))))
script_tests_tst= $(addsuffix .tst, $(script_tests))

# static pattern rule to test python modules:
$(module_tests_tst): %.tst: $(LIBDIR)/%.py 
	@echo -e "\n-> run doctest of sumolib/$*.py" >&2
	@$(PYTHON) $<
	@touch $@

# static pattern rule to test scripts:
$(script_tests_tst): %.tst: $(BINDIR)/% 
	@echo -e "\n-> run selftest of $*" >&2
	@$(PYTHON) $< --test
	@touch $@

.PHONY : target_module_tests target_script_tests target_shell_tests

target_module_tests: $(module_tests_tst)

target_script_tests: $(script_tests_tst)

target_shell_tests: $(shell_tests_tst)

# how to generate an out file:
%.out: %.sh data/epics/stamp
	@bash ./$< > $@

ifeq "$(CREATE_TESTS)" "yes"
%.ok: %.out
	cp $< $@
endif

sumo-db-convert.out: sumo-scan-all.tst
sumo-db-modconvert.out: sumo-scan-all.tst
sumo-db-dependency-delete.out: sumo-db-convert.tst
sumo-db-dependency-add.out: sumo-db-convert.tst
sumo-db-alias-add.out: sumo-db-convert.tst
sumo-db-releasefilename.out: sumo-db-convert.tst
sumo-db-make-recipes.out: sumo-db-convert.tst
sumo-db-commands.out: sumo-db-convert.tst
sumo-db-replaceversion.out: sumo-db-convert.tst
sumo-db-cloneversion.out: sumo-db-convert.tst
sumo-db-cloneversion-2.out: sumo-db-convert.tst
sumo-db-clonemodule.out: sumo-db-convert.tst
sumo-db-weight.out: sumo-db-convert.tst
sumo-db-extra.out: sumo-db-convert.tst
sumo-db-show.out: sumo-db-convert.tst
sumo-db-list.out: sumo-db-convert.tst
sumo-db-list-nowrite.out: sumo-db-convert.tst
sumo-db-find.out: sumo-db-convert.tst
sumo-db-check.out: sumo-db-convert.tst
sumo-db-dbrepo-create.out: sumo-db-convert.tst
sumo-db-cloneversion-dbrepo.out: sumo-db-dbrepo-create.tst
sumo-db-cloneversion-dbrepo-2.out: sumo-db-dbrepo-create.tst
sumo-db-edit-dbrepo.out: sumo-db-dbrepo-create.tst
sumo-db-merge.out: sumo-db-convert.tst
sumo-db-dbrepo-pull.out: sumo-db-cloneversion-dbrepo.tst sumo-db-dbrepo-create.tst
sumo-db-dbrepo-pull-nowrite.out: sumo-db-cloneversion-dbrepo.tst sumo-db-dbrepo-create.tst
sumo-db-dbrepo-conflict.out: sumo-db-cloneversion-dbrepo.tst sumo-db-dbrepo-create.tst
sumo-config-make.out: sumo-db-convert.tst
sumo-config-make-2.out: sumo-db-convert.tst
sumo-build-new-0.out: sumo-db-convert.tst
sumo-build-new-releasefile.out: sumo-db-releasefilename.tst 
sumo-build-new-extra.out: sumo-db-extra.tst 
sumo-build-new-make-recipes.out: sumo-db-make-recipes.tst 
sumo-build-new-commands.out: sumo-db-commands.tst 
sumo-build-modulespecs.out: sumo-build-new-0.tst sumo-db-convert.tst
sumo-build-try.out: sumo-build-new-0.tst sumo-db-convert.tst
sumo-build-new.out: sumo-db-convert.tst
sumo-build-new-1.out: sumo-db-convert.tst
sumo-build-delete-2.out: sumo-db-convert.tst
sumo-build-state.out: sumo-build-new-0.tst 
sumo-build-state-2.out: sumo-build-new-0.tst 
sumo-build-new-2.out: sumo-build-new.tst sumo-db-convert.tst
sumo-build-delete.out: sumo-build-new-2.tst sumo-db-convert.tst
sumo-build-delete-3.out: sumo-build-new-2.tst sumo-db-convert.tst
sumo-build-delete-5.out: sumo-build-new-2.tst sumo-db-convert.tst
sumo-build-delete-4.out: sumo-build-new-2.tst sumo-db-convert.tst
sumo-scan-all-2.out: sumo-build-new-2.tst
sumo-build-new-3.out: sumo-build-new.tst sumo-db-convert.tst
sumo-build-remake.out: sumo-db-convert.tst
sumo-build-find.out: sumo-build-new-2.tst
sumo-build-list.out: sumo-build-new-2.tst
sumo-build-show.out: sumo-build-new-2.tst
sumo-build-use.out: sumo-build-new-2.tst
sumo-build-use-2.out: sumo-build-new-2.tst
sumo-build-use-3.out: sumo-build-new-2.tst
sumo-config-standalone-new.out: sumo-build-new-1.tst sumo-db-dbrepo-create.tst
sumo-config-local-new.out: sumo-build-new-1.tst sumo-db-dbrepo-create.tst

# how to perform a shell test:
$(shell_tests_tst): %.tst: %.sh %.ok %.out
	@diff $(wordlist 2, 3, $+) 
	@touch $@


# Makefile for additional class for python-weka-wrapper
#
# Author: Fracpete (pythonwekawrapper at gmail dot com)

SRCDIR        = src
BUILDDIR      = build
DISTDIR       = dist
LIBDIR        = ../python/weka/lib

all: clean compile dist

clean:
	@echo
	@echo cleaning up...
	@echo
	rm -rf $(BUILDDIR)
	rm -rf $(DISTDIR)
	find -name "*~" -delete

compile:
	@echo
	@echo compiling source files...
	@echo
	mkdir -p $(BUILDDIR)
	@echo
	@echo first pass - can have some errors with ClassHelper
	@echo
	find $(SRCDIR) -name "*.java" -exec javac -source 1.6 -target 1.6 -classpath $(LIBDIR)/weka.jar:$(BUILDDIR) -d $(BUILDDIR) {} \;
	@echo
	@echo second pass - should not have errors
	@echo
	find $(SRCDIR) -name "*.java" -exec javac -source 1.6 -target 1.6 -classpath $(LIBDIR)/weka.jar:$(BUILDDIR) -d $(BUILDDIR) {} \;

dist:
	@echo
	@echo creating jar archive...
	@echo
	mkdir -p $(DISTDIR)
	jar -cf $(DISTDIR)/python-weka-wrapper.jar -C $(BUILDDIR) weka
	jar -cf $(DISTDIR)/python-weka-wrapper-src.jar -C $(SRCDIR) weka
	cp $(DISTDIR)/python-weka-wrapper.jar $(LIBDIR)
	cp $(DISTDIR)/python-weka-wrapper-src.jar $(LIBDIR)


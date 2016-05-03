# Makefile for additional class for python-weka-wrapper
#
# Author: Fracpete (pythonwekawrapper at gmail dot com)

SRCDIR        = src
BUILDDIR      = build
DISTDIR       = dist
LIBDIR        = ../python/weka/lib

all: clean compile dist

clean:
	@echo cleaning up...
	rm -rf $(BUILDDIR)
	rm -rf $(DISTDIR)
	find -name "*~" -delete

compile:
	@echo compiling source files...
	mkdir -p $(BUILDDIR)
	find $(SRCDIR) -name "*.java" -exec javac -source 1.6 -target 1.6 -classpath $(LIBDIR)/weka.jar -d $(BUILDDIR) {} \;

dist:
	@echo creating jar archive...
	mkdir -p $(DISTDIR)
	jar -cf $(DISTDIR)/python-weka-wrapper.jar -C $(BUILDDIR) weka
	jar -cf $(DISTDIR)/python-weka-wrapper-src.jar -C $(SRCDIR) weka
	cp $(DISTDIR)/python-weka-wrapper.jar $(LIBDIR)
	cp $(DISTDIR)/python-weka-wrapper-src.jar $(LIBDIR)


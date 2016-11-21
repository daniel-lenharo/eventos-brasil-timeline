prefix ?= /usr/local
datadir ?= ${prefix}/share/eventos-brasil-timeline
symlinks ?= 1

all: build

INPUT    := $(wildcard data/*)
OUTPUT   := $(addsuffix .xml,$(subst data/,xml/,$(basename $(INPUT))))
INSHTML  := $(addprefix ${DESTDIR}${datadir}/,$(wildcard *.html))
INSXML   := $(addprefix ${DESTDIR}${datadir}/,$(OUTPUT))
INSMEDIA := $(addprefix ${DESTDIR}${datadir}/,$(wildcard media/debian*) media/timeline_js media/timeline_ajax)

xml/%.xml: data/% data/%/* build.py
	@mkdir -p xml
	python build.py $< >$@

media/timeline_js: /usr/share/javascript/timeline_js
	ln -sf /usr/share/javascript/timeline_js $@

media/timeline_ajax: /usr/share/javascript/timeline_ajax
	ln -sf /usr/share/javascript/timeline_ajax $@

build: $(OUTPUT) media/timeline_js media/timeline_ajax

${DESTDIR}${datadir}:
	install -d ${DESTDIR}${datadir}

${DESTDIR}${datadir}/%.html: %.html ${DESTDIR}${datadir}
	install -m644 -t ${DESTDIR}${datadir} $<

${DESTDIR}${datadir}/xml: ${DESTDIR}${datadir}
	install -d ${DESTDIR}${datadir}/xml

${DESTDIR}${datadir}/xml/%.xml: xml/%.xml ${DESTDIR}${datadir}/xml
	install -m644 -t ${DESTDIR}${datadir}/xml $<

${DESTDIR}${datadir}/media: ${DESTDIR}${datadir}
	install -d ${DESTDIR}${datadir}/media

${DESTDIR}${datadir}/media/%: media/% ${DESTDIR}${datadir}/media
	install -m644 -t ${DESTDIR}${datadir}/media $<

${DESTDIR}${datadir}/media/timeline_%: media/timeline_% ${DESTDIR}${datadir}/media
	rm --force --recursive ${DESTDIR}${datadir}/$<
ifeq (1,${symlinks})
	ln -sf /usr/share/javascript/$(notdir $<) ${DESTDIR}${datadir}/media
else
	cp --dereference --recursive $< ${DESTDIR}${datadir}/media
endif

install: build ${DESTDIR}${datadir} ${INSHTML} ${INSXML} ${INSMEDIA}

uninstall:
	rm -rf ${DESTDIR}${datadir}

clean:
	rm -rf xml media/timeline_*

.PHONY: all build install clean

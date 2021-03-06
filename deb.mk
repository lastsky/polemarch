define DEBIAN_CONTROL
Source: $(NAME)
Section: unknown
Priority: optional
Maintainer: $(VENDOR)
Build-Depends: debhelper (>= 9), python-virtualenv, python-pip, apache2, apache2-dev, python-dev, gcc, libffi-dev, libssl-dev
Standards-Version: 3.9.5
Homepage: <insert the upstream URL, if relevant>
Vcs-Git: git://anonscm.debian.org/collab-maint/polemarch.git
Vcs-Browser: http://anonscm.debian.org/?p=collab-maint/polemarch.git;a=summary

Package: $(NAME)
Architecture: amd64
Depends: $${shlibs:Depends}, $${misc:Depends}, apache2, python-virtualenv, libffi6, libssl-dev, sshpass, libpython2.7
Description: $(SUMMARY)
$(DESCRIPTION)
endef
export DEBIAN_CONTROL

define DEBIAN_COPYRIGHT
Format: http://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: $(NAME)
Source: <url://example.com>

Files: *
Copyright: 2017 VST Consulting
License: ${LICENSE}
 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU Affero Public License for more details.

 You should have received a copy of the GNU Affero Public License
 along with this program.  If not, see <http://www.gnu.org/licenses/>.
endef
export DEBIAN_COPYRIGHT

# paths and executables variables
BUILDROOT = debian/$(NAME)
INSTALLDIR = opt/$(NAME)
define DEBIAN_RULES
#!/usr/bin/make -f
# maximum verbosity during deb build
DH_VERBOSE = 1
export DH_OPTIONS=-v
# targets, that we want to override with no actions
override_dh_auto_test:
	# don't want to test during package build
override_dh_strip:
	# it is broken for some unknown reason
override_dh_link:
	# it is replacing python in virtualenv with system python
override_dh_shlibdeps:
	# it generates dependency which breaks compartibility with newer distros:
	# libssl with exact version 1.0.0
# real install
override_dh_auto_install:
	# create taget directory and clear it in case of some files exist from
	# previous build
	mkdir -p $(BUILDROOT)
	touch $(BUILDROOT)/dummy
	rm -rf $(BUILDROOT)/*
	# install our package with all required python dependencies in virtualenv
	virtualenv --no-site-packages $(BUILDROOT)/$(INSTALLDIR)
	$(BUILDROOT)/$(INSTALLDIR)/bin/pip install $(PIPARGS) -r requirements.txt -r requirements-doc.txt
	$(BUILDROOT)/$(INSTALLDIR)/bin/pip install $(PIPARGS) dist/$(NAME)-$(VER).tar.gz[apache]
	$(BUILDROOT)/$(INSTALLDIR)/bin/pip install $(PIPARGS) -r requirements.txt -r requirements-git.txt
	find $(BUILDROOT)/ -name "RECORD" -exec rm -rf {} \;
	venvctrl-relocate --source=$(BUILDROOT)/$(INSTALLDIR) --destination=/$(INSTALLDIR)
	find $(BUILDROOT)/$(INSTALLDIR)/lib -type f -name "*.c" -print0 | xargs -0 rm -rf
	# system folders which is needed for application to work (lob, lock, etc)
	mkdir -p $(BUILDROOT)/var/log/$(NAME)
	mkdir -p $(BUILDROOT)/var/run/$(NAME)
	mkdir -p $(BUILDROOT)/var/lock/$(NAME)
	mkdir -p $(BUILDROOT)/etc/$(NAME)
	# systemd services
	mkdir -p $(BUILDROOT)/etc/systemd/system/
	cp initbin/*.service $(BUILDROOT)/etc/systemd/system/
	# settings
	cp $(NAME)/main/settings.ini $(BUILDROOT)/etc/$(NAME)/
%:
	dh $$@ 
endef
export DEBIAN_RULES

define DEBIAN_PREINST
#!/bin/bash
# making sure user created
id -u $(USER) &>/dev/null || useradd -M $(USER)
id -g $(USER) &>/dev/null || groupadd $(USER)
endef
export DEBIAN_PREINST

define DEBIAN_POSTINST
#!/bin/bash
# change owner of all dirs
chown -R $(USER):$(USER) /opt/$(NAME)
chown -R $(USER):$(USER) /var/log/$(NAME)
chown -R $(USER):$(USER) /var/run/$(NAME)
chown -R $(USER):$(USER) /var/lock/$(NAME)
# making migration and activate services
sudo -u $(USER) /opt/$(NAME)/bin/polemarchctl migrate > /dev/null 2>&1
sudo -u $(USER) /opt/$(NAME)/bin/polemarchctl webserver \
                                          --setup-only --port=8080 \
                                          --user $(USER) --group $(USER) \
                                          --server-root=/opt/$(NAME)/httpd \
                                          --log-directory=/var/log/$(NAME) \
                                          --access-log \
                                          --pid-file=/var/run/$(NAME)/web.pid \
                                           > /dev/null 2>&1
systemctl enable polemarchweb.service
systemctl enable polemarchworker.service
systemctl daemon-reload
endef
export DEBIAN_POSTINST

define DEBIAN_PRERM
#!/bin/bash
case "$$1" in
  remove)
    # deactivating services
    systemctl disable polemarchweb.service > /dev/null 2>&1
    systemctl disable polemarchworker.service > /dev/null 2>&1
    service polemarchweb stop >/dev/null 2>&1
    service polemarchworker stop >/dev/null 2>&1
  ;;
esac
# cleaning after yourself
rm -r /opt/$(NAME)/lib/python2.7/site-packages/$(NAME)/projects/
rm -rf /opt/$(NAME)/httpd/
endef
export DEBIAN_PRERM

define DEBIAN_POSTRM
#!/bin/bash
# remove whole /opt/polemarch (database included) if purge called
case "$$1" in
  purge)
    rm -rf /opt/$(NAME)
  ;;
esac
endef
export DEBIAN_POSTRM

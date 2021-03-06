
Installation and quick start
============================

Red Hat/CentOS installation
---------------------------

1. Download rpm from official site.

2. Install it with command

   .. sourcecode:: bash

      sudo yum localinstall polemarch-0.0.1-2612.x86_64.rpm.

3. Run services with commands

   .. sourcecode:: bash

      sudo service polemarchweb start
      sudo service polemarchworker start

That's it. Polemarch web panel on 8080 port. Default administrative account is
admin/admin.

Ubuntu/Debian installation
--------------------------

1. Download deb from official site.

2. Install it with command

   .. sourcecode:: bash

      sudo dpkg -i polemarch_0.0.1-1_amd64.deb || sudo apt-get install -f

3. Run services with commands

   .. sourcecode:: bash

      sudo service polemarchweb start
      sudo service polemarchworker start

That's it. Polemarch web panel on 8080 port. Default administrative account is
admin/admin.

Quickstart
----------

After you install Polemarch by instructions above you can use it without any
further configurations. Interface is pretty intuitive and common for any web
application.

Default installation is suitable for most simple and common cases, but
Polemarch is highly configurable system. If you need something more advanced
(scalability, dedicated DB, custom cache, logging or directories) you can
always configure Polemarch like said in :doc:`Configuration manual </config>`.
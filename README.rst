sys11.sensu.stash
=================

Use this module in your sensu environment. It connects to the configured redis-server and listens for new stashes.
If one is detected, sys11.sensu.stash calls the defined notifier.

By default, this notifier send out an email. You can configure the sender and receiver as well.
`sys11.sensu.stash` also ships a `NoopNotifer`, to just print about the stash.

How to run it?
--------------

`sys11.sensu.stash` ships a binary `stashnotifier`. Just start this

.. code-block::
   
   $ stashnotifier

You may want to start it by some kind of init script.


Configuration
-------------

The default configuration file is `/etc/sensu/stash_notifier.cfg`. By default, the sections `DEFAULT`
and `mailnotifier`:

.. code-block::
   
   [DEFAULT]
   # redis_host = localhost
   # redis_port = 6379
   # notifier = mailnotifier
   # logging = /etc/sensu/stash_notifier_logging.cfg

   [mailnotifier]
   from = root@sensu.example.com
   to = admins@sensu.example.com
   uchiwa_url = http://sensu.example.com:3001
   # smtp_host = localhost
   # smtp_port = 25

If `/etc/sensu/stash_notifier_logging.cfg` is not available, `basicConfig` is used.

You need your own notifier?
---------------------------

Write your own package. It must contain an `entry_point`:

.. code-block:: python
   
   entry_points = {
       'sys11.sensu.stash.notifiers': [
           'yournotifier = your.package.notifier:YourNotifier',
       ]
   }

Now, you can use `notifier = yournotifier` in `/etc/sensu/stash_notifier.cfg`.

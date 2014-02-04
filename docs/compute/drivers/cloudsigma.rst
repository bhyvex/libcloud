CloudSigma Compute Driver Documentation
=======================================

`CloudSigma`_ is a pure IaaS provided based in Zurich, Switzerland with
data centers in Zurich, Switzerland, Las Vegas, United States and Washington DC,
United States.

CloudSigma driver supports working with legacy `API v1.0`_ and a new and
actively supported `API v2.0`_. API v1.0 has been deprecated and as such,
you are strongly encouraged to migrate any existing code which uses API v1.0 to
API v2.0.

Instantiating a driver
----------------------

CloudSigma driver constructor takes different arguments with which you tell
it which region to connect to, which api version to use and so on.

Available arguments:

* ``region`` - Which region to connect to. Defaults to ``zrh``. All the
  supported values: ``zrh``, ``lvs``, ``wdc``
* ``api_version`` - Which API version to use. Defaults to ``2.0``. All the
  supported values: ``1.0`` (deprecated), ``2.0``

Examples
--------

1. Connect to zrh region using new API v2.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. literalinclude:: /examples/compute/cloudsigma/connect_to_api_2_0.py
   :language: python

2. Connect to zrh region using deprecated API v1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

As noted above, API 1.0 has been deprecated and you are strongly encouraged to
migrate any code which uses API 1.0 to API 2.0. This example is only included
here for completeness.

.. literalinclude:: /examples/compute/cloudsigma/connect_to_api_1_0.py
   :language: python

3. Listing available sizes, images and drives
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In Libcloud, a :class:`libcloud.compute.base.NodeSize` represents a physical
configuration of a server and a :class:`libcloud.compute.base.NodeImage`
represents an operating system.

To comply with a standard Libcloud API,
:class:`libcloud.compute.base.NodeDriver.list_images` method only returns
available pre-installed library images. Those images can be passed directly
to
:class:`libcloud.compute.drivers.cloudsigma.CloudSigma_2_0_NodeDriver.create_node`
method and used to create a server.

If you want to list all the available images and drives, you should use
:class:`libcloud.compute.drivers.cloudsigma.CloudSigma_2_0_NodeDriver.ex_list_drives`
method.

The example bellow shows how to list all the available sizes, images and
drives.

.. literalinclude:: /examples/compute/cloudsigma/list_sizes_images_drives.py
   :language: python

4. Create a server using a custom node size
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Unlike most of the other cloud providers out there, CloudSigma is not limited
to pre-defined instance sizes and allows you to specify your own custom size
when creating a node.

This means you can totally customize server for your work-load and specify
exactly how much CPU, memory and disk space you want.

To follow Libcloud standard API, CloudSigma driver also exposes some
pre-defined instance sizes through the
:meth:`libcloud.compute.drivers.cloudsigma.CloudSigma_2_0_NodeDriver.list_sizes`
method.

This example shows how to create a node using a custom size.

.. literalinclude:: /examples/compute/cloudsigma/create_server_custom_size.py
   :language: python

Keep in mind that there are some limits in place:

* CPU - 1 GHz to 80GHz
* Memory - 1 GB to 128 GB
* Disk - 1 GB to 8249 GB

You can find exact limits and free capacity for your account's location using
:meth:`libcloud.compute.drivers.cloudsigma.CloudSigma_2_0_NodeDriver.ex_list_capabilities`
method.

5. Associate metadata with a server upon creation
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CloudSigma allows you to associate arbitrary key / value pairs with each
server. This examples shows how to do that upon server creation.

.. literalinclude:: /examples/compute/cloudsigma/create_server_with_metadata.py
   :language: python

6. Add a tag to the server
~~~~~~~~~~~~~~~~~~~~~~~~~~

CloudSigma allows you to ogranize resources such as servers and drivers by
tagging them. This example shows how to do that.

.. literalinclude:: /examples/compute/cloudsigma/tag_server.py
   :language: python

7. Open a VNC tunnel to the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CloudSigma allows you to connect and manage your server using `VNC`_. To
connect to the server using VNC, you can use clients such as ``vinagre`` or
``vncviewer`` on Ubuntu and other Linux distributions.

This example shows how to open a VNC connection to your server and retrieve
a connection URL.

After you have retrieved the URL, you will also need a password which you
specified (or it was auto-generated if you haven't specified it) when creating a
server.

If you can't remember the password, you can use
:meth:`libcloud.compute.drivers.CloudSigma_2_0_NodeDriver.list_nodes` method
and access ``node.extra['vnc_password']`` attribute.

After you are done using VNC, it's recommended to close a tunnel using
:meth:`libcloud.compute.drivers.cloudsigma.CloudSigma_2_0_NodeDriver.ex_close_vnc_tunnel`
method.

.. literalinclude:: /examples/compute/cloudsigma/open_vnc_tunnel.py
   :language: python

8. Attach firewall policy to the server
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CloudSigma allows you to restrict access to your servers by using firewall
policies. This example shows how to attach an existing policy to all your
servers tagged with ``database-server``.

.. literalinclude:: /examples/compute/cloudsigma/attach_firewall_policy.py
   :language: python

9. Starting a server in a different availability group using avoid functionality
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

CloudSigma allows you to specify a list of server UUIDs which to avoid when
starting a server.

This helps make your infrastructure more highly available and is useful when
you want to create a server in a different availability zone than the existing
server.

The example bellow shows how to create a new server in a different availability
zone from all the existing servers.

Keep in mind that `as noted in the CloudSigma documentation
<https://zrh.cloudsigma.com/docs/availability_groups.html#general-notes-on-avoid-functionality>`_,
this functionality uses the best effort mode. This means that the request might
succeed even if the avoid can not be satisfied and the requested resource ends
in the same availability group as an avoid resource.

.. literalinclude:: /examples/compute/cloudsigma/create_node_ex_avoid.py
   :language: python

10. Retrieving the account balance
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example shows how to retrieve the account balance. The method returns a
dictionary with two keys - ``balance`` and ``currency``.

.. literalinclude:: /examples/compute/cloudsigma/get_account_balance.py
   :language: python

API Docs
--------

.. autoclass:: libcloud.compute.drivers.cloudsigma.CloudSigma_2_0_NodeDriver
    :members:

.. autoclass:: libcloud.compute.drivers.cloudsigma.CloudSigmaDrive
    :members:

.. autoclass:: libcloud.compute.drivers.cloudsigma.CloudSigmaTag
    :members:

.. autoclass:: libcloud.compute.drivers.cloudsigma.CloudSigmaSubscription
    :members:

.. autoclass:: libcloud.compute.drivers.cloudsigma.CloudSigmaFirewallPolicy
    :members:

.. autoclass:: libcloud.compute.drivers.cloudsigma.CloudSigmaFirewallPolicyRule
    :members:

.. _`CloudSigma`: http://www.cloudsigma.com/
.. _`API v1.0`: https://www.cloudsigma.com/legacy/cloudsigma-api-1-0/
.. _`API v2.0`: https://zrh.cloudsigma.com/docs/
.. _`VNC`: http://en.wikipedia.org/wiki/Virtual_Network_Computing

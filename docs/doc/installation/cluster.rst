Cluster (HPC)
=============

The procedure for installing Skrypy and its dependencies on a cluster is the same as for a local installation.
Check with the cluster administrator.

   .. |pic1| image:: ../ressources/Skrypy_buttons.png
      :width: 100%
      :alt: (skrypy buttons)

   .. |pic2| image:: ../ressources/arrow.png
      :width: 20px
      :height: 20px
      :alt: (arrow)

Clusters configuration
^^^^^^^^^^^^^^^^^^^^^^^^

   .. |blank4|  image:: ../ressources/blank.png
      :width: 52%
      :alt: (blank)

   .. |pic4| image:: ../ressources/cluster_config.png
      :width: 80%
      :alt: (cluster config)

You can put several clusters in the list. |br|
(Configuration to be done on your PC, not on the cluster)

1. Click on blue button
|pic1| |blank4| |pic2|

2. A window opens:
|pic4|

3. Fill in the fields  

- ``Host name``: login@clusterhost
   ..
- ``Skrypy directory on this cluster``: specifies the path where Skrypy is installed on the cluster
   ..
- ``Workspace on this cluster``: specifies the workspace on the cluster. This allows you to transfer your diagrams to be run on the cluster and can also (optional) be used to transfer your data to be processed.
   ..
- ``Max number of cpus to use``: maximum number of CPUs to use for your multiprocessing mode treatments. 
   ..
- ``X11 forwarding``: Check this box if display returns (image or curves) are expected.
   .. attention::
	Depending on the cluster's graphics management capability, the result is not guaranteed.
- ``Pre-execution command``: This field allows you to enter shell-like instructions to be executed before your diagrams run. Often useful when you need to activate conda first for example. 
   ..

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

4. ``Save As ...`` for a new cluster name  or ``Save`` for modification

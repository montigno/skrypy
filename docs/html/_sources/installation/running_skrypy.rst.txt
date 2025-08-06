Running Skrypy
==============

This page explains how to launch Skrypy locally or on a cluster.

   .. |pic1| image:: ../ressources/Skrypy_buttons.png
      :width: 100%
      :alt: (skrypy buttons)

   .. |pic2| image:: ../ressources/arrow.png
      :width: 20px
      :height: 20px
      :alt: (arrow)

   .. |pic3| image:: ../ressources/order_processes.png
      :width: 60%
      :alt: (order processes)

Local execution
---------------

   .. |blank1|  image:: ../ressources/blank.png
      :width: 39%
      :alt: (blank)
   .. |blank2|  image:: ../ressources/blank.png
      :width: 43%
      :alt: (blank)
   .. |blank3|  image:: ../ressources/blank.png
      :width: 47%
      :alt: (blank)

.. |br| raw:: html

   <br />

.. raw:: html

    <style> .blue {color:#0000ff} </style>

.. role:: blue

1. Standard mode (CTRL+R)
	:blue:`Allows to launch your current diagram sequentially (no multithreading)`

	|pic1| |blank1| |pic2|

2. Multithreading mode (CTRL+T)
	:blue:`Allows to launch your current diagram in multithreading mode. Several different blocks will run in parallel, reducing processing time.`

	|pic1| |blank2| |pic2|

3. Running multiple diagrams (CTRL+M)
	:blue:`Allows you to launch all your open diagrams.`

	|pic1| |blank3| |pic2|

        :blue:`A 'Order of processes' window opens, indicate the order of the diagrams to launch.`

	|pic3|

Execution on a cluster
----------------------

   .. |blank4|  image:: ../ressources/blank.png
      :width: 52%
      :alt: (blank)
   .. |blank5|  image:: ../ressources/blank.png
      :width: 56%
      :alt: (blank)
   .. |blank6|  image:: ../ressources/blank.png
      :width: 60%
      :alt: (blank)

1. Standard mode

|pic1| |blank4| |pic2|

2. Multithreading mode

|pic1| |blank5| |pic2|

3. Running multiple diagrams

|pic1| |blank6| |pic2|

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

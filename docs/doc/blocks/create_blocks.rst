How to create a block
=====================

This page explains how to create a new block in the library.

   .. |pic1| image:: ../ressources/explorer_modules.png
      :width: 30%
      :alt: (skrypy buttons)

   .. |pic2| image:: ../ressources/Blocks_library_sum.png
      :width: 30%
      :alt: (arrow)

   .. |pic3| image:: ../ressources/explorer_modules_pcnn.png
      :width: 30%
      :alt: (order processes)

   .. |pic4| image:: ../ressources/Blocks_library_spat.png
      :width: 30%
      :alt: (order processes cluster)

   .. |pic5| image:: ../ressources/Blocks_library_pcnn.png
      :width: 30%
      :alt: (order processes cluster)

   .. |pic6| image:: ../ressources/block_explain1.jpg
      :width: 60%
      :alt: (skrypy buttons)

   .. |pic7| image:: ../ressources/block_explain2.jpg
      :width: 60%
      :alt: (arrow)

   .. |pic8| image:: ../ressources/explorer_modules_pcnn_options.png
      :width: 30%
      :alt: (arrow)

The source codes
----------------

All blocks in the library are written in Python and are located in the 'root_of_skrypy_venv/skrypy/NodeEditor/modules' folder. |br|

|pic1| ' ' |pic2|

|pic3| ' ' |pic4| ' ' |pic5|

If you open a .py file, you find a list of classes. |br|
A block corresponds to a simple Python class. |br|

|pic6|
|pic7|

The options
-----------

Options are stored in joint yaml files

|pic8|

If you open the .yaml file, you find a list of options with default values. |br|
Options are managed in blocks.

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

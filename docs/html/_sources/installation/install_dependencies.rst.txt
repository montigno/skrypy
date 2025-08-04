How to install dependencies
===========================

`ANTs <https://github.com/ANTsX/ANTs>`__
----

#. Download from the `site <https://github.com/ANTsX/ANTs/releases>`__ (choose according to your OS version)

#. Decompress in a folder (e.g /home/user/Applications/)

#. Edit .bashrc::
	
	#ANTs
	export PATH=/home/user/Applications/ants-2.5.0/bin:$PATH
	export ANTSPATH=/home/user/Applications/ants-2.5.0/bin
________________________________________________________________

`AFNI <https://afni.nimh.nih.gov/>`__
----

#. See `install <https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/index.html>`__

   .. NOTE::

      settings will be automatically generated in .bashrc

________________________________________________________________

`FSL <https://fsl.fmrib.ox.ac.uk/fsl/docs/#/>`__
----

#. See `install <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation>`__

#. Edit .bashrc::

	# FSL Setup
	FSLDIR=~/Applications/fsl
	PATH=${FSLDIR}/share/fsl/bin:${PATH}
	export FSLDIR PATH
	. ${FSLDIR}/etc/fslconf/fsl.sh

________________________________________________________________

`ImageJ <https://imagej.net/ij/>`__
-------

#. Download ImageJ `here <https://imagej.net/ij/download.html>`__ 

#. Unzip and put in a directory (eg /home/user/Applications)

#. Edit .bashrc::

	#ImageJ
	export PATH=/home/user/Applications/ImageJ/

________________________________________________________________

`Matlab engine <https://www.mathworks.com/help/matlab/matlab-engine-for-python.html>`__
-------------

#. For MATLAB < R2022b::

	source root/skrypy_venv/bin/activate
	cd matlabroot/MATLAB/R2021a/extern/engines/python
	python3 setup.py build --build-base ~/Applications/skrypy_venv/build install
	exit

#. For MATLAB >= R2022b::

        source root/skrypy_venv/bin/activate
	export LD_LIBRARY_PATH=<matlabroot>/MATLAB/R2024b/bin/glnxa64/
	python3 -m pip install matlabengine==24.2.2
	exit	

________________________________________________________________

`RS2 <https://github.com/VitoLin21/Rodent-Skull-Stripping>`__
----

Download RS2 `here <https://github.com/VitoLin21/Rodent-Skull-Stripping/archive/refs/heads/main.zip>`__


.. # define a hard line break for HTML
.. |br| raw:: html

   <br />

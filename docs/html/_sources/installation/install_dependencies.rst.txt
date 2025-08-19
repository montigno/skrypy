How to install dependencies
===========================

Environment variables
---------------------
.. important::
   Skrypy needs to point programs to specific versions of dependencies. |br|
   The .bashrc file is in principle sufficient, but it has been found that when processing on a cluster, it does not always load. |br|
   The best solution is to edit the file 'env_parameters.txt' which is located in /home/username/.skrypy/

`ANTs <https://github.com/ANTsX/ANTs>`__
----------------------------------------

#. Download from the `site <https://github.com/ANTsX/ANTs/releases>`__ (choose according to your OS version)

#. Decompress in a folder (e.g /home/user/Applications/)

#. Edit env_parameters.txt and add::
	
	#ANTs
	export PATH=/home/user/Applications/ants-2.5.0/bin:$PATH
	export ANTSPATH=/home/user/Applications/ants-2.5.0/bin

________________________________________________________________

`AFNI <https://afni.nimh.nih.gov/>`__
-------------------------------------

#. See `install <https://afni.nimh.nih.gov/pub/dist/doc/htmldoc/background_install/install_instructs/index.html>`__

   .. NOTE::

      settings will be automatically generated in .bashrc

________________________________________________________________

`FSL <https://fsl.fmrib.ox.ac.uk/fsl/docs/#/>`__
------------------------------------------------

#. See `install <https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FslInstallation>`__

#. Edit env_parameters.txt and add::

	# FSL Setup
	FSLDIR=~/Applications/fsl
	PATH=${FSLDIR}/share/fsl/bin:${PATH}
	export FSLDIR PATH
	. ${FSLDIR}/etc/fslconf/fsl.sh

________________________________________________________________

`ImageJ <https://imagej.net/ij/>`__
-----------------------------------

#. Download ImageJ `here <https://imagej.net/ij/download.html>`__ 

#. Unzip and put in a directory (eg /home/user/Applications)

#. Edit env_parameters.txt and add::

	#ImageJ
	export PATH=/home/user/Applications/ImageJ/

________________________________________________________________

`Matlab engine <https://www.mathworks.com/help/matlab/matlab-engine-for-python.html>`__
---------------------------------------------------------------------------------------

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

`MRTrix3 <https://mrtrix.readthedocs.io/en/latest/installation/build_from_source.html>`__
-----------------------------------------------------------------------------------------

#. Required dependencies::

	sudo apt-get install git g++ python libeigen3-dev zlib1g-dev libqt5opengl5-dev libqt5svg5-dev libgl1-mesa-dev libfftw3-dev libtiff5-dev libpng-dev

#. Choose or create a directory where MRTrix3 will be installed (eg /home/user/Applications):

#. In this directory, type::

	git clone https://github.com/MRtrix3/mrtrix3.git
	cd mrtrix3
	./configure
	./build
	./set_path
	
#. Close the terminal and start another one::

	mrview

   .. NOTE::

      settings will be automatically generated in .bashrc

________________________________________________________________

`RS2 <https://github.com/VitoLin21/Rodent-Skull-Stripping>`__
-------------------------------------------------------------

Download RS2 `here <https://github.com/VitoLin21/Rodent-Skull-Stripping/archive/refs/heads/main.zip>`__

________________________________________________________________

`SPM (requires MATLAB) <https://www.fil.ion.ucl.ac.uk/spm/>`__
--------------------------------------------------------------

#. Download SPM12 `here <https://www.fil.ion.ucl.ac.uk/spm/docs/installation/>`__

#. Uncompress the zip file and put the directory 'SPM12' in the 'toolbox' folder of your Matlab (eg /usr/local/MATLAB/R2024b/toolbox/)

#. In terminal::

	cd /usr/local/MATLAB/R2024b/toolbox/local/
	sudo nano pathdef.m

#. find the line %%% BEGIN ENTRIES %%% and add to the line below: matlabroot,'/toolbox/spm12:', ...::

	%%% BEGIN ENTRIES %%%
	matlabroot,'/toolbox/spm12:', ...

#. Save it

#. Edit env_parameters.txt and add::

	#SPM12
	export SPM_PATH=/usr/local/MATLAB/R2024b/toolbox/spm12/

 

.. # define a hard line break for HTML
.. |br| raw:: html

   <br />


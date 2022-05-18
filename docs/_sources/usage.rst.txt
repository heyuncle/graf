#####
Usage
#####

Installation
============

gräf is available on Windows, MacOS, and Ubuntu.

Windows
-------

To use gräf with windows, you need to first download the zip found `here <https://github.com/heyuncle/graf/archive/refs/heads/main.zip>`_.

Then, you need to install the required programs using pip:

.. code-block:: console

    $ pip install -r requirements.txt

Ubuntu
------

To use gräf with ubuntu, follow these steps:

1. `Download <https://github.com/heyuncle/graf/archive/refs/heads/main.zip>`_ the ZIP file and extract to target location.
2. Run:
   
   .. code-block:: console
   
    sudo apt-get install python3 python3-pip PyQt5

3. Install the pip packages with:
   
   .. code-block:: console

    pip install latex2sympy2 PyQt5 QDarkStyle requests sympy

4. Install Manim:
   
   .. code-block:: console

    sudo apt update sudo apt install libcairo2-dev libpango1.0-dev ffmpeg 

   .. code-block:: console

    pip3 install manim

5. Install the GStreamer plugins with:
   
   .. code-block:: console

    sudo apt install ubuntu-restricted-extras

Running the program
===================

Execute the ``manim.pyw`` file.
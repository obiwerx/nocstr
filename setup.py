##############################################################################
##        NOCSTR: NetOps Automation (Formerly Operation: MOTORHEAD)         ##
##       Written in Python, Flask, HTML, CSS, JavaScript, and BootStrap     ##
##                                                                          ##
## module: nostr.py     Version: 0.91 ALPHA     Purpose: NetOps Automation  ##
## Author: Tim O'Brien  Team: Network Team A    Date: 06/30/2017            ##
##############################################################################

###########################################################################
######                     ALL OF THE IMPORTS!                        #####
###########################################################################
from setuptools import setup

###########################################################################
######                      SETUP SCRIPT                              #####
###########################################################################
setup(
    name='nocstr',
    packages=['nocstr'],
    include_package_data=True,
    install_requires=['flask',]
)

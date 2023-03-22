#!/usr/bin/env python3
import os
import sys
import argparse
from argparse import RawTextHelpFormatter

from mpet.version import __version__
import mpet.main as main

import time
from itertools import count
from multiprocessing import Process

desc="""MPET - Multiphase Porous Electrode Theory
This software is designed to run simulations of batteries with porous electrodes
using porous electrode theory, which is a volume-averaged, multiscale approach
to capture the coupled behavior of electrolyte and active material within
electrodes.

If you use this software in academic work, please cite the relevant references
detailing its development as presented in the LICENSE file.

See also: https://bitbucket.org/bazantgroup/mpet"""

parser = argparse.ArgumentParser(description=desc, formatter_class=RawTextHelpFormatter)
parser.add_argument('timeout', help='MPET timeout')
parser.add_argument('folder', help='MPET system output dir')
parser.add_argument('file', help='MPET system configuration file')
parser.add_argument('-v','--version', action='version',
                    version='%(prog)s '+__version__)
#args = parser.parse_args()
arg1=os.path.join('configs','params_system_A123LFP_optimalcontrol.cfg')
arg2='simout'
arg3='500000000'
try:
    if __name__ == '__main__':

        counter = count(0)    
        p = Process(target=main.main, args=(arg1,arg2), name='MPET')
        p.start()
        p.join(timeout=float(arg3))
        p.terminate()
    

    #main.main(arg1,arg2)
except IndexError:
    print("ERROR: No parameter file specified. Aborting")
    raise

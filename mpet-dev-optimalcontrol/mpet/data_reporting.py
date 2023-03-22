"""Helper functions/classes for outputting data generated by the simulation."""
import numpy as np
import re
import os
import sys
import time
import h5py
import scipy.io as sio

import daetools.pyDAE as dae
from daetools.pyDAE.data_reporters import daeMatlabMATFileDataReporter


class Myhdf5DataReporterFast(daeMatlabMATFileDataReporter):
    """Ignores internal particle concentrations with hdf5 data saving to be faster.
    Input is dataReporter"""

    def WriteDataToFile(self):
        mdict = {}
        # 0 if single simulation, 1 if continued simulation
        continued_sim = 0
        # if we are in a directory that has continued simulations (maccor reader)
        if os.path.isfile(self.ConnectionString + ".hdf5"):
            if os.stat(self.ConnectionString + ".hdf5").st_size != 0:
                continued_sim = 1
                # remains 0 if not continued sim
        with h5py.File(self.ConnectionString + ".hdf5", 'a') as mat_dat:
            for var in self.Process.Variables:
                # Remove the model name part of the output key for
                # brevity.
                dkeybase = var.Name[var.Name.index(".")+1:]
                # Remove dots from variable keys. This enables the mat
                # file to be read by, e.g., MATLAB.
                dkeybase = dkeybase.replace(".", "_")
                # Remove port variables
                if "port" not in dkeybase:
                    mdict[dkeybase] = var.Values  # mdict stores the new data
                    # if we are in a directory that has continued simulations (maccor reader)
                    if continued_sim == 1:
                        # increment time by the previous end time of the last simulation
                        tend = mat_dat['phi_applied_times'][-1]

                        # if particle concentrations, remove and overwrite, but not if its cbar
                        if (re.match("partTrode.vol.part._c", dkeybase) is None) or \
                                (re.search("cbar", dkeybase) is not None):
                            # resize and append dkeybase variable
                            mat_dat[dkeybase].resize(
                                (mat_dat[dkeybase].shape[0] + mdict[dkeybase].shape[0]), axis=0)
                            mat_dat[dkeybase][-mdict[dkeybase].shape[0]:] = mdict[dkeybase]

                            if dkeybase == 'phi_applied':
                                mdict['times'] = var.TimeValues + tend
                                # resize and append dkeybase varibale
                                mat_dat['phi_applied_times'].resize(
                                    (mat_dat['phi_applied_times'].shape[0]
                                     + mdict['times'].shape[0]), axis=0)
                                mat_dat['phi_applied_times'][-mdict['times'].shape[0]:] = \
                                    mdict['times']

                        else:
                            # overwrite the old file
                            del mat_dat[dkeybase]
                            mat_dat.create_dataset(
                                dkeybase, data=mdict[dkeybase][-2:,:], compression='lzf')

                    else:  # (continued_sim == 1)
                        # if cwe are not in a continuation directory
                        # if particle concentrations, remove and overwrite, but not if its cbar
                        if (re.match("partTrode.vol.part._c", dkeybase) is None) or \
                                (re.search("cbar", dkeybase) is not None):
                            # create dataset if continued_sim == 0
                            # maxshape is set dpeending on whether its a 2D array or a 1D array
                            shape = len(mdict[dkeybase].shape)
                            mat_dat.create_dataset(dkeybase, data=mdict[dkeybase],
                                                   maxshape=(None,)*shape, compression='lzf')

                            if dkeybase == 'phi_applied':
                                # only save times for voltage
                                mdict['times'] = var.TimeValues
                                mat_dat.create_dataset('phi_applied_times', data=mdict['times'],
                                                       maxshape=(None,), compression='lzf')

                        else:
                            # only save the last two points
                            shape = len(mdict[dkeybase].shape)
                            mat_dat.create_dataset(dkeybase, data=mdict[dkeybase][-2:],
                                                   maxshape=(None,)*shape, compression='lzf')


class Myhdf5DataReporter(daeMatlabMATFileDataReporter):
    """Reports hdf5 file outputs in full, otherwise ignores internal particle concentrations"""

    def WriteDataToFile(self):
        mdict = {}
        # 0 if single simulaiton, 1 if continued simulation
        continued_sim = 0
        # if we are in a directory that has continued simulations (maccor reader)
        if os.path.isfile(self.ConnectionString + ".hdf5"):
            if os.stat(self.ConnectionString + ".hdf5").st_size != 0:
                continued_sim = 1
                # remains 0 if not continued sim
        with h5py.File(self.ConnectionString + ".hdf5", 'a') as mat_dat:
            for var in self.Process.Variables:
                # Remove the model name part of the output key for
                # brevity.
                dkeybase = var.Name[var.Name.index(".")+1:]
                # Remove dots from variable keys. This enables the mat
                # file to be read by, e.g., MATLAB.
                dkeybase = dkeybase.replace(".", "_")
                # remove port variables
                if "port" not in dkeybase:
                    mdict[dkeybase] = var.Values
                    # if we are in a directory that has continued simulations (maccor reader)
                    if continued_sim == 1:
                        # increment time by the previous end time of the last simulation
                        tend = mat_dat['phi_applied_times'][-1]

                        mat_dat[dkeybase].resize(
                            (mat_dat[dkeybase].shape[0] + mdict[dkeybase].shape[0]), axis=0)
                        mat_dat[dkeybase][-mdict[dkeybase].shape[0]:] = mdict[dkeybase]

                        if dkeybase == 'phi_applied':
                            mdict['times'] = var.TimeValues + tend
                            # resize and append dkeybase varibale
                            mat_dat['phi_applied_times'].resize(
                                (mat_dat['phi_applied_times'].shape[0]
                                 + mdict['times'].shape[0]), axis=0)
                            mat_dat['phi_applied_times'][-mdict['times'].shape[0]:] \
                                = mdict['times']

                    else:  # (continued_sim == 0)
                        # create dataset if continued_sim == 0
                        # maxshape is set dpeending on whether its a 2D array or a 1D array
                        shape = len(mdict[dkeybase].shape)
                        mat_dat.create_dataset(dkeybase, data=mdict[dkeybase],
                                               maxshape=(None,)*shape, compression='lzf')

                        if dkeybase == 'phi_applied':
                            # only save times for voltage
                            mdict['times'] = var.TimeValues
                            mat_dat.create_dataset('phi_applied_times', data=mdict['times'],
                                                   maxshape=(None,), compression='lzf')


class MyMATDataReporter(daeMatlabMATFileDataReporter):
    """See source code for pyDataReporting.daeMatlabMATFileDataReporter
    Takes in dataReporter"""
    
    def WriteDataToFile(self):

        mdict = {}
        # 0 if single simulaiton, 1 if continued simulation
        continued_sim = 0
        # set an empty mat_dat
        mat_dat = {}
        # if we are in a directory that has continued simulations (maccor reader)
        if os.path.isfile(self.ConnectionString + ".mat"):
            if os.stat(self.ConnectionString + ".mat").st_size != 0:
                continued_sim = 1
                mat_dat = sio.loadmat(self.ConnectionString + ".mat")
                # remains 0 if not continued sim
        for var in self.Process.Variables:
            # Remove the model name part of the output key for
            # brevity.
            dkeybase = var.Name[var.Name.index(".")+1:]
            # Remove dots from variable keys. This enables the mat
            # file to be read by, e.g., MATLAB.
            dkeybase = dkeybase.replace(".", "_")
            # Remove port variables
            if "port" not in dkeybase:
                if continued_sim == 0:
                    mdict[dkeybase] = var.Values
                    if dkeybase == 'phi_applied':
                        # if we are not in a continuation directory
                        mdict[dkeybase + '_times'] = var.TimeValues
                else:
                    # if we are in a directory that has continued simulations (maccor reader)
                    # increment time by the previous end time of the last simulation
                    tend = mat_dat['phi_applied_times'][0, -1]
                    # get previous values from old output_mat
                    if dkeybase == 'phi_applied':

                        mdict[dkeybase + '_times'] = (var.TimeValues + tend).T
                        mdict[dkeybase + '_times'] = np.append(mat_dat[dkeybase + '_times'],
                                                               mdict[dkeybase + '_times'])
                    # may flatten array, so we specify axis
                    if mat_dat[dkeybase].shape[0] == 1:
                        mat_dat[dkeybase] = mat_dat[dkeybase].T
                        mdict[dkeybase] = mdict[dkeybase].reshape(-1, 1)
                    # data output does weird arrays where its (n, 2) but (1, n) if only one row
                    if mdict[dkeybase].ndim == 1:
                        mdict[dkeybase] = mdict[dkeybase].reshape(-1, 1)
                    mdict[dkeybase] = np.append(mat_dat[dkeybase], mdict[dkeybase], axis=0)
                    # flip axes to be consistent with plotting if shape is not (x,1)
                    if mdict[dkeybase].shape[1] == 1:
                        mdict[dkeybase] = np.squeeze(mdict[dkeybase])

        sio.savemat(self.ConnectionString + ".mat",
                    mdict, appendmat=False, format='5',
                    long_field_names=False, do_compression=False,
                    oned_as='row')


def setup_data_reporters(simulation, config, outdir):
    """Create daeDelegateDataReporter and add data reporter."""
    datareporter = dae.daeDelegateDataReporter()
    # if default, use mat data reporter
    simulation.dr = MyMATDataReporter()
    # else if specified, we use hdf5 data reporter
    if config["dataReporter"] == "hdf5":
        simulation.dr = Myhdf5DataReporter()
    elif config["dataReporter"] == "hdf5Fast":
        simulation.dr = Myhdf5DataReporterFast()
    elif config["dataReporter"] != "mat":
        # if the data reporter called hasn't been implemented yet
        raise Exception("Data Reporter " + config["dataReporter"] + " not installed")

    datareporter.AddDataReporter(simulation.dr)
    # Connect data reporters
    simName = simulation.m.Name + time.strftime(" [%d.%m.%Y %H:%M:%S]",
                                                time.localtime())
    # we name it another name so it doesn't overwrite our output data file
    matDataName = "output_data"
    matfilename = os.path.join(outdir, matDataName)
    if not simulation.dr.Connect(matfilename, simName):
        sys.exit()
    # a hack to make compatible with pre/post r526 daetools
    try:
        simulation.dr.ConnectionString = simulation.dr.ConnectString
    except AttributeError:
        pass
    return datareporter

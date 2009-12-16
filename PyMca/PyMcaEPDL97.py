#/*##########################################################################
# Copyright (C) 2004-2009 European Synchrotron Radiation Facility
#
# This file is part of the PyMCA X-ray Fluorescence Toolkit developed at
# the ESRF by the Beamline Instrumentation Software Support (BLISS) group.
#
# This toolkit is free software; you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option) 
# any later version.
#
# PyMCA is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# PyMCA; if not, write to the Free Software Foundation, Inc., 59 Temple Place,
# Suite 330, Boston, MA 02111-1307, USA.
#
# PyMCA follows the dual licensing model of Trolltech's Qt and Riverbank's PyQt
# and cannot be used as a free plugin for a non-free program. 
#
# Please contact the ESRF industrial unit (industry@esrf.fr) if this license 
# is a problem for you.
#############################################################################*/
__doc__= "Interface to the PyMca EPDL97 description" 
import os
import sys
try:
    from PyMca import specfile
except ImportError:
    print "Importing specfile from local directory"
    import specfile
import numpy
#import copy
log = numpy.log
exp = numpy.exp
ElementList = ['H', 'He', 
            'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
            'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar',
            'K', 'Ca', 'Sc', 'Ti', 'V', 'Cr', 'Mn', 'Fe',
            'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se',
            'Br', 'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo',
            'Tc', 'Ru', 'Rh', 'Pd', 'Ag', 'Cd', 'In', 'Sn',
            'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce',
            'Pr', 'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 
            'Ho', 'Er', 'Tm', 'Yb', 'Lu', 'Hf', 'Ta', 'W', 
            'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 
            'Bi', 'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 
            'Pa', 'U', 'Np', 'Pu', 'Am', 'Cm', 'Bk', 'Cf', 
            'Es', 'Fm', 'Md', 'No', 'Lr', 'Rf', 'Db', 'Sg', 
            'Bh', 'Hs', 'Mt']

dirmod = os.path.dirname(__file__)
EPDL97_FILE = os.path.join(dirmod,"EPDL97_CrossSections.dat")
if os.path.exists(EPDL97_FILE):
    pass
else:
    #freeze does bad things with the path ...
    EPDL97_FILE = os.path.join(os.path.dirname(dirmod),
                               os.path.basename(EPDL97_FILE))
    if not os.path.exists(EPDL97_FILE):
        raise IOError, "Cannot find the EPDL97 specfile"

EADL97_FILE = os.path.join(dirmod,"EADL97_BindingEnergies.dat")
if os.path.exists(EADL97_FILE):
    pass
else:
    #freeze does bad things with the path ...
    EADL97_FILE = os.path.join(os.path.dirname(dirmod),
                               os.path.basename(EADL97_FILE))
    if not os.path.exists(EADL97_FILE):
        raise IOError, "Cannot find the EADL97 specfile"


EPDL97_DICT = {}
for element in ElementList:
    EPDL97_DICT[element] = {}

#initialize the dictionnary, for the time being compatible with PyMca 4.3.0
EPDL97_DICT = {}
for element in ElementList:
    EPDL97_DICT[element] = {}
    EPDL97_DICT[element]['binding'] = {}
    EPDL97_DICT[element]['EPDL97']  = {}
    EPDL97_DICT[element]['original'] = True

#fill the dictionnary with the binding energies
def _initializeBindingEnergies():
    #read the specfile data
    sf = specfile.Specfile(EADL97_FILE)
    scan = sf[0]
    labels = scan.alllabels()
    data = scan.data()
    scan = None
    sf = None
    i = -1
    for element in ElementList:
        if element == 'Md':
            break
        i += 1
        EPDL97_DICT[element]['binding'] = {}
        for j in range(len(labels)):
            if j == 0:
                #this is the atomic number
                continue
            label = labels[j].replace(" ","").split("(")[0]
            EPDL97_DICT[element]['binding'][label] = data[j, i]

_initializeBindingEnergies()

def setElementBindingEnergies(element, ddict):
    """
    Allows replacement of the element internal binding energies by a different
    set of energies. This is made to force this implementaticon of EPDL97 to
    respect other programs absorption edges. Data will be extrapolated when
    needed. WARNING: Coherent resonances are not replaced.
    """
    if len(EPDL97_DICT[element]['EPDL97'].keys()) < 2:
        _initializeElement(element)
    EPDL97_DICT[element]['original'] = False
    EPDL97_DICT[element]['binding']={}
    if ddict.has_key('binding'):
        EPDL97_DICT[element]['binding'].update(ddict['binding'])
    else:
        EPDL97_DICT[element]['binding'].update(ddict)

def _initializeElement(element):
    """
    _initializeElement(element)
    Supposed to be of internal use.
    Reads the file and loads all the relevant element information contained
    int the EPDL97 file into the internal dictionnary.
    """
    #read the specfile data
    sf = specfile.Specfile(EPDL97_FILE)
    scan = sf[ElementList.index(element)]
    labels = scan.alllabels()
    data = scan.data()
    scan = None

    #fill the information into the dictionnary
    i = -1
    for label0 in labels:
        i += 1
        label = label0.lower()
        #translate the label to the PyMca keys
        if ('coherent' in label) and ('incoherent' not in label):
            EPDL97_DICT[element]['EPDL97']['coherent'] = data[i, :]
            EPDL97_DICT[element]['EPDL97']['coherent'].shape = -1
            continue
        if ('incoherent' in label) and ('plus' not in label):
            EPDL97_DICT[element]['EPDL97']['compton'] = data[i, :]
            EPDL97_DICT[element]['EPDL97']['compton'].shape = -1
            continue
        label = label.replace(" ","").split("(")[0]
        if 'energy' in label:
            EPDL97_DICT[element]['EPDL97']['energy'] = data[i, :]
            EPDL97_DICT[element]['EPDL97']['energy'].shape = -1
            continue
        if 'photoelectric' in label:
            EPDL97_DICT[element]['EPDL97']['photo'] = data[i, :]
            EPDL97_DICT[element]['EPDL97']['photo'].shape = -1
            #a reference should not be expensive ...
            EPDL97_DICT[element]['EPDL97']['photoelectric'] =\
                                EPDL97_DICT[element]['EPDL97']['photo']
            continue
        if 'total' in label:
            EPDL97_DICT[element]['EPDL97']['total'] = data[i, :]
            EPDL97_DICT[element]['EPDL97']['total'].shape = -1
            continue
        if label[0].upper() in ['K', 'L', 'M']:
            #for the time being I do not use the other shells in PyMca
            EPDL97_DICT[element]['EPDL97'][label.upper()] = data[i, :]
            EPDL97_DICT[element]['EPDL97'][label.upper()].shape = -1
            continue
    EPDL97_DICT[element]['EPDL97']['pair'] = 0.0 * EPDL97_DICT[element]['EPDL97']['energy']
    EPDL97_DICT[element]['EPDL97']['total'] =\
            EPDL97_DICT[element]['EPDL97']['coherent']+\
            EPDL97_DICT[element]['EPDL97']['compton']+\
            EPDL97_DICT[element]['EPDL97']['pair']+\
            EPDL97_DICT[element]['EPDL97']['photo']
    EPDL97_DICT[element]['EPDL97']['all other']=1 *\
            EPDL97_DICT[element]['EPDL97']['photo']
    atomic_shells = ['K', 'L1', 'L2', 'L3', 'M1', 'M2', 'M3', 'M4', 'M5']
    for key in atomic_shells:
        EPDL97_DICT[element]['EPDL97']['all other']-=\
                EPDL97_DICT[element]['EPDL97'][key]

def getElementCrossSections(element, energy=None, forced_shells=None):
    """
    getCrossSections(element, energy, excited_shells=None)
    Returns total and partial cross sections of element at the specified
    energies. If excited_shells are not specified, it uses the internal
    binding energies of EPDL97 for all shells. If excited_shells is specified,
    it enforces excitation of the relevant shells via log-log extrapolation
    if needed.
    """
    if forced_shells is None:
        forced_shells = []
    if element not in ElementList:
        raise ValueError, "Invalid chemical symbol %s" % element
    if len(EPDL97_DICT[element]['EPDL97'].keys()) < 2:
        _initializeElement(element)

    if energy is None and EPDL97_DICT[element]['original']:
        return EPDL97_DICT[element]['EPDL97']
    elif energy is None:
        energy = EPDL97_DICT[element]['EPDL97']['energy']

    if type(energy) in [type(1), type(1.0)]:
        energy = numpy.array([energy])

    binding = EPDL97_DICT[element]['binding']
    wdata = EPDL97_DICT[element]['EPDL97']
    ddict = {}
    ddict['energy']     = energy
    ddict['coherent']   = 0.0 * energy
    ddict['compton']    = 0.0 * energy
    ddict['photo']      = 0.0 * energy
    ddict['pair']       = 0.0 * energy
    ddict['all other']  = 0.0 * energy
    ddict['total']      = 0.0 * energy
    atomic_shells = ['K', 'L1', 'L2', 'L3', 'M1', 'M2', 'M3', 'M4', 'M5']
    for key in atomic_shells:
        ddict[key] = 0.0 * energy

    #find interpolation point
    for i in range(len(energy)):
        x = energy[i]
        if x > wdata['energy'][-2]:
            #take last value or extrapolate?
            print "Warning: Extrapolating data at the end"
            j1 = len(wdata['energy']) - 1 
            j0 = j1 - 1
        elif x < wdata['energy'][0]:
            #take first value or extrapolate?
            print "Warning: Extrapolating data at the beginning"
            j1 = 1 
            j0 = 0
        else:
            j0 = numpy.max(numpy.nonzero(wdata['energy'] <= x), axis=1)
            j1 = j0 + 1
        x0 = wdata['energy'][j0]
        x1 = wdata['energy'][j1]

        #coherent and incoherent
        for key in ['coherent', 'compton', 'all other']:
            y0 = wdata[key][j0]
            y1 = wdata[key][j1]
            #if key == 'all other':
            #    print "energy = ", x
            #    print "x0 = ", x0
            #    print "x1 = ", x1
            #    print 1, y0
            #    print 2, y1
            ddict[key][i] = exp((log(y0) * log(x1/x) +\
                                 log(y1) * log(x/x0))/log(x1/x0))

        #partial cross sections
        for key in atomic_shells:
            y0 = wdata[key][j0]
            if (y0 > 0.0) and (x >= binding[key]):
                #standard way
                y1 = wdata[key][j1]
                ddict[key][i] = exp((log(y0) * log(x1/x) +\
                                 log(y1) * log(x/x0))/log(x1/x0))
            elif (forced_shells == []) and (x < binding[key]):
                continue
            elif (key in forced_shells) or (x >= binding[key]):
                l = numpy.nonzero(wdata[key] > 0.0)
                if not len(l[0]):
                    continue
                j00 = numpy.min(l)
                j01 = j00 + 1
                x00 = wdata['energy'][j00]
                x01 = wdata['energy'][j01]
                y0 = wdata[key][j00]
                y1 = wdata[key][j01]
                ddict[key][i] = exp((log(y0) * log(x01/x) +\
                                 log(y1) * log(x/x00))/log(x01/x00))
                                    
        for key in ['all other'] + atomic_shells:            
            ddict['photo'][i] += ddict[key][i]

        for key in ['coherent', 'compton', 'photo']:
            ddict['total'][i] += ddict[key][i]
    return ddict        
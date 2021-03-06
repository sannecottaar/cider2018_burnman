# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences
# Copyright (C) 2012 - 2017 by the BurnMan team, released under the GNU
# GPL v2 or later.


# This is a standalone program that converts the Holland and Powell data format into the standard burnman format (printed to stdout)
# It only outputs properties of solid endmembers - other endmembers are
# currently ignored.


import sys
import os.path

if os.path.isfile('tc-ds62.txt') == False:
    print('This code requires the data file tc-ds62.txt.')
    print(
        'This file is bundled with the software package THERMOCALC, which can be found here:')
    print(
        'http://www.metamorph.geo.uni-mainz.de/thermocalc/dataset6/index.html')
    print('')
    print('Please download the file and place it in this directory.')
    exit()

# Components
components = ['Si', 'Ti', 'Al', 'Fe', 'Mg', 'Mn', 'Ca', 'Na',
              'K', 'O', 'H', 'C', 'Cl', 'e-', 'Ni', 'Zr', 'S', 'Cu', 'Cr']


class Endmember:

    def __init__(self, name, atoms, formula, sites, comp, H, S, V, Cp, a, k, flag, od):
        self.name = name  # Name of end member
        self.atoms = atoms  # Number of atoms in the unit formula
        self.formula = formula
        self.sites = sites  # Notional number of sites
        self.comp = comp  # Composition
        self.H = H  # Enthalpy
        self.S = S  # Entropy
        self.V = V  # Volume
        self.Cp = Cp  # Heat capacity (c0 + c1*T + c2*T**2 + c3*T**(-0.5))
        self.a = a  # Thermal expansion
        self.k = k  # Bulk Modulus (and first two derivatives wrt pressure)
        self.flag = flag
        self.od = od


def read_dataset(datafile):
    f = open(datafile, 'r')
    ds = []
    for line in f:
        ds.append(line.split())
    return ds

ds = read_dataset('tc-ds62.txt')


def getmbr(ds, mbr):
    mbrarray = []
    for i in range(0, int(ds[0][0])):
        if ds[i * 4 + 3][0] == mbr:
            atoms = 0.0
            formula = ''
            for j in range(3, len(ds[i * 4 + 3]) - 1, 2):
                atoms += float(ds[i * 4 + 3][j])
                formula = formula + \
                    components[int(ds[i * 4 + 3][j - 1]) - 1] + str(
                        round(float(ds[i * 4 + 3][j]), 10))
            if mbr.endswith('L'):
                flag = -2
                od = [0]
            else:
                flag = int(ds[i * 4 + 6][4])
            endmember = Endmember(mbr, atoms, formula, int(ds[i * 4 + 3][1]), list(map(float, ds[i * 4 + 3][2:(len(ds[i * 4 + 3]) - 1)])), float(ds[i * 4 + 4][0]), float(
                ds[i * 4 + 4][1]), float(ds[i * 4 + 4][2]), map(float, ds[i * 4 + 5]), float(ds[i * 4 + 6][0]), list(map(float, ds[i * 4 + 6][1:4])), flag, list(map(float, ds[i * 4 + 6][5:])))
            return endmember

print '# This file is part of BurnMan - a thermoelastic and thermodynamic toolkit for the Earth and Planetary Sciences'
print '# Copyright (C) 2012 - 2017 by the BurnMan team, released under the GNU GPL v2 or later.'
print ''
print ''
print '"""'
print 'HP_2011 (ds-62)'
print 'Minerals from Holland and Powell 2011 and references therein'
print 'Update to dataset version 6.2'
print 'The values in this document are all in S.I. units,'
print 'unlike those in the original tc-ds62.txt'
print 'File autogenerated using HPdata_to_burnman.py'
print '"""'
print ''
print 'from ..mineral import Mineral'
print 'from ..solidsolution import SolidSolution'
print 'from ..solutionmodel import *'
print 'from ..processchemistry import dictionarize_formula, formula_mass'
print ''

solutionfile = 'tc-ds62_solutions.txt'
with open(solutionfile, 'r') as fin:
    print fin.read()
fin.close()

print '"""'
print 'ENDMEMBERS'
print '"""'
print ''
formula = '0'
for i in range(int(ds[0][0])):
    mbr = ds[i * 4 + 3][0]
    M = getmbr(ds, mbr)
    if mbr == 'and':  # change silly abbreviation
        mbr = 'andalusite'
    if M.flag != -1 and M.flag != -2 and M.k[0] > 0:
        print 'class', mbr, '(Mineral):'
        print '    def __init__(self):'
        print ''.join(['        formula=\'', M.formula, '\''])
        print '        formula = dictionarize_formula(formula)'
        print '        self.params = {'
        print ''.join(['            \'name\': \'', M.name, '\','])
        print '            \'formula\': formula,'
        print '            \'equation_of_state\': \'hp_tmt\','
        print '            \'H_0\':', M.H * 1e3, ','
        print '            \'S_0\':', M.S * 1e3, ','
        print '            \'V_0\':', M.V * 1e-5, ','
        print '            \'Cp\':', [round(M.Cp[0] * 1e3, 10), round(M.Cp[1] * 1e3, 10), round(M.Cp[2] * 1e3, 10), round(M.Cp[3] * 1e3, 10)], ','
        print '            \'a_0\':', M.a, ','
        print '            \'K_0\':', M.k[0] * 1e8, ','
        print '            \'Kprime_0\':', M.k[1], ','
        print '            \'Kdprime_0\':', M.k[2] * 1e-8, ','
        print '            \'n\': sum(formula.values()),'
        print '            \'molar_mass\': formula_mass(formula)}'
        if M.flag != 0:
            print '        self.property_modifiers = [['
        if M.flag == 1:
            print '            \'landau_hp\', {\'P_0\':', 1.e5, ','
            print '                          \'T_0\':', 298.15, ','
            print '                          \'Tc_0\':', M.od[0], ','
            print '                          \'S_D\':', M.od[1] * 1e3, ','
            print '                          \'V_D\':', M.od[2] * 1e-5, '}]]'
        if M.flag == 2:
            print '            \'bragg_williams\', {\'deltaH\':', M.od[0] * 1e3, ','
            print '                               \'deltaV\':', M.od[1] * 1e-5, ','
            print '                               \'Wh\':', M.od[2] * 1e3, ','
            print '                               \'Wv\':', M.od[3] * 1e-5, ','
            print '                               \'n\':', M.od[4], ','
            print '                               \'factor\':', M.od[5], '}]]'
        print '        Mineral.__init__(self)'
        print ''
print ''

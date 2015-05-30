# this is a class of chemistry 
# it can be used to deal with infomation of atoms and molecules
import visual
import os

import numpy as np
import copy

# constants
elementDict={1:'H', 2:'He', 6:'C', 7:'N', 8:'O',
'1':'H', '2':'He', '6':'C', '7':'N', '8':'O'
}

eleWeightDict={'H': 1.008, 'He': 4.0026, 'C': 12.011, 'O': 15.999, 'N': 14.007}

eleColorDict={'H': visual.color.white, 'He': visual.color.cyan, 'C': visual.color.yellow, 'O': visual.color.red, 'N': visual.color.green}

# gaussian default bond length threshold parameters
# bondDisDict={
# 'H': {'H': [0.6350], 'C': [1.1342], 'O': [1.01760]},
# 'C': {'H': [1.1342], 'C': [1.24740, 1.3860, 1.4475, 1.6324], 'O': [1.15829, 1.287, 1.34419, 1.5158]},
# 'O': {'H': [1.01760], 'C': [1.15829, 1.287, 1.34419, 1.5158], 'O': [1.0692, 1.18800, 1.2408, 1.39919]}
# }

# self-defined parameters
# version 1.0 used for ROO->QOOH (best)
# bondDisDict={
# 'H': {'H': [0.6350], 'C': [1.5], 'O': [1.5]},
# 'C': {'H': [1.5], 'C': [1.24740, 1.3860, 1.4475, 1.6324], 'O': [1.15829, 1.287, 1.34419, 1.5158]},
# 'O': {'H': [1.5], 'C': [1.15829, 1.287, 1.34419, 1.5158], 'O': [1.0692, 1.18800, 1.2408, 1.5]}
# }

# version 1.1 used for RO2->QOOH and QOOH->cyclic ether + OH (best)
bondDisDict={
'H': {'H': [0.6350], 'C': [1.5], 'O': [1.5]},
'C': {'H': [1.5], 'C': [1.24740, 1.3860, 1.4475, 1.6324], 'O': [1.15829, 1.287, 1.34419, 2.16]},
'O': {'H': [1.5], 'C': [1.15829, 1.287, 1.34419, 2.16], 'O': [1.0692, 1.18800, 1.2408, 1.9]}
}

bondOrderDict={
'H': {'H': [1.0], 'C': [1.0], 'O': [1.0]},
'C': {'H': [1.0], 'C': [3.0, 2.0, 1.5, 1.0], 'O': [3.0, 2.0, 1.5, 1.0]},
'O': {'H': [1.0], 'C': [3.0, 2.0, 1.5, 1.0], 'O': [3.0, 2.0, 1.5, 1.0]}
}


# units:
# P: atm
# T: K
class reactionSystem:
	freqScaleFactor = 1.0
	reactions = []
	bathGas = []
	PTpairs = []

	_hinderedRotation = True

	def __init__(self):
		self.freqScaleFactor = 1.0
		self.reactions = []
		self.bathGas = []
		self.PTpairs = []

	def setFreqScale(self, freqScaleFactor):
		self.freqScaleFactor = freqScaleFactor

	def setPTpairs(self, PTpairs):
		self.PTpairs = PTpairs

	def addReaction(self, reaction):
		self.reactions.append(reaction)

	def addBathGas(self, bathGas):
		self.bathGas.append(bathGas)

	def addPTpair(self, PTpair):
		self.PTpairs.append(PTpair)

	def addPTpairs(self, PTpairs):
		self.PTpairs.extend(PTpairs)

	def hinderedRotationCorrection(self, HR):
		self._hinderedRotation = HR

class reaction:
	reactants = []
	TSs = []
	products = []

	def __init__(self, input_Rs, input_TSs, input_Ps):
		# self.reactants = copy.deepcopy(input_Rs)
		# self.TSs = copy.deepcopy(input_TSs)
		# self.products = copy.deepcopy(input_Ps)
		self.reactants = input_Rs
		self.TSs = input_TSs
		self.products = input_Ps
		if len(self.TSs) != 1:
			print 'Error! The number of TSs is not 1!'

# units:
# ZPE: kcal/mol
# rotConsts: cm-1
# frequency: cm-1
# hessian: Hartree/Bohr2
# MW: amu
# exponentialDown: cm-1
# hinderedRotorQM1D: angle: degree energy: cm-1
class molecule:
	atoms = []
	
	bonds = []
	label = ''
	ZPE = 0.0
	rotConsts = []
	symmetryNumber = 1
	# frequency scaling factor could be set for each molecule separately if the freq computational methods are different but all accurate 
	# currently the freq scaling factor used is the factor in reaction system, which is a uniformed number
	freqScaleFactor = 1.0
	imfreq = 0.0
	frequencies = []
	hessian = []
	spinMultiplicity = 1
	epsilon = 0.0
	sigma = 0.0
	exponentialDown = 0.0
	hinderedRotorQM1D = []
	description = ''
	role = ''

	_RingBanned = False

	# the default geom and connectivity are from gjf file
	def __init__(self, geom=[], connect=[], inputAtoms=[]):
		self.bonds = []
		self.label = ''
		self.ZPE = 0.0
		self.rotConsts = []
		self.symmetryNumber = 1
		self.freqScaleFactor = 1.0
		self.imfreq = 0.0
		self.frequencies = []
		self.hessian = []
		self.spinMultiplicity = 1
		self.epsilon = 0.0
		self.sigma = 0.0
		self.exponentialDown = 0.0
		self.hinderedRotorQM1D = []
		self.role = ''

		self._RingBanned = False

		if inputAtoms == []:
			self.atoms = []
			atomsNum = len(geom)
			for i in range(0, atomsNum):
				tmp_line = geom[i]
				tmp_line.strip()
				tmp_line = tmp_line.split()
				tmp_atom = atom(tmp_line[0],i+1,map(float, tmp_line[1:4]))
				self.atoms.append(tmp_atom)

			if len(connect) == atomsNum:
				for i in range(0, atomsNum):
					tmp_line = connect[i]
					tmp_line.strip()
					tmp_line = tmp_line.split()
					for j in range(1, len(tmp_line), 2):
						tmp_bond = bond(self.atoms[i], self.atoms[int(tmp_line[j]) - 1], float(tmp_line[j+1]))
						self.atoms[i].addBond(tmp_bond)
						self.atoms[int(tmp_line[j]) - 1].addBond(tmp_bond)
						self.bonds.append(tmp_bond)
			elif connect != []:
				print 'Error! Worng coonectivity in molecule initiation!'					
		else:
			self.atoms = copy.deepcopy(inputAtoms)

	def getLogGeom(self, geom):
		self.atoms = []
		for tmp_line in geom:
			tmp_line = tmp_line.strip()
			tmp_line = tmp_line.split()
			tmp_atom = atom(elementDict[tmp_line[1]] , int(tmp_line[0]), map(float, tmp_line[3:6]))
			self.atoms.append(tmp_atom)

	def getGjfGeom(self, geom):
		self.atoms = []
		for (i,tmp_line) in enumerate(geom):
			tmp_line = tmp_line.strip()
			tmp_line = tmp_line.split()
			tmp_atom = atom(tmp_line[0],i+1,map(float, tmp_line[1:4]))
			self.atoms.append(tmp_atom)

	def addAtom(self, atom):
		tmp_atom = copy.deepcopy(atom)
		tmp_atom.label = len(self.atoms)+1
		self.atoms.append(tmp_atom)


	# only a fresh virtual bond could be accepted as the parameter of this function 
	def addBond(self, freshBond):
		if not (freshBond.atom1 in self.atoms) and (freshBond.atom2 in self.atoms):
			print 'Error! The atoms to be bonded are not both in the atoms list!', freshBond.atom1.label, freshBond.atom2.label
		else:
			freshBond.atom1.addBond(freshBond)
			freshBond.atom2.addBond(freshBond)
			self.bonds.append(freshBond)

	# input parameters are the two atoms and the bond order
	def addBond2(self, atom1, atom2, bondOrder):
		if not (atom1 in self.atoms) and (atom2 in self.atoms):
			print 'Error! The atoms to be bonded are not both in the atoms list!', atom1.label, atom2.label
		else:
			tmp_bond = bond(atom1, atom2, bondOrder)
			self.addBond(tmp_bond)


	def setLabel(self, label):
		self.label = label

	def setZPE(self, ZPE):
		self.ZPE = ZPE

	def setRotConsts(self, rotConsts):
		self.rotConsts = rotConsts

	def setSymmetryNumber(self, symmetryNumber):
		self.symmetryNumber = symmetryNumber

	def setFreqScaleFactor(self, freqScaleFactor):
		self.freqScaleFactor = freqScaleFactor

	def setImfreq(self, imfreq):
		self.imfreq = imfreq

	def setFrequencies(self, frequencies):
		self.frequencies = frequencies

	def setHessian(self, hessian):
		self.hessian = hessian

	def setSpinMultiplicity(self, spinMultiplicity):
		self.spinMultiplicity = spinMultiplicity

	def setEpsilon(self, epsilon):
		self.epsilon = epsilon

	def setSigma(self, sigma):
		self.sigma = sigma

	def setExponentialDown(self, exponentialDown):
		self.exponentialDown = exponentialDown

	def setHinderedRotorQM1D(self, hinderedRotorQM1D):
		self.hinderedRotorQM1D = hinderedRotorQM1D

	def setDescription(self, description):
		self.description = description

	def setRole(self, role):
		self.role = role
	
	def setRingBanned(self, banned):
		self._RingBanned = banned

	def getWeight(self):
		weight = 0.0
		for tmp_atom in self.atoms:
			weight += tmp_atom.mass
		return	weight

	# get the bond between atom1 and atom2
	def getBond(self, atom1Label, atom2Label):
		tmp_children = self.atoms[atom1Label-1].children
		if self.atoms[atom2Label-1] in tmp_children:
			tmp_index = tmp_children.index(self.atoms[atom2Label-1])
			tmp_bond = self.atoms[atom1Label-1].bonds[tmp_index]
		else:
			print 'Error! This bond is not in current molecule', self.label, str(atom1Label), str(atom2Label)
			tmp_bond = None
		return tmp_bond

	# this function is used to get the two parts if a molecule is divided by a certain bond with the tabuAtom, 
	# this is the combination of atom.dividedGraph2 and a double check to guarantee the molecule is correctly divided into two parts. 
	# Only proper for a bond not in a ring. Safer to be used
	# if result==1, then end normally
	# if result==0, the bond is in a cycle
	# if result==-1, there are more than two groups
	def connectedGraph2(self, bond):
		result = 1
		tmp_group1 = bond.atom1.dividedGraph2([bond.atom2])
		# - is equal to .difference() for a set(), but freer parameters are allowed for .difference()
		comple_group1 = list(set(self.atoms) - set(tmp_group1))
		tmp_group2 = bond.atom2.dividedGraph2([bond.atom1])
		tmp_set = set(comple_group1) - set(tmp_group2)
		if len(tmp_set) > 0:
			print 'Error! There are some atoms with labels ' + str([x.label for x in tmp_set]) + ' neither connected with ' + str(bond.atom1.label) + ' nor ' + str(bond.atom2.label) + '!'
			result = -1
		tmp_set = set(tmp_group2) - set(comple_group1)
		if len(tmp_set) > 0:
			# print 'Error! There are some rings in the molecule! Ring members are labeled as ' + str([x.label for x in tmp_set]) + ' , certainly also including ' + str(bond.atom1.label) + ' and ' + str(bond.atom2.label) + '.'
			result = 0
		return tmp_group1, tmp_group2, result

	# get all rotations
	# return a list of rotations 
	def getRotations(self):
		rotations = []
		for tmp_atom in self.atoms:
			if tmp_atom.childrenNum() == 1:
				continue
			for (index, tmp_atom2) in enumerate(tmp_atom.children):
				if tmp_atom2.childrenNum() == 1:
					continue
				# do not rotate if this is a double bond
				if abs(tmp_atom.bonds[index].bondOrder - 1) > 1e-2:
					continue
				if tmp_atom.label > tmp_atom2.label:
					continue
				tmp_group1, tmp_group2, tmp_result = self.connectedGraph2(tmp_atom.bonds[index])
				# print str(tmp_atom.bonds[index].atom1.label) + ' ' + str(tmp_atom.bonds[index].atom2.label)
				# print [x.label for x in tmp_group1]
				# print [x.label for x in tmp_group2]
				if self._RingBanned == True and tmp_result == 0:
					# print 'Warning! The bond between ' + str(tmp_atom.label) + ' and ' + str(tmp_atom2.label) + ' is in a ring! Now it is not added in the MomInert input file.' 
					pass
				else:
					tmp_rotation = rotation(tmp_atom.bonds[index], tmp_group1, tmp_group2)
					rotations.append(tmp_rotation)
		return rotations

	def getAtomsNum(self):
		return len(self.atoms)

	def displayBonds(self):
		print 'all bonds for ' + self.label
		for tmp_atom in self.atoms:
			print tmp_atom.label, tmp_atom.symbol
			for tmp_bond in tmp_atom.bonds:
				print '[', tmp_bond.atom1.label, tmp_bond.atom2.label, ']', tmp_bond.bondOrder

	def clearBonds(self):
		self.bonds = []
		for tmp_atom in self.atoms:
			tmp_atom.children = []
			tmp_atom.bonds = []

	# fulfill the bonds using distance infomation rather than connectivity
	def fulfillBonds(self):
		self.clearBonds()
		atomsNum = len(self.atoms)
		for i in range(0, atomsNum):
			for j in range(i+1, atomsNum):
				tmp_order = 0
				tmp_distance = self.atoms[i].distance(self.atoms[j])
				
				distances = bondDisDict[self.atoms[i].symbol][self.atoms[j].symbol]
				orders = bondOrderDict[self.atoms[i].symbol][self.atoms[j].symbol]

				for (index, distance) in enumerate(distances):
					if tmp_distance <= distance:
						tmp_order = orders[index]
					if tmp_order != 0: 
						break
				# if i==6 and j==26:
					# print self.atomsNum.label, self.atomsNum.label, tmp_order
				if tmp_order != 0:
					tmp_bond = bond(self.atoms[i], self.atoms[j], tmp_order)
					self.atoms[i].addBond(tmp_bond)
					self.atoms[j].addBond(tmp_bond)
					self.bonds.append(tmp_bond)


	def generateRotScanFile(self):
		rotations = self.getRotations()

		if not os.path.exists(self.label):
			os.mkdir(self.label)
		fw = file(os.path.join(self.label, ''.join([self.label, '.rot'])), 'w')	
		fw.write('spinMultiplicity: '+str(self.spinMultiplicity)+'\n')
		fw.write('\ngeometry:\n')
		fw.write(''.join(['%s %.8f %.8f %.8f\n' % (x.symbol, x.coordinate[0], x.coordinate[1], x.coordinate[2]) for x in self.atoms]))
		fw.write('\nrotation information:\n')

		for tmp_rotation in rotations:
			if tmp_rotation.rotBondAxis.atom1.label < tmp_rotation.rotBondAxis.atom2.label:
				tmp_atom1 = tmp_rotation.rotBondAxis.atom1
				tmp_atom2 = tmp_rotation.rotBondAxis.atom2
			else:
				tmp_atom1 = tmp_rotation.rotBondAxis.atom2
				tmp_atom2 = tmp_rotation.rotBondAxis.atom1

			neighbour1 = None
			neighbour2 = None

			# search the neighbour atom for atom1
			# search C atoms as the neighbour in priority
			for tmp_atom in tmp_atom1.children:
				if tmp_atom.symbol == 'C' and tmp_atom != tmp_atom2:
					neighbour1 = tmp_atom
			# search other heavy atoms as the neighbour if C atom not found
			if neighbour1 == None:
				for tmp_atom in tmp_atom1.children:
					if tmp_atom.symbol != 'H' and tmp_atom != tmp_atom2:
						neighbour1 = tmp_atom
			# search left atoms (H) as the neighbour if C and other heavy atoms not found
			if neighbour1 == None:
				for tmp_atom in tmp_atom1.children:
					if tmp_atom != tmp_atom2:
						neighbour1 = tmp_atom

			# search the neighbour atom for atom2
			# search C atoms as the neighbour in priority
			for tmp_atom in tmp_atom2.children:
				if tmp_atom.symbol == 'C' and tmp_atom != tmp_atom1:
					neighbour2 = tmp_atom
			# search other heavy atoms as the neighbour if C atom not found
			if neighbour2 == None:
				for tmp_atom in tmp_atom2.children:
					if tmp_atom.symbol != 'H' and tmp_atom != tmp_atom1:
						neighbour2 = tmp_atom
			# search left atoms (H) as the neighbour if C and other heavy atoms not found
			if neighbour2 == None:
				for tmp_atom in tmp_atom2.children:
					if tmp_atom != tmp_atom1:
						neighbour2 = tmp_atom
			fw.write(''.join([str(neighbour1.label), ' ', str(tmp_atom1.label), ' ', str(tmp_atom2.label), ' ', str(neighbour2.label), '\n']))

		fw.write('\n\n\n\n\n')
		fw.close()

class atom:
	symbol = ''
	label = 0
	mass = 0.0
	coordinate =[]
	children = []
	bonds = []
	color = (1,1,1)

	def __init__(self, inputSymbol='', inputLabel=0, inputCoordinate=[], inputBonds=[]):
		self.symbol = inputSymbol
		self.label = inputLabel
		if inputSymbol in eleWeightDict:
			self.mass = eleWeightDict[inputSymbol]
			self.color = eleColorDict[inputSymbol]
		else: 
			self.mass = 0.0
			self.color = (0,0,0)
		if inputCoordinate == []:
			self.coordinate = []
		else:
			self.coordinate = inputCoordinate
		self.children = []
		self.bonds = []
		for tmp_bond in inputBonds:
			self.addBond(tmp_bond)

	def addBond(self,bond):
		# print 'atoms:\t' + str(bond.atom1.label) + '\t' + str(bond.atom2.label)
		if bond.atom1.label == self.label and bond.atom2.label != self.label:
			if bond.atom2 not in self.children:
				self.children.append(bond.atom2)
				self.bonds.append(bond)
			else:
				print 'this bond has been added!\t' + str(self.label) + ' ' + str(bond.atom2.label)
				pass
		elif bond.atom1.label != self.label and bond.atom2.label == self.label:
			if bond.atom1 not in self.children:
				self.children.append(bond.atom1)
				self.bonds.append(bond)
			else:
				print 'this bond has been added!\t' + str(self.label) + ' ' + str(bond.atom1.label)
				pass
		else:
			print 'Error! There is a wrong bond between ' + str(bond.atom1.label) + ' and ' + str(bond.atom2.label) + ' on atom ' + str(self.label) + '.'

	# this function is used to get the left connected part after prohibiting the route to tabuAtomPool, but without double check. 
	# It's unknown whether the left part is a part or not. It is also a arbitary division if there is a ring structure in the molecule.
	def dividedGraph2(self,tabuPool):
		connectedPool = [self]
		tabuPool.append(self)
		for tmp_atom in self.children:
			if tmp_atom not in tabuPool:
				connectedPool += tmp_atom.dividedGraph2(tabuPool)
				tabuPool += connectedPool
		return connectedPool

	def childrenNum(self):
		return len(self.children)

	def distance(self, atom2):
		tmp = np.array(self.coordinate)-np.array(atom2.coordinate)
		tmp = (sum(tmp**2))**0.5
		return tmp		


class bond:
	atom1 = atom()
	atom2 = atom()
	bondOrder = 0.0

	# this bond initialized is not a real bond
	# it would not be a real one until verified in a molecule level or added logically
	# we can call it a fresh virtual bond now
	def __init__(self, inputAtom1, inputAtom2, inputBondOrder=0.0):
		self.atom1 = inputAtom1
		self.atom2 = inputAtom2
		self.bondOrder = inputBondOrder


class rotation:
	rotBondAxis = None
	atomGroup1 = []
	atomGroup2 = []
	angles = []
	energies = []

	# rotBondAxis is a bond instance
	def __init__(self, rotBondAxis, atomGroup1=[], atomGroup2=[]):
		self.rotBondAxis = rotBondAxis
		angles = []
		energies = []
		if atomGroup1 == []:
			self.atomGroup1	= []
		else:
			self.atomGroup1 = atomGroup1
		if atomGroup2 == []:
			self.atomGroup2 = []
		else:
			self.atomGroup2 = atomGroup2
	
	def group1Add(self,atom):
		self.atomGroup1.append(atom)	

	def group2Add(self,atom):
		self.atomGroup2.append(atom)

	def group1Labels(self):
		tmp_list = [x.label for x in self.atomGroup1]
		tmp_list.sort()
		return tmp_list

	def group2Labels(self):
		tmp_list = [x.label for x in self.atomGroup2]
		tmp_list.sort()
		return tmp_list

	def group1Num(self):
		return len(self.atomGroup1)

	def group2Num(self):
		return len(self.atomGroup2)

	def group1Info(self):
		info=str(self.rotBondAxis.atom1.label) + ' ' + str(self.rotBondAxis.atom2.label) + '\n'
		info += str(self.group1Num()) + '\n'
		info += ''.join(str(x) + ' ' for x in self.group1Labels()) + '\n'
		return info

	def group2Info(self):
		info=str(self.rotBondAxis.atom2.label) + ' ' + str(self.rotBondAxis.atom1.label) + '\n'
		info += str(self.group2Num()) + '\n'
		info += ''.join(str(x) + ' ' for x in self.group2Labels()) + '\n'
		return info

	def singleGroupInfo(self):
		if self.group1Num() <= self.group2Num():
			return self.group1Info()
		else:
			return self.group2Info()

	def setPotential(self, angles, energies):
		self.angles = angles
		self.energies = energies	


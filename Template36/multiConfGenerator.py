# READING--------------------------------------------------------------------------------------
# Read from specifically formatted excel sheet and store them as data arrays
from xlrd import *
from xlwt import *
import pyExcelerator
from xlutils.copy import copy
from re import *
import re
import os
import shutil
import chem


#input
# cluster could be set as cce or Tsinghua100
# the path where the jobs would lie should be announced
rotCH3 = False

# symbol indicating the position
pattern_name = re.compile('^.*.*$')

# constants


# definetion of comparing pattern
pattern_multi = re.compile('^.*Multiplicity = ([0-9]+).*$')
pattern_fixBond = re.compile('^ *B *([0-9]+) *([0-9]+) *F *$')
pattern_freqCom = re.compile('^.*#[PN]? Geom=AllCheck Guess=TCheck SCRF=Check.*Freq.*$')
pattern_optimized = re.compile('^.*Optimized Parameters.*$')
pattern_standard = re.compile('^.*Standard orientation:.*$') 
pattern_endline = re.compile('^.*---------------------------------------------------------------------.*$')

#variables
multi = 1
fixedBond = []

#flags
multi_done = -1
barrierless = False
freqCom_done = -1
optimized_done = -1
standard_done = -1
coordinate_done = -1

# temporary variables
tmp_m = []
tmp_num = 0

pwd = os.getcwd()

# traverse folders to get result_.*.gjf files and get optimized geometry of species
if not os.path.exists('geom'):
	print 'Error! There is no geom directory!'

tmp_pwd = os.path.join(pwd,'geom')
tmp_fileLists = os.listdir(tmp_pwd)

print '\ngenerating .rot files\n'
fw = file('ConfGen.sh', 'w')
for tmp_file in tmp_fileLists:
	if os.path.isdir(os.path.join(tmp_pwd, tmp_file)):
		continue
	print tmp_file

	# traverse files
	if re.search('\.log',tmp_file):
		tmp_m = pattern_name.match(tmp_file[0:-4])	
		# if target file found
		if tmp_m:
			print 'Target file:\t' + tmp_file
			
			multi = 1
			fixedBond = []

			multi_done = -1
			if barrierless == True:
				fixBond_done = -1
			else:
				fixBond_done = 1
			freqCom_done = 1
			optimized_done = -1
			standard_done = -1
			coordinate_done = -1

			fr = file(os.path.join(tmp_pwd, tmp_file), 'r')
			tmp_lines = fr.readlines()		
			for (lineNum, tmp_line) in enumerate(tmp_lines):
				if multi_done != 1:
					tmp_m = pattern_multi.match(tmp_line)
					if tmp_m:
						multi = int(tmp_m.group(1))
						multi_done = 1
				elif fixBond_done != 1:
					tmp_m = pattern_fixBond.match(tmp_line)
					if tmp_m:
						fixedBond = [int(tmp_m.group(1)), int(tmp_m.group(2))]
						fixBond_done = 1
				elif freqCom_done != 1:
					if lineNum < len(tmp_lines) - 1:
						tmp2_line = tmp_lines[lineNum].strip() + tmp_lines[lineNum+1].strip()
						tmp_m = pattern_freqCom.match(tmp2_line)
						if tmp_m:
							freqCom_done = 1
				elif optimized_done != 1:
					tmp_m = pattern_optimized.match(tmp_line)
					if tmp_m:
						optimized_done = 1	
				elif standard_done != 1:
					tmp_m = pattern_standard.match(tmp_line)
					if tmp_m:
						tmp_num = lineNum + 5
						standard_done = 1
				elif coordinate_done != 1:
					tmp_m = pattern_endline.match(tmp_line)
					if tmp_m:
						if lineNum > tmp_num:
							tmp_geom = tmp_lines[tmp_num: lineNum]
							coordinate_done = 1

			molecule1 = chem.molecule()
			molecule1.getLogGeom(tmp_geom)
			# label should be indicated in an excel in the future
			molecule1.setLabel(tmp_file[0:-4])
			molecule1.setDescription(tmp_file[0:-4])
			molecule1.setSpinMultiplicity(multi)
			molecule1.setRingBanned(True)

			molecule1.fulfillBonds()
			molecule1.generateMultiConfFile(fixedBond=fixedBond, rotCH3=rotCH3)
			print molecule1.label
			fw.write('echo ' + molecule1.label + '\n')
			fw.write('cd ' + molecule1.label + '\n')
			fw.write('ConfGen.exe<'+molecule1.label+'.rot\n')
			fw.write('cd ..\n\n')

fw.close()
os.system("..\\dos2unix-6.0.6-win64\\bin\\dos2unix.exe " + fw.name + ' > log_dos2unix.txt 2>&1')

print '\ngenerating rotation scan jobs\n'

print 'Rotation scan files generated successfully!'

# THE END



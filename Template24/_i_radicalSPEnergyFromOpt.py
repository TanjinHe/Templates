# READING--------------------------------------------------------------------------------------
# Read from specifically formatted excel sheet and store them as data arrays
from xlrd import *
from xlwt import *
from re import *
import re
import os
import shutil
import textExtractor
import cluster

# input
# cluster could be set as cce or Tsinghua100 or Tianhe
# the path where the jobs would lie should be announced
# clusterName = 'cce'
# clusterPath = '/home/hetanjin/newGroupAdditivityFrog2/CnH2n'
# clusterName = 'Tianhe'
# clusterPath = '/vol-th/home/you/hetanjin/newGroupAdditivityFrog2/CnH2n_4'
clusterName = 'TianheII'
clusterPath = '/WORK/tsinghua_xqyou_1/hetanjin/newGroupAdditivityFrog2/B3woDispersion/CnH2n+2'
jobsPerSlot = 12

# constants
cluster1 = cluster.cluster(clusterName, clusterPath)
cluster1._g09D01=True 

pattern_logFile = re.compile('^(C[0-9]*H[0-9]*_*[0-9]*_+[r0-9]+_+[CO0-9]+).*\.log$')
pattern_fileConf = re.compile('^(C[0-9]*H[0-9]*_[0-9]*_[0-9]+)_[0-9]+_.*$')
pattern_gjfFile = re.compile('^(C[0-9]*H[0-9]*_*[0-9]*_+[r0-9]+_+[CO0-9]+).*\.gjf$')
pattern_multi = re.compile('^.*Multiplicity = ([0-9]+).*$')
pattern_optimized = re.compile('^.*Optimized Parameters.*$') 
pattern_standard = re.compile('^.*Standard orientation:.*$') 
pattern_input = re.compile('^.*Input orientation:.*$') 
pattern_endline = re.compile('^.*---------------------------------------------------------------------.*$')
# pattern_energy = re.compile('^.*Sum of electronic and zero-point Energies= *(-?[0-9]+\.[0-9]+).*$')
pattern_energy = re.compile('^.*SCF Done:  E\([RU]B3LYP\) = *([\-\.0-9Ee]+) +A\.U\. after.*$')
pattern_end = re.compile('^.*Normal termination of Gaussian 09.*$')

# variables
energyDict = {}
molecules = []
multi = 1

#flags
logExist = 0
multi_done = 0
optimized_done = 0
standard_done = 0
coordinate_done = 0

# temporary variables
tmp_energy = 0.0

#counters
error_file_num = 0

# extract energies
if os.path.exists('_i_radicalSPEnergy'):
	shutil.rmtree('_i_radicalSPEnergy')
os.mkdir('_i_radicalSPEnergy')

os.chdir('_h_radicalGeneration')
tmp_folderLists = os.listdir('.')
for tmp_folder in tmp_folderLists:
	logExist = 0
	tmp_energy = 0.0
	if os.path.isfile(tmp_folder):
		tmp_m = pattern_logFile.match(tmp_folder)
		if tmp_m:
			tmp_name = tmp_m.group(1)
			if tmp_name not in energyDict.keys():
				energyDict[tmp_name] = {} 
			fr = file(os.path.join(tmp_folder), 'r')
			tmp_lines = fr.readlines()
			tmp2_m = pattern_end.match(tmp_lines[-1])
			if not tmp2_m:
				print 'Error! ' + tmp_folder + ' not ends normally!'
				error_file_num += 1
			else:
				for tmp_line in tmp_lines:
					tmp3_m = pattern_energy.match(tmp_line)
					if tmp3_m:
						tmp_energy = float(tmp3_m.group(1))
				energyDict[tmp_name][tmp_folder[0:-4]] = tmp_energy
			fr.close()
	else:
		tmp_fileList = os.listdir(tmp_folder)
		# print tmp_folder
		print tmp_folder
		for tmp_file in tmp_fileList:
			tmp_m = pattern_logFile.match(tmp_file)
			if tmp_m:
				logExist = 1
				tmp_name = tmp_m.group(1)
				if tmp_name not in energyDict.keys():
					energyDict[tmp_name] = {} 
				fr = file(os.path.join(tmp_folder, tmp_file), 'r')
				tmp_lines = fr.readlines()
				tmp2_m = pattern_end.match(tmp_lines[-1])
				if not tmp2_m:
					print 'Error! ' + tmp_file + ' not ends normally!'
					error_file_num += 1
				else:
					for tmp_line in tmp_lines:
						tmp3_m = pattern_energy.match(tmp_line)
						if tmp3_m:
							tmp_energy = float(tmp3_m.group(1))
					energyDict[tmp_name][tmp_file[0:-4]] = tmp_energy
				fr.close()
		if logExist != 1:
			print 'Error! The name of folder is not invalid! ' + tmp_folder	
			error_file_num += 1	

# write to excel
wb_new = Workbook()
sh = wb_new.add_sheet('energy', cell_overwrite_ok=True)
tmp_row = 0
tmp_col = 0
sh.write(tmp_row, tmp_col, 0)
sh.write(tmp_row, tmp_col+2, 'File Name 1 (Lowest)')
sh.write(tmp_row, tmp_col+3, 'File Name 2')
sh.write(tmp_row+1, tmp_col, 1)
sh.write(tmp_row+1, tmp_col+1, 'Molecule Name')
sh.write(tmp_row+1, tmp_col+2, 'Energy 1 (Lowest)')
sh.write(tmp_row+1, tmp_col+3, 'Energy 2')
sh.write(tmp_row+2, tmp_col, 2)
molecules = sorted(energyDict.keys())
for tmp_mole in  molecules:
	tmp_dict = energyDict[tmp_mole]
	# sortedDict = sorted(tmp_dict.iteritems(), key=lambda d:d[1])
	sortedDict = sorted(tmp_dict.items(), key=lambda d:d[1])
	# sortedFiles = sorted(tmp_dict.keys, key=tmp_dict.__getitem__)
	
	for tmp_file in sortedDict:
		tmp_m = pattern_fileConf.match(tmp_file[0])
		if tmp_m:
			if tmp_file != sortedDict[0]:
				# print 'Warning! The optimized structure from conformer search is not the first one!'
				# print ''.join(['molecule: ', tmp_mole, '\tlowest: ', sortedDict[0][0], '\tconformer: ', tmp_file[0]]) 
				tmp_energyDiff = (tmp_file[1] - sortedDict[0][1]) * 627.51
				# print 'energy difference:\t' + str(tmp_energyDiff)
				if tmp_energyDiff > 0.1:
					print 'Warning! The optimized structure from conformer search is not the lowest one!'
					print ''.join(['molecule: ', tmp_mole, '\tlowest: ', sortedDict[0][0], '\tconformer: ', tmp_file[0]])
					print 'energy difference:\t' + str(tmp_energyDiff) 
			break

	tmp_row +=3
	tmp_col = 0
	sh.write(tmp_row, tmp_col, 0)
	sh.write(tmp_row+1, tmp_col, 1)
	sh.write(tmp_row+1, tmp_col+1, tmp_mole)
	sh.write(tmp_row+2, tmp_col, 2)
	tmp_col = 2
	for tmp_file in sortedDict:
		sh.write(tmp_row, tmp_col, tmp_file[0])
		sh.write(tmp_row+1, tmp_col, tmp_file[1])
		tmp_col += 1
	# this code is used to copy the lowest-energy file to LogFileCollection directory
	# if len(sortedDict) > 0:
	# 	shutil.copyfile(os.path.join(pwd, tmp_folder, sortedDict[0][0]+'.log'), os.path.join(pwd, '_i_radicalSPEnergy', sortedDict[0][0]+'.log'))
	# else:
	# 	print 'Error! There is no file corresponding to molecule ' + tmp_mole
wb_new.save('EnergyCollection.xls')

# extract geom from log files
for tmp_mole in molecules:
	tmp_dict = energyDict[tmp_mole]
	sortedDict = sorted(tmp_dict.items(), key=lambda d:d[1])
	if len(sortedDict) > 0:
		tmp_file = sortedDict[0]
		fr = file(os.path.join(tmp_file[0], tmp_file[0]+'.log'))

		multi_done = 0
		optimized_done = 0
		standard_done = 0
		coordinate_done =0

		tmp_lines = fr.readlines()
		for (lineNum, tmp_line) in enumerate(tmp_lines):
			if multi_done != 1:
				tmp_m = pattern_multi.match(tmp_line)
				if tmp_m:
					multi = int(tmp_m.group(1))
					multi_done = 1
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
						tmp_geom = textExtractor.geometryExtractor(tmp_lines[tmp_num: lineNum])
						coordinate_done = 1
		fw = file(os.path.join('..', '_i_radicalSPEnergy', tmp_file[0]+'.gjf'), 'w')
		fw.write(
'''%mem=28GB
%nprocshared=12
%chk=''' + tmp_file[0] + '''.chk
#p B3LYP/6-31G(d) opt freq

using B3LYP/6-31G(d) to do opt and freq calc.

0 '''+str(multi) + '\n' + tmp_geom + '\n\n\n\n\n\n')
		fw.close()
		fr.close()
	else:
		print 'Error! There is no jobs about molecule ' + tmp_mole
os.chdir('../')

# generate B3LYP jobs from Gjfs in _i_radicalSPEnergy
os.chdir('_i_radicalSPEnergy')
tmp_fileList = os.listdir('.')
for tmp_file in tmp_fileList:
	if re.search('\.gjf', tmp_file):
		if re.search('[Tt][sS]', tmp_file):
			cluster1.setTS(True)
		else:
			cluster1.setTS(False)
		tmp_m = pattern_gjfFile.match(tmp_file)
		if tmp_m:
			cluster1.generateJobFromGjf(tmp_file, jobName=tmp_m.group(1)+'_3_opt_M06' ,command='#p M062X/def2TZVP')

# generate cluster script
tmp_num = 0
slot_num = 1
fw2 = file('submitFleet.sh', 'w')
if clusterName == 'Tianhe' or clusterName == 'Tianhe2' or clusterName == 'TianheII':
	fw2.write('''#!/bin/bash

source $HOME/.bash_profile

declare -i numJobs=0

''')
else:
	fw2.write('''#!/bin/csh
#
''')

if clusterName == 'Tianhe' or clusterName == 'Tianhe2':
	fw2.write('''numJobs=`yhq |grep TH_NET | wc -l` 
while ((numJobs>28))
do
	echo $numJobs
	sleep 120
	numJobs=`yhq | grep TH_NET | wc -l`  
done

''')

if clusterName == 'TianheII':
	fw2.write('''numJobs=`yhq |grep tsinghua_xqy | wc -l` 
while ((numJobs>63))
do
	echo $numJobs
	sleep 120
	numJobs=`yhq |grep tsinghua_xqy | wc -l`  
done

''')

if jobsPerSlot > 1:
	tmp_fileList = os.listdir('.') 
	for tmp_file in tmp_fileList:
		if os.path.isdir(tmp_file):
			if tmp_num == 0:
				fw = file('slot_' + '%04d'%slot_num + '.sh', 'w')
				fw.write('#!/bin/bash\n\n')
			if clusterName == 'TianheII':
				fw.write('sh ' + tmp_file + '/' + tmp_file + '''.job &
sleep 2
numJobs=`ps | grep g09 | wc -l`
while((numJobs>3))
do 
	sleep 120
	numJobs=`ps | grep g09 | wc -l`
done
''')
			else:			
				fw.write('sh ' + tmp_file + '/' + tmp_file + '.job\n')
			tmp_num += 1
			if tmp_num >= jobsPerSlot:
				tmp_num = 0
				slot_num += 1
				if clusterName == 'TianheII':
					fw.write('wait\n')
				fw.close()
				os.system("..\\dos2unix-6.0.6-win64\\bin\\dos2unix.exe " + fw.name + ' > log_dos2unix.txt 2>&1')
	if clusterName == 'TianheII' and tmp_num != 0:
		fw.write('wait\n')	
	fw.close()
	os.system("..\\dos2unix-6.0.6-win64\\bin\\dos2unix.exe " + fw.name + ' > log_dos2unix.txt 2>&1')
	
	tmp_fileList = os.listdir('.')
	for tmp_file in tmp_fileList:
		if re.search('slot_.*sh', tmp_file):
			if clusterName == 'Tianhe' or clusterName == 'Tianhe2':
				fw2.write('echo \'submit to Tianhe:\'\necho \'' + tmp_file + '\'\nyhbatch -pTH_NET -c 12 ' + tmp_file + '''
sleep 1
numJobs=`yhq |grep TH_NET | wc -l` 
while ((numJobs>28))
do
	echo $numJobs
	sleep 120
	numJobs=`yhq | grep TH_NET | wc -l`  
done
''')
			elif clusterName == 'TianheII':
				fw2.write('echo \'submit to TianheII:\'\necho \'' + tmp_file + '\'\nyhbatch -N 1 ' + tmp_file + '''
sleep 1
numJobs=`yhq |grep tsinghua_xqy | wc -l` 
while ((numJobs>63))
do
	echo $numJobs
	sleep 120
	numJobs=`yhq |grep tsinghua_xqy | wc -l`  
done
''')
			else:
				fw2.write('sh submit12.sh ' + tmp_file + '\nsleep 5\n')
elif jobsPerSlot == 1:
	tmp_fileList = os.listdir('.')	
	for tmp_file in tmp_fileList:
		if os.path.isdir(tmp_file):
			if clusterName == 'Tianhe' or clusterName == 'Tianhe2':
				fw2.write('sh submitTH.sh ' + tmp_file + '''
sleep 1
numJobs=`yhq |grep TH_NET | wc -l` 
while ((numJobs>28))
do
	echo $numJobs
	sleep 120
	numJobs=`yhq | grep TH_NET | wc -l`  
done
''')
			else:
				fw2.write('sh submit12.sh ' + tmp_file + '\nsleep 5\n')
fw2.close()
os.system("..\\dos2unix-6.0.6-win64\\bin\\dos2unix.exe " + fw2.name + ' > log_dos2unix.txt 2>&1')

os.chdir('../')

print '---------------------------------------\nLog of task 1\n'
print 'Energy extracted successfully!'
print 'error_file_num:\t' + str(error_file_num)
if error_file_num == 0:
	print 'All are successful log files!'
print '\nLog of task 2\n'
print 'Energy written to excel successfully!'
print '\nLog of task 3\n'
print 'Geometry .gjf files extracted successfully!'
print '\nLog of task 4\n'
print 'B3LYP opt jobs generated successfully!'

# THE END



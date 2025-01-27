# READING--------------------------------------------------------------------------------------
from xlrd import *
import os
import re
import shutil

__barrier__ = True

# from xlrd import open_workbook,cellname
name = ''
temperature=[298.15, 300, 400, 450, 500, 550, 600, 650, 700, 750, 800, 850, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500]
pwd = os.getcwd()
tmp_fileLists = os.listdir(pwd)
for tmp_file in tmp_fileLists:
	if re.search('.name',tmp_file):
		name = tmp_file[0:-5]
		fr = file(tmp_file, 'r')
		tmp_lines = fr.readlines()
		tmp_line = tmp_lines[1].strip(' \n')
		if tmp_line == 'barrier':
			__barrier__ = True
			print '\n-------------------------------------\nbarrier reactions\n-------------------------------------\n'
		elif tmp_line == 'barrierless':
			__barrier__ = False
			print '\n-------------------------------------\nbarrierless reaction\n-------------------------------------\n'
		else:
			print '\n-------------------------------------\nWarning! Barrier or barrierless is not announced! Barrier is used as default!\n-------------------------------------\n'
		tmp_line = tmp_lines[5].strip(' \n')
		temperature = map(float, tmp_line.split())
		fr.close()

wb=open_workbook(name + '.xls')
sh=wb.sheet_by_name('SpeciesInfo')

# Define variables
total=int(sh.cell_value(1,0)) 		# Total number of activated reactions
reacs_line = 0  					# Total number of reactants line in excel, not equal to those in activated reactions, would changed while reading, it's used to count lines
prods_line = 0 						# Total number of products line in excel, not equal to those in activated reactions, would changed while reading, it's used to count lines
# max_freq=75

# parameters of R 
name_R=[]						# name abbreviation
energy_R=[]						# enthalpy of formation at 0 K in kcal/mol
K_rotor_R=[]					# K-rotor of the rotational constants in GHZ
TwoD_rotor_R=[]					# 2D-rotor of the rotational constants in GHZ
RSN_R = []						# rotational symmetry number of R
multi_R = []					# multiplicity of R in ground sate
freq_R=[]						# frequency array 
num_freq_R=[]					# Frequency counter
formula_R=[]					# chemical formula 

# parameters of TS
name_TS=[]						# name abbreviation
energy_TS=[]					# enthalpy of formation at 0 K in kcal/mol
reverse_barrier=[]				# reverse barrier energy
K_rotor_TS=[]					# K-rotor of the rotational constants in GHZ
TwoD_rotor_TS=[]				# 2D-rotor of the rotational constants in GHZ
RSN_TS = []						# rotational symmetry number of TS
multi_TS = []					# multiplicity of TS in ground sate
i_freq_TS=[]					# imaginary frequency array
freq_TS=[]						# frequency array 
num_freq_TS=[]					# Frequency counter
formula_TS=[]					# chemical formula 

#temporary variables
tmp_freq=[]

# Read the information about TS
# Read the information about R
row_index = 3

while sh.cell_value(row_index,0) != '':
	reacs_line += 1

	if int(sh.cell_value(row_index,0)) != 0:

		############################
		##need to update for multi-reacs later
		############################
		
		name_R.append(sh.cell_value(row_index,1))

		#corresponding to the similar sentense above
		energy_R.append(sh.cell_value(row_index,7))
		formula_R.append(sh.cell_value(row_index,10))
		K_rotor_R.append(float(sh.cell_value(row_index,11)))
		TwoD_rotor_R.append(float(sh.cell_value(row_index,14)))
		RSN_R.append(int(sh.cell_value(row_index,15)))
		multi_R.append(int(sh.cell_value(row_index,16)))
		num_freq_R.append(int(sh.cell_value(row_index,21)))

		tmp_freq = []
		for col_num in range(num_freq_R[-1]): 
			tmp_freq.append(sh.cell_value(row_index,23+col_num))
		freq_R.append(tmp_freq)			
	row_index += 1

row_index += 1
while sh.cell_value(row_index,0) != '':
	prods_line += 1
	row_index += 1

row_index += 1
while sh.cell_value(row_index,0) != '':
	if int(sh.cell_value(row_index,0)) != 0:
		name_TS.append(sh.cell_value(row_index,1))

		# using barrier or formation energy?	
		energy_TS.append(sh.cell_value(row_index,7))
		
		reverse_barrier.append(sh.cell_value(row_index,8))
		formula_TS.append(sh.cell_value(row_index,10))
		K_rotor_TS.append(float(sh.cell_value(row_index,11)))
		TwoD_rotor_TS.append(float(sh.cell_value(row_index,14)))
		RSN_TS.append(int(sh.cell_value(row_index,15)))
		multi_TS.append(int(sh.cell_value(row_index,16)))
		i_freq_TS.append(sh.cell_value(row_index,20))
		if not i_freq_TS[-1] > 0:
			print 'Error! There is some problem with the imaginary frequency of ' + name_TS[-1]	
		num_freq_TS.append(int(sh.cell_value(row_index,21)))

		tmp_freq = []
		for col_num in range(num_freq_TS[-1]): 
			tmp_freq.append(sh.cell_value(row_index,23+col_num))
		freq_TS.append(tmp_freq)			
	row_index += 1
	if row_index >= sh.nrows:
		break

print 'get reactions successfully!'


# WRITING --------------------------------------------------------------------------------------

total = len(name_TS)
if os.path.exists(os.getcwd()+'/thermoInput'):
	shutil.rmtree(os.getcwd()+'/thermoInput')
os.mkdir('thermoInput')

for k in range(total):

	# Read from the existing template file
	
	# Open the new .dat file and append the remaining changes to the file
	#with open('thermo_{0}.dat'.format((bond_length[k])*100),'a') as fw:
	fw = file('thermoInput/' + name_TS[k]+'.dat','w')

	#write information about R
	fw.write(
'''KCAL  MCC
''' + str(len(temperature)) + '\n' + ''.join(str(x) + ' ' for x in temperature) + '''
2
reac  ''' + name_R[k] + ' ' + str(energy_R[k]) + '\n' + \
formula_R[k] + '''
1. (blank comment line)
2. (blank comment line)
3. (blank comment line)
'''+ str(RSN_R[k]) + '''  1   1
0.0   ''' + str(multi_R[k]) + '\n' + str(num_freq_R[k]+2) + "\tHAR\tGHZ\n")

	for m in range(num_freq_R[k]):
		fw.write(str(m+1) + "\tvib\t" + str(freq_R[k][m]) + "\t\t0\t1\n")
			
	#why not use kro but qro here
	fw.write(str(m+2) + "\tqro\t" + str(K_rotor_R[k]) + "\t\t1\t1\t!	K-rotor\n")
	fw.write(str(m+3) + "\tqro\t" + str(TwoD_rotor_R[k]) + "\t\t1\t2\t!	2D\n\n")

	#write information about TS
	if __barrier__ == True:
		fw.write("ctst\t" + name_TS[k]  + "  " + str(energy_TS[k]) + "  " + str(i_freq_TS[k]) + "  " + str(reverse_barrier[k]) + '''\t!!!!!!!!!!!    <= TS
''' + formula_TS[k] + '''
1. (blank comment line)
2. (blank comment line)
3. (blank comment line)
''' + str(RSN_TS[k]) + '''   1   1
0.0   ''' + str(multi_TS[k]) + '\n' + str(num_freq_TS[k]+2) + "\tHAR GHZ\n")
	else:
		fw.write("ctst\t" + name_TS[k]  + "  " + str(energy_TS[k]) + " 0.0 0.0" + '''\t!!!!!!!!!!!    <= loose TS
''' + formula_TS[k] + '''
1. (blank comment line)
2. (blank comment line)
3. (blank comment line)
''' + str(RSN_TS[k]) + '''   1   1
0.0   ''' + str(multi_TS[k]) + '\n' + str(num_freq_TS[k]+2) + "\tHAR GHZ\n")

	for m in range(num_freq_TS[k]):
		fw.write(str(m+1) + "\tvib\t" + str(freq_TS[k][m]) + "\t\t0\t1\n")
			
	#why not use kro but qro here
	fw.write(str(m+2) + "\tqro\t" + str(K_rotor_TS[k]) + "\t\t1\t1\t!	K-rotor\n")
	fw.write(str(m+3) + "\tqro\t" + str(TwoD_rotor_TS[k]) + "\t\t1\t2\t!	2D\n\n")
	fw.close()

# for loops of all reactions ended

print '\nThermo input generated successfully!\n'		

# THE END



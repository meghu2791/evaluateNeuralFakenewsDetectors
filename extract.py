import json
import os
for r, d, file in os.walk('./'):
	for f in file:
		if 'results' in f:	
			with open(f) as json_file:
				human = 0
				machine = 0
				for line1 in json_file.readlines():
					line = json.loads(line1)
					if 'label' in line.keys():
						if line['label'] == 'machine':
							machine += 1
						else:
							human += 1
				if 'syntactic' in f:
					if human+machine !=0:
						print(f+"  "+"accuracy:"+ str(machine/(machine+human))+" 	total count"+":  "+str(human+machine))
				elif human+machine != 0:
					print(f+"   "+"accuracy:"+str(machine/(machine+human))+"   total count"+ ": "+str(human+machine))
		 

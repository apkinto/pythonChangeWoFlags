import ps
from ps import model
import datetime
import xml.etree.ElementTree as ET
import sys, os
import logging

''' 
	USAGE: PSBatch psmodel.py <modelXml>
		example: C:/test/scp/12.2/PS/bin>PSBatch D:/Python/ps/<SCRIPT> Vision.xml
'''

def getTime():
	currentTime = datetime.datetime.now()
	return currentTime

def setVariables(config):
	'''
		Sets variables from psPythonConfig.xml.   Currently assumes it is in the PS bin directory.
	'''
	variable = {}
	config = ET.parse(config)
	root = config.getroot()
	for var in root.find('variableList'):
		variable[var.tag] = var.text
	return variable
		
def openModel(inputDir, model):
	log.info('\tImport Start...')
	start = getTime()
	psModel = os.path.join(inputDir, model)
	app = ps.app.Application.instance()
	model = app.importModel(psModel)
	end = getTime()
	log.info('\tImport End.  %s sec' % (end-start))
	return model

def	psSolve(model):
	log.info('\tSolve Start...')
	start = getTime()
	model.solve()
	end = getTime()
	solveTime = end - start
	log.info('\tSolved in %s sec' % (end - start))

def psSaveDxt(model, outputDir, modelName):
	name = modelName.split('.')
	dxtName = name[0] + ".dxt"
	app = ps.app.Application.instance()
	app.saveModel(os.path.join(outputDir, dxtName))

def setLogging():
	logger = logging.getLogger(__name__)
	logger.setLevel(logging.DEBUG)
	
	fh = logging.FileHandler('psPython.log')
	fh.setLevel(logging.INFO)
	
	ch = logging.StreamHandler()
	ch.setLevel(logging.INFO)
	
	formatter = logging.Formatter('%(asctime)s \t %(name)s  \t %(levelname)s \t %(message)s \t %(lineno)d')
	fh.setFormatter(formatter)
	ch.setFormatter(formatter)
	
	logger.addHandler(fh)
	logger.addHandler(ch)
	return logger

def getModel():
	app = ps.app.Application.instance()
	model = app.currentScenario
	return model

def objectToVector( list ):
	vector = ps.model.PeggingInfoVector()
	vector.extend(object for object in list)
	return vector

'''
	Above functions are basic functions.   Below is the core logic specific to the purpose of the script
'''

def getResFromGroup(model, resGroupName):
	'''
		Get resources for a given resource group
	'''
	resGroup = model.getResourceGroups()
	r = resGroup[resGroupName].getElements()
	resources = []
	for res in r:
		resources.append(res.code)
	return resources

def	setWoOp( model, resInGroup ):
	resSeq = {}
	res = model.getResources()
	
	for resource in resInGroup:
		log.info('Processing: %s ' % (resource) )
		r = res[resource]
		#print resource
		resSeq = model.solution.findResourceSchedule(r)										#Get the resource schedule
		
		'''		For each ai, get corresponding work order and schedule oerations so they are adjacent 	'''
		if resSeq:
			for ai in resSeq:																	#for each scheduled operation, get the work order if work order
				woOp = ai.getWorkOrderOperation()
				if woOp:																		#if it is a WO Operation
					woOp.firmStart(woOp.scheduleSpan[0]) 
					for bor in woOp.getWOResources():
						bor.allowOffloading = False
						bor.resetPlannedResource(bor.getChosenResource())
		else:
			log.info('***Nothing scheduled on resource: %s ' % (resource) )
			



if __name__ == "__main__":
	
	log = setLogging()
	#modelXml = sys.argv[1]
	Single = 'Single'
	Multi = 'Multi'	
	variables = setVariables('psPythonConfig.xml')
	outDir = variables['psOutputDirectory']
	
	#resources = variables['resource']
	#rList = resources.split()
	#print rList
	resGroupName = variables['resourceGroup']
	
	#myModel = openModel(variables['psInputDirectory'], modelXml)
	myModel = getModel()
	resInGroup = getResFromGroup(myModel, resGroupName)
	#psSolve(myModel) 
	setWoOp(myModel, resInGroup)

	#WO = psGetWoOp(myModel, outDir)
	
	#psSaveDxt(myModel, outDir, modelXml)
	
	

#/opt/splunk/bin/python
import sys
import ConfigParser
import os
splunkHome = os.environ.get('SPLUNK_HOME', '/opt/splunk')
sys.path.append(splunkHome + '/etc/apps/oovoo')
from azure.storage import BlobService
from azure.servicemanagement import ServiceManagementService
import threading
import signal
import re

sdkRegex = re.compile('/ooVoo.Sdk.Api/.+/Common')


class TimeoutException(Exception):
	pass


def getBlobService(config):
	return BlobService(config.get('Azure','subscription'),config.get('Azure','subscription_key'),config.get('Azure','protocol'))


def getSingleBlob(blobService,config,name):
	return blobService.get_blob(config.get('Azure','container_name'),name)

def getAllServiceDeployments(serviceMgr, config):
	allServices = serviceMgr.list_hosted_services()
	allDeployments = []
	for oneService in allServices:
		fetchDeploymentId(serviceMgr, oneService.service_name, allDeployments, config)	
	return allDeployments

def fetchDeploymentId(service, name, arr, config):
	srv = None
	try:
		srv = service.get_deployment_by_slot(name, config.get('Azure','slot_name'))
	except Exception, e:
		pass
	if srv:	
		arr.append(service.get_deployment_by_slot(name, config.get('Azure','slot_name')))


def getList(blobService, config, prefix):
	bulk = int(config.get('Flow','bulk'))
	marker = None
	return blobService.list_blobs(config.get('Azure','container_name'), prefix, marker, bulk)

def deleteBlob(blobService, config, name):
	blobService.delete_blob(config.get('Azure','container_name'), name)


def createBlobPrint(iBlobService, prefix, config):
	allBlobs = getList(iBlobService,config, prefix)
	if len(allBlobs) > 0:
		for oneBlob in allBlobs:
			blobData = getSingleBlob(iBlobService,config,oneBlob.name)
			dataStrs = blobData.split('\r\n')
			for string in dataStrs:
				if string and (not sdkRegex.search(oneBlob.name)):
				   try:		
					print(string.replace('\n','') + ' ' + oneBlob.name + '\n')
				   except Exception, e:
					print(string)


			#if config.get('Flow','delete') == 'yes':
			#	deleteBlob(iBlobService, config, oneBlob.name)

def main(argv):
	def timeout_handler(signum, frame):
		raise TimeoutException()

	timeout = int(argv[1])
	signal.signal(signal.SIGALRM, timeout_handler) 
        signal.alarm(timeout) # triger alarm in timeout seconds
	
	try:
		config = ConfigParser.ConfigParser()
		config.read([splunkHome + '/etc/apps/oovoo/config/app.conf'])
		#config.read('/root/oovoo/config/app.conf')
		sms = ServiceManagementService(config.get('Azure','subscription_id'),config.get('Azure','certificate'))	
		blobService = getBlobService(config)
		deployments = getAllServiceDeployments(sms, config)	
		for oneDeployment in deployments:
			createBlobPrint(blobService, oneDeployment.private_id, config)			
	except TimeoutException:
		print 'Script timeout ' + str(timeout)
		return -1
	return 0
#Load all data for Maxim
#Prod after use eat this
def main1(argv):
	config = ConfigParser.ConfigParser()
	config.read([splunkHome + '/etc/apps/oovoo/config/app.conf'])
	srv = BlobService('oovooperformancecounters','2o4VfvZTHjH73RECHt8CBbnjRKNy2Y/1aEkWn2/5c/1ai3OzBete19+AEr1PhFKK5xPF/cXVLAXOJNKs8XJSMw==',config.get('Azure','protocol'))
	#createBlobPrint(srv,'959bf94bc82e4aeb85310ec8297e56e4',config)	
	marker = None
        allBlobs =  srv.list_blobs(config.get('Azure','container_name'), '959bf94bc82e4aeb85310ec8297e56e4', marker, None)
	if len(allBlobs) > 0:
		for oneBlob in allBlobs:
			blobData = getSingleBlob(srv, config, oneBlob.name)
			blobFile = open('./' + oneBlob.name.replace('/','-'),'w')
			blobFile.write(blobData)
			blobFile.close()
			print 'File ' + oneBlob.name + ' saved'


	
if __name__ == '__main__':
	main(sys.argv)


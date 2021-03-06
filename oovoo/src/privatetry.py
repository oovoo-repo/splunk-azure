import sys
import os
import ConfigParser
sys.path.append('/root/oovoo')
splunkHome = os.environ.get('SPLUNK_HOME', '/opt/splunk')
from azure.storage import BlobService
from azure.servicemanagement import ServiceManagementService





def main(argv):
	config = ConfigParser.ConfigParser()
        #config.read([splunkHome + '/etc/apps/oovoo/config/app.conf'])
	config.read('/root/oovoo/config/app.conf')
	sms = ServiceManagementService(config.get('Azure','subscription_id'),config.get('Azure','certificate'))
	services = sms.list_hosted_services()
	for oneService in services:
		print('Service name:' + oneService.service_name)
	
	print 'Finish...'


if __name__ == '__main__':
	main(sys.argv)

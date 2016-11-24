from pysimplesoap.client import SoapClient

import logging.config

logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

url="http://energywatch.natgrid.co.uk/EDP-PublicUI/PublicPI/InstantaneousFlowWebService.asmx"
wsdl = "{0}?wsdl".format(url)
#client = SoapClient(wsdl="{0}?wsdl".format(url),trace=False)
import zeep
from zeep.transports import Transport
transport = Transport()
transport.http_headers['Accept Encoding'] = 'gzip'
client = zeep.Client(wsdl=wsdl, transport=transport)

print(client.service.GetInstantaneousFlowData())

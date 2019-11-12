import json
import configparser
import os
import requests
from akamai.edgegrid import EdgeGridAuth


config = configparser.ConfigParser()
config.read(os.path.join(os.path.expanduser("~"), '.edgerc'))
try:
    client_token = config['papi']['client_token']
    client_secret = config['papi']['client_secret']
    access_token = config['papi']['access_token']
    access_hostname = config['papi']['host']

    session = requests.Session()
    session.auth = EdgeGridAuth(
        client_token=client_token,
        client_secret=client_secret,
        access_token=access_token
    )

except (NameError, AttributeError, KeyError):
    print('edgerc file is missing or has invalid entries\n')
    exit()

# Search for the property to clone from
def searchProperty(configname):
    print("Inside search Property ", configname)
    headers = {"content-type": "application/json"}
    data = {"propertyName": configname}
    searchurl = 'https://' + access_hostname + '/papi/v1/search/find-by-value'
    searchresponse = session.post(searchurl, data=json.dumps(data), headers=headers)
    return searchresponse


def getAVersionInfo(contractid, groupid, propertyid, propertyversion):
    print("Inside getPropertyRules of papiwrapper. Printing contractid, sessionid,groupid,propertyid,propertyversion ",
          contractid, groupid, propertyid, propertyversion)
    headers = {"PAPI-Use-Prefixes": "true"}
    getpropertyrulesurl = 'https://' + access_hostname + '/papi/v1/properties/' + propertyid + '/versions/' + str(
        propertyversion) + '?contractId=' + contractid + '&groupId=' + groupid + '&validateRules=true&validateMode=fast'
    print("Get property rule url is ", getpropertyrulesurl)
    getpropertyruleresponse = session.get(getpropertyrulesurl, headers=headers)
    print("Debugging info")
    return getpropertyruleresponse


def cloneProperty(contractid, groupid, clonedata):
    print("Inside Clone Property Function")
    # headers = {"PAPI-Use-Prefixes": "true"}
    headers = {"content-type": "application/json"}
    cloneurl = 'https://' + access_hostname + '/papi/v1/properties?contractId=' + contractid + '&groupId=' + groupid 
    print("Clone url is ", cloneurl)
    cloneResponse = session.post(cloneurl, data=clonedata, headers=headers)
    return cloneResponse

def addHostNames(contractid,groupid,propertyid,hostdigitalproperty,hostnamedata):
    print("Inside Add Hostname function")
    headers = {"content-type": "application/json"}
    baseurl = 'https://' + access_hostname + '/papi/v1/properties/' + propertyid + '/versions/1/hostnames/?contractId=' + contractid + '&groupId=' + groupid + '&validateHostnames=true'
    result = session.put(baseurl,data=hostnamedata, headers=headers)
    return result

def getPropertyRuleTree(contractid, groupid, propertyid):
    print("Inside getPropertyRules of papiwrapper. Printing contractid, sessionid,groupid,propertyid,propertyversion ",
          contractid, groupid, propertyid)
    #headers = {"Content-Type": "true"}
    getpropertyrulesurl = 'https://' + access_hostname + '/papi/v1/properties/' + propertyid + '/versions/1/rules?contractId=' + contractid + '&groupId=' + groupid + '&validateRules=true&validateMode=fast'
    print("Get property rule url is ", getpropertyrulesurl)
    getpropertyruleresponse = session.get(getpropertyrulesurl)
    print("Debugging info")
    return getpropertyruleresponse


def updatePropertyRuleTree(contractid, groupid,propertyid,propertyruletreedata):
    print("Inside update property rule")
    headers = {"content-type": "application/json"}
    baseurl = 'https://' + access_hostname + '/papi/v1/properties/'+propertyid+'/versions/1/rules?contractId=' +contractid +'&groupId='+groupid+'&validateRules=true'
    print ("Baseurl for updatepropertyrule is ",baseurl)
    result = session.put(baseurl,data=propertyruletreedata,headers=headers)
    return result
    

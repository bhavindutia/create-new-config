import json


__all__=['PapWrapper']

class papiwrapper(object):
    """All basic operations that can be performed using PAPI """

    final_response = "NULL" #This variable holds the SUCCESS or FAILURE reason
    headers = {
        "Content-Type": "application/json"
    }

    access_hostname = "mandatory"
    property_name = "optional"
    version = "optional"
    notes = "optional"
    emails = "optional"
    groupId = "optional"
    contractId = "optional"
    propertyId = "optional"

    def __init__(self, access_hostname, property_name = "optional", \
                version = "optional",notes = "optional", emails = "optional", \
                groupId = "optional", contractId = "optional", propertyId = "optional"):
        self.access_hostname = access_hostname
        self.property_name = property_name
        self.version = version
        self.notes = notes
        self.emails = emails
        self.groupId = groupId
        self.contractId = contractId
        self.propertyId = propertyId


    def getGroups(self,session):
        groupUrl = 'https://' + self.access_hostname + '/papi/v1/groups'
        groupResponse = session.get(groupUrl)
        if groupResponse.status_code == 200:
            self.final_response = "SUCCESS"
        else:
            self.final_response = "FAILURE"
        return groupResponse

    #Search for the property to clone from
    def searchProperty(self,session,configname):
        print("Inside search Property ",configname)
        headers = {"content-type": "application/json"}
        data = {"propertyName":configname}
        searchurl = 'https://' + self.access_hostname + '/papi/v1/search/find-by-value'
        searchresponse = session.post(searchurl,data=json.dumps(data),headers=headers)
        return searchresponse

    def getAVersionInfo(self,session,contractid, groupid, propertyid,propertyversion):
        print("Inside getPropertyRules of papiwrapper. Printing contractid, sessionid,groupid,propertyid,propertyversion ",contractid,groupid,propertyid,propertyversion)
        headers = {"PAPI-Use-Prefixes": "true"}
        getpropertyrulesurl = 'https://' + self.access_hostname + '/papi/v1/properties/' + propertyid + '/versions/' + str(propertyversion) + '?contractId='+ contractid +'&groupId=' + groupid +'&validateRules=true&validateMode=fast'
        print("Get property rule url is ",getpropertyrulesurl)
        getpropertyruleresponse = session.get(getpropertyrulesurl, headers=headers)
        print("Debugging info")
        return getpropertyruleresponse



    def getPropertyRules(self,session,contractid, groupid, propertyid, propertyversion):
        print("Inside getPropertyRules of papiwrapper. Printing contractid, sessionid,groupid,propertyid,propertyversion ",contractid,groupid,propertyid,propertyversion)
        headers = {"PAPI-Use-Prefixes": "true"}
        getpropertyrulesurl = 'https://' + self.access_hostname + '/papi/v1/properties/' + propertyid + '/versions/' + str(propertyversion) + '/rules?contractId='+ contractid +'&groupId=' + groupid +'&validateRules=true&validateMode=fast'
        print("Get property rule url is ",getpropertyrulesurl)
        getpropertyruleresponse = session.get(getpropertyrulesurl, headers=headers)
        print("Debugging info")
        return getpropertyruleresponse

    def cloneProperty(self,session,contractid, groupid,clonedata):
        print("Inside Clone Property Function")
        #headers = {"PAPI-Use-Prefixes": "true"}
        headers = {"content-type": "application/json"}
        cloneurl = 'https://' + self.access_hostname + '/papi/v1/properties?contractId=' + contractid + '&groupId=' + groupid
        print ("Clone url is ",cloneurl)
        cloneResponse = session.post(cloneurl, data=clonedata, headers=headers)
        return cloneResponse





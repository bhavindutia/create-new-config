#!/usr/bin/env python
#Importing the libraries
import json
import re
import argparse
import yaml
from papiwrapper import searchProperty, getAVersionInfo, cloneProperty, addHostNames, getPropertyRuleTree,updatePropertyRuleTree

if __name__ == '__main__':
    print("\nLoading up!!! We are now reading your input, please give us a moment... \n \n \n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config", help="yaml file input")
    args=parser.parse_args()
    inputfilename=args.config
    # Extract the account/contract details from the YAML file.
    yamlhandle=yaml.load(open(inputfilename))
    configtoclonefrom = yamlhandle['OnboardConfig']['ConfigToCloneFrom'][0]
    print ("Config to Clone from ",configtoclonefrom)

    newpropertyname = yamlhandle['OnboardConfig']['NewConfigName'][0]
    print("New Config Name is ",newpropertyname)

    hostdigitalproperty = yamlhandle['OnboardConfig']['HostDigitalProperty'][0]
    print("DP: ",hostdigitalproperty)

    hostorigin = yamlhandle['OnboardConfig']['HostOrigin'][0]
    print("Origin: ", hostorigin)

    edgehostname = yamlhandle['OnboardConfig']['EdgeHostName'][0]
    print("Edge Host Name is ",edgehostname)

    #papiobject = papiwrapper(access_hostname)
    searchversionobject = searchProperty(configtoclonefrom)
    print (searchversionobject)

    propertyid = contractid = groupid = propertyversion = propertyetag = propertyid = ''
    activeonstaging = False


    #Search result gives response code of 200 even when no property is to be found
    print("\nStep 1) Searching for your property!... \n \n \n")
    if searchversionobject.status_code == 200:
        propertyversions = searchversionobject.json()['versions']['items']
        if len(propertyversions)>0:
            for propertyinfo in propertyversions:
                #print("Property Version is ",propertyversion['propertyVersion'])
                if propertyinfo['stagingStatus'] == 'ACTIVE':
                    print("\nStep 1) Found a staging version... \n \n \n")
                    print("Active Staging version is ",propertyinfo['propertyVersion'])
                    contractid = propertyinfo['contractId']
                    groupid = propertyinfo['groupId']
                    propertyversion = propertyinfo['propertyVersion']
                    propertyid = propertyinfo['propertyId']
                    print("Contractid, GroupID, PropertyID, PropertyVersion are ",contractid,groupid,propertyid,propertyversion)
                    activeonstaging = True
                    break


            # Getting a version info. Extracting etag and productID from it
            #propertyversionobject = papiobject.getAVersionInfo(session,contractid, groupid, propertyid,propertyversion)
            propertyversionobject = getAVersionInfo(contractid, groupid, propertyid,propertyversion)
            if propertyversionobject.status_code == 200:
                propertyetag = propertyversionobject.json()['versions']['items'][0]['etag']
                print ("Etag value is ",propertyetag)
                productid = propertyversionobject.json()['versions']['items'][0]['productId']
                print("Product ID is ", productid)

                clonedata = {
                    "productId": productid,
                    "propertyName": newpropertyname,
                    "cloneFrom": {
                        "propertyId": propertyid,
                        "version": propertyversion,
                        "copyHostnames": "false",
                        "cloneFromVersionEtag": propertyetag
                    }
                }

                clonedata = json.dumps(clonedata)
                print ("JSON Object is ",clonedata)


                #cloneobject = papiobject.cloneProperty(session, contractid, groupid,clonedata)
                cloneobject = cloneProperty(contractid, groupid, clonedata)
                if cloneobject.status_code == 201:
                    outputcatch = re.search('(.*)\/properties\/(.*)\?(.*)',str(cloneobject.json()))  ### Property ID stored in the below variable.
                    propertyid = outputcatch.group(2)
                    print("propertyid is ", propertyid)


                    #Update config with Hostnames
                    hostnamedata = [{
                        "cnameTo": edgehostname,
                        "cnameFrom": hostdigitalproperty,
                        "cnameType": "EDGE_HOSTNAME",
                        "secure":"true"
                    }]

                    hostnamedata = json.dumps(hostnamedata)
                    print("JSON Object of hostnamedata is ", hostnamedata)


                    result = addHostNames(contractid, groupid, propertyid,hostdigitalproperty,hostnamedata)
                    if result.status_code == 200:
                        print("Config updated successfully with hostnames")
                        #Download property rule JSON object

                        propertyruletreeobject = getPropertyRuleTree(contractid, groupid, propertyid)
                        if propertyruletreeobject.status_code == 200:
                            print("Newly created property with updated hostnames found")
                            propertyruletreeobject = propertyruletreeobject.json()
                            print ("Downloaded property rule tree json object is ", propertyruletreeobject)

                            originvariablevalue = propertyruletreeobject['rules']['variables'][0]['value']
                            if originvariablevalue:
                                print ("Origin variable value is ",propertyruletreeobject['rules']['variables'][0]['value'])
                                #Update the variable
                                propertyruletreeobject['rules']['variables'][0]['value'] = hostorigin
                                print("Updated Downloaded property rule tree json object is ", propertyruletreeobject)

                                #Pushing the json object with updated origin

                                updatepropertyruletreeobject = updatePropertyRuleTree(contractid,groupid,propertyid,json.dumps(propertyruletreeobject))
                                if updatepropertyruletreeobject.status_code == 200:
                                    print("Property updated with specified origin")
                                else:
                                    print("Reason of failure. Details:",updatepropertyruletreeobject.json()['detail'])
                                    print("Something went wrong in updating property with specified origin")


                            else:
                                print ("Origin variable not found")


                        else:
                            print ("Couldn't find newly created property with updated hostnames")
                            exit()

                    

                    else:
                        print("Something went wrong in updating config with hostnames")
                        print("Error while cloning: ", result.json()['title'])
                        exit()


                else:
                    print("Sorry, something went wrong with the configuration creation! Exiting the program now!\n \n")
                    print ("Error while cloning: ",cloneobject.json()['title'])

            else:
                print("Couldn't get a property version detail")
                exit()


        else:
            print("No active version of the property results found")
            exit()

    else:
    	print ('Something went wrong with the search\n')
    	exit()

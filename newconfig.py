#!/usr/bin/env python
#Importing the libraries
import requests
import json
from akamai.edgegrid import EdgeGridAuth
from urllib.parse import urljoin
from openpyxl import load_workbook
import re
import openpyxl, pprint
import sys
import argparse
from datetime import datetime
import calendar
import yaml
import time
from papiwrapper import papiwrapper
import configparser
import os

if __name__ == '__main__':
    print("\nLoading up!!! We are now reading your input, please give us a moment... \n \n \n")

    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--config", help="yaml file input")
    args=parser.parse_args()
    inputfilename=args.config
    # Extract the account/contract details from the YAML file.
    yamlhandle=yaml.load(open(inputfilename))
    #Extracting the contract ID.
    contractid = yamlhandle['OnboardConfig']['Account'][0]
    #Extracting the group ID.
    groupid=yamlhandle['OnboardConfig']['Account'][1]
    print (contractid,groupid)

    configtoclonefrom = yamlhandle['OnboardConfig']['ConfigToCloneFrom'][0]
    print ("Config to Clone from ",configtoclonefrom)

    newpropertyname = yamlhandle['OnboardConfig']['NewConfigName'][0]
    print("New Config Name is ",newpropertyname)

    config = configparser.ConfigParser()
    config.read(os.path.join(os.path.expanduser("~"),'.edgerc'))

    try:
    	client_token = config['papi']['client_token']
    	client_secret = config['papi']['client_secret']
    	access_token = config['papi']['access_token']
    	access_hostname = config['papi']['host']
    	
    	session = requests.Session()
    	session.auth = EdgeGridAuth(
    		client_token = client_token,
    		client_secret = client_secret,
    		access_token = access_token
            	)
		
    except (NameError, AttributeError, KeyError):
    	print ('edgerc file is missing or has invalid entries\n')
    	exit()

    papiobject = papiwrapper(access_hostname)
    searchversionobject = papiobject.searchProperty(session,configtoclonefrom)
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
            propertyversionobject = papiobject.getAVersionInfo(session,contractid, groupid, propertyid,propertyversion)
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


                cloneobject = papiobject.cloneProperty(session, contractid, groupid,clonedata)
                if cloneobject.status_code == 201:
                    outputcatch = re.search('(.*)\/properties\/(.*)\?(.*)',str(cloneobject.json()))  ### Property ID stored in the below variable.
                    propertyid = outputcatch.group(2)
                    print("propertyid is ", propertyid)

                    #Update config with Hostnames

                else:
                    print("Sorry, something went wrong with the configuration creation! Exiting the program now!\n \n")
                    print(cloneobject.json())

            else:
                print("Couldn't get a property version detail")
                exit()


        else:
            print("No results found. Please check the property you want to clone from")
            exit()

    else:
    	print ('Something went wrong with the search\n')
    	exit()

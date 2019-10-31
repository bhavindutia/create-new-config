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

    configname = yamlhandle['OnboardConfig']['ConfigName'][0]
    print (configname)

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
    searchobject = papiobject.searchProperty(session,configname)
    print (searchobject)

    propertyid = contractid = groupid = ''
    activeonprod = False


    #Search result gives response code of 200 even when no property is to be found
    print("\nStep 1) Searching for your property!... \n \n \n")
    if searchobject.status_code == 200:
        propertyversions = searchobject.json()['versions']['items']
        if len(propertyversions)>0:
            for propertyinfo in propertyversions:
                #print("Property Version is ",propertyversion['propertyVersion'])
                if propertyinfo['stagingStatus'] == 'ACTIVE':
                    print("Active Staging version is ",propertyinfo['propertyVersion'])
                    contractid = propertyinfo['contractId']
                    groupid = propertyinfo['groupId']
                    propertyid = propertyinfo['propertyId']
                    propertyversion = propertyinfo['propertyVersion']
                    #print("Contractid, GroupID, PropertyID, PropertyVersion are ",contractid,groupid,propertyid,propertyversion)
                    activeonprod = True
                    break

        else:
            print("No results found. Please check the property you want to clone from")
            exit()

    else:
    	print ('Something went wrong with the search\n')
    	exit()

#Search is successful and we want to download version on prod
    if activeonprod:
        print("\nStep 2) Found your property! Downloading it... \n \n \n")
        print("Contractid, GroupID, PropertyID, PropertyVersion are ", contractid, groupid, propertyid, propertyversion)
        getpropertyinfo = papiobject.getPropertyRules(session,contractid, groupid, propertyid, propertyversion)

        if getpropertyinfo.status_code == 200:
            if not os.path.exists('downloadedproperties'):
                os.makedirs('downloadedproperties')
            try:
                with open(os.path.join('downloadedproperties', configname+'.json'), 'w') as propertywritefilehandler:
                    propertywritefilehandler.write(json.dumps(getpropertyinfo.json(), indent=4))
                    print("Downloaded the property you want to clone from at ",'downloadedproperties/'+configname+'.json')

            except FileNotFoundError:
                print('Unable to write file ' + configname + '.json')
                exit()

            print("Step 3) Reading the written file")

            try:
                with open(os.path.join('downloadedproperties', configname + '.json'), 'r') as propertyreadfilehandler:
                    propertystringcontent = propertyreadfilehandler.read()
                    print("Read property is  ",propertystringcontent)

            except FileNotFoundError:
                print('Unable to read file ' + configname + '.json')
                exit()



        else:
            print ("Couldn't download the property")
            exit()


    else:
        print("No active version found on Production. Flag activeonprod didn't get set to true")
        exit()








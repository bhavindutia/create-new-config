# Create New Configs

Create new config based on existing config. Then update origin and add hostnames and push it out to staging


## Installation Guide

### Step 1: Install the neccesary python libraries
```
pip3 install requests
pip3 install edgegrid-python
pip3 install pyyaml
```
### Step 2: Configure your input.yaml file
```
OnboardConfig:
 ConfigToCloneFrom:
  - foo.example.com
 NewConfigName:
  - bar.example.com
 DigitalProperty:
  - bar.example.com
 HostOrigin:
  - origin.bar.example.com<br />
 CommonName:
  - '*.example.com'
```

### Step 3: Configure your Akamai Credentials [here](https://developer.akamai.com/api/getting-started). Then update credential.yaml file as below

Enter the appropriate API secrets within credentials.yml
```
Credentials:
  - https://akab-xxxxx   <-- Base URL
  - akab-xxxxxx          <-- Client Token
  - jcHFxxxxxxxxxx       <-- Client Secret
  - akab-vxxxx           <-- Access Token
```

## Usage Instructions

Execute the python script
```
python3 hulkcreator.py -f input.yml
```
This script will create a config based on template config. Update the config with Digital Property, Origin, Edgehostname as mentioned in yaml file. 

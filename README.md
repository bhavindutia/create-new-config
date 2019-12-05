# Create New Configs

Create new config based on existing config. Then update origin and add hostnames and push it out to staging

## Installation Guide

### Step 1: Install the neccesary python libraries

pip3 install requests
pip3 install edgegrid-python
pip3 install pyyaml

## Step 2: Configure your YAML file

OnboardConfig:
 \ConfigToCloneFrom:
  - foo.example.coom
 NewConfigName:
  - bar.example.coom
 DigitalProperty:
  - bar.example.com
 HostOrigin:
  \- origin.example.com
 EdgeHostName:
  \- bar.example.com.edgekey.net
 CommonName:
  \- '*.example.com

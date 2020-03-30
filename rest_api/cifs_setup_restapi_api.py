#! /usr/bin/env python3

"""
ONTAP REST API Python Sample Scripts

This script was developed by NetApp to help demonstrate NetApp technologies. This
script is not officially supported as a standard NetApp product.

Purpose: THE FOLLOWING SCRIPT SHOWS CIFS SETUP OPERATIONS USING REST API.

usage: python3 cifs_setup_restapi_api.py [-h] -c CLUSTER [-u API_USER]
                                     [-p API_PASS]

Copyright (c) 2020 NetApp, Inc. All Rights Reserved.
Licensed under the BSD 3-Clause “New” or Revised” License (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
https://opensource.org/licenses/BSD-3-Clause

"""

import sys,time,base64,argparse,requests,json,requests,logging
from getpass import getpass
requests.packages.urllib3.disable_warnings()



def get_size(vol_size):
    tmp = int(vol_size) * 1024 * 1024
    return tmp

def get_svms():
    
    url = "https://{}/api/svm/svms".format(cluster)
    try:
        r = requests.get(url, headers=headers,verify=False)
    except requests.exceptions.HTTPError as err:
        print (str(err))
        sys.exit(1)		
    except requests.exceptions.RequestException as err:
        print (str(err)) 
        sys.exit(1)
    url_text = r.json()
    if 'error' in url_text:
        print (url_text)
        sys.exit(1)
    
    return r.json()

def show_svm(cluster,base64string,headers):
    
    url = "https://{}/api/svm/svms".format(cluster)
    try:
        r = requests.get(url, headers=headers,verify=False)
    except requests.exceptions.HTTPError as err:
        print (str(err))
        sys.exit(1)		
    except requests.exceptions.RequestException as err:
        print (str(err)) 
        sys.exit(1)
    url_text = r.json()
    if 'error' in url_text:
        print (url_text)
        sys.exit(1)
    
    tmp = dict(r.json())
    svms = tmp['records']
    print()
    print("List of SVMs:- ")
    print("================")
    for i in svms:
        print(i['name'])

    return r.json()

def show_volume(cluster,base64string,headers,svm_name):
    
    print()
    print ("Getting Volume Details")
    print ("======================")
    url = "https://{}/api/storage/volumes/?svm.name={}".format(cluster,svm_name)
    try:
        r = requests.get(url, headers=headers,verify=False)
    except requests.exceptions.HTTPError as err:
        print (str(err))
        sys.exit(1)		
    except requests.exceptions.RequestException as err:
        print (str(err)) 
        sys.exit(1)
    url_text = r.json()
    if 'error' in url_text:
        print (url_text)
        sys.exit(1)
    
    tmp = dict(r.json())
    svms = tmp['records']
    print()
    print("List of Volumes :- ")
    print("===================")
    for i in svms:
        print(i['name'])
    return r.json()


def cifs_setup(cluster,base64string,headers):

    print("THE FOLLOWING SCRIPT DEMOSTRATES CIFS SETUP USING REST API .")
    print("====================================================================")
    print()
    show_svm(cluster,base64string,headers)
    print()
    svm_name = input("Choose the SVM on which you would like to create a CIFS Share :")
    print("Make sure that NAS  LIFs on each nodes are created on the SVM :")
    print()
    
    print("Enable CIFS Protocol:-")
    print("======================")
    
    fqdn = input("Input the Fully Qualified Domain Name :")
    organizational_unit = input("Input the Org Unit :")
    password = input("Input the Password :")
    user = input("Input the User :")
    
    payload1={
    "ad_domain": {
    "fqdn": fqdn,
    "organizational_unit": organizational_unit,
    "password": password,
    "user": user
     },
    "comment": "This CIFS Server",
    "enabled": bool("true"),
    "svm": {
    "name": svm_name
    },
    "name": "cifsserver"
    }
    
    
    url1 = "https://{}/api/protocols/cifs/services".format(cluster)
    try:
        response = requests.post(url1,headers=headers,json=payload1,verify=False)
    except requests.exceptions.HTTPError as err:
        print (str(err))
        sys.exit(1)		
    except requests.exceptions.RequestException as err:
        print (str(err)) 
        sys.exit(1)
    url_text = response.json()
    if 'error' in url_text:
        print (url_text)
        sys.exit(1)
    
    print()
    print("Create the Volume:-")
    print("===================")
    vol_name = input("Enter the Volume Name to create CIFS Share:-")
    vol_size = input("Enter the Volume Size in MBs :-")
    aggr_name = input("Enter the aggregate name:-")
	
    v_size=get_size(vol_size)

    pather = "/" + vol_name 

    payload2 = {
    "aggregates": [{"name": aggr_name }],
    "svm": {"name":svm_name},
    "name": vol_name,
    "size": v_size,
    "nas": {"security_style": "ntfs","path": pather }
    }
    
    url2 = "https://{}/api/storage/volumes".format(cluster)
    try:
        response = requests.post(url2,headers=headers,json=payload2,verify=False)
    except requests.exceptions.HTTPError as err:
        print (str(err))
        sys.exit(1)		
    except requests.exceptions.RequestException as err:
        print (str(err)) 
        sys.exit(1)
    url_text = response.json()
    if 'error' in url_text:
        print (url_text)
        sys.exit(1)
    
    print()
    print("Create the Share:-")
    print("==================")

    share_name = input("Enter the share  name:-")

    payload3 = {
    "path": pather,
    "svm": {
    "name": svm_name,
     },
     "name": share_name
     }

    
    url = "https://{}/api/protocols/cifs/shares".format(cluster)
    try:
        response = requests.post(url,headers=headers,json=payload3,verify=False)
    except requests.exceptions.HTTPError as err:
        print (str(err))
        sys.exit(1)		
    except requests.exceptions.RequestException as err:
        print (str(err)) 
        sys.exit(1)
    url_text = response.json()
    if 'error' in url_text:
        print (url_text)
        sys.exit(1)
    
    return
	
def parse_args() -> argparse.Namespace:
    """Parse the command line arguments from the user"""

    parser = argparse.ArgumentParser(
        description="This script will execute CIFS operations using ONTAP REST APIs.",
    )
    parser.add_argument(
        "-c", "--cluster", required=True, help="API server IP:port details"
    )
    parser.add_argument("-u", "--api_user", default="admin", help="API Username")
    parser.add_argument("-p", "--api_pass", help="API Password")
    parsed_args = parser.parse_args()

    # collect the password without echo if not already provided
    if not parsed_args.api_pass:
        parsed_args.api_pass = getpass()

    return parsed_args


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] [%(levelname)5s] [%(module)s:%(lineno)s] %(message)s",
    )
    args = parse_args()
    base64string = base64.encodestring(('%s:%s' %(args.api_user,args.api_pass)).encode()).decode().replace('\n', '')
	
    headers = {
    'authorization': "Basic %s" % base64string,
    'content-type': "application/json",
    'accept': "application/json"
    }
	
    cifs_setup(args.cluster,base64string,headers) 
    print ("Script Complete")

	

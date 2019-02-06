import requests
import urllib3 
import getpass
import json
from pprint import pprint 

urllib3.disable_warnings()

def dnac_login(username, password, host):
  login_url='https://' + host + '/api/system/v1/auth/token'
  session = requests.session()
  session.auth = username, password
  session.verify = False
  session.headers.update({'Content-Type':'application/json'})
  
  login_results = session.post(login_url)
  
  #token  = login_results.json()['Token']
  
  return session, login_results

def get_inventory(host, session):
    
    inventory_url = 'https://' + host + '/api/v1/network-device'
    inventory_results = session.get(inventory_url)
    return inventory_results.json()

def list_hosts(inventory, session):

    host_list = [(host['managementIpAddress'], host['hostname'], host['id']) for host in inventory['response']]
    
    return host_list

def get_groups(host, session):

    group_url = 'https://' + host + '/api/v1/group'
    group_results = session.get(group_url)

    groups = group_results.json()['response']

    return groups

def get_group_members(host, session, group_name):
    #passhttps://dnac-prod.campus.wwtatc.local/api/v1/group/member?groupNameHierarchy=Global%2FDemo%20Environment%2FData%20Center%202&memberType=networkdevice&sortBy=groupName&order=asc
    
    group_name = 'Global/Demo Environment/Data Center 2'
    group_member_url = 'https://' + host + '/api/v1/group/member?groupNameHierarchy=' + group_name + '&memberType=networkdevice'
    results = session.get(group_member_url)
    return results 

if __name__ == "__main__":

    pwd = getpass.getpass("What is your password:")
    host = 'dnac-prod.campus.wwtatc.local'
    
    session, results = dnac_login('andiorij',pwd,host)
    
    if results.status_code == 200:
        print("logged in successfully")
        session.headers.update({'x-auth-token':results.json()['Token']})

    inventory = get_inventory('dnac-prod.campus.wwtatc.local',session)
    
    list_of_hosts = list_hosts(inventory, session)

    pprint(list_of_hosts)

    # groups = list_groups(host, session)

    # g_list = [(group['name'],group['id']) for group in groups if not group['systemGroup']]
    
    # pprint(g_list)
    
    print('-'*80)
    print('This is the list of group members')
    print('-'*80)
    
    gm = get_group_members(host, session, 'Global/Demo Environment/Data Center 2')
    pprint(gm.json())
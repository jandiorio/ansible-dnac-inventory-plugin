try: 
    import requests
except ImportError:
    print('failed to import requests module.  verify the module is installed.')
    SystemExit

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

def get_hosts(inventory):

    host_list = [ (host['managementIpAddress'], host['hostname'], host['id']) for host in inventory['response'] if host['type'].find('Access Point') == -1 ]
    
    return host_list

# def get_groups(host, session):

#     group_url = 'https://' + host + '/api/v1/group'
#     group_results = session.get(group_url)

#     groups = group_results.json()['response']
    
#     groups = [(group['name'], group['id']) for group in groups if group['systemGroup'] == False]
#     return groups

def _get_groups(host, session):
    '''
        :return A list of tuples for groups containing the group name and the unique ID of the group.
    '''
    group_url = 'https://' + host + '/api/v1/group'
    group_results = session.get(group_url)

    groups = group_results.json()['response']
    
    group_list = []
    group_dict = {}
    
    # groups = [(group['name'], group['id']) for group in groups if group['systemGroup'] == False]
    for group in groups: 
        if group['systemGroup'] == False: 
            group_dict = {}
            group_dict.update({'name': group['name'].replace(' ','_').lower(), 'id': group['id']})
            group_list.append(group_dict)
        else: 
            continue
    return group_list

def get_group_members(host, session, group_id):
    
    group_member_url = 'https://' + host + '/api/v1/group/member?id=' + group_id + '&memberType=networkdevice'
    results = session.get(group_member_url)
    gm = results.json()
    group_members = [(member['hostname'], member['managementIpAddress']) for member in gm['response']]
    
    return group_members

def get_member_site(device_id):
    
    site_assignments = 'https://' + host + '/api/v1/member/group?id=' + device_id 
    results = session.get(site_assignments)
    sites = results.json()
    
    site_name = [ site['name'] for site in sites['response'][device_id] if 'SITE' in site['groupTypeList'] ]
    
    if len(site_name) == 1:
        site_name = site_name[0].replace(' ','_').lower()
        return site_name
    else: 
        sys.exit

if __name__ == "__main__":

    pwd = '8635Dav1nc11417!'
    #pwd = getpass.getpass("What is your password:")
    host = 'dnac-prod.campus.wwtatc.local'
    
    try:
        session, results = dnac_login('andiorij',pwd,host)

        if results.status_code == 200:
            print("logged in successfully")
            session.headers.update({'x-auth-token':results.json()['Token']})
    except Exception:
        print("Failed to establish a session\n",results.status_code)


    # obtain unfiltered inventory
    print("-"*80)
    print("Obtain Inventory from DNA Center...")
    inventory = get_inventory('dnac-prod.campus.wwtatc.local',session)
    # for device in inventory['response']: 
    #     print(device['hostname'])

    # Get all Groups 
    print("-"*80)
    print("Obtain Groups from DNA Center...")
    groups = _get_groups(host, session)
    #pprint(groups)
    
    #Get Network Devices in Group 
    inventory_list = []

    print('printing groups')
    print('='*80)
    pprint(groups)
    print('='*80)
    
    # inv = {}
    # for group in groups: 
        
    #     gm = get_group_members(host, session, group[1])

    #     if len(gm) > 1: 
    #         inventory_list.append({group[0]:[]})
    #         print(group[0])
    #         #pprint(gm)
    #         for member in gm: 
    #             members = members.update(
    #                 {'hostname:':member[0],
    #                  'ansible_host':member[1]
    #                 }
    #             )
            
    #             #print(member[0] + '\n    ansible_host: ' + member[1])
    # pprint(inventory_list)
    
    print('-'*80)
    print('parsing hosts...')

    list_of_hosts = get_hosts(inventory)

    pprint(list_of_hosts)

    # pprint(list_of_hosts)

    # # groups = list_groups(host, session)

    # # g_list = [(group['name'],group['id']) for group in groups if not group['systemGroup']]
    
    # # pprint(g_list)
    
    # print('-'*80)
    # print('This is the list of group members')
    # print('-'*80)
    
    # gm = get_group_members(host, session, 'Global/Demo Environment/Data Center 2')
    # pprint(gm.json())


# Get the groups

# Loop through groups and get members 

#
site = get_member_site('b3c955b7-40a6-4b5e-9116-9980f14f07ee')
print('*'*80)
print(site)

print('*'*80)
# pprint(inventory)

#/usr/bin/python

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
    name: dna_center
    plugin_type: inventory
    short_description: Returns Inventory from DNA Center
    description:
        - Retrieves inventory from DNA Center
        - Adds inventory to ansible working inventory

    options:
        plugin:  
            description: Name of the plugin
            required: true
            choices: ['dna_center']
        host: 
            description: FQDN of the target host 
            required: true
        username: 
            description: user credential for target system 
            required: true
        password: 
            description: user pass for the target system
            required: true
'''

EXAMPLES = r'''
    # ansible -i 'host1.example.com, host2' -m user -a 'name=me state=absent' all
'''

from ansible.errors import AnsibleError, AnsibleParserError
from ansible.module_utils._text import to_bytes, to_native
from ansible.parsing.utils.addresses import parse_address
from ansible.plugins.inventory import BaseInventoryPlugin
import json
import sys

try: 
    import requests
except ImportError:
    raise AnsibleError("Python requests module is required for this plugin.")

from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class InventoryModule(BaseInventoryPlugin):

    NAME = 'dna_center'

    def __init__(self):
        super(InventoryModule, self).__init__()

        # from config 
        self.username = None
        self.password = None
        self.host = None
        self.session = None

    def _login(self):
        '''
            :return Login results from the request.
        '''
        login_url='https://' + self.host + '/api/system/v1/auth/token'
        self.session = requests.session()
        self.session.auth = self.username, self.password
        self.session.verify = False
        self.session.headers.update({'Content-Type':'application/json'})
        
        try:
            login_results = self.session.post(login_url)
        except Exception as e:
            raise AnsibleError('failed to login to DNA Center: {}'.format(e.message))

        if login_results.status_code not in [200, 201, 202, 203, 204]:
          raise AnsibleError('failed to login. status code was not in the 200s')
        else: 
            self.session.headers.update({'x-auth-token':login_results.json()['Token']})
            
            return login_results

    def _get_inventory(self):
        '''
            :return The json output from the request object response. 
        '''
        inventory_url = 'https://' + self.host + '/api/v1/network-device'
        inventory_results = self.session.get(inventory_url)
        return inventory_results.json()

    def _get_hosts(self, inventory):
        '''
             :param inventory A list of dictionaries representing the entire DNA Center inventory. 
             :return A List of tuples that include the management IP, device hostnanme, and the unique indentifier of the device.
        '''
        #host_list = [ (host['managementIpAddress'], host['hostname'], host['id']) for host in inventory['response'] if host['type'].find('Access Point') == -1 ]
        host_list = []

        for host in inventory['response']: 
            if host['type'].find('Access Point') == -1: 
                host_dict = {}
                host_dict.update({
                    'managementIpAddress': host['managementIpAddress'],
                    'hostname' : host['hostname'],
                    'id': host['id'],
                    'os': host['softwareType'], 
                    'version': host['softwareVersion']
                })
                host_list.append(host_dict)

        return host_list

    def _get_groups(self):
        '''
            :return A list of tuples for groups containing the group name and the unique ID of the group.
        '''
        group_url = 'https://' + self.host + '/api/v1/group'
        group_results = self.session.get(group_url)

        groups = group_results.json()['response']
        
        group_list = []
        
        # Build a list of dictionaries
        for group in groups: 
            if group['systemGroup'] == False: 
                group_dict = {}
                if group['name']:
                    group_dict.update({'name': group['name'].replace(' ','_').lower(), 'id': group['id']})
                    group_list.append(group_dict)
            else: 
                continue
        return group_list

    def _get_member_site(self, device_id):
        '''
            :param device_id: The unique identifier of the target device.
            :return A single string representing the name of the SITE group of which the device is a member.
        '''
        site_assignments = 'https://' + self.host + '/api/v1/member/group?id=' + device_id 
        results = self.session.get(site_assignments)
        sites = results.json()
        
        site_name = [ site['name'] for site in sites['response'][device_id] if 'SITE' in site['groupTypeList'] ]
        
        if len(site_name) == 1:
            site_name = site_name[0].replace(' ','_').lower()
            return site_name
        else: 
            sys.exit

    def verify_file(self, path):
        return True  # looks good

    def parse(self, inventory, loader, path, cache=True):
        
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        
        # initializes variables read from the config file based on the documentation string definition. 
        #  if the options are not defined in the docstring, the are not imported from config file
        self._read_config_data(path)

        try:
            self.host = self.get_option('host')
            self.username = self.get_option('username')
            self.password = self.get_option('password')

        except Exception as e: 
            raise AnsibleParserError('getting options failed:  {}'.format(e))

        login_results = self._login()

        inventory = self._get_inventory()

        host_list = self._get_hosts(inventory)
      
        #  add groups to the inventory 
        group_list = self._get_groups()
        for group in group_list: 
            self.inventory.add_group(group['name'])

        #  add the hosts to the inventory 
        for h in host_list: 
            site_name = self._get_member_site( h['id'] )
            if site_name:
              self.inventory.add_host(h['hostname'], group=site_name)
              #  add variables to the hosts
            #   self.inventory.set_variable(h['hostname'],'ansible_host',h['managementIpAddress'])
              self.inventory.set_variable(h['hostname'], 'os', h['os'])
              self.inventory.set_variable(h['hostname'], 'version', h['version'])
              if h['os'].lower() in ['ios', 'ios-xe']:
                  self.inventory.set_variable(h['hostname'], 'ansible_network_os', 'ios')
                  self.inventory.set_variable(h['hostname'], 'ansible_connection', 'network_cli')
                  self.inventory.set_variable(h['hostname'], 'ansible_become', 'yes')
                  self.inventory.set_variable(h['hostname'], 'ansible_become_method', 'enable')
              elif h['os'].lower() in ['nxos']:
                  self.inventory.set_variable(h['hostname'], 'ansible_network_os', 'nxos')
                  self.inventory.set_variable(h['hostname'], 'ansible_connection', 'network_cli')
                  self.inventory.set_variable(h['hostname'], 'ansible_become', 'yes')
                  self.inventory.set_variable(h['hostname'], 'ansible_become_method', 'enable')
        #  add variables to the hosts 
        #  - ansible_network_connection: network_cli 
        #  - ansible_network_os: validate os
        # 

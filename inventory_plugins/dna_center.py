# Copyright (c) 2019 World Wide Technology
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

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
        validate_certs: 
            description: certificate validation
            required: false
            choices: ['yes', 'no']
        use_dnac_mgmt_int: 
            description: map the dnac mgmt interface to `ansible_host`
            required: false
            default: true
            choices: [true, false]
'''

EXAMPLES = r'''
    ansible-inventory --graph
    
    ansible-inventory --list 
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

class InventoryModule(BaseInventoryPlugin):

    NAME = 'dna_center'

    def __init__(self):
        super(InventoryModule, self).__init__()

        # from config 
        self.username = None
        self.password = None
        self.host = None
        self.session = None
        self.use_dnac_mgmt_int = None


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
            raise AnsibleError('failed to login to DNA Center: {}'.format(e))

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
                    group_dict.update({
                                      'name': group['name'].replace(' ','_').lower(),
                                      'id': group['id'],
                                      'parentId': group['parentId']
                                      })
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


    def _add_groups(self, group_list):
        ''' Add groups and associate them with parent groups
            :param group_list: list of group dictionaries containing name, id, parentId
        '''
            
        # Global is a system group and the parent of all top level groups
        group_ids = [grp['id'] for grp in group_list ]
        parent_name = ''

        for group in group_list: 

            self.inventory.add_group(group['name'])
            
            if group['parentId'] in group_ids:
                parent_name = [grp['name'] for grp in group_list if grp['id'] == group['parentId'] ][0]
            
                try: 
                    self.inventory.add_child(parent_name, group['name'])
                except Exception as e:
                    raise AnsibleParserError('adding child groups failed:  {} \n {}:{}'.format(e,group['name'],parent_name))


    def _add_hosts(self, host_list):
        """
            Add the devicies from DNAC Inventory to the Ansible Inventory
            :param host_list: list of dictionaries for hosts retrieved from DNAC

        """
        for h in host_list: 
            site_name = self._get_member_site( h['id'] )
            if site_name:
              self.inventory.add_host(h['hostname'], group=site_name)
              
              #  add variables to the hosts
              if self.use_dnac_mgmt_int:
                  self.inventory.set_variable(h['hostname'],'ansible_host',h['managementIpAddress'])

              self.inventory.set_variable(h['hostname'], 'os', h['os'])
              self.inventory.set_variable(h['hostname'], 'version', h['version'])
              if h['os'].lower() in ['ios', 'ios-xe']:
                  self.inventory.set_variable(h['hostname'], 'ansible_network_os', 'ios')
                  self.inventory.set_variable(h['hostname'], 'ansible_connection', 'network_cli')
                  self.inventory.set_variable(h['hostname'], 'ansible_become', 'yes')
                  self.inventory.set_variable(h['hostname'], 'ansible_become_method', 'enable')
              elif h['os'].lower() in ['nxos','nx-os']:
                  self.inventory.set_variable(h['hostname'], 'ansible_network_os', 'nxos')
                  self.inventory.set_variable(h['hostname'], 'ansible_connection', 'network_cli')
                  self.inventory.set_variable(h['hostname'], 'ansible_become', 'yes')
                  self.inventory.set_variable(h['hostname'], 'ansible_become_method', 'enable')


    def verify_file(self, path):
        
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(('dnac.yaml', 'dnac.yml', 'dna_center.yaml', 'dna_center.yml')):
                valid = True
        return valid


    def parse(self, inventory, loader, path, cache=True):
        
        super(InventoryModule, self).parse(inventory, loader, path, cache)
        
        # initializes variables read from the config file based on the documentation string definition. 
        #  if the options are not defined in the docstring, the are not imported from config file
        self._read_config_data(path)

        # Set options values from configuration file
        try:
            self.host = self.get_option('host')
            self.username = self.get_option('username')
            self.password = self.get_option('password')
            self.map_mgmt_ip = self.get_option('use_dnac_mgmt_int')
        except Exception as e: 
            raise AnsibleParserError('getting options failed:  {}'.format(e))

        # Attempt login to DNAC
        login_results = self._login()
        if login_results.status_code not in [200,201,202,203]: 
            raise AnsibleError('failed to login: {}'.format(login_results.status_code))
        
        # Obtain Inventory Data
        inventory = self._get_inventory()
      
        #  add groups to the inventory 
        group_list = self._get_groups()
        self._add_groups(group_list)
        
        #  add the hosts to the inventory 
        host_list = self._get_hosts(inventory)
        self._add_hosts(host_list)
DNA Center Inventory Plugin
=============================
DNA Center Inventory Plugin allows you to utilize the network discovery
capabilities of Cisco's DNA Center controller as a source of inventory for
Ansible Playbooks. 

Functionality 
--------------
The DNA Center Inventory plugin will gather all groups (sites) and inventory devices from DNA Center.  The hosts are associated with appropriate sites.  

The following host_vars are associated with the network devices: 
- `ansible_connection` : **network_cli** for ios and nxos devices
- `ansible_become_method` : for ios and nxos types. 
- `ansible_become` : yes for ios and nxos types. 
- `ansible_host` : using the managementIpAddress from DNA Center - conditionally mapped based on control file `dna_center.yml`
- `ansible_network_os` : derived from `os` below and required for Ansible network_cli connection plugin
- `os` : network operating system as stored in DNA Center's `softwareType`
- `version` : network operating system version as stored in DNA Center's `softwareVersion`

Requirements
-------------
- Python
- Python requests module
- Ansible 

Setup
------
- Clone or fork this repo
- place the files in the appropriate location or update the environment
  variable with the location

Most ansible inventory plugins are disabled by default so the must be enabled
to be used. 

The Ansible documentation will explain how to consume inventory plugins. 

https://docs.ansible.com/ansible/latest/plugins/inventory.html


`export ANSIBLE_INVENTORY_ENABLED=dna_center`

`export ANSIBLE_INVENTORY_PLUGINS=$(PWD)`

The alternate way of configuring these options using the `ansible.cfg` file: 

1.  Add the plugin name to the list of enabled plugins. The order determines the execution order.

```ini
[inventory]
enable_plugins = host_list, script, yaml, ini, auto, dna_center
```
2. Add the path to the inventory_plugins setting in the defaults section. (use a colon : to separate multiple entries)
```ini
[defaults]
inventory_plugins = /Users/andiorij/development/dnac_inventory_plugin
```
https://docs.ansible.com/ansible/latest/reference_appendices/config.html


Example Usage
--------------
To test if your inventory source is functioning correctly, execute the command
below. 

`ansible-inventory --graph`
`ansible-inventory --list`

TODO
-----

- polish documents and release

References
--------------
https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory

https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html#dynamic-inventory

https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html

Observed Issues
----------------

The inventory plugin builds the inventory from DNA Center includinig group mappings and some limited host variable mappings seen here: 

```json
"dna-3-d2.campus.wwtatc.local": {
                "ansible_become": "yes", 
                "ansible_become_method": "enable", 
                "ansible_connection": "network_cli", 
                "ansible_host": "192.168.19.3",
                "ansible_network_os": "ios", 
                "os": "IOS-XE", 
                "version": "16.9.1"
            }
```
**Issue Observed** - mapping of `ansible_host` is controlled by the plugin control file  `dna_center.yml`.  if this value is mapped, that address will be used for connection.  It must be reachable.  In the lab environment, this was behind a NAT and not reachable directly.  

**Issue Observed** - if `ansible_host` is not mapped, the `inventory_hostname` must be resolvable by the ansible control mode. 
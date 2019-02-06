DNA Center Inventory Plugin
=============================
DNA Center Inventory Plugin allows you to utilize the network discovery
capabilities of Cisco's DNA Center controller as a source of inventory for
Ansible Playbooks. 

Requirements
-------------
- Python
- Python requests module
- Ansible (tested with 2.6.2)

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

Example Usage
--------------
To test if your inventory source is functioning correctly, execute the command
below. 

`ansible-inventory --graph`

TODO
-----
- determine how to add hostvars 
- test consuming in playbook
- integrate/test vaulted variables (loader should decrypt)

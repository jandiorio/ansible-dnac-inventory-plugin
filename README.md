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

TODO
-----

- test consuming in playbook
- integrate/test vaulted variables (loader should decrypt)

References
--------------
https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory

https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html#dynamic-inventory

https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html

DNA Center Inventory Plugin
=============================
DNA Center Inventory Plugin allows you to utilize the network discovery
capabilities of Cisco's DNA Center controller as a source of inventory for
Ansible Playbooks. 

Change Log
------------
 - [04/12/2022] Updated plugin dependencies to DNA Center SDK for proper abstraction
 - [04/12/2022] Fixed issue with large deployments in which DNA Center API result is limited to 500 records

DevNet Code Exchange 
---------------------

This repository is featured on Cisco DevNet Code Exchange.

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/jandiorio/ansible-dnac-inventory-plugin)

Functionality 
--------------
The DNA Center Inventory plugin will gather all groups (sites) and inventory devices from DNA Center.  The hosts are associated with appropriate sites in the hierarchy. 

The following host_vars are associated with the network devices: 
- `ansible_connection` : **network_cli** for ios and nxos devices
- `ansible_become_method` : for ios and nxos types. (**enable**)
- `ansible_become` : **yes** for ios and nxos types. 
- `ansible_host` : using the `managementIpAddress` from DNA Center - conditionally mapped based on control file `dna_center.yml`.  (*see note at the bottom*)
- `ansible_network_os` : derived from `os` below and required for Ansible network_cli connection plugin
- `os` : network operating system as stored in DNA Center's `softwareType`
- `version` : network operating system version as stored in DNA Center's `softwareVersion`
- `id` : managed network device unique identifier used by DNA Center. Device Id (or UUID) can be used for filtering and scoping in DNAC API calls

Getting Started
-------------

Follow the instructions below to install the Ansible Inventory Plugin for Cisco DNA Center on your Ansible control node. 

### Requirements

To utilize the inventory plugin your environment would need to include the following elements: 

- Ansible - (tested 2.12.3)
- Python - min 3.5 (tested 3.10.3)
- Cisco DNA Center - tested 2.3.2. Refer to DNA Center SDK for supported DNAC Versions: https://dnacentersdk.readthedocs.io/en/latest/api/intro.html
- Python `requests` module
- Python DNA Center SDK `DNACenterAPI` module

### Setup
Follow these steps to prepare your environment appropriately to consume the inventory plugin. 

**STEP 1.**  Clone or fork this repo and install Python modules

```shell
vagrant@ubuntu-xenial:~$ git clone https://github.com/jandiorio/ansible-dnac-inventory-plugin
Cloning into 'ansible-dnac-inventory-plugin'...
remote: Enumerating objects: 101, done.
remote: Counting objects: 100% (101/101), done.
remote: Compressing objects: 100% (47/47), done.
remote: Total 101 (delta 49), reused 101 (delta 49), pack-reused 0
Receiving objects: 100% (101/101), 32.73 KiB | 0 bytes/s, done.
Resolving deltas: 100% (49/49), done.
Checking connectivity... done.

pip3 install -r requirements.txt
```

**STEP 2.** Place the files in the appropriate location or update the environment
variable with the location

```shell
vagrant@ubuntu-xenial:~$ cp -r ansible-dnac-inventory-plugin/inventory_plugins dna_3_legacy/
```

**STEP 3.**  Enable the inventory plugin

Most Ansible inventory plugins are disabled by default so the must be enabled
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

**STEP 4.**  Update the plugin configuration file `inventory_plugins/dna_center.yml`

```yaml
---
plugin: dna_center
host: 'dnac-ip-address.local'
dnac_version: '2.2.3.3'
validate_certs: False
use_dnac_mgmt_int: False
username: '{{ your_dnac_username }}'
password: '{{ your_dnac_pwd }}'
toplevel:
```

**STEP 5.**  Execute the example below to test functionality

```shell
vagrant@ubuntu-xenial:~/dna_3_legacy$ ansible-inventory -i inventory_plugins/ --graph

/home/vagrant/.local/lib/python2.7/site-packages/urllib3/connectionpool.py:847: InsecureRequestWarning: Unverified HTTPS request is being made. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
  InsecureRequestWarning)
  
@all:
  |--@central:
  |  |--@maryland_heights:
  |  |  |--@atc56:
  |  |  |  |--dna-3-a1.campus.wwtatc.local
  |  |  |  |--dna-3-a2.campus.wwtatc.local
  |  |  |  |--dna-3-d1.campus.wwtatc.local
  |  |  |  |--dna-3-d2.campus.wwtatc.local
  |--@east:
  |--@ungrouped:
  |--@west:
```


Example Usage
--------------
To test if your inventory source is functioning correctly, execute the command
below. 

`ansible-inventory --graph`

`ansible-inventory --list`

`ansible-playbook -i inventory_plugins/  samples/sample_playbook.yml`

Supporting Collateral
-----

- [Ansible Inventory Plugin Overview Slides](https://www.slideshare.net/secret/P4ltP8elhAw0A)

References
--------------
https://github.com/ansible/ansible/blob/devel/lib/ansible/plugins/inventory

https://docs.ansible.com/ansible/latest/user_guide/intro_dynamic_inventory.html#dynamic-inventory

https://docs.ansible.com/ansible/latest/dev_guide/developing_inventory.html

https://dnacentersdk.readthedocs.io/en/latest/installation.html

https://dnacentersdk.readthedocs.io/en/latest/api/api.html

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

**Issue Observed** - when executing on OSX Monterey, following error message observed:

```
objc[13508]: +[__NSCFConstantString initialize] may have been in progress in another thread when fork() was called. We cannot safely call it or ignore it in the fork() child process. Crashing instead. Set a breakpoint on objc_initializeAfterForkError to debug.
```

Workaround: set environment variable prior to execution
```
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

**Issue Observed** - If DNA Center Site Hierarchy contains site names starting with a number, plugin outputs a warning message
```
[WARNING]: Invalid characters were found in group names but not replaced, use -vvvv to see details
```


## Author

**Jeff Andiorio** - World Wide Technology 

**Igor Manassypov** - Cisco Systems, <imanassy@cisco.com>

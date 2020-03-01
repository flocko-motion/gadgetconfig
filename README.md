# Gadget Config
## Stuart Lynne 
## Sun Mar 01 13:36:16 PST 2020 

This package contains tools for configuring Gadget USB Devices.

It relies on the Gadget ConfigFS module libcomposite to create and manage Gadget USB Devices.

This package also has *systemd* scripts to start and stop the Gadget Device.


## Gadget USB Device Overview

The Gadge USB Device implementation has three layers when using the new libcomposite
driver:

- Function Drivers, e.g. usb_f_acm, usb_f_ecm, usb_f_eem
- LibComposite, for selecting and configuring the device to use the Function Drivers
- UDC, to connect the Function Drivers to the underlying USB Device Controller hardware

The libcomposite implementation allows the USB Device configuration to be specified ad hoc
and changed as needed. 

A USB Device definition contains:
- idVendor, idProduct, bcdDevice and other attributes
- one of more configurations
- a list of functions that configurations may use
- strings describing the device

Each configuration contains:
- attributes
- list of functions to be used 
- strings describing the configuration




## Gadget USB Device Lifecycle

The *gadgetconfig* program uses USB Device definitions stored in *JSON* files.


Gadget Libcomposite:

- Create: *gadgetconfig --create gadget-definition.json*
- Enable: *gadgetconfig --enable configuration_name*
- Disable: *gadgetconfig --disable*
- Destroy: *gadgetconfig --destroy*

Gadget UDC:
- Disconnect: *gadgetconfig --soft_connect disconnect*
- Connect: *gadgetconfig --soft_connect connect*


```
            +-------------------+
            |     No Gadget     |
            +-------------------+
                  |       ^             
                  |       |
               Create   Destroy
                  |       |
                  v       |
            +-------------------+
            | Distabled Gadget  |<---
            +-------------------+   |
                  |                 | 
                  |                 |
                Enable           Disable
                  |                 |
                  v                 |
            +-------------------+   |
            | Configured Gadget |---|
   Gadget   +-------------------+                                    
     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   UDC      +-------------------+  Disconnect   +-------------------+ 
            | Attached Gadget   |-------------->| Detached Gadget   |
            |                   |<------------- |                   |
            +-------------------+   Connect     +-------------------+
     - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
   Hardware                                                           


```
N.B.
1. Multiple Gadget USB Device Definitions can be created and co-exist.
2. Only a single Gadget USB Device can be *enabled* at one time.
3. Attempting to enable a Gadget USB Device will fail another Gadget Device is enabled.
3. When *enabled* a device defaults to *attached*.
4. An enabled Gadget Device cannot be *removed*.
5. Each of multiple Gadget Devices must be separately *removed*.


## Gadget USB Device Definition File

*Gadget USB Device Definition Files* are *JSON* files that contain all of the information to define
one or more USB Device's along with their attributes, strings, os descriptors, functions and configurations.

There is a close correspondence between the JSON definition file and the resulting Gadget ConfigFS information. 

N.B.
- multiple *USB Device Definitions* can be present and can be configured into the GadgetFS
- multiple *USB Device Functions* can be specified (from the list of Gadget Functions available)
- multiple *USB Device Configurations* can be specified, each with a different set of the available *USB Device Functions*
- within a configuration the array of *configuration function definitions* are used to create the symlinks pointing to the defined functions by the creation process.
- some entries in ConfigFS functions display Gadget generated data, notably acm port_num and ecm ifname are automatically created and not set from the definition file
- the os_desc entry rules are specific and designed to support Windows, see the RNDIS example for more information
- multiple languages can have strings by specifying separate LANG identifiers for each, for both the *USB Device Definition* and each *USB Device Configuration*

## Example

This defines a composite USB Device called *belcarra* containing two ACM and one ECM functions. There
is one configuration called "Belcarra Composite CDC 2xACM+ECM.1" which will be the default configuration
presented to the host during enumeration.

This is belcarra-2acm+ecm.json file:
```
{ "belcarra": {
        "bDeviceClass": "0x00",
        "bDeviceProtocol": "0x00",
        "bDeviceSubClass": "0x00",
        "bMaxPacketSize0": "0x40",
        "bcdDevice": "0x0001",
        "bcdUSB": "0x0200",
        "configs": {
            "Belcarra Composite CDC 2xACM+ECM.1": {
                "MaxPower": "2",
                "bmAttributes": "0x80",
                "functions": [
                    { "function": "acm.usb0", "name": "acm.GS0" },
                    { "function": "acm.usb1", "name": "acm.GS1" },
                    { "function": "ecm.usb0", "name": "ecm.usb0" }
                ],
                "strings": { "0x409": { "configuration": "CDC 2xACM+ECM" } }
            }
        },
        "functions": {
            "acm.usb0": {},
            "acm.usb1": {},
            "ecm.usb0": {
                "dev_addr": "4e:28:20:f0:35:ab",
                "host_addr": "b6:fe:ea:86:2a:50",
                "qmult": "5"
            }
        },
        "idProduct": "0xd031",
        "idVendor": "0x15ec",
        "os_desc": {
            "b_vendor_code": "0x00",
            "qw_sign": "",
            "use": "0"
        },
        "strings": {
            "0x409": {
                "manufacturer": "Belcarra Technologies",
                "product": "Composite CDC 2xACM+ECM",
                "serialnumber": "0123456789"
            }
        }
    }
}
```
We can view the generated Gadget ConfigFS using *sysfstree_raspian*:
```
# gadgetconfig --create belcarra-2acm+ecm.json
# sysfstree_raspbian --gadget
[/sys/kernel/config/usb_gadget]
└──[belcarra]
    ├──bcdDevice: 0x0001
    ├──bcdUSB: 0x0200
    ├──bDeviceClass: 0x00
    ├──bDeviceProtocol: 0x00
    ├──bDeviceSubClass: 0x00
    ├──bMaxPacketSize0: 0x40
    ├──[configs]
    │   └──[Belcarra Composite CDC 2xACM+ECM.1]
    │       ├──acm.GS0 -> /sys/kernel/config/usb_gadget/belcarra/functions/acm.usb0
    │       ├──acm.GS1 -> /sys/kernel/config/usb_gadget/belcarra/functions/acm.usb1
    │       ├──bmAttributes: 0x80
    │       ├──ecm.usb0 -> /sys/kernel/config/usb_gadget/belcarra/functions/ecm.usb0
    │       ├──MaxPower: 2
    │       └──[strings]
    │           └──[0x409]
    │               ├──configuration: CDC 2xACM+ECM
    ├──[functions]
    │   ├──[acm.usb0]
    │   │   ├──port_num: 0
    │   ├──[acm.usb1]
    │   │   ├──port_num: 1
    │   └──[ecm.usb0]
    │       ├──dev_addr: 4e:28:20:f0:35:ab
    │       ├──host_addr: b6:fe:ea:86:2a:50
    │       ├──ifname: usb0
    │       ├──qmult: 5
    ├──idProduct: 0xd031
    ├──idVendor: 0x15ec
    ├──[os_desc]
    │   ├──b_vendor_code: 0x00
    │   ├──qw_sign:
    │   ├──use: 0
    ├──[strings]
    │   └──[0x409]
    │       ├──manufacturer: Belcarra Technologies
    │       ├──product: Composite CDC 2xACM+ECM
    │       ├──serialnumber: 0123456789
    ├──UDC: fe980000.usb
```


## Running Tests

gadgetconfig currently only has doctests.

Run tests with nose::

    nosetests --with-doctest src/gadgetconfig

Run tests with doctest::

    python -m doctest -v src/gadgetconfig/__init__.py

## Author
Stuart.Lynne@belcarra.com
Copyright (c) 2020 Belcarra Technologies (2005) Corp.


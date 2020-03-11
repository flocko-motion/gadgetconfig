#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Set encoding default for python 2.7
# vim: syntax=python noexpandtab

# gadgetconfig configures and enables a Gadget USB configuration
#

import os
import sys

import io
import re
import argparse
import json

try:
	from gadgetconfig.add import AddGadget
	from gadgetconfig.export import ExportGadget
	from gadgetconfig.manage import ManageGadget
	from gadgetconfig.remove import RemoveGadget
except ModuleNotFoundError:
	from add import AddGadget
	from export import ExportGadget
	from manage import ManageGadget
	from remove import RemoveGadget


"""gadgetconfig.py: ..."""

# __author__  = "Stuart.Lynne@belcarra.com"


def remove_old_device(self, configname):

	fpath = "%s/%s" % (self.configpath, configname)

	print("Check for old configuration: %s" % (fpath))

	if not os.path.exists(fpath) and not os.path.lexists(fpath):
		print("%s does not exist" % (fpath))
		return

	if not os.path.isdir(fpath):
		print("ERROR %s exists and is not a directory" % (fpath))
		exit(1)

	exit(1)


# def replace(data, match, repl):
# 	if isinstance(data, (dict, list)):
# 		for k, v in (data.items() if isinstance(data, dict) else enumerate(data)):
# 			if k == match:
# 				data[k] = repl
# 			replace(v, match, repl)


# this is mainly for testing standalone
#
def main():
	parser = argparse.ArgumentParser(
		usage='%(prog)s [command][options]',
		description="Configure Gadget Device using SysFS and ConfigFS",
		formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog, width=999))

	# parser.add_argument("-L", "--conf", nargs='?', help="include (shell pattern match)", default='')
	# parser.add_argument("paths", metavar='Path', type=str, nargs=argparse.REMAINDER, help="pathname", default=[])

	# parser.add_argument("-D", "--disable", help="Disable the current Gadget", action='store_true')
	# parser.add_argument("path", metavar='path', nargs='?', type=str, help="pathname", default=None)
	# parser.add_argument("-A", "--attr", help="Dump Scheme Attr", action='store_true')
	# parser.add_argument("-2", "--scheme2json", help="Scheme Attr to JSON", action='store_true')
	# parser.add_argument("-S", "--scheme", help="Scheme Attr to JSON", action='store_true')


	group = parser.add_mutually_exclusive_group(required=False)

	group.add_argument("--export", help="Export JSON to STDOUT", action='store_true')
	group.add_argument("--add", type=str, help="Add Gadget device definitions from JSON file", default=None)
	group.add_argument("--remove", type=str, help="Remove Named Gadget device definition\n \n", default=None)
	# group.add_argument("-R", "--remove", nargs='?', type=str, help='Remove Gadget device definition', default=None)

	group.add_argument("--enable", type=str, help="enable specified Gadget Device", default=None)
	group.add_argument("--disable", help="disable currently enabled Gadget Device", action='store_true')
	group.add_argument("--query-gadget", help="display currently enabled Gadget Device", action='store_true')
	group.add_argument("--query-gadgets", help="display current Gadget Devices\n \n", action='store_true')

	parser.add_argument("--soft-disconnect", help="Disconnect or detach the UDC", action='store_true')
	parser.add_argument("--soft-connect", help="Connect or attach the UDC", action='store_true')
	#group.add_argument("--query-soft-connect", help="display current UDC Soft-Connect status", action='store_true')
	group.add_argument("--query-udc", help="display current UDC function and state", action='store_true')
	group.add_argument("--query-udc-state", help="display current UDC state", action='store_true')
	group.add_argument("--query-udc-function", help="display current UDC function\n \n", action='store_true')

	# group.add_argument("path", metavar='path', nargs='?', type=str, help="Gadget Device Scheme", default=None)

	parser.add_argument("--idVendor", type=str, help="Optional device idVendor attribute")
	parser.add_argument("--idProduct", type=str, help="Optional device idProduct attribute")

	parser.add_argument("--manufacturer", type=str, help="Optional device manufacturer string")
	parser.add_argument("--product", type=str, help="Optional device product string")
	parser.add_argument("--serialnumber", type=str, help="Optional device serialnumber string")

	parser.add_argument("--dev_addr", type=str, help="Optional ecm dev_addr attribute")
	parser.add_argument("--host_addr", type=str, help="Optional ecm host_addr attribute")

	parser.add_argument("--name", nargs='?', type=str, help='device name override', default=None)
	# parser.add_argument("-I", "--id", nargs='?', type=int, help='enable ID', default=1)
	parser.add_argument("--test", action='store_true')


	args = parser.parse_args()

	print("args: %s" % (args), file=sys.stderr)
	print("", file=sys.stderr)

	if args.test:
		sys_config_path = "sys/kernel/config/usb_gadget"
	else:
		sys_config_path = "/sys/kernel/config/usb_gadget"

	m = ManageGadget(sys_config_path)
	if args.query_gadget:
		print("Currently configured: %s" % (m.query_gadget()))
		exit(0)
	if args.query_gadgets:
		print("Currently defined gadgets: %s" % (m.query_gadgets()))
		exit(0)
	#if args.query_soft_connect:
	#	print("Soft-Connect: %s" % (m.query_soft_connect()))
	#	exit(0)
	if args.query_udc:
		print("UDC State: %s" % (m.query_udc_state()))
		print("UDC Function: %s" % (m.query_udc_function()))
		exit(0)

	if args.query_udc_state:
		print("UDC State: %s" % (m.query_udc_state()))
		exit(0)
	if args.query_udc_function:
		print("UDC Function: %s" % (m.query_udc_function()))
		exit(0)

	m = ManageGadget(sys_config_path, test=args.test)
	#if not m.checkfs(verbose=False):
	#	if not args.test:
	#		exit(1)
	#	os.makedirs("sys/kernel/config/usb_gadget")

	# m.find_udcs(verbose=True)
	# m.check_current(verbose=False)

	if args.disable:
		m.disable_current()
		exit(0)

	if args.enable is not None:
		m.enable_current(args.enable)
		exit(0)

	if args.soft_disconnect:
		m.soft_connect(False)
		exit(0)

	if args.soft_connect:
		m.soft_connect(True)
		exit(0)

	if args.export:
		e = ExportGadget(sys_config_path)
		devices = e.export_devices()
		j = json.dumps(devices, indent=4)
		print(re.sub(r'"(#.*)":.*,', r'\1', j))
		exit(0)

	if args.remove is not None:
		r = RemoveGadget(sys_config_path)
		r.remove_device(args.remove)
		exit(0)

	if args.add is not None:
		#a = AddGadget(sys_config_path)
		m.add_device_file(args.add, new_device_name=args.name, args=args)
		#with io.open(args.add) as f:
		#	device_definitions = commentjson.load(f)
		#	for device_name in device_definitions:
		#		device_definition = device_definitions[device_name]
		#		if args.idVendor: replace(device_definition, 'idVendor', args.idVendor)
		#		if args.idProduct: replace(device_definition, 'idProduct', args.idProduct)
		#		if args.manufacturer: replace(device_definition, 'manufacturer', args.manufacturer)
		#		if args.product: replace(device_definition, 'product', args.product)
		#		if args.serialnumber: replace(device_definition, 'serialnumber', args.serialnumber)
		#		if args.dev_addr: replace(device_definition, 'dev_addr', args.dev_addr)
		#		if args.host_addr: replace(device_definition, 'host_addr', args.host_addr)
		#		print('device_name: %s' % (device_name))
		#		if args.name is not None:
		#			device_name = args.name
		#			print('device_name: %s' % (device_name))
		#		a.add_device_json(device_definition, device_name=device_name)

	exit(1)


if __name__ == "__main__":
	main()

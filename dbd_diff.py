import sys
import os
import dbd
import argparse
import re

#
#   dbd_diff.py
#   tool for displaying differences between client definitions.
#

parser = argparse.ArgumentParser(
    prog="dbd_diff",
    description="Diff tool for dbd versions"
)

parser.add_argument('src', 
                    help="Directory containing .dbd files, or filename of .dbd")
parser.add_argument("target_version", 
                    help="Target client version")
parser.add_argument("compare_version",
                    help="Client version to compare against")
parser.add_argument('-v', '--verbose',
                        action="store_true")

args = parser.parse_args()


# validate args
is_src_file = os.path.isfile(args.src)
is_src_dir = os.path.isdir(args.src)

if not is_src_file and not is_src_dir:
    print("src is not valud.")
    sys.exit(1)
    
version_pattern = r"^(\d+)\.(\d+)\.(\d+)\.(\d+)$"
target_version = None
compare_version = None

if match := re.match(version_pattern, args.target_version):
    target_version = dbd.build_version_raw(
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4))
    )
else:
    print("Target version doesnt match pattern.")
    sys.exit(1)
    
if match := re.match(version_pattern, args.compare_version):
    compare_version = dbd.build_version_raw(
        int(match.group(1)),
        int(match.group(2)),
        int(match.group(3)),
        int(match.group(4))
    )
else:
    print("Compare version doesnt match pattern.")
    sys.exit(1)
    
defintion_files = []
root_path = ""
if is_src_file:
    root_path = os.path.dirname(args.src)
    defintion_files = [os.path.basename(args.src)]
else:
    root_path = args.src
    defintion_files = os.listdir(args.src)
    defintion_files = [file for file in defintion_files if file.endswith('.dbd')]
    if(args.verbose):
        print("Found {} .dbd files.".format(len(defintion_files)))

summary = {
    "checked": 0,
    "changed": 0
}
checked_definitions = 0
changed_definitions = 0

multi_defs = len(defintion_files) > 1
shown_def_name = False

def msg_print(msg):   
    global shown_def_name
    if (not shown_def_name):
        print("---- " + defintion_file + " ----")
        shown_def_name = True
    
    print(msg)

for defintion_file in defintion_files:
    shown_def_name = False
    
    parsed = dbd.parse_dbd_file(os.path.join(root_path, defintion_file))
    target_def = None
    compare_def = None
    
    for definition in parsed.definitions:
        for build in definition.builds:
            if build == target_version:
                target_def = definition
            
            if build == compare_version:
                compare_def = definition

    if not target_def and not compare_def:
        continue
    
    summary["checked"] += 1
    
    if not target_def:
        msg_print("Unable to find target version definition.")
        
    if not compare_def:
        msg_print("Unable to find compare version definition.")
        
    if not target_def or not compare_def:
        summary["changed"] += 1
        continue
    
    target_entries_len = len(target_def.entries)
    compare_entries_len = len(compare_def.entries)
    
    if args.verbose:
        if target_entries_len != compare_entries_len:
            msg_print("Entry count different.")
    
    largest_entries = max(target_entries_len, compare_entries_len)
    has_changes = False
    for i in range(0, largest_entries - 1):
        target_entry = target_def.entries[i] or  None
        compare_entry = compare_def.entries[i] or None
        
        if target_entry.__str__() != compare_entry.__str__():
            msg_print("- Change at row {} - ".format(i))
            msg_print(target_entry)
            msg_print(compare_entry)
            has_changes = True
            
    if not has_changes:
        if (not multi_defs):
            msg_print("No changes")
    else:
        summary["changed"] += 1
        
if(args.verbose):
    print("{checked} definitions checked, {changed} changes.".format(**summary))

sys.exit(0)

#!/bin/python3

from pathlib import Path
import argparse
import configparser
import selinux
import os

def set_dir_context (path, context, verbose=False, dry_run=False):
    path = path.replace('.','\.')
    cmd = f'semanage fcontext -a -t {context} "{path}(/.*)?"'
    run_command (cmd, verbose=verbose, dry_run=dry_run)

def set_file_context (path, context, verbose=False, dry_run=False):
    path = path.replace('.','\.')
    cmd = f'semanage fcontext -a -t {context} "{path}"'
    run_command (cmd, verbose=verbose, dry_run=dry_run)

def set_port_context (port, context, verbose=False, dry_run=False):
    cmd = f'semanage port -a -t {context} -p {port}'
    run_command (cmd, verbose=verbose, dry_run=dry_run)

def restorecon (path, verbose=False, dry_run=False):
    cmd = f'restorecon -Rv {path}'
    run_command (cmd, verbose=verbose, dry_run=dry_run)
   
def run_command (command, verbose=False, dry_run=False):
    if verbose or dry_run:
        print (command)
    if not dry_run:
        os.system(command) 


parser = argparse.ArgumentParser(description='Reads either the default my.cnf or a user specified one, and sets the SELinux file contexts based on the file.',epilog='These options are read from the mysqld section: datadir, socket, log-bin, relay-log, tmpdir, port. These options are read from the mysqld_safe section: log-error, pid-file')
parser.add_argument("-c","--conf", help="my.cnf file to read, assumes /etc/my.cnf",default="/etc/my.cnf")
parser.add_argument("-v","--verbose", help="Display verbose output", action="store_true")
parser.add_argument("-d","--dry-run", help="Show commands, but do not execute them.",action="store_true",default=False)
args = parser.parse_args()

verbose = args.verbose
dry_run = args.dry_run
sourcefile = Path(args.conf)
if not sourcefile.exists() or not sourcefile.is_file():
    print(f"The source file, {sourcefile}, does not exist or is not a file.")
    exit(2)

if dry_run:
    print("Informational output only. These commands will not be executed.")

mycnf = configparser.ConfigParser(allow_no_value=True)
mycnf.read(sourcefile)

if mycnf.has_option('mysqld','datadir'):
    set_dir_context(mycnf.get('mysqld','datadir'),'mysqld_db_t',verbose=verbose, dry_run=dry_run)
    restorecon(mycnf.get('mysqld','datadir'), verbose=verbose, dry_run=dry_run)

if mycnf.has_option('mysqld','socket'):
    set_file_context(mycnf.get('mysqld','socket'),'mysqld_var_run_t', verbose=verbose, dry_run=dry_run)
    restorecon(mycnf.get('mysqld','socket'), verbose=verbose, dry_run=dry_run)

if mycnf.has_option('mysqld','log-bin'):
    set_dir_context(mycnf.get('mysqld','log-bin'),'mysqld_db_t', verbose=verbose, dry_run=dry_run)
    restorecon(mycnf.get('mysqld','log-bin'), verbose=verbose, dry_run=dry_run)

if mycnf.has_option('mysqld','relay-log'):
    set_dir_context(mycnf.get('mysqld','relay-log'),'mysqld_db_t', verbose=verbose, dry_run=dry_run)
    restorecon(mycnf.get('mysqld','relay-log'), verbose=verbose, dry_run=dry_run)

if mycnf.has_option('mysqld','tmpdir'):
    set_dir_context(mycnf.get('mysqld','tmpdir'),'mysqld_tmp_t', verbose=verbose, dry_run=dry_run)
    restorecon(mycnf.get('mysqld','tmpdir'), verbose=verbose, dry_run=dry_run)

if mycnf.has_option('mysqld_safe','log-error'):
    set_file_context(mycnf.get('mysqld_safe','log-error'),'mysqld_log_t', verbose=verbose, dry_run=dry_run)
    restorecon(mycnf.get('mysqld_safe','log-error'), verbose=verbose, dry_run=dry_run)

if mycnf.has_option('mysqld_safe','pid-file'):
    set_file_context(mycnf.get('mysqld_safe','pid-file'),'mysqld_var_run_t', verbose=verbose, dry_run=dry_run)
    restorecon(mycnf.get('mysqld_safe','pid-file'), verbose=verbose, dry_run=dry_run)

if mycnf.has_option('mysqld','port'):
    set_port_context(f"tcp {mycnf.get('mysqld','port')}", 'mysqld_port_t', verbose=verbose, dry_run=dry_run)


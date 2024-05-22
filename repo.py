#!/usr/env python3
# -*- coding: utf-8 -*-

# This is a simple script to clone git repository from repos.json

import json
import os
import sys
import subprocess
from prettytable import PrettyTable

work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
repos={}

def clone_repo(repo):
    print('-------------------------------------------------------')
    print('Cloning %s from %s' % (repo['path'], repo['url']))
    print('-------------------------------------------------------')
    if not os.path.exists(repo['path']):
        os.makedirs(repo['path'])
        subprocess.run(['git', 'clone', repo['url']])
    subprocess.run(['git', 'checkout', repo['branch']])
    print('-------------------------------------------------------')

def menu_list():
    print('List repositories\' from repos.json:')

    # 使用prettytable输出repos的信息
    tb = PrettyTable()
    tb.field_names = ['Path', 'URL', 'Branch', 'build_type']
    for repo in repos['modules']:
        tb.add_row([repo['path'], repo['url'], repo['branch'], repo['build_type']])
    print(tb)

def menu_clone():

    # 列出当前的repos信息
    menu_list()

    # 选择要clone的repo
    names = input('Please input the names of repos to clone(--all for all): ')
    names = names.strip()

    if names == '--all':
        # 如果用户输入--all，clone所有的repo
        for repo in repos['modules']:
            clone_repo(repo)
    else:
        # 否则，clone用户输入的repo
        names = names.split()
        for name in names:
            for repo in repos['modules']:
                if name == repo['path']:
                    clone_repo(repo)
                    break

def menu_status():
    # 调用git status命令，获得所有repo的状态
    # 以prettytable输出
    tb = PrettyTable()
    tb.field_names = ['Path', 'Status']
    for repo in repos['modules']:
        os.chdir(os.path.join(work_dir, repo['path']))
        status = subprocess.run(['git', 'status', '-sb'], stdout=subprocess.PIPE)
        tb.add_row([repo['path'], status.stdout.decode('utf-8')])
    print(tb)

def reset_repo(path,branch):
    print('-------------------------------------------------------')
    print('Resetting %s' % path)
    print('-------------------------------------------------------')
    os.chdir(os.path.join(work_dir, path))
    subprocess.run(['git', 'reset', '--hard'], stdout=subprocess.PIPE)
    subprocess.run(['git', 'clean', '-df'], stdout=subprocess.PIPE)

def menu_reset():
    menu_status()

    # 选择要reset的repo
    names = input('Please input the names of repos to reset(--all for all): ')
    names = names.strip()
    if names == '':
        print('No repo to reset')
        sys.exit(1)
    if names == '--all':
        # 如果用户输入--all，reset所有的repo
        for repo in repos['modules']:
            reset_repo(repo['path'],repo['branch'])
    else:
        # 否则，reset用户输入的repo
        names = names.split()
        for name in names:
            for repo in repos['modules']:
                if name == repo['path']:
                    reset_repo(repo['path'],repo['branch'])

    print('-------------------------------------------------------')
    menu_status()

if __name__ == '__main__':
    with open('repos.json') as f:
        repos = json.load(f)
    
    if len(sys.argv) < 2:
        print('Usage: repo list|clone|status|reset')
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == 'list':
        menu_list()
    elif cmd == 'clone':
        menu_clone()
    elif cmd == 'status':
        menu_status()
    elif cmd == 'reset':
        menu_reset()
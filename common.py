#!/usr/bin/env python3

# 提供标准化的工具函数

# 定义控制台输出规范
# 工具进入时，应调用echo_entry_tool。
# 工具退出时，应调用echo_exit_tool_failed或者echo_exit_tool_success
# 输出提示信息，应调用echo_tip
# 输出成功信息，应调用echo_success
# 输出失败信息，应调用echo_fail
# 输出进度信息，应调用echo_process

def echo_entry_tool() :
    print('------------ 欢迎使用 知码匠(izmj.net) 脚本 ------------')

def echo_process(msg) :
    print(f'>>  {msg}')

def echo_fail(msg) :
    print(f'\033[91m>>  {msg}\033[0m')

def echo_success(msg) :
    print(f'\033[92m>>  {msg}\033[0m')

def echo_tip(msg) :
    print(f'\033[93m>>  {msg}\033[0m')

def echo_menu(msg):
    print(f'>>  {msg}')

def echo_hr():
    # 计算控制台的宽度
    import shutil
    width = shutil.get_terminal_size().columns

    # 最多输出80个等号
    if width >= 80:
        width = 80

    print('=' * width)

def echo_select(msg=None):
    if msg is not None:
        print(f'\033[92m>>  {msg}\033[0m', end='')
    return input()

def color_error(msg) :
    return f'\033[91m{msg}\033[0m'

def color_success(msg) :
    return f'\033[92m{msg}\033[0m'

def color_tip(msg) :
    return f'\033[93m{msg}\033[0m'

def echo_exit_tool_failed(msg=''):
    if msg != "":
        echo_fail(msg)
    exit(1)

def echo_exit_tool_success(msg=''):
    if msg != "":
        echo_success(msg)
    exit(0)
    
def check_python_version() :
    # 如果当前运行环境是python2，则退出。
    import sys
    if sys.version_info.major != 3:
        echo_exit_tool_failed('本脚本仅支持Python 3下运行！')

def check_config_exists(file) :
    import os
    if not os.path.exists(file):
        echo_exit_tool_failed(f'{file}未找到。')

def decode_str(str):
    import platform

    if platform.system() == 'Windows':
        str = str.encode('gbk', errors="ignore").decode('utf-8', errors="ignore")
    else:
        str = str.decode('utf-8', errors="ignore")
    return str

def wrap_str(str, width=80):
    import textwrap
    return textwrap.fill(str, width)
#!/usr/env python3
# -*- coding: utf-8 -*-

# This is a simple script to clone git repository from repos.json

import json
import os
import sys
import subprocess
from prettytable import PrettyTable
import common
import urllib.request
import datetime

work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))
repos = {}

def menu_init():
    # 下载repos.json文件
    common.echo_hr()
    common.echo_tip("已选择init命令")
    common.echo_tip("我们将根据输入的路径下载更新repos.json文件")
    common.echo_tip(
        "如果已经存在旧的repos.json文件，我们将重命名至.trash/repos_[时间].json"
    )

    url = common.echo_select("请输入repos.json的路径地址：")
    if url == "":
        url = "http://proj.navinfo.xyz/repos.json"

    common.echo_hr()

    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    if os.path.exists("repos.json"):
        os.makedirs("./.trash", exist_ok=True)
        os.rename("repos.json", f"./.trash/repos_{current_time}.json")
        common.echo_process(
            f"已将旧的repos.json文件重命名为.trash/repos_{current_time}.json"
        )

    common.echo_process(f"下载repos.json文件: {url}")

    try:
        # 伪装的浏览器User-Agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

        # 创建Request对象，并设置User-Agent
        req = urllib.request.Request(url, headers={"User-Agent": user_agent})

        # 使用urlopen打开URL
        with urllib.request.urlopen(req) as response:

            # 读取响应内容
            data = response.read()

            # 将内容写入到本地文件
            with open("repos.json", "wb") as f:
                f.write(data)

    except:
        # 输出urllib下载失败原因
        common.echo_fail(sys.exc_info()[1])
        common.echo_exit_tool_failed(f"无法从{url}下载更新")

    if os.path.exists("repos.json"):
        common.echo_success("下载repos.json文件成功")

    global repos
    # 读取repos.json文件
    with open("repos.json", encoding="utf-8", errors="ignore") as f:
        repos = json.load(f)

    menu_list()


def clone_repo(repo):

    os.chdir(work_dir)
    common.echo_process(f"下载库[{repo['path']}]")

    if not os.path.exists(repo["path"]):
        os.makedirs(repo["path"])
        result = subprocess.run(["git", "clone", repo["url"]], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error("下载失败：\n" + result.stderr.strip())

        result = subprocess.run(["git", "checkout", repo["branch"]], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error(f"下载成功，切换分支[{repo["branch"]}]失败: \n" + result.stderr.strip())

        return common.echo_success("下载成功")

    else:
        return common.color_tip("已经存在，跳过下载")


def menu_list():

    common.echo_hr()

    # 使用prettytable输出repos的信息
    tb = PrettyTable()
    tb.field_names = [
        common.color_success("路径(path)"),
        common.color_success("Git路径(URL)"),
        common.color_success("分支名(Branch)"),
        common.color_success("编译任务(build_task)"),
    ]

    tb.align[common.color_success("路径(path)")] = "r"
    tb.align[common.color_success("Git路径(URL)")] = "l"
    for repo in repos["modules"]:
        tb.add_row([repo["path"], repo["url"], repo["branch"], repo["build_task"]])
    print(tb)


def menu_clone():

    common.echo_hr()
    common.echo_tip("已选择clone命令")
    common.echo_tip("我们将根据repos.json文件下载指定库")

    # 列出当前的repos信息
    menu_list()

    # 选择要clone的repo
    names = input("请输入需要clone的模块，以空格分隔(--all代表全部下载): ")
    names = names.strip()

    common.echo_hr()

    effect_count = 0

    tb = PrettyTable()
    tb.field_names = ["路径(path)", "状态(status)"]
    tb.align["路径(path)"] = "r"
    tb.align["状态(status)"] = "l"

    if names == "--all":
        # 如果用户输入--all，clone所有的repo
        for repo in repos["modules"]:
            result = clone_repo(repo)
            tb.add_row([repo["path"], result])
            effect_count += 1
    else:
        # 否则，clone用户输入的repo
        names = names.split()
        for name in names:
            for repo in repos["modules"]:
                if name == repo["path"]:
                    result = clone_repo(repo)
                    tb.add_row([repo["path"], result])
                    effect_count += 1
                    break

    if effect_count == 0:
        common.echo_fail("没有选择任何库进行下载")
    else:
        print(tb)

def print_branch_info():

    tb = PrettyTable()
    tb.field_names = ["路径(path)", "分支(branch)"]
    tb.align["路径(path)"] = "r"
    tb.align["分支(branch)"] = "l"

    for repo in repos["modules"]:
        os.chdir(os.path.join(work_dir, repo["path"]))

        result = subprocess.run(
            ["git", "branch", "-v"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            tb.add_row(
                [repo["path"], common.color_error(f"查询分支失败")]
            )
        else:
            branch = common.decode_str(result.stdout.strip()).splitlines()[0][:60]
            tb.add_row([repo["path"], branch])

    print(tb)

def checkout_repo(repo, branch):
    if os.path.exists(repo["path"]):
        os.chdir(os.path.join(work_dir, repo["path"]))
        result = subprocess.run(["git", "checkout", branch], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error("切换分支[{branch}]失败：\n" + result.stderr.strip())
        else:
            return common.color_success(f"切换分支[{branch}]成功")
    else:
        return common.color_error("库不存在，请先clone")

def menu_checkout():
    # 选择要checkout的repo

    names = common.echo_select("请输入需要切换分支的模块，以空格分隔(--all代表全部下载): ")
    branch = common.echo_select("请输入分支名: ")

    tb = PrettyTable()
    tb.field_names = ["路径(path)", "状态(status)"]
    tb.align["路径(path)"] = "r"
    tb.align["状态(status)"] = "l"

    effect_count = 0
    if names == "--all":
        # 如果用户输入--all，reset所有的repo
        for repo in repos["modules"]:
            result = checkout_repo(repo, branch)
            tb.add_row([repo["path"], result])
            effect_count += 1
    else:
        # 否则，reset用户输入的repo
        names = names.split()
        for name in names:
            for repo in repos["modules"]:
                if name == repo["path"]:
                    result = checkout_repo(repo, branch)
                    tb.add_row([repo["path"], result])
                    effect_count += 1
                    break
    
    if effect_count == 0:
        common.echo_fail("没有选择任何库进行分支切换")
    else:
        print(tb)

    print_branch_info()


def menu_status():
    # 调用git status命令，获得所有repo的状态
    # 以prettytable输出

    tb = PrettyTable()
    tb.field_names = ["路径(path)", "状态(status)"]
    tb.align["路径(path)"] = "r"
    tb.align["状态(status)"] = "l"
    for repo in repos["modules"]:
        os.chdir(os.path.join(work_dir, repo["path"]))
        result = subprocess.run(
            ["git", "status", "-sb"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if result.returncode != 0:
            tb.add_row(
                [repo["path"], common.color_error(f"查询状态失败：\n" + result.stderr.strip())]
            )
        else:
            result = common.decode_str(result.stdout.strip())
            if len(result.splitlines()) > 1:
                tb.add_row([repo["path"] + '\n', common.color_tip(result)])
            else:
                tb.add_row(
                    [repo["path"] + '\n', common.color_success(result)]
                )
    print(tb)


def reset_repo(repo):

    if os.path.exists(repo["path"]):
        os.chdir(os.path.join(work_dir, repo["path"]))

        common.echo_process(f"重置库[{repo['path']}]")
    
        # 获取被重置库的状态
        tb = PrettyTable()
        tb.field_names = ["路径(path)", "状态(status)"]
        tb.align["路径(path)"] = "r"
        tb.align["状态(status)"] = "l"

        status = subprocess.run(
            ["git", "status", "-sb"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if status.returncode != 0:
            tb.add_row(
                [repo["path"], common.color_error(f"查询状态失败：\n" + result.stderr.strip())]
            )
        else:
            status = common.decode_str(status.stdout.strip())
            if len(status.splitlines()) > 1:
                tb.add_row([repo["path"], common.color_tip(status)])
            else:
                tb.add_row(
                    [repo["path"], common.color_success(status)]
                )
        print(tb)

        common.echo_fail("重置(reset)将会清除所有未提交的修改，包括stash和未提交的文件")
        common.echo_fail("请确认是否继续？(Y/n)")
        select = common.echo_select()
        if select != 'Y' and select != 'y':
            return common.color_error("用户取消")

        result = subprocess.run(["git", "restore", "--staged", "*"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error(f"还原(restore)失败: \n{result.stderr.strip()}")
        
        result = subprocess.run(["git", "reset", "HEAD", "--hard"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error(f"重置(reset)失败: \n{result.stderr.strip()}")
        
        result = subprocess.run(["git", "clean", "-df"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error(f"清理(clean)失败: \n{result.stderr.strip()}")
        
        return common.color_success(f"清理成功")
        
    else:
        return common.color_error("库不存在，请先clone")


def menu_reset():

    common.echo_hr()
    common.echo_tip("已选择reset命令")
    common.echo_tip("将通过git restore --stashed & git reset HEAD --hard & git clean -fx命令进行更新")
    common.echo_tip("如果执行失败，请手动进行更新")

    names = common.echo_select("请输入需要更新的模块，以空格分隔(--all代表全部下载): ")
    common.echo_hr()

    names = names.strip()

    tb = PrettyTable()
    tb.field_names = ["路径(path)", "状态(status)"]
    tb.align["路径(path)"] = "r"
    tb.align["状态(status)"] = "l"

    effect_count = 0
    if names == "--all":
        # 如果用户输入--all，reset所有的repo
        for repo in repos["modules"]:
            result = reset_repo(repo)
            tb.add_row([repo["path"], result])
            effect_count += 1
    else:
        # 否则，reset用户输入的repo
        names = names.split()
        for name in names:
            for repo in repos["modules"]:
                if name == repo["path"]:
                    result = reset_repo(repo)
                    tb.add_row([repo["path"], result])
                    effect_count += 1
                    break
    
    if effect_count == 0:
        common.echo_fail("没有选择任何库进行重置")
    else:
        print(tb)

def update_repo(repo):

    if os.path.exists(repo["path"]):
        os.chdir(os.path.join(work_dir, repo["path"]))

        common.echo_process(f"更新库[{repo['path']}]")

        result = subprocess.run(["git", "fetch"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error(f"拉去(fetch)失败: \n{result.stderr.strip()}")

        result = subprocess.run(["git", "rebase", "--autostash"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            return common.color_error(f"变基(rebase)失败: \n{result.stderr.strip()}")

        result = subprocess.run(["git", "stash", "pop"], errors="ignore", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            if "CONFLICT" in result.stderr:
                return common.color_error(f"变基(rebase)成功，但gi恢复stash时发生合并冲突，请手动解决")
            elif "No stash entries found" in result.stderr:
                return common.color_success("变基(rebase)成功")
            else:
                return common.color_error(f"恢复stash失败: \n{result.stderr.strip()}")
        
        return common.color_success("变基(rebase)成功")

    else:
        return common.color_error("库不存在")
    

def menu_update():
    common.echo_hr()
    common.echo_tip("已选择update命令")
    common.echo_tip("将通过git stash push & git rebase & git stash pop命令进行更新")
    common.echo_tip("如果在git statsh pop时发生冲突，请手动进行更新")
    common.echo_tip("如果在工具无法继续执行，请在备份好环境后，执行reset命令")

    menu_list()

    # 选择要checkout的repo
    names = common.echo_select("请输入需要更新的模块，以空格分隔(--all代表全部下载): ")
    common.echo_hr()

    names = names.strip()

    tb = PrettyTable()
    tb.field_names = ["路径(path)", "状态(status)"]
    tb.align["路径(path)"] = "r"
    tb.align["状态(status)"] = "l"

    effect_count = 0
    if names == "--all":
        # 如果用户输入--all，update所有的repo
        for repo in repos["modules"]:
            result = update_repo(repo)
            tb.add_row([repo["path"], result])
            effect_count += 1
    else:
        # 否则，update用户输入的repo
        names = names.split()
        for name in names:
            for repo in repos["modules"]:
                if name == repo["path"]:
                    result = update_repo(repo)
                    tb.add_row([repo["path"], result])
                    effect_count += 1
                    break
    
    if effect_count == 0:
        common.echo_fail("没有选择任何库进行更新")
    else:
        print(tb)

if __name__ == "__main__":

    common.echo_entry_tool()

    # 检查Python版本
    common.check_python_version()

    # 获取工作目录
    # 如果当前路径下，有repo.py或者repo.exe。则认为是..是工作目录
    if os.path.exists("repo.py") or os.path.exists("repo.exe"):
        common.echo_tip("检测到repo.py或者repo.exe文件，将设置工作目录为上级目录（..）")
        work_dir = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), ".."))
    else:
        work_dir = os.path.abspath(os.path.dirname(sys.argv[0]))

        common.echo_tip("未检测到repo.py或者repo.exe文件")

    common.echo_success(f"工作目录设置为: {work_dir}")

    # 显示菜单
    common.echo_hr()
    common.echo_menu("请选择要执行的命令：")
    common.echo_menu("  1. init: 根据url，下载repos.json文件")
    common.echo_menu("  2. clone: 调用git clone")
    common.echo_menu("  3. list: 显示repos.json中的全部repos信息")
    common.echo_menu("  4. checkout: 针对指定库，切换分支")
    common.echo_menu("  5. status: 显示指定库的状态信息")
    common.echo_menu("  6. reset: 重置本地库")
    common.echo_menu("  7. update: 更新本地库到最新版本")
    common.echo_menu("  8. push: 推送本地修改到远程仓库")
    common.echo_menu("  0. exit: 退出")
    common.echo_hr()

    try:
        cmd = int(common.echo_select("请输出命令编号："))
        if cmd < 0 or cmd > 7:
            common.echo_exit_tool_failed("输入命令编号错误！")
    except:
        common.echo_exit_tool_failed("输入命令编号错误！")

    # 以下命令不需要repos.json文件
    if cmd == 1:
        menu_init()
    elif cmd == 0:
        common.echo_exit_tool_success("退出成功")

    # 载入repos.json文件
    if not os.path.exists("repos.json"):
        common.echo_fail("未找到repos.json文件")
        common.echo_fail(f"  1. 请检查[{work_dir}]是否为工作目录")
        common.echo_fail("  2. 请使用repo init命令下载一套repos.json")

    with open("repos.json", encoding="utf-8", errors="ignore") as f:
        repos = json.load(f)

    # 以下命令需要repos.json文件
    if cmd == 2:
        menu_clone()
    elif cmd == 3:
        menu_list()
    elif cmd == 4:
        menu_checkout()
    elif cmd == 5:
        menu_status()
    elif cmd == 6:
        menu_reset()
    elif cmd == 7:
        menu_update()
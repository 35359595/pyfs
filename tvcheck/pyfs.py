#!/usr/bin/env python3
"""fs.to tvcheck by Ivan Temchenko @ yandex.ua

@about:
    This program writen to be runned with python version 3. Any problems with other python versions should
    NOT been reported and will not be reviewed for fixes.

@author:
    Ivan Temchenko (C) 2016

@version:
    51916.1340

@license:
    Apache License Version 2.0

    Read LICENSE file for details.

"""


from urllib.request import urlopen
from os.path import expanduser, exists, join
from os import makedirs
import sys as Sys
import time

#Globals
HOME = expanduser('~')
speed = 0
metrics = 'bps'
START_TIME = time.process_time()
list_location = join(HOME, '.tvcheck', 'list')


def arg_parsing():
    """Arg parsing function"""
    args = list()
    if len(list(Sys.argv)) > 2:
        if len(Sys.argv[1]) == 1:
            args = Sys.argv
    return args


def check_filesystem():
    """Function for checking existance of working dir and list file"""
    if not exists(join(HOME, '.tvcheck')):
        makedirs(join(HOME, '.tvcheck'))

    if not exists(join(HOME, '.tvcheck', 'list')):
        with open(join(HOME, '.tvcheck', 'list'), mode = 'w+') as new_list:
            print('No list file found.')
            new_list.write(input('Paste episode list url:'))


def read_from_fs(url=None):
    """Getting the list from file located @ fs server
    @params:
        url - http link to file"""
    with urlopen(url) as remote_list:
        urls = list()
        for line in remote_list:
            urls.append(line.decode('utf-8'))
        return urls


def read_from_file(path=None):
    """Reading lines from file and returning array of lines
    @usage: read_from_file('/path/name.extension')"""
    with open(path, mode='rt', encoding='utf-8') as link_list:
        return list(link_list.readlines())


def append_to_file(path=None, new_link=None):
    """Appending one line to file, adding newline afterwards"""
    with open(path, mode='at', encoding='utf-8') as local_list:
        local_list.write(new_link.__add__('\n'))


def round_to_mb(bts):
    """Returns Mb from b rounded to .xx"""
    return round((int(bts) / 1024 / 1024), 2)


def print_progress(iteration, total, start, prefix = '', suffix = '', decimals = 2, barLength = 100):
    """Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    global metrics
    global START_TIME
    global speed
    if (time.process_time() - START_TIME) * 1000  > 5:
        START_TIME = time.process_time()
        speed           = round((iteration*8//(time.process_time() - start)//1024), decimals)
        metrics         = 'Kbps'
        if speed > 1024:
            speed = speed//1024
            metrics = 'Mbps'

    Sys.stdout.write('%s [%s] %s%s %s%s %s\r' % (prefix, bar, percents, '%', suffix, speed, metrics)),
    Sys.stdout.flush()
    if iteration == total:
        print("\n")


def callback(progress, size=0):
    """Downloading progress displaying function"""
    start = time.process_time()
    print_progress(progress, size, start, prefix = 'Downloading:', suffix = 'Speed:', barLength = 50)


def copyfileobject(fsrc, fdst, callback, size, length=16*1024):
    """Function for saving the file. Iteration with callable function."""
    copied = 0
    while True:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)
        copied += len(buf)
        callback(copied, size)
        

def download_episode(url=None, episode_name=None):
    """Downloading function"""
    out_file = join(HOME, 'Downloads', episode_name)
    with urlopen(url) as response, open(out_file, 'wb') as out_file:
        size = response.getheader("Content-Length")
        copyfileobject(response, out_file, callback, size) 


def main():
    """Main function
    @algorythm:
        1. reads list of series from list file;
        2. reads list of episodes from each of the series;
        3. compares the list of episodes from fs.to with local list;
        4. if new episodes found - downloading with aria2;
        5. after successfull download append new episode to local list."""

    args = list(arg_parsing())
    check_filesystem()

    if args:
        if len(args) > 2:
            print('To many arguments, bye!')
            Sys.exit()
        elif args[1] == 'l':
            for series in read_from_file(join(HOME, '.tvcheck', 'list')):
                print(series)
            Sys.exit()
        elif args[1] == 'n':
            new_url = input('Provide URL of new list in format http://fs.to/flist/...:')
            if new_url[:19] == 'http://fs.to/flist/':
                append_to_file(list_location, new_url)
            else:
                print('Wrong Url format, bye!')
                Sys.exit()
        elif args[1] == 'h':
            print("""
Parameters:\n
    h - show this help;\n
    l - show local series list;\n
    n - add series to local list (follow the instructions).\n""")
            Sys.exit()
        else:
            while True:
                decision = input("Parameter not found. Continue check? Y/N: ")
                if decision.upper() == 'Y':
                    break
                elif decision.upper() == 'N':
                    Sys.exit()

    #1:
    local_list = read_from_file(list_location)
    for url in local_list:
        remote_list = read_from_fs(url)

        #2:
        local_list_name = join(HOME, '.tvcheck', url[19:].rstrip())
        local_list = read_from_file(local_list_name)

        #3:
        if len(local_list) == len(remote_list):
            print('No new episodes. Already watched', len(remote_list), 'episodes.')

        elif len(remote_list) == 0:
            print('Server returned empty list. Redownload:', url)
        
        #4:
        elif len(remote_list) > len(local_list):
            new_episodes = list()
            new_episodes_count = len(remote_list) - len(local_list)
            while new_episodes_count > 0:
                new_episodes.append(remote_list.pop().rstrip())
                new_episodes_count -= 1
            
            for new_link in new_episodes.__reversed__():
                last_slash = new_link.rfind('/')
                episode_name = new_link[last_slash+1:]
                print('New episode:', episode_name)
                global START_TIME
                START_TIME = time.process_time()
                download_episode(new_link, episode_name)
                print(new_link)
                #5:
                append_to_file(local_list_name, new_link)
                

#call execution if runned from console
if __name__ == '__main__':
    main()


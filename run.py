#!/usr/bin/env python3
"""fs.to tvcheck by Ivan Temchenko @ yandex.ua

ABOUT:
    This program writen to be runned with python version 3. Any problems with other python versions should
    NOT been reported and will not be reviewed for fixes.

AUTHOR:
    Ivan Temchenko

VERSION:
    51616.1038

"""



from urllib.request import urlopen
import sys as Sys
import time



"""Getting the list from file located @ fs server

PARAM: url - http link to file"""

def read_from_fs(url=None):
    with urlopen(url) as remote_list:
        urls = list()
        for line in remote_list:
            urls.append(line.decode('utf-8'))
        return urls

"""Reading lines from file and returning array of lines

USAGE: read_from_file('/path/name.extension')"""

def read_from_file(path=None):
    link_list = open(path, mode='rt', encoding='utf-8')
    readed_list = list(link_list.readlines())
    link_list.close()
    return readed_list

"""Appending one line to file, adding newline afterwards"""

def append_to_file(path=None, new_link=None):
    local_list = open(path, mode='at', encoding='utf-8')
    local_list.write(new_link.__add__('\n'))
    local_list.close()

"""Returns Mb from b rounded to .xx"""
def round_to_mb(bts):
    return round((int(bts) / 1024 / 1024), 2)


def print_progress(iteration, total, start, prefix = '', suffix = '', decimals = 2, barLength = 100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
    """
    filledLength    = int(round(barLength * iteration / float(total)))
    percents        = round(100.00 * (iteration / float(total)), decimals)
    bar             = '#' * filledLength + '-' * (barLength - filledLength)
    speed           = round((iteration*8//((time.process_time() - start)*1000)//1024//1024), decimals)
    Sys.stdout.write('%s [%s] %s%s %s%s Kbps\r' % (prefix, bar, percents, '%', suffix, speed)),
    Sys.stdout.flush()
    if iteration == total:
        print("\n")


"""Downloading progress displaying function"""
def callback(progress, size=0):
    start = time.process_time()
    print_progress(progress, size, start, prefix = 'Downloading:', suffix = 'Speed:', barLength = 50)

def copyfileobject(fsrc, fdst, callback, size, length=16*1024):
    copied = 0
    while True:
        buf = fsrc.read(length)
        if not buf:
            break
        fdst.write(buf)
        copied += len(buf)
        callback(copied, size)
        

"""Downloading function"""
def download_episode(url=None, episode_name=None):
    out_file = str('/home/jony/Downloads/')
    out_file = out_file.__add__(episode_name)
    with urlopen(url) as response, open(out_file, 'wb') as out_file:
        size = response.getheader("Content-Length")
        copyfileobject(response, out_file, callback, size) 
        

"""Main function

ALGORYTHM: 
    1. reads list of series from list file;
    2. reads list of episodes from each of the series;
    3. compares the list of episodes from fs.to with local list;
    4. if new episodes found - downloading with aria2;
    5. after successfull download append new episode to local list."""

def main():

    #1:
    local_list = read_from_file('/home/jony/.tvcheck/list')
    for url in local_list:
        remote_list = read_from_fs(url)

        #2:
        local_list_name = str('/home/jony/.tvcheck/')
        local_list_name = local_list_name.__add__(url[19:].rstrip())

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
                download_episode(new_link, episode_name)
                print(new_link)                #put download part here
                #5:
                append_to_file(local_list_name, new_link)
                

"""call execution if runned from console"""

if __name__ == '__main__':
    main()


import os
import errno
import shutil
import sys
import re
import glob
import warnings
import math

import pydub
from pydub import AudioSegment
import matplotlib.pyplot as plt
import pandas as pd

from typing import List, Dict

# paths
CWD = os.getcwd()
DATA_ROOT = './data'
DATA_RAW = os.path.join(DATA_ROOT, 'raw_source_clips')

# convert class_num from int or str to proper type and value
# possible original formats: 2 (int) or '2, 3' (str)
def get_class(fclass, duration_ms:int, time_hour:int):
  if type(fclass) is not str:
    this_class = str(fclass)
  else:
    this_class = fclass

  this_class = this_class.replace(" ", "")
  class_path = os.path.join(DATA_RAW, this_class)
  if not os.path.exists(class_path):
    os.mkdir(class_path)
  return class_path

# convert a time given in the format "01:22" to an int (in milliseconds)
def time_str_to_int(time:str):
  time_parts:List[str] = time.split(':') # returns a list ['01', '22']
  min_ms:int = int(time_parts[0]) * 60000  # '01' -> 1 -> 60000
  sec_ms:int = int(time_parts[1]) * 1000  # '22' -> 22 -> 22000
  total_ms: int = min_ms + sec_ms
  return total_ms

# Clip the specified audio and put it in the corresponding folder
def clip(fname:str, start:str, end:str, fclass, fnames:List[str], input_path:str):
  # If name is blank, use previous fname. If no previous fname, exit with error
  if pd.isnull(fname):
    if not fnames:
      print("error: names empty");
      sys.exit(1)
    fname = fnames[-1]
  else:
    fnames.append(fname)

  # Load original_clip corresponding with fname
  # extension = fname.split('.')[-1]
  match = re.search('\w+-\d+-\d+-(\d+)-\d+-\d+', fname)
  if not match:
    sys.stderr.write('Couldn\'t find hour!\n')
    sys.exit(1)
  time_hour:int = int(match.group(1))
  fname_full = fname + ".wav"
  input_file = os.path.join(input_path, fname_full)
  original_clip = AudioSegment.from_wav(input_file)

  # Set defaults
  this_class = 'noise'
  new_clip = original_clip
  this_clip_name:str = fname_full

  # if file is empty/noise/no classes
  if not pd.isnull(fclass):
    # convert from seconds to milliseconds
    start_time_ms:int = time_str_to_int(start)
    end_time_ms:int = time_str_to_int(end)
    # clip original_clip according to start_time_ms and end_time_ms
    new_clip = original_clip[start_time_ms:end_time_ms]
    this_class = fclass
    this_clip_name = fname + '_' + start + '-' + end + ".wav"

  # Put clipped audio into directory corresponding with class
  duration_ms:int = len(new_clip)
  class_path:str = get_class(this_class, duration_ms, time_hour)
  new_clip_path:str = os.path.join(class_path, this_clip_name)
  new_clip.export(new_clip_path, format="wav")


# Parse Excel files to grab audio file 'name', 'start_time', 'end_time', 'class'
def parse(xl_name: str, input_path:str):
  col_names = ['name', 'start', 'end', 'class']
  dfs = pd.read_excel(xl_name, names=col_names, usecols=[0,1,2,3]) # panda Dataframe type
  fnames = []
  dfs.apply(lambda row: clip(row['name'], row['start'], row['end'], row['class'], fnames, input_path), axis=1)

def main():
  args = sys.argv[1:]
  if not args:
    print('usage: classify_audio.py dir');
    sys.exit(1)

  input_path = args[0]
  if not os.path.exists(DATA_ROOT):
    os.mkdir(DATA_ROOT)
  if not os.path.exists(DATA_RAW):
    os.mkdir(DATA_RAW)

  fnames = os.listdir(CWD)
  for fname in fnames:
    if not fname.lower().endswith(('.xlsx')):
      continue
    parse(fname, input_path)

if __name__ == '__main__':
  main()

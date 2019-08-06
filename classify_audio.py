#import subprocess
import os
import errno
import shutil
import sys
import re
import glob
import warnings
import math

#import librosa
#import librosa.display
import pydub
from pydub import AudioSegment
# import IPython
import matplotlib.pyplot as plt
import pandas as pd

from typing import List, Dict

# paths
CWD = os.getcwd()
# INPUT_PATH = os.path.join(CWD, 'data_curation_staging')
DATA_ROOT = './data'
DATA_RAW = os.path.join(DATA_ROOT, 'raw_source_clips')
# STATS = [0] * 10
# BABY_HOURS = [0] * 24
# MALE_DIR = os.path.join(DATA_RAW, 'adult_male')
# FEMALE_DIR = os.path.join(DATA_RAW, 'adult_female')
# MALE_PAREN_DIR = os.path.join(DATA_RAW, 'adult_male_parentese')
# FEMALE_PAREN_DIR = os.path.join(DATA_RAW, 'adult_female_parentese')
# BABBLE_MARG_DIR = os.path.join(DATA_RAW, 'baby_babble_marginal')
# BABBLE_DUP_DIR = os.path.join(DATA_RAW, 'baby_babble_duplicated')
# BABBLE_VAR_DIR = os.path.join(DATA_RAW, 'baby_babble_variagated')
# BABY_COO_DIR = os.path.join(DATA_RAW, 'baby_cooing')
# BABY_CRY_DIR = os.path.join(DATA_RAW, 'baby_cry')
# NOISE_DIR = os.path.join(DATA_RAW, 'noise')


# # create directories for each class
# def make_all_dirs():
#
#   if not os.path.exists(INPUT_PATH):
#     os.mkdir(INPUT_PATH)
#   if not os.path.exists(DATA_ROOT):
#     os.mkdir(DATA_ROOT)
#   if not os.path.exists(DATA_RAW):
#     os.mkdir(DATA_RAW)
#
#   if not os.path.exists(MALE_DIR):
#     os.mkdir(MALE_DIR)
#   if not os.path.exists(FEMALE_DIR):
#     os.mkdir(FEMALE_DIR)
#   if not os.path.exists(MALE_PAREN_DIR):
#     os.mkdir(MALE_PAREN_DIR)
#   if not os.path.exists(FEMALE_PAREN_DIR):
#     os.mkdir(FEMALE_PAREN_DIR)
#
#   if not os.path.exists(BABBLE_MARG_DIR):
#     os.mkdir(BABBLE_MARG_DIR)
#   if not os.path.exists(BABBLE_DUP_DIR):
#     os.mkdir(BABBLE_DUP_DIR)
#   if not os.path.exists(BABBLE_VAR_DIR):
#     os.mkdir(BABBLE_VAR_DIR)
#
#   if not os.path.exists(BABY_COO_DIR):
#     os.mkdir(BABY_COO_DIR)
#   if not os.path.exists(BABY_CRY_DIR):
#     os.mkdir(BABY_CRY_DIR)
#   if not os.path.exists(NOISE_DIR):
#     os.mkdir(NOISE_DIR)

# convert class_num from int or str to proper type and value
# possible original formats: 2 (int) or '2, 3' (str)
def get_class(fclass, duration_ms:int, time_hour:int):
  if type(fclass) is not str:
    #STATS[fclass] += duration_ms
    this_class = str(fclass)
  else:
    # if fclass != 'noise':
      # class_nums = fclass.split(',')
      # for class_num in class_nums:
      #   STATS[int(class_num)] += duration_ms
    this_class = fclass
  # if re.search('[56789]', this_class):  # if this clip contains baby sounds
  #   BABY_HOURS[time_hour] += duration_ms
  this_class = this_class.replace(" ", "")
  class_path = os.path.join(DATA_RAW, this_class)
  if not os.path.exists(class_path):
    os.mkdir(class_path)
  # dir_list = [NOISE_DIR, MALE_DIR, FEMALE_DIR, MALE_PAREN_DIR, FEMALE_PAREN_DIR,
  #             BABBLE_MARG_DIR, BABBLE_DUP_DIR, BABBLE_VAR_DIR,
  #             BABY_COO_DIR, BABY_CRY_DIR]
  # return dir_list[class_num]
  return class_path

# convert a time given in the format "01:22" to an int (in milliseconds)
def time_str_to_int(time:str):
  time_parts:List[str] = time.split(':') # returns a list ['01', '22']
  min_ms:int = int(time_parts[0]) * 60000  # '01' -> 1 -> 60000
  sec_ms:int = int(time_parts[1]) * 1000  # '22' -> 22 -> 22000
  total_ms: int = min_ms + sec_ms
  return total_ms

# Clip the specified audio and put it in the corresponding folder
# format of fname: "Village0_2019-6-7-16-59-18"
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
    # Clip original_clip according to start_time_ms and end_time_ms
    # ****** DO NOT MODIFY THIS ******
    new_clip = original_clip[start_time_ms:end_time_ms]
    # this_class = None  # reset as a safeguard
    # new_clip
    # ********************************
    this_class = fclass
    this_clip_name = fname + '_' + start + '-' + end + ".wav"

  # Put clipped audio into directory corresponding with class
  duration_ms:int = len(new_clip)
  class_path:str = get_class(this_class, duration_ms, time_hour)
  new_clip_path:str = os.path.join(class_path, this_clip_name)
  new_clip.export(new_clip_path, format="wav")


# Parse Excel files to grab audio file 'name', 'start_time', 'end_time', 'class'
# Example format: 'Village0_2019-6-8-19-25-29  00:00  00:05  6  High'
def parse(xl_name: str, input_path:str):
  #xl_file = pd.ExcelFile(fname)
  col_names = ['name', 'start', 'end', 'class']
  dfs = pd.read_excel(xl_name, names=col_names, usecols=[0,1,2,3]) # panda Dataframe type
  fnames = []
  dfs.apply(lambda row: clip(row['name'], row['start'], row['end'], row['class'], fnames, input_path), axis=1)

# # Display the distribution of classes with a pie chart
# def pie():
#   pie_name = os.path.join(DATA_ROOT, 'audio_stats.png')
#   classes = ['Male', 'Female', 'Male_paren', 'Female_paren',
#              'Babble_marg', 'Babble_dup', 'Babble_var', 'Baby_coo', 'Baby_cry']
#   plt.pie(STATS[1:], labels=classes)
#   plt.savefig(pie_name)
#
# def baby_hours():
#   baby_stats_name = os.path.join(DATA_ROOT, 'baby_audio_stats.xlsx')
#   baby_hours_in_sec = [time / 1000 for time in BABY_HOURS]
#   df = pd.DataFrame(data=baby_hours_in_sec)
#   df.to_excel(baby_stats_name)

def main():
  args = sys.argv[1:]
  if not args:
    print('usage: classify_audio.py dir');
    sys.exit(1)

  # make_all_dirs()
  # if not os.path.exists(INPUT_PATH):
  #   os.mkdir(INPUT_PATH)
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

  #pie()
  #baby_hours()

if __name__ == '__main__':
  main()

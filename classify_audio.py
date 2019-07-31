import subprocess
import os
import errno
import shutil
import sys
import re
import glob
import warnings
import math

import librosa
import librosa.display
import pydub
from pydub import AudioSegment
import IPython
import matplotlib.pyplot as plt
import pandas as pd

from typing import List, Dict

# paths
CWD = os.getcwd()
INPUT_PATH = os.path.join(CWD, 'data_curation_staging')
DATA_ROOT = './data'
DATA_RAW = os.path.join(DATA_ROOT, 'raw_source_clips')

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
def get_class(fclass):
  if type(fclass) is not str:
     this_class = str(fclass)
  else:
    this_class = fclass
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

def clip(fname:str, start:str, end:str, fclass, fnames: List[str]):
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
  fname_full = fname + ".wav"
  input_file = os.path.join(INPUT_PATH, fname_full)
  original_clip = AudioSegment.from_wav(input_file)

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

    # Put clipped audio into directory corresponding with class
    class_path:str = get_class(fclass)
    this_clip:str = fname + '_' + start + '-' + end + ".wav"
    new_clip.export(os.path.join(class_path, this_clip), format="wav")

  else:
    class_path:str = get_class('noise')
    original_clip.export(os.path.join(class_path, fname_full), format="wav")

# Parse Excel files to grab audio file 'name', 'start_time', 'end_time', 'class'
# Example format: 'Village0_2019-6-8-19-25-29  00:00  00:05  6  High'
def parse(xl_name: str):
  #xl_file = pd.ExcelFile(fname)
  col_names = ['name', 'start', 'end', 'class']
  dfs = pd.read_excel(xl_name, names=col_names, usecols=[0,1,2,3]) # panda Dataframe type
  fnames = []
  dfs.apply(lambda row: clip(row['name'], row['start'], row['end'], row['class'], fnames), axis=1)

# # Load files from data_curation_staging folder
# # ****** DO NOT MODIFY THIS ******
#
# # get all staged filenames
# file_names = [os.path.basename(name) for name in glob.glob(INPUT_PATH + '/*')]
# print('Number of files still in staging folder:', len(file_names))
#
# # we'll work only with the first entry
# input_file_name = file_names[0]
# extension = input_file_name.split('.')[-1]
# print('Name of Input File:', input_file_name)
# print('Extracted Extension:', extension)
#
# # load into pydyb
# input_file = os.path.join(INPUT_PATH, input_file_name)
# original_clip = AudioSegment.from_file(input_file, format=extension)
# print('Length of original clip (ms):', len(original_clip))
#
# # # we'll also load into librosa for easy waveform visualization
# # audio_clip, sampling_rate = librosa.load(input_file)
# # IPython.display.Audio(data=audio_clip, rate=sampling_rate)
# # plt.figure(figsize=(12, 4))
# # fig = librosa.display.waveplot(audio_clip, sr=sampling_rate)
#
# # # the notebook will auto-embed an audio player
# # original_clip
#
# # ********************************
#
# # trim clip and sample audio
# start_time_ms = 000
# end_time_ms = 45000
# #end_time_ms = len(original_clip)
#
#
# # ****** DO NOT MODIFY THIS ******
# new_clip = original_clip[start_time_ms:end_time_ms]
# this_class = None  # reset as a safeguard
# new_clip
# # ********************************
#
# # Classify the audio clip
# # first select the correct class... be sure about your selection!
#
# # this_class = "baby_babble"
# # this_class = "baby_cry"
# # this_class = "baby_laugh"
# # this_class = "adult_infant_directed"
# this_class = "domestic_background"
#
# # was this file obtained through a URL?
# #this_URL = 'https://freesound.org/people/Ephemeral_Rift/sounds/77447/'
# this_URL = None
#
# # add a description (optional, mostly for background sounds)
# # description_string = "now henry look over here"
# # description_string = "bathtub with water splashing"
# description_string = None
#
#
#
# # ****** DO NOT MODIFY THIS ******
# print('***\nThis clip has been categorized as:', this_class)
# print('Description:', description_string, '\n***')
#
# if this_URL is None:
#     print('\nNo source URL has been specified.')
# else:
#     print('\nSource clip was downloaded from:', this_URL)
# # ********************************

def main():
  args = sys.argv[1:]
  if not args:
    print("error: must specify one or more files as input");
    sys.exit(1)

  # make_all_dirs()
  if not os.path.exists(INPUT_PATH):
    os.mkdir(INPUT_PATH)
  if not os.path.exists(DATA_ROOT):
    os.mkdir(DATA_ROOT)
  if not os.path.exists(DATA_RAW):
    os.mkdir(DATA_RAW)
    
  for fname in args:
    if not fname.lower().endswith(('.xlsx')):
      continue
    parse(fname)


if __name__ == '__main__':
  main()

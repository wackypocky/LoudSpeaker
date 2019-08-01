import os
import errno
import shutil
import sys
import re
import glob
import warnings
from typing import List, Dict

import pydub
from pydub import AudioSegment
import IPython
import matplotlib.pyplot as plt
import pandas as pd

def iterate_dirs(source_dir:str, data_tuple = None, non_speech_dur:int = 0,
                 speech_dur:int = 0):
  if data_tuple is None:
    audio_by_class = [0] * 10
    baby_hours = [0] * 24
  else:
    (audio_by_class, baby_hours) = data_tuple
  entries = os.scandir(source_dir)
  for entry in entries:
    # if entry is not a subdirectory
    if not entry.is_dir():
      continue
    dir_name:str = entry.name.replace(" ", "")  # in case the directory has extra spaces

    # if directory does not have the right format for name
    if not re.fullmatch('[1-9](,[1-9])*|(noise)', dir_name):
      sys.stderr.write('Not a class directory')
      continue

    fnames:List[str] = os.listdir(entry.path)
    for fname in fnames:
      if not fname.lower().endswith(('.wav')):
        continue
      clip_path:str = os.path.join(entry.path, fname)
      this_clip = AudioSegment.from_wav(clip_path)
      duration_ms:int = len(this_clip)

      # update total non_speech duration if class is 'noise'
      if dir_name == 'noise':
        non_speech_dur += duration_ms
        continue

      # otherwise, update the other stats
      speech_dur += duration_ms
      class_nums:List[str] = dir_name.split(',')
      # update class stats
      for class_num in class_nums:
        audio_by_class[int(class_num)] += duration_ms

      # update baby_hours if current directory contains baby audio
      if re.search('[56789]', dir_name):
        match = re.search('\w+-\d+-\d+-(\d+)-\d+-\d+', fname)
        if not match:
          sys.stderr.write('Couldn\'t find hour!\n')
          sys.exit(1)
        time_hour:int = int(match.group(1))
        baby_hours[time_hour] += duration_ms
  return (audio_by_class, baby_hours, non_speech_dur, speech_dur)

# Create a pie chart w/ given data (list of ints)
def pie(name:str, dest_dir:str, data:List[int], labels:List[str]):
  pie_path:str = os.path.join(dest_dir, name)
  plt.pie(data, labels=labels)
  plt.savefig(pie_path)
  plt.clf()

# # Create a bar graph w/ given data (list of ints)
# def bar(data:List[int]):

# Create an excel file w/ given data (list of ints)
def to_excel(xl_name:str, dest_dir:str, data:List[int], labels:List[str] = []):
  xl_path:str = os.path.join(dest_dir, xl_name)
  data_in_sec = [time / 1000 for time in data]
  if labels:
    df = pd.DataFrame(data=data_in_sec, index=labels, columns=['Duration (sec)'])
  else:
    df = pd.DataFrame(data=data_in_sec, columns=['Duration (sec)'])
  df.to_excel(xl_path)

def main():
  args = sys.argv[1:]
  if not args:
    print('usage: stats.py {--by_dir | --total} file');
    sys.exit(1)

  option = args[0]
  dirs = args[1:]
  classes:List[str] = ['Male', 'Female', 'Male_paren', 'Female_paren',
                       'Babble_marg', 'Babble_dup', 'Babble_var', 'Baby_coo', 'Baby_cry']
  labels:List[str] = ['Speech (adult/baby)', 'Non-speech (silence/noise)']

  # iterate through input directories
  for dirname in dirs:
    entries = os.listdir(dirname)
    if not entries:  # if the directory is empty, continue
      continue
    if option == '--by_dir':
      (audio_by_class, baby_hours, non_speech_dur, speech_dur) = iterate_dirs(dirname)
      audio_by_class = audio_by_class[1:] # don't include first cell
      to_excel('audio_by_class.xlsx', dirname, audio_by_class, classes)
      to_excel('baby_hours.xlsx', dirname, baby_hours)
      speech_vs_noise:List[int] = [speech_dur, non_speech_dur]
      to_excel('speech_vs_noise.xlsx', dirname, speech_vs_noise, labels)
      pie('audio_by_class.png', dirname, audio_by_class, classes)
    else:
      if dirname == dirs[0]:
        (audio_by_class, baby_hours, non_speech_dur, speech_dur) = iterate_dirs(dirname)
      else:
        (audio_by_class, baby_hours, non_speech_dur, speech_dur) = iterate_dirs(dirname, (audio_by_class, baby_hours), non_speech_dur, speech_dur)

  # Create total stats over all directories if option is --total in cwd
  if option == '--total':
    cwd = os.getcwd()
    audio_by_class = audio_by_class[1:] # don't include first cell
    to_excel('audio_by_class.xlsx', cwd, audio_by_class, classes)
    to_excel('baby_hours.xlsx', cwd, baby_hours)
    speech_vs_noise:List[int] = [speech_dur, non_speech_dur]
    to_excel('speech_vs_noise.xlsx', cwd, speech_vs_noise, labels)
    pie('audio_by_class.png', cwd, audio_by_class, classes)

if __name__ == '__main__':
  main()

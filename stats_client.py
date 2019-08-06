import os
import sys
from typing import List, Dict

import pydub
from pydub import AudioSegment
# import IPython
import stats

def duration_dir(source_path:str):
  total_dur = 0
  fnames:List[str] = os.listdir(source_path)
  for fname in fnames:
    if not fname.lower().endswith(('.wav')):
      continue
    clip_path:str = os.path.join(source_path, fname)
    this_clip = AudioSegment.from_wav(clip_path)
    duration_ms:int = len(this_clip)
    total_dur += duration_ms
  return total_dur

def main():
  args = sys.argv[1:]
  if not args:
    print('usage: stats_client.py raw_dirs final_dir');
    sys.exit(1)

  # iterate through raw directories OR take the existing duration
  cwd = os.getcwd()
  path_to_file:str = os.path.join(cwd, "total_dur_raw.txt")
  if len(args) == 1:
    if not os.path.exists(path_to_file):
      print('error: total_dur_raw.txt file does not exist')
      sys.exit(1)
    final_dir = args[0]
    with open(path_to_file) as f:
      initial_dur:int = int(f.read())
  else:
    raw_dirs = args[:-1]
    final_dir = args[-1]
    initial_dur:int = 0
    for dirname in raw_dirs:
      initial_dur += duration_dir(dirname)
    f = open(path_to_file, 'w')
    f.write(str(initial_dur))
    f.close()

  # grab stats using final_dir as input
  (audio_by_class, baby_hours, speech_dur) = stats.iterate_dirs(final_dir)
  non_speech_dur:int = initial_dur - speech_dur
  speech_vs_noise:List[int] = [speech_dur, non_speech_dur]

  # export stats to excel files
  labels:List[str] = ['Speech (adult/baby)', 'Non-speech (silence/noise)']
  classes:List[str] = ['Male', 'Female', 'Male_paren', 'Female_paren',
                       'Babble_marg', 'Babble_dup', 'Babble_var', 'Baby_coo',
                       'Baby_cry']
  hours:List[str] = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10',
                     '11', '12', '13', '14', '15', '16', '17', '18', '19',
                     '20', '21', '22', '23']
  stats.to_excel('speech_vs_noise', cwd, speech_vs_noise, labels)
  stats.to_excel('audio_by_class', cwd, audio_by_class, classes)
  stats.to_excel('baby_hours', cwd, baby_hours)
  stats.pie('audio_by_class', cwd, audio_by_class, classes)
  stats.pie('speech_vs_noise', cwd, speech_vs_noise, labels)
  stats.bar('baby_hours', cwd, baby_hours, hours, 'Hour (24-hour clock)')

if __name__ == '__main__':
  main()

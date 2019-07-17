# Goal: automating the detection/removal of silent files, +90% white noise files,
# and the removal of silent periods within audio files

#from ffmpy import FFmpeg
import subprocess
import os
import errno
import shutil
import sys
import bpfilter
#import wave
#import matplotlib.pyplot as plt
from pydub import AudioSegment
#import soundfile as sf

DEFAULT_DURATION = 2 #seconds
DEFAULT_THRESHOLD = -35 #dBFS
SILENCE_CEILING = -25
NOISE_CEILING = -15
LOW_THRESHOLD = '-41.5dB'
HIGH_THRESHOLD = '-32dB'

# Check if file is silent
def is_silent(in_filename: str, ceiling: int):
  sound = AudioSegment.from_file(in_filename)
  peak_amplitude = sound.max_dBFS
  #print(in_filename, "peak:", peak_amplitude)
  if peak_amplitude < ceiling:
    return True
  else:
    return False

# Then, cut the sections of audio quieter than -32dB and delete the normalized directory
def remove_silence(source_path:str, dest_path:str, threshold:int):
  fnames: List[str] = os.listdir(source_path)
  if not os.path.exists(dest_path):
    os.mkdir(dest_path)
  for fname in fnames:
    if not fname.lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
      continue
    path_to_file = os.path.join(source_path, fname)
    args: List[str] = ['ffmpeg', '-i', path_to_file, '-af',
                       'silenceremove=start_periods=1:start_duration=0:'
                       'start_threshold=%s:start_silence=2:stop_periods=-1'
                       ':stop_duration=2:stop_threshold=%s' %(threshold, threshold),
                        dest_path + '/' + fname]
    p = subprocess.Popen(args)
    p.wait()
    p = subprocess.run(['rm', path_to_file])
  p = subprocess.run(['rm', '-r', source_path])

def filter_empty_audio(source_path:str, dest_path:str, ceiling:int):
  fnames: List[str] = os.listdir(source_path)
  if not os.path.exists(dest_path):
    os.mkdir(dest_path)
  for fname in fnames:
    if not fname.lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
      continue
    #plot(fname)
    path_to_file = os.path.join(source_path, fname)
    abspath = os.path.abspath(path_to_file)
    if is_silent(abspath, ceiling):
      continue
    else:
      shutil.copy(abspath, dest_path)
    p = subprocess.run(['rm', path_to_file])
  p = subprocess.run(['rm', '-r', source_path])

# First step: filtering out silent/white noise files
def main():
  args = sys.argv[1:]
  if not args:
    print("error: must specify one or more dirs");
    sys.exit(1)

  for dirname in args:
    # apply a band-pass filter
    dest_path = os.path.join(dirname, 'bp_filtered')
    bpfilter.filter(dirname, dest_path)

    # second pass through files to eliminate noise files
    source_path = dest_path
    dest_path = os.path.join(dirname, 'filtered')
    filter_empty_audio(source_path, dest_path, NOISE_CEILING)

    # second pass to cut pure silence in audio files
    source_path = dest_path
    dest_path = os.path.join(dirname, 'processed')
    remove_silence(source_path, dest_path, LOW_THRESHOLD)

if __name__ == '__main__':
  main()

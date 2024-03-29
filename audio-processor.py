# Automates the detection/removal of silent files, +90% white noise files,
# and the removal of silent periods within audio files

#from ffmpy import FFmpeg
import subprocess
import os
import errno
import shutil
import sys
import bpfilter
import merge
import re
from pydub import AudioSegment

DEFAULT_DURATION = 2 #seconds
DEFAULT_THRESHOLD = -35 #dBFS
SILENCE_CEILING = -25
PEAK_VOLUME_CEILING = -20
LOW_THRESHOLD = '-41dB'
HIGH_THRESHOLD = '-31dB'
MEAN_VOLUME_CEILING = -47.5

# Check if file is silent
def is_silent(in_filename: str, mean_ceiling: int, peak_ceiling:int):
  args: List[str] = ['ffmpeg', '-i', in_filename, '-af',
                     'volumedetect', '-f', 'null', '/dev/null']
  p = subprocess.Popen(args, stderr=subprocess.PIPE)
  stderr = p.communicate()[1].decode("utf-8")
  match = re.search('\[Parsed_volumedetect_0\s@\s\w+\]\smean_volume:\s(-\d+[.]?\d*)', stderr)
  if not match:
    sys.stderr.write('Couldn\'t find mean_volume!\n')
    sys.exit(1)
  mean_volume = float(match.group(1))
  sound = AudioSegment.from_file(in_filename)
  peak_amplitude = sound.max_dBFS
  # f = open("output.txt", "a")
  # print(in_filename, "mean_vol:", mean_volume, "peak:", peak_amplitude, file=f)
  # f.close()
  if mean_volume < mean_ceiling or peak_amplitude < peak_ceiling:
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
                       ':stop_duration=4:stop_threshold=%s' %(threshold, threshold),
                        dest_path + '/' + fname]
    p = subprocess.Popen(args)
    p.wait()
    p = subprocess.run(['rm', path_to_file])
  p = subprocess.run(['rm', '-r', source_path])

def filter_empty_audio(source_path:str, dest_path:str, mean_ceiling:int, peak_ceiling:int):
  fnames: List[str] = os.listdir(source_path)
  if not os.path.exists(dest_path):
    os.mkdir(dest_path)
  for fname in fnames:
    if not fname.lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
      continue
    path_to_file = os.path.join(source_path, fname)
    abspath = os.path.abspath(path_to_file)
    if is_silent(abspath, mean_ceiling, peak_ceiling):
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

    # first pass through files to eliminate noise files
    source_path = dest_path
    dest_path = os.path.join(dirname, 'filtered')
    filter_empty_audio(source_path, dest_path, MEAN_VOLUME_CEILING, PEAK_VOLUME_CEILING)

    # first pass to cut pure silence in audio files
    source_path = dest_path
    dest_path = os.path.join(dirname, 'silence_removed')
    remove_silence(source_path, dest_path, HIGH_THRESHOLD)

    # merge the files to ideally 5min lengths, but up to 10min
    source_path = dest_path
    dest_path = os.path.join(dirname, 'merged')
    merge.merge(source_path, dest_path)

    # second pass to cut pure silence in audio files (to get rid of concat silence)
    source_path = dest_path
    dest_path = os.path.join(dirname, 'processed')
    remove_silence(source_path, dest_path, HIGH_THRESHOLD)

if __name__ == '__main__':
  main()

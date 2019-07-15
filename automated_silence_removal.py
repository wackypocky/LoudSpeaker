# Goal: automating the detection/removal of silent files, +90% white noise files, and the removal of silent periods within audio files

#from ffmpy import FFmpeg
import subprocess
import os
import errno
import shutil
import sys
from pydub import AudioSegment

DEFAULT_DURATION = 2 #seconds
DEFAULT_THRESHOLD = -9 #dBFS

# TODO: Check if file is silent
def is_silent(in_filename):
  sound = AudioSegment.from_file(in_filename)
  peak_amplitude = sound.max_dBFS
  #print('file:', in_filename)
  #print('if', peak_amplitude, '>', DEFAULT_THRESHOLD)
  if peak_amplitude < DEFAULT_THRESHOLD:
    return True
  else:
    return False

# only files with speech are left in directory 'filtered'
# First, normalize all the files, they get put into 'normalized'
# Then, delete the filtered directory
def normalize(dirname):
  path_to_filtered = os.path.join(dirname, 'filtered')
  args: str = 'ffmpeg-normalize *.wav -of ../normalized -ext wav' #TODO: adjust file type as needed
  p = subprocess.Popen(args, shell=True, cwd=path_to_filtered)
  p.wait()
  p = subprocess.run(['rm', '-r', path_to_filtered])

# Then, cut the sections of audio quieter than -32dB and delete the normalized directory
def remove_silence(dirname):
  path_to_normalized = os.path.join(dirname, 'normalized')
  path_to_processed = os.path.join(dirname, 'processed')
  fnames: List[str] = os.listdir(path_to_normalized)
  if not os.path.exists(path_to_processed):
    os.mkdir(path_to_processed)
  for fname in fnames:
    args: List[str] = ['ffmpeg', '-i', path_to_normalized + '/' + fname, '-af',
                       'silenceremove=start_periods=1:start_duration=0:'
                       'start_threshold=-32dB:start_silence=0.5:stop_periods=-1'
                       ':stop_duration=2:stop_threshold=-32dB', path_to_processed + '/' + fname]
    p = subprocess.Popen(args)
    p.wait()
  p = subprocess.run(['rm', '-r', path_to_normalized])

def filter_empty_audio(dirname):
  fnames: List[str] = os.listdir(dirname)
  #abspath_dir = os.path.abspath(dirname)
  path_to_filtered = os.path.join(dirname, 'filtered')
  if not os.path.exists(path_to_filtered):
    os.mkdir(path_to_filtered)
  for fname in fnames:
    if not fname.lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
      continue
    path_to_file = os.path.join(dirname, fname)
    if is_silent(path_to_file):
      continue
    else:
      shutil.copy(path_to_file, path_to_filtered)

# First step: filtering out silent/white noise files
def main():
  args = sys.argv[1:]
  if not args:
    print("error: must specify one or more dirs");
    sys.exit(1)

  for dirname in args:
    filter_empty_audio(dirname)
    normalize(dirname)
    remove_silence(dirname)

  # path_to_dir = os.getcwd()
  # directory = os.listdir(path_to_dir)
  # os.mkdir('filtered')
  #
  # # 1) filter completely silent files
  # # 2) filter completely continuous (white noise) audio files
  # for file in directory:
  #   # write the file to new directory only if it contains usable audio
  #   if check_silent(file):
  #     continue
  #   else:
  #     shutil.copy(file, 'filtered')
  # work_dir = os.listdir('filtered')
  #
  # # 3) do a very low-pass filter (-60dB?) on remaining files
  # for file in work_dir:

if __name__ == '__main__':
  main()

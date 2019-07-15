# Goal: automating the detection/removal of silent files, +90% white noise files, and the removal of silent periods within audio files

#from ffmpy import FFmpeg
import subprocess
import os
import errno
import shutil
import sys

DEFAULT_DURATION = 2
DEFAULT_THRESHOLD = -30

# TODO: Check if file is silent
def is_silent(in_filename):
  # a) go through file and determine continuity of frequency/volume
  # b) filter by volume
  # c) use a denoiser
  return False

# only files with speech are left in directory 'filtered'
# First, normalize all the files, they get put into 'normalized'
# Then, delete the filtered directory
def normalize():
  args: str = 'ffmpeg-normalize *.m4a -of ../normalized -ext wav' #TODO: adjust file type as needed
  p = subprocess.Popen(args, shell=True, cwd='filtered')
  p.wait()
  p = subprocess.run(['rm', '-r', 'filtered'])

# Then, cut the sections of audio quieter than -32dB and delete the normalized directory
def remove_silence():
  fnames: List[str] = os.listdir('normalized')
  if not os.path.exists('processed'):
    os.mkdir('processed')
  for fname in fnames:
    args: List[str] = ['ffmpeg', '-i', './normalized/' + fname, '-af',
                       'silenceremove=start_periods=1:start_duration=0:'
                       'start_threshold=-32dB:start_silence=0.5:stop_periods=-1'
                       ':stop_duration=2:stop_threshold=-32dB', './processed/' + fname]
    p = subprocess.Popen(args)
    p.wait()
  p = subprocess.run(['rm', '-r', 'normalized'])

def filter_empty_audio(dirname):
  fnames: List[str] = os.listdir(dirname)
  if not os.path.exists('filtered'):
    os.mkdir('filtered')
  for fname in fnames:
    if is_silent(fname):
      continue
    else:
      path = os.path.join(dirname, fname)
      abspath = os.path.abspath(path)
      shutil.copy(abspath, 'filtered')

# First step: filtering out silent/white noise files
def main():
  args = sys.argv[1:]
  if not args:
    print("error: must specify one or more dirs");
    sys.exit(1)

  for dirname in args:
    filter_empty_audio(dirname)
    normalize()
    remove_silence()

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

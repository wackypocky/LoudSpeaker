# applies a band-pass filter on all audio files in given directories
# supports wav, m4a, mp3, mp4 file types
import subprocess
import os
import errno
import shutil
import sys
from pydub import AudioSegment

# def denoise(source_path:str, dest_path:str):
#   fnames: List[str] = os.listdir(source_path)
#   if not os.path.exists(dest_path):
#     os.mkdir(dest_path)
#   for fname in fnames:
#     if not fname.lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
#       continue
#     path_to_file = os.path.join(source_path, fname)
#     args: List[str] = ['ffmpeg', '-i', path_to_file, '-af',
#                        'lowpass=3000,highpass=200', dest_path + '/' + fname]
#     p = subprocess.Popen(args)
#     p.wait()
#
# apply the filter on all files in the current directory
def filter(source_path: str, dest_path: str):
  fnames: List[str] = os.listdir(source_path)
  if not os.path.exists(dest_path):
    os.mkdir(dest_path)
  for fname in fnames:
    if not fname.lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
      continue
    path_to_file = os.path.join(source_path, fname)
    args: List[str] = ['ffmpeg', '-i', path_to_file, '-af',
                       'lowpass=2750,highpass=300', dest_path + '/' + fname] #2750 for June
    p = subprocess.Popen(args)
    p.wait()

# iterate through the directories given as command line arguments
def main():
  args = sys.argv[1:]
  if not args:
    print("error: must specify one or more dirs");
    sys.exit(1)

  for dirname in args:
    dest_path = os.path.join(dirname, 'bp_filtered')
    filter(dirname, dest_path)

if __name__ == '__main__':
  main()

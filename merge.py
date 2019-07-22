# applies a band-pass filter on all audio files in given directories
# supports wav, m4a, mp3, mp4 file types
import subprocess
import os
import errno
import shutil
import sys
import re
from pydub import AudioSegment
import soundfile as sf

def duration(in_filename:str):
  file = sf.SoundFile(in_filename)
  duration:float = len(file) / file.samplerate
  return duration

def sorted_ls(path):
  #mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
  return list(sorted(os.listdir(path)))

# merge audio into files with length 5-10min long, ideally 5min
def merge(source_path: str, dest_path: str):
  fnames: List[str] = sorted_ls(source_path)
  if not os.path.exists(dest_path):
    os.mkdir(dest_path)
  print(fnames)
  while fnames:
    first:str = fnames.pop(0)
    if not first.lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
      continue
    absfirst = os.path.abspath(os.path.join(source_path, first))
    fdur:float = duration(absfirst) # in seconds
    # If file is already > 5min = 300sec, don't touch
    if fdur >= 300.0:
      shutil.copy(absfirst, dest_path)
      continue

    # Else file is < 5 minutes, combine with others
    nextdur:float = 0.0
    last:str = ''
    inlistname:str = os.path.join(source_path, 'inlist.txt')
    input = open(inlistname, 'a')
    print('file', "'%s'" %(absfirst), file=input)
    #input: List[str] = ['-i', absfirst] # list of all input arguments
    # If the next file + the current file > 10 min = 600sec, don't touch
    while fnames and fdur + nextdur <= 600.0:
      fnames.pop(0) # pop the current last item in merge (the one that corresponds with nextdur)
      if nextdur:   # if not the first iteration
        print('file', "'%s'" %(absnext), file=input)
        last:str = next

      if not fnames or not fnames[0].lower().endswith(('.wav', '.m4a', '.mp3', 'mp4')):
        continue
      fdur += nextdur
      next:str = fnames[0]
      absnext = os.path.abspath(os.path.join(source_path, next))
      nextdur:float = duration(absnext) # in seconds

    # either list is empty or next is the first in the next combined file
    # so concat
    if not last:
      shutil.copy(absfirst, dest_path)
      continue
    match = re.search('([\w-]+).wav', absfirst)
    if not match:
      sys.stderr.write('Couldn\'t find base name!\n')
      sys.exit(1)
    start_name = match.group(1)
    match = re.search('Village0_2019-\d+-\d+-(\d+-\d+-\d+.wav)', last)
    if not match:
      sys.stderr.write('Couldn\'t find end-timestamp!\n')
      sys.exit(1)
    end_time = match.group(1)
    input.close()

    destfilename:str = dest_path + '/' + start_name + '-to-' + end_time
    args: List[str] = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', inlistname,
                       '-c', 'copy', destfilename]
    p = subprocess.Popen(args)
    p.wait()
    #p = subprocess.run(['rm', inlistname])

# iterate through the directories given as command line arguments
def main():
  args = sys.argv[1:]
  if not args:
    print("error: must specify one or more dirs");
    sys.exit(1)

  for dirname in args:
    dest_path = os.path.join(dirname, 'merge')
    merge(dirname, dest_path)

if __name__ == '__main__':
  main()

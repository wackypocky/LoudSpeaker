# simple program to automate play-through of all audio files in a directory
import os
import sys
import simpleaudio as sa

def main():
  dir_name = sys.argv[1]
  files = os.listdir(dir_name)
  for file in files:
    path_to_file = os.path.join(dir_name, file)
    wave_obj = sa.WaveObject.from_wave_file(path_to_file)
    print(file)
    play_obj = wave_obj.play()
    play_obj.wait_done()

if __name__ == '__main__':
  main()

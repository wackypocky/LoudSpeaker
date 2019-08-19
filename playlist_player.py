# simple program to automate play-through of all audio files in a directory
import os
import sys
from pydub import AudioSegment
import simpleaudio as sa
from pydub.playback import play

def main():
  dir_name = sys.argv[1]
  files = os.listdir(dir_name)
  files = sorted(files)
  total_duration_ms:int = 0
  for file in files:
    if not file.lower().endswith(('.flac')):
      continue
    path_to_file = os.path.join(dir_name, file)
    if os.path.getsize(path_to_file) < 1000:  # in case the clip is empty
      continue
    flac_audio = AudioSegment.from_file(path_to_file, "flac")
    print(file)
    play(flac_audio)
    # total_duration_ms += len(flac_audio)
    # wave_obj = sa.WaveObject.from_wave_file(path_to_file)
    # print(total_duration_ms)
    # play_obj = wave_obj.play()
    # play_obj.wait_done()
  # f = open("processed_total_duration", 'w')
  # f.write(str(total_duration_ms))
  # f.close()
if __name__ == '__main__':
  main()

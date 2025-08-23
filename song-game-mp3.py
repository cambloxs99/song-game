# MAC
import tkinter as tk
import random
import re
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from pydub import AudioSegment
from tkinter import filedialog
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from pydub.playback import _play_with_ffplay as play

def main():

    # sys.argv[0] is the path to this file.
    ffmpegPath = os.path.join(os.path.dirname(sys.argv[0]), "ffmpeg", "ffmpeg")
    AudioSegment.converter = ffmpegPath
    def seconds(n):
        return n * 1000 # converts milliseconds to seconds

    def segmentRandom(song, duration):
        songAsMP3 = MP3(song)
        milliLength = int(songAsMP3.info.length * 1000)
        start = random.randint(0, milliLength - duration)
        song = AudioSegment.from_mp3(song)
        segmentClip = song[start:start + duration]
        return segmentClip
    
    def doGame(fileName, fileName2, segmentClip, score):
        x = False
        while x == False:
            guess = input("What is the name of the song? (Type \"?\" to replay)\n")
            if re.fullmatch(fileName.lower(), guess.lower()) or re.fullmatch(fileName2.lower(), guess.lower()):
                print("Correct!")
                score += 1
                x = True
            elif guess == "?":
                play(segmentClip)
            else:
                print("Incorrect!")
                print(fileName)
                x = True
        return score
    def advancedFileName(name):
        m = re.search(r"\(.*?\)", name) # finds () if in file title
        if m:
            name = rf"^{re.escape(name[:m.start()].strip())}\s?({re.escape(name[m.start():m.end()])})?" # e.g. "Teammate" or "Teammate (syrvivor)"- from "Teammate (syrvivor)"
        else:
            m = re.search(r"\.mp3$", name)
            if m:
                name = name[:m.start()] # e.g. "Gateway" - from "Gateway.mp3"
        m = re.search(r"^The\s", name)
        if m:
            name = rf"^(The\s)?" + name[4:] # removes "The ", which apparently is 4 i thought it was 3 i guess i was wrong
        elif re.search(r"^\^The\\\s", name):
            name = rf"^(The\s)?" + name[6:]
        return name.strip()

    score = 0
    songPaths = None
    useFileName = False
    f = filedialog.askdirectory(title="Select File")
    path = Path(f)
    songPaths = list(path.glob("**/*.mp3"))
    t = input("Use file names? (As opposed to metadata song titles)\ny/n\n")
    useFileName = True if t.lower() == 'y' else False
    if not useFileName:
        for file in songPaths:
            fileAsMP3 = MP3(file)
            name = fileAsMP3.get("TIT2")
            if not name:
                print('Missing name found, using file names.')
                useFileName = True
            if not (name.text[0]): # type: ignore
                print('Missing name found, using file names.')
                useFileName = True
    random.shuffle(songPaths) # shuffle song play order


    playFor = int(input("Preview songs for how many seconds?\n"))
    playFor = seconds(playFor)

    if songPaths:
        for file in songPaths: # e.g. /Users/user/song/Gateway.mp3
            segmentClip = segmentRandom(file, playFor)
            fileAsMP3 = MP3(file)
            if useFileName:
                fileName = (str(fileAsMP3.filename)).split("/")[-1] # e.g. "Gateway.mp3"
            else:
                fileAsID3 = ID3(file)
                fileName = fileAsID3.get('TIT2')
                fileName = fileName.text[0] # type: ignore
            fileName2 = advancedFileName(fileName)
            play(segmentClip)
            # print(f"\"{fileName}\"") if need check errors in regex operation
            score = doGame(fileName, fileName2, segmentClip, score)
        print(f"All songs completed.\nFinal score:\n{score}/{len(songPaths)}")
    else:
        print("No songs (.mp3) found.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    main()

<div align="center">

# Automatic Audio Segment based on Text (AAST)

<a href="https://pytorch.org/get-started/locally/"><img alt="PyTorch" src="https://img.shields.io/badge/PyTorch-ee4c2c?logo=pytorch&logoColor=white"></a>
[![paper](http://img.shields.io/badge/paper-arxiv.1001.2234-B31B1B.svg)](https://arxiv.org/abs/2305.13516)
[![github](http://img.shields.io/badge/github-181717)](https://github.com/facebookresearch/fairseq/tree/main/examples/mms/data_prep)
</div>

This repository makes it easier and more powerful to use the Audio Segment Model provided by [MMS Aligner](https://github.com/facebookresearch/fairseq/tree/main/examples/mms/data_prep).
For Japanese, kanji to hiragana conversion is supported before voice segmentation. (use *-l* args)


## Installation
- Step 1: **Git clone**
  ```
  git clone https://github.com/YJ-20/Automatic-Audio-Segment-based-on-Text.git
  ```
- Step 2: **Executes the installation script**
  ```
  cd Automatic-Audio-Segment-based-on-Text
  bash install.sh
  ```
---
## Run


- Step 1: **Prepare Data** 
Creates a text file corresponding to the original audio file. The audio will be split according to the text file's newlines. *txt*, *csv*, and *xlsx* are supported as text file extensions.

  Example content of the input text file :
  ```
  Text of the desired first segment
  Text of the desired second segment
  Text of the desired third segment
  ```
<br>

- Step 2: **Run AAST** 
You can choose run the audio segment code using **GUI** or **CLI**. <br>

- Step 2-1: **GUI Run**
Just execute the Python file ***run.py*** and follow the buttons on the tkinter GUI window.
  ```
  python run.py
  ```

- Step 2-2: **CLI Run**
Directly execute the Python file ***align_and_segment.py***. (required: -a, -t) Specify the audio path and text file path. (optional: -o, -l) Specify the path where the output file will be saved and the language of the audio.
  ```
  python align_and_segment.py -a /path/to/audio.wav -t /path/to/textfile -o /path/to/output_dir -l <iso_code>
  ```

---
The code above saves the split audio files under the output directory based on newlines in the input test file. Splitted audio information is stored in the ***splitted_audio_info.csv*** file in the output directory. Information stored: 1. original start time (audio_start_sec), 2. audio path (audio_filepath) 3. length (duration) 4. text

  ```
  {"audio_start_sec": 0.0, "audio_filepath": "/path/to/output/segment1.wav", "duration": 6.8, "text": "she wondered afterwards how she could have spoken with that hard serenity how she could have"}
  {"audio_start_sec": 6.8, "audio_filepath": "/path/to/output/segment2.wav", "duration": 5.3, "text": "gone steadily on with story after story poem after poem till"}
  {"audio_start_sec": 12.1, "audio_filepath": "/path/to/output/segment3.wav", "duration": 5.9, "text": "allan's grip on her hands relaxed and he fell into a heavy tired sleep"}
  ```
---
  Source: [MMS Aligner](https://github.com/facebookresearch/fairseq/tree/main/examples/mms/data_prep)

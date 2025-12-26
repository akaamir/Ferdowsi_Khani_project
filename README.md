# Praat TextGrid Parser and Audio Segment Extractor

A Python tool for parsing Praat TextGrid files and extracting audio segments based on interval labels. Supports both WAV and MP3 audio formats.

## Features

- Parse Praat TextGrid files in long format
- Extract intervals by label (e.g., 'r', 'e', 'm')
- Concatenate audio segments and save to WAV or MP3 files
- Support for both `pydub` and `librosa` audio processing
- Automatic format detection from file extension
- Command-line interface and Python API

## Installation

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install ffmpeg (required for MP3 support)

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/)

## Usage

### Command Line Interface

Basic usage to extract 'r' labeled segments from WAV:

```bash
python praat_textgrid_parser.py input.wav input.TextGrid output_r.wav
```

Extract from MP3 and save as MP3:

```bash
python praat_textgrid_parser.py input.mp3 input.TextGrid output_r.mp3
```

Extract from MP3 and save as WAV:

```bash
python praat_textgrid_parser.py input.mp3 input.TextGrid output_r.wav
```

Extract a different label (e.g., 'e' or 'm'):

```bash
python praat_textgrid_parser.py input.wav input.TextGrid output_e.wav --label e
```

Use librosa instead of pydub:

```bash
python praat_textgrid_parser.py input.wav input.TextGrid output.wav --method librosa
```

### Python API

**Working with WAV files:**
```python
from praat_textgrid_parser import TextGridParser, extract_and_concatenate_audio

# Parse TextGrid file
parser = TextGridParser('input.TextGrid')
parser.parse()

# Get time ranges for 'r' labeled intervals
time_ranges = parser.get_time_ranges('r')

# Extract and concatenate audio
extract_and_concatenate_audio('input.wav', time_ranges, 'output_r.wav')
```

**Working with MP3 files:**
```python
from praat_textgrid_parser import TextGridParser, extract_and_concatenate_audio

# Parse TextGrid file
parser = TextGridParser('input.TextGrid')
time_ranges = parser.get_time_ranges('r')

# Extract from MP3, save as MP3
extract_and_concatenate_audio('input.mp3', time_ranges, 'output_r.mp3')

# Or extract from MP3, save as WAV
extract_and_concatenate_audio('input.mp3', time_ranges, 'output_r.wav')
```

## Examples

See `example_usage.py` for more detailed examples:

1. **Extract specific label segments (WAV)**
2. **Extract specific label segments (MP3)**
3. **Extract multiple labels to separate files**
4. **Analyze TextGrid statistics**

## TextGrid Format

This parser supports Praat TextGrid files in long format:

```
File type = "ooTextFile"
Object class = "TextGrid"

xmin = 0
xmax = 3712.0344217687075
tiers? <exists>
size = 1
item []:
    item [1]:
        class = "IntervalTier"
        name = "Style_Segment"
        xmin = 0
        xmax = 3712.0344217687075
        intervals: size = 73
        intervals [1]:
            xmin = 0
            xmax = 7.494897959183674
            text = "e"
        intervals [2]:
            xmin = 7.494897959183674
            xmax = 30.20011733017007
            text = "m"
        ...
```

## API Reference

### TextGridParser

**`__init__(textgrid_path: str)`**
- Initialize parser with path to TextGrid file

**`parse() -> List[Dict]`**
- Parse the TextGrid file and return all intervals
- Returns list of dicts with keys: `interval_num`, `xmin`, `xmax`, `text`

**`get_intervals_by_label(label: str) -> List[Dict]`**
- Get all intervals matching a specific label

**`get_time_ranges(label: str) -> List[Tuple[float, float]]`**
- Get (start_time, end_time) tuples for intervals with specific label

### extract_and_concatenate_audio

**`extract_and_concatenate_audio(audio_path, time_ranges, output_path, use_pydub=True)`**
- Extract audio segments and concatenate them
- `audio_path`: Path to input audio file (WAV or MP3)
- `time_ranges`: List of (start_time, end_time) tuples in seconds
- `output_path`: Path for output audio file (WAV or MP3, auto-detected from extension)
- `use_pydub`: Use pydub (True) or librosa (False)

## Output

The script will:
1. Parse the TextGrid file to find all intervals with the specified label
2. Extract corresponding audio segments from the WAV file
3. Concatenate segments in order
4. Save to a new WAV file
5. Print statistics (number of segments, total duration)

Example output:
```
Parsing TextGrid file: input.TextGrid
Found 25 intervals with label 'r'

Extracting audio segments from: input.wav
Extracted 25 segments
Total duration: 125.43 seconds
Saved to: output_r.wav
```

## Requirements

- Python 3.7+
- pydub (recommended) OR librosa + soundfile
- ffmpeg (required for MP3 support)

## License

This is open-source software. Feel free to use and modify as needed.

## Troubleshooting

**Error: "ffmpeg not found"**
- Install ffmpeg (see Installation section)
- ffmpeg is required for MP3 support with both pydub and librosa methods

**Error: "No intervals found"**
- Check that the label matches exactly (case-sensitive)
- Verify the TextGrid file format matches the expected structure

**Memory issues with large files**
- Use `--method librosa` for better memory efficiency with large files
- Consider processing in smaller chunks if needed

**MP3 quality concerns**
- Output MP3 files use the default quality settings
- For lossless audio, use WAV format for both input and output
- You can convert between formats: MP3 input → WAV output or vice versa

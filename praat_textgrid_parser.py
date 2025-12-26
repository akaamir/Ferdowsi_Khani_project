"""
Praat TextGrid Parser and Audio Segment Extractor

This script parses Praat TextGrid files and extracts audio segments
based on interval labels. Supports both WAV and MP3 audio formats.
"""

import re
import os
from typing import List, Dict, Tuple


class TextGridParser:
    """Parser for Praat TextGrid files in long format."""

    def __init__(self, textgrid_path: str):
        """
        Initialize the TextGrid parser.

        Args:
            textgrid_path: Path to the TextGrid file
        """
        self.textgrid_path = textgrid_path
        self.intervals = []

    def parse(self) -> List[Dict[str, any]]:
        """
        Parse the TextGrid file and extract all intervals.

        Returns:
            List of dictionaries containing interval information
            Each dict has keys: 'xmin', 'xmax', 'text'
        """
        with open(self.textgrid_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract intervals using regex
        # Pattern matches: intervals [n]: ... xmin = ... xmax = ... text = "..."
        interval_pattern = r'intervals\s*\[(\d+)\]:\s*xmin\s*=\s*([\d.]+)\s*xmax\s*=\s*([\d.]+)\s*text\s*=\s*"([^"]*)"'

        matches = re.findall(interval_pattern, content)

        self.intervals = []
        for match in matches:
            interval_num, xmin, xmax, text = match
            self.intervals.append({
                'interval_num': int(interval_num),
                'xmin': float(xmin),
                'xmax': float(xmax),
                'text': text
            })

        return self.intervals

    def get_intervals_by_label(self, label: str) -> List[Dict[str, any]]:
        """
        Get all intervals with a specific label.

        Args:
            label: The text label to filter by (e.g., 'r', 'e', 'm')

        Returns:
            List of intervals matching the label
        """
        if not self.intervals:
            self.parse()

        return [interval for interval in self.intervals if interval['text'] == label]

    def get_time_ranges(self, label: str) -> List[Tuple[float, float]]:
        """
        Get time ranges (xmin, xmax) for intervals with a specific label.

        Args:
            label: The text label to filter by

        Returns:
            List of (start_time, end_time) tuples
        """
        intervals = self.get_intervals_by_label(label)
        return [(interval['xmin'], interval['xmax']) for interval in intervals]


def extract_and_concatenate_audio(audio_path: str,
                                  time_ranges: List[Tuple[float, float]],
                                  output_path: str,
                                  use_pydub: bool = True):
    """
    Extract audio segments from a WAV or MP3 file and concatenate them.

    Args:
        audio_path: Path to input audio file (WAV or MP3)
        time_ranges: List of (start_time, end_time) tuples in seconds
        output_path: Path for output audio file (WAV or MP3)
        use_pydub: If True, use pydub library; otherwise use librosa
    """
    if use_pydub:
        _extract_with_pydub(audio_path, time_ranges, output_path)
    else:
        _extract_with_librosa(audio_path, time_ranges, output_path)


def _extract_with_pydub(audio_path: str,
                        time_ranges: List[Tuple[float, float]],
                        output_path: str):
    """Extract and concatenate audio segments using pydub (supports WAV and MP3)."""
    from pydub import AudioSegment

    # Auto-detect input format from file extension
    input_ext = os.path.splitext(audio_path)[1].lower()
    if input_ext == '.mp3':
        audio = AudioSegment.from_mp3(audio_path)
    elif input_ext == '.wav':
        audio = AudioSegment.from_wav(audio_path)
    else:
        # Try generic file loader
        audio = AudioSegment.from_file(audio_path)

    # Extract and concatenate segments
    concatenated = AudioSegment.empty()

    for start_time, end_time in time_ranges:
        # Convert seconds to milliseconds (pydub uses milliseconds)
        start_ms = int(start_time * 1000)
        end_ms = int(end_time * 1000)

        # Extract segment
        segment = audio[start_ms:end_ms]
        concatenated += segment

    # Auto-detect output format from file extension
    output_ext = os.path.splitext(output_path)[1].lower()
    if output_ext == '.mp3':
        output_format = 'mp3'
    elif output_ext == '.wav':
        output_format = 'wav'
    else:
        output_format = 'wav'  # Default to WAV

    # Export the concatenated audio
    concatenated.export(output_path, format=output_format)
    print(f"Extracted {len(time_ranges)} segments")
    print(f"Total duration: {len(concatenated) / 1000:.2f} seconds")
    print(f"Saved to: {output_path}")


def _extract_with_librosa(audio_path: str,
                          time_ranges: List[Tuple[float, float]],
                          output_path: str):
    """Extract and concatenate audio segments using librosa (supports WAV and MP3)."""
    import numpy as np
    import soundfile as sf
    import librosa

    # Load the audio file (librosa handles both WAV and MP3)
    audio_data, sample_rate = librosa.load(audio_path, sr=None, mono=False)

    # librosa.load returns shape (n_samples,) for mono and (2, n_samples) for stereo
    # Transpose if stereo to match soundfile convention (n_samples, 2)
    if len(audio_data.shape) == 2:
        audio_data = audio_data.T

    # Extract and concatenate segments
    segments = []

    for start_time, end_time in time_ranges:
        # Convert seconds to samples
        start_sample = int(start_time * sample_rate)
        end_sample = int(end_time * sample_rate)

        # Extract segment
        if len(audio_data.shape) == 1:  # Mono
            segment = audio_data[start_sample:end_sample]
        else:  # Stereo or multi-channel
            segment = audio_data[start_sample:end_sample, :]

        segments.append(segment)

    # Concatenate all segments
    concatenated = np.concatenate(segments, axis=0)

    # Determine output format
    output_ext = os.path.splitext(output_path)[1].lower()

    # Save the concatenated audio
    if output_ext == '.mp3':
        # For MP3 output with librosa/soundfile, we need to use pydub as fallback
        # since soundfile doesn't support MP3 writing
        try:
            from pydub import AudioSegment
            import io

            # Write to temporary WAV in memory
            wav_buffer = io.BytesIO()
            sf.write(wav_buffer, concatenated, sample_rate, format='WAV')
            wav_buffer.seek(0)

            # Convert to MP3 using pydub
            audio_segment = AudioSegment.from_wav(wav_buffer)
            audio_segment.export(output_path, format='mp3')
        except ImportError:
            print("Warning: MP3 output requires pydub. Saving as WAV instead.")
            output_path = os.path.splitext(output_path)[0] + '.wav'
            sf.write(output_path, concatenated, sample_rate)
    else:
        # WAV or other formats supported by soundfile
        sf.write(output_path, concatenated, sample_rate)

    print(f"Extracted {len(time_ranges)} segments")
    print(f"Total duration: {len(concatenated) / sample_rate:.2f} seconds")
    print(f"Saved to: {output_path}")


def main():
    """Example usage of the TextGrid parser and audio extractor."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Extract audio segments from WAV/MP3 file based on Praat TextGrid labels'
    )
    parser.add_argument('audio_file', help='Path to input audio file (WAV or MP3)')
    parser.add_argument('textgrid_file', help='Path to TextGrid file')
    parser.add_argument('output_file', help='Path to output audio file (WAV or MP3)')
    parser.add_argument('--label', default='r',
                       help='Label to extract (default: r)')
    parser.add_argument('--method', choices=['pydub', 'librosa'], default='pydub',
                       help='Library to use for audio processing (default: pydub)')

    args = parser.parse_args()

    # Parse TextGrid file
    print(f"Parsing TextGrid file: {args.textgrid_file}")
    tg_parser = TextGridParser(args.textgrid_file)
    tg_parser.parse()

    # Get time ranges for the specified label
    time_ranges = tg_parser.get_time_ranges(args.label)
    print(f"Found {len(time_ranges)} intervals with label '{args.label}'")

    if not time_ranges:
        print(f"No intervals found with label '{args.label}'")
        return

    # Extract and concatenate audio
    print(f"\nExtracting audio segments from: {args.audio_file}")
    use_pydub = (args.method == 'pydub')
    extract_and_concatenate_audio(args.audio_file, time_ranges, args.output_file, use_pydub)


if __name__ == '__main__':
    main()

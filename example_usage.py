"""
Example usage of the Praat TextGrid parser and audio extractor.

This script demonstrates how to use the parser programmatically.
"""

from praat_textgrid_parser import TextGridParser, extract_and_concatenate_audio


def example_extract_r_segments():
    """Example: Extract all 'r' labeled segments from audio."""

    # File paths
    wav_file = 'input_audio.wav'  # Replace with your WAV file path
    textgrid_file = 'input_textgrid.TextGrid'  # Replace with your TextGrid file path
    output_file = 'output_r_segments.wav'  # Output file path

    # Parse the TextGrid file
    print("Parsing TextGrid file...")
    parser = TextGridParser(textgrid_file)
    parser.parse()

    # Get all intervals with label 'r'
    r_intervals = parser.get_intervals_by_label('r')
    print(f"Found {len(r_intervals)} intervals labeled 'r'")

    # Display the intervals
    for i, interval in enumerate(r_intervals[:5], 1):  # Show first 5
        print(f"  Interval {i}: {interval['xmin']:.3f}s - {interval['xmax']:.3f}s")
    if len(r_intervals) > 5:
        print(f"  ... and {len(r_intervals) - 5} more")

    # Get time ranges
    time_ranges = parser.get_time_ranges('r')

    # Extract and concatenate audio
    print(f"\nExtracting audio segments...")
    extract_and_concatenate_audio(wav_file, time_ranges, output_file, use_pydub=True)
    print(f"\nDone! Output saved to: {output_file}")


def example_extract_multiple_labels():
    """Example: Extract multiple different labels to separate files."""

    wav_file = 'input_audio.wav'
    textgrid_file = 'input_textgrid.TextGrid'

    # Parse once
    parser = TextGridParser(textgrid_file)
    parser.parse()

    # Extract each label to a separate file
    labels = ['r', 'e', 'm']

    for label in labels:
        time_ranges = parser.get_time_ranges(label)
        if time_ranges:
            output_file = f'output_{label}_segments.wav'
            print(f"\nExtracting '{label}' segments to {output_file}...")
            extract_and_concatenate_audio(wav_file, time_ranges, output_file, use_pydub=True)
        else:
            print(f"No intervals found for label '{label}'")


def example_analyze_textgrid():
    """Example: Analyze TextGrid without extracting audio."""

    textgrid_file = 'input_textgrid.TextGrid'

    # Parse the TextGrid
    parser = TextGridParser(textgrid_file)
    intervals = parser.parse()

    print(f"Total intervals: {len(intervals)}")

    # Count intervals by label
    label_counts = {}
    total_duration_by_label = {}

    for interval in intervals:
        label = interval['text']
        duration = interval['xmax'] - interval['xmin']

        label_counts[label] = label_counts.get(label, 0) + 1
        total_duration_by_label[label] = total_duration_by_label.get(label, 0) + duration

    print("\nLabel statistics:")
    for label in sorted(label_counts.keys()):
        count = label_counts[label]
        total_duration = total_duration_by_label[label]
        avg_duration = total_duration / count
        print(f"  '{label}': {count} intervals, "
              f"total {total_duration:.2f}s, "
              f"avg {avg_duration:.2f}s")


if __name__ == '__main__':
    # Uncomment the example you want to run:

    # Example 1: Extract 'r' segments
    # example_extract_r_segments()

    # Example 2: Extract multiple labels to separate files
    # example_extract_multiple_labels()

    # Example 3: Analyze TextGrid without audio extraction
    # example_analyze_textgrid()

    print("Please uncomment one of the examples above to run it.")
    print("Make sure to update the file paths with your actual files.")

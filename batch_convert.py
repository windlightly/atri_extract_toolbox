import os
import subprocess
import argparse
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List


def convert(input_file: str, output_dir: str, format: str) -> None:
    """Convert single file to target format"""
    output_file = os.path.join(output_dir, os.path.splitext(os.path.basename(input_file))[0] + '.' + format)
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', input_file, output_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            print(f"Error converting {input_file}: {result.stderr}")
    except Exception as e:
        print(f"Fatal error converting {input_file}: {str(e)}")
    


def batch_convert(input_files: List[str], output_dir: str, format: str, max_workers: int) -> None:
    """Batch convert files using thread pool"""
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(convert, input_file, output_dir, format)
            for input_file in input_files
        ]
        
        for _ in tqdm(as_completed(futures), total=len(futures)):
            pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Batch audio file converter')
    parser.add_argument('-i', '--input', type=str, default=os.getcwd(), help='Path to the input directory.')
    parser.add_argument('-o', '--output', type=str, default=os.path.join(os.getcwd(), "converted"), help='Path to the output directory.')
    parser.add_argument('-f', '--format', type=str, default='mp3', choices=['mp3', 'wav', 'flac', 'aac'], help='Output format.')
    parser.add_argument('-t', '--thread', type=int, default=16, help='Maximum number of concurrent conversions.')
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    SUPPORTED_INPUT_FORMATS = ["opus", "ogg", "wav", "flac", "m4a", "mp3", "aac"]
    
    input_files = []
    for f in os.listdir(args.input):
        file = os.path.join(args.input, f)
        if os.path.isfile(file):
            ext = os.path.splitext(f)[1][1:].lower()  # 获取不带点的扩展名
            if ext in SUPPORTED_INPUT_FORMATS:
                input_files.append(file)

    print(f"Found {len(input_files)} files to convert")
    batch_convert(input_files, args.output, args.format, args.thread)
    print("Conversion completed!")

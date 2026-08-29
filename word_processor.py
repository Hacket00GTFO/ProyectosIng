#!/usr/bin/env python3
"""
Word Processor - Actividad 3
Processes text files, extracts words, handles special characters, sorts alphabetically, and generates sorted word files.
Measures processing times and generates detailed log file.
"""

import os
import time
import re
from pathlib import Path
from typing import Tuple, Optional, List


def open_file(filename: str, base_dir: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Opens and reads a text file efficiently.
    
    Args:
        filename: Name of the file to open (e.g., "001.txt")
        base_dir: Base directory containing the files
        
    Returns:
        Tuple of (success: bool, content: Optional[str], error: Optional[str])
    """
    file_path = Path(base_dir) / filename
    
    # Try different encodings, starting with UTF-8
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return True, content, None
        except UnicodeDecodeError:
            continue  # Try next encoding
        except FileNotFoundError:
            return False, None, f"File not found: {filename}"
        except PermissionError:
            return False, None, f"Permission denied: {filename}"
        except Exception as e:
            return False, None, f"Error reading {filename}: {str(e)}"
    
    # If all encodings failed
    return False, None, f"Could not decode {filename} with any supported encoding"


def extract_words(text: str) -> List[str]:
    """
    Extracts words from text, handling special characters and hyphens.
    
    Args:
        text: String containing text content
        
    Returns:
        List of words (lowercase, no special characters)
    """
    # Replace hyphens with spaces to separate hyphenated words
    # "Automata-based" becomes "Automata based"
    text = text.replace('-', ' ')
    
    # Replace other common separators with spaces
    text = text.replace('_', ' ')
    text = text.replace('/', ' ')
    
    # Extract words using regex (only alphabetic characters)
    # This pattern matches sequences of letters
    words = re.findall(r'[a-zA-Z]+', text)
    
    # Convert to lowercase for consistent sorting
    words = [word.lower() for word in words]
    
    return words


def sort_and_save_words(words: List[str], output_filename: str) -> Tuple[bool, Optional[str]]:
    """
    Sorts words alphabetically and saves to file.
    
    Args:
        words: List of words to sort and save
        output_filename: Name of the output file
        
    Returns:
        Tuple of (success: bool, error: Optional[str])
    """
    try:
        # Sort words alphabetically
        sorted_words = sorted(words)
        
        # Remove duplicates if desired (optional - keeping duplicates for now)
        # sorted_words = sorted(set(words))
        
        # Write to file, one word per line
        with open(output_filename, 'w', encoding='utf-8') as f:
            for word in sorted_words:
                f.write(word + '\n')
        
        return True, None
    except PermissionError:
        return False, f"Permission denied writing {output_filename}"
    except Exception as e:
        return False, f"Error writing {output_filename}: {str(e)}"


def process_text_files(files_dir: str, log_filename: str) -> dict:
    """
    Process all text files, extract words, sort them, save as _sorted.txt, and generate timing log.
    
    Args:
        files_dir: Directory containing text files
        log_filename: Name of the log file to generate
        
    Returns:
        Dictionary with processing statistics
    """
    # Get all text files and sort them
    files_path = Path(files_dir)
    text_files = sorted([f for f in files_path.glob("*.txt") if not f.name.endswith('_sorted.txt')])
    
    if not text_files:
        print(f"No text files found in {files_dir}")
        return {"total_files": 0, "total_time": 0, "errors": 0}
    
    print(f"Found {len(text_files)} text files to process")
    
    # Timing variables
    total_start_time = time.perf_counter()
    cumulative_time = 0.0
    file_count = 0
    error_count = 0
    total_words_processed = 0
    
    # Statistics tracking
    individual_times = []
    word_counts = []
    error_files = []
    
    # Open log file for writing
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        # Write header
        log_file.write("=" * 80 + "\n")
        log_file.write("WORD PROCESSING LOG - ACTIVIDAD 3\n")
        log_file.write("=" * 80 + "\n")
        log_file.write(f"Processing directory: {files_dir}\n")
        log_file.write(f"Total files found: {len(text_files)}\n")
        log_file.write(f"Log file: {log_filename}\n")
        log_file.write("=" * 80 + "\n\n")
        
        # Write column headers
        log_file.write(f"{'File Name':<20} {'Process Time (ms)':<20} {'Cumulative (ms)':<20} {'Files Processed':<15} {'Status':<10}\n")
        log_file.write("-" * 80 + "\n")
        
        # Process each file
        for text_file in text_files:
            # Step 1: Open the file
            success, content, error = open_file(text_file.name, files_dir)
            
            if not success:
                # Log the error even if we couldn't open the file
                error_count += 1
                error_files.append((text_file.name, error))
                log_file.write(f"{text_file.name:<20} {'N/A':<20} {cumulative_time:<20.3f} {file_count + 1:<15} {'ERROR':<10}\n")
                file_count += 1
                continue
            
            # Step 2: Extract words and sort (measure this time specifically)
            process_start_time = time.perf_counter()
            
            try:
                # Extract words
                words = extract_words(content)
                word_counts.append(len(words))
                total_words_processed += len(words)
                
                # Sort and save
                output_filename = text_file.name.replace('.txt', '_sorted.txt')
                output_path = Path(files_dir) / output_filename
                
                save_success, save_error = sort_and_save_words(words, output_path)
                
                if not save_success:
                    error_count += 1
                    error_files.append((text_file.name, save_error))
                    status = "ERROR"
                else:
                    status = "SUCCESS"
                
            except Exception as e:
                error_count += 1
                error_files.append((text_file.name, f"Processing error: {str(e)}"))
                status = "ERROR"
            
            process_end_time = time.perf_counter()
            process_time_ms = (process_end_time - process_start_time) * 1000  # Convert to milliseconds
            
            cumulative_time += process_time_ms
            file_count += 1
            
            # Record individual time for statistics
            individual_times.append(process_time_ms)
            
            # Write to log file
            log_file.write(f"{text_file.name:<20} {process_time_ms:<20.3f} {cumulative_time:<20.3f} {file_count:<15} {status:<10}\n")
            
            # Print progress every 50 files
            if file_count % 50 == 0:
                print(f"Processed {file_count}/{len(text_files)} files...")
        
        # Calculate final statistics
        total_end_time = time.perf_counter()
        total_time_seconds = total_end_time - total_start_time
        total_time_ms = total_time_seconds * 1000
        
        # Write summary section
        log_file.write("\n" + "=" * 80 + "\n")
        log_file.write("PROCESSING SUMMARY\n")
        log_file.write("=" * 80 + "\n")
        log_file.write(f"Total files processed: {file_count}\n")
        log_file.write(f"Successful: {file_count - error_count}\n")
        log_file.write(f"Errors: {error_count}\n")
        log_file.write(f"Total words processed: {total_words_processed}\n")
        log_file.write(f"Total processing time: {cumulative_time:.3f} ms\n")
        log_file.write(f"Total program time: {total_time_ms:.3f} ms ({total_time_seconds:.3f} seconds)\n")
        
        if individual_times:
            avg_time = sum(individual_times) / len(individual_times)
            min_time = min(individual_times)
            max_time = max(individual_times)
            min_file = text_files[individual_times.index(min_time)].name
            max_file = text_files[individual_times.index(max_time)].name
            
            log_file.write(f"Average processing time per file: {avg_time:.3f} ms\n")
            log_file.write(f"Fastest file: {min_file} ({min_time:.3f} ms)\n")
            log_file.write(f"Slowest file: {max_file} ({max_time:.3f} ms)\n")
        
        if word_counts:
            avg_words = sum(word_counts) / len(word_counts)
            min_words = min(word_counts)
            max_words = max(word_counts)
            min_words_file = text_files[word_counts.index(min_words)].name
            max_words_file = text_files[word_counts.index(max_words)].name
            
            log_file.write(f"Average words per file: {avg_words:.0f}\n")
            log_file.write(f"File with fewest words: {min_words_file} ({min_words} words)\n")
            log_file.write(f"File with most words: {max_words_file} ({max_words} words)\n")
        
        log_file.write("=" * 80 + "\n")
        
        # Write error details if any
        if error_files:
            log_file.write("\nERROR DETAILS\n")
            log_file.write("-" * 80 + "\n")
            for filename, error in error_files:
                log_file.write(f"{filename}: {error}\n")
            log_file.write("-" * 80 + "\n")
    
    # Return statistics
    return {
        "total_files": file_count,
        "successful": file_count - error_count,
        "errors": error_count,
        "total_words_processed": total_words_processed,
        "total_processing_time_ms": cumulative_time,
        "total_program_time_ms": total_time_ms,
        "total_program_time_seconds": total_time_seconds,
        "avg_time_ms": sum(individual_times) / len(individual_times) if individual_times else 0,
        "min_time_ms": min(individual_times) if individual_times else 0,
        "max_time_ms": max(individual_times) if individual_times else 0,
        "avg_words": sum(word_counts) / len(word_counts) if word_counts else 0,
        "min_words": min(word_counts) if word_counts else 0,
        "max_words": max(word_counts) if word_counts else 0
    }


def main():
    """Main program entry point."""
    # Configuration
    files_directory = "CS13309_Archivos_HTML/Files"
    log_file = "log_a3_matricula.txt"
    
    print("Word Processor - Actividad 3")
    print("=" * 50)
    
    # Check if directory exists
    if not os.path.exists(files_directory):
        print(f"Error: Directory '{files_directory}' not found.")
        print("Please ensure the text files are in the correct location.")
        return
    
    # Process files
    print(f"Processing files from: {files_directory}")
    print(f"Generating log file: {log_file}")
    print(f"Output files will be saved as _sorted.txt in the same directory")
    print()
    
    stats = process_text_files(files_directory, log_file)
    
    # Print summary to console
    print("\n" + "=" * 50)
    print("PROCESSING COMPLETE")
    print("=" * 50)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Successful: {stats['successful']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total words processed: {stats['total_words_processed']}")
    print(f"Total processing time: {stats['total_processing_time_ms']:.3f} ms")
    print(f"Total program time: {stats['total_program_time_ms']:.3f} ms ({stats['total_program_time_seconds']:.3f} seconds)")
    print(f"Average processing time per file: {stats['avg_time_ms']:.3f} ms")
    print(f"Average words per file: {stats['avg_words']:.0f}")
    print(f"Log file saved: {log_file}")
    print("=" * 50)


if __name__ == "__main__":
    main()
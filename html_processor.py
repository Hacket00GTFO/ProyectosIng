#!/usr/bin/env python3
"""
HTML File Processor
Processes HTML files and measures opening times for academic assignment.
Generates detailed log file with timing information.
"""

import os
import time
from pathlib import Path
from typing import Tuple, Optional


def open_file(filename: str, base_dir: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Opens and reads an HTML file efficiently.
    
    Args:
        filename: Name of the file to open (e.g., "001.html")
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


def process_html_files(files_dir: str, log_filename: str) -> dict:
    """
    Process all HTML files in the specified directory and generate timing log.
    
    Args:
        files_dir: Directory containing HTML files
        log_filename: Name of the log file to generate
        
    Returns:
        Dictionary with processing statistics
    """
    # Get all HTML files and sort them
    files_path = Path(files_dir)
    html_files = sorted([f for f in files_path.glob("*.html") if f.is_file()])
    
    if not html_files:
        print(f"No HTML files found in {files_dir}")
        return {"total_files": 0, "total_time": 0, "errors": 0}
    
    print(f"Found {len(html_files)} HTML files to process")
    
    # Timing variables
    total_start_time = time.perf_counter()
    cumulative_time = 0.0
    file_count = 0
    error_count = 0
    
    # Statistics tracking
    individual_times = []
    error_files = []
    
    # Open log file for writing
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        # Write header
        log_file.write("=" * 80 + "\n")
        log_file.write("HTML FILE PROCESSING LOG\n")
        log_file.write("=" * 80 + "\n")
        log_file.write(f"Processing directory: {files_dir}\n")
        log_file.write(f"Total files found: {len(html_files)}\n")
        log_file.write(f"Log file: {log_filename}\n")
        log_file.write("=" * 80 + "\n\n")
        
        # Write column headers
        log_file.write(f"{'File Name':<20} {'Time (ms)':<15} {'Cumulative (ms)':<20} {'Files Processed':<15} {'Status':<10}\n")
        log_file.write("-" * 80 + "\n")
        
        # Process each file
        for html_file in html_files:
            file_start_time = time.perf_counter()
            
            # Open the file
            success, content, error = open_file(html_file.name, files_dir)
            
            file_end_time = time.perf_counter()
            file_time_ms = (file_end_time - file_start_time) * 1000  # Convert to milliseconds
            cumulative_time += file_time_ms
            file_count += 1
            
            # Record individual time for statistics
            individual_times.append(file_time_ms)
            
            # Determine status
            status = "SUCCESS" if success else "ERROR"
            if not success:
                error_count += 1
                error_files.append((html_file.name, error))
            
            # Write to log file
            log_file.write(f"{html_file.name:<20} {file_time_ms:<15.3f} {cumulative_time:<20.3f} {file_count:<15} {status:<10}\n")
            
            # Print progress every 50 files
            if file_count % 50 == 0:
                print(f"Processed {file_count}/{len(html_files)} files...")
        
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
        log_file.write(f"Total processing time: {total_time_ms:.3f} ms ({total_time_seconds:.3f} seconds)\n")
        
        if individual_times:
            avg_time = sum(individual_times) / len(individual_times)
            min_time = min(individual_times)
            max_time = max(individual_times)
            min_file = html_files[individual_times.index(min_time)].name
            max_file = html_files[individual_times.index(max_time)].name
            
            log_file.write(f"Average time per file: {avg_time:.3f} ms\n")
            log_file.write(f"Fastest file: {min_file} ({min_time:.3f} ms)\n")
            log_file.write(f"Slowest file: {max_file} ({max_time:.3f} ms)\n")
        
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
        "total_time_ms": total_time_ms,
        "total_time_seconds": total_time_seconds,
        "avg_time_ms": sum(individual_times) / len(individual_times) if individual_times else 0,
        "min_time_ms": min(individual_times) if individual_times else 0,
        "max_time_ms": max(individual_times) if individual_times else 0
    }


def main():
    """Main program entry point."""
    # Configuration
    files_directory = "CS13309_Archivos_HTML/Files"
    log_file = "a1_matricula.txt"
    
    print("HTML File Processor")
    print("=" * 50)
    
    # Check if directory exists
    if not os.path.exists(files_directory):
        print(f"Error: Directory '{files_directory}' not found.")
        print("Please ensure the HTML files are in the correct location.")
        return
    
    # Process files
    print(f"Processing files from: {files_directory}")
    print(f"Generating log file: {log_file}")
    print()
    
    stats = process_html_files(files_directory, log_file)
    
    # Print summary to console
    print("\n" + "=" * 50)
    print("PROCESSING COMPLETE")
    print("=" * 50)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Successful: {stats['successful']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total time: {stats['total_time_ms']:.3f} ms ({stats['total_time_seconds']:.3f} seconds)")
    print(f"Average time per file: {stats['avg_time_ms']:.3f} ms")
    print(f"Log file saved: {log_file}")
    print("=" * 50)


if __name__ == "__main__":
    main()
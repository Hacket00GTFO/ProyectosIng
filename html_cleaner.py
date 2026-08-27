#!/usr/bin/env python3
"""
HTML File Cleaner - Actividad 2
Processes HTML files, removes HTML tags, and generates clean text files.
Measures cleaning times and generates detailed log file.
"""

import os
import time
import re
from pathlib import Path
from typing import Tuple, Optional


def open_file(filename: str, base_dir: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    """
    Opens and reads an HTML file efficiently.
    
    Args:
        filename: Name of the file to open (e.g., "001.html")
        base_dir: Base directory containing the files
        
    Returns:
        Tuple of (success: bool, content: Optional[str], encoding: Optional[str], error: Optional[str])
    """
    file_path = Path(base_dir) / filename
    
    # Try different encodings, starting with UTF-8
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return True, content, encoding, None
        except UnicodeDecodeError:
            continue  # Try next encoding
        except FileNotFoundError:
            return False, None, None, f"File not found: {filename}"
        except PermissionError:
            return False, None, None, f"Permission denied: {filename}"
        except Exception as e:
            return False, None, None, f"Error reading {filename}: {str(e)}"
    
    # If all encodings failed
    return False, None, None, f"Could not decode {filename} with any supported encoding"


def remove_html_tags(html_content: str) -> str:
    """
    Removes HTML tags from content using regex.
    
    Args:
        html_content: String containing HTML content
        
    Returns:
        Clean text without HTML tags
    """
    # Remove HTML comments
    clean_content = re.sub(r'<!--.*?-->', '', html_content, flags=re.DOTALL)
    
    # Remove HTML tags (including attributes)
    clean_content = re.sub(r'<[^>]*>', '', clean_content)
    
    # Clean up multiple whitespace characters
    clean_content = re.sub(r'\s+', ' ', clean_content)
    
    # Remove leading/trailing whitespace from each line
    lines = clean_content.split('\n')
    clean_lines = [line.strip() for line in lines if line.strip()]
    
    # Join lines back together
    clean_content = '\n'.join(clean_lines)
    
    return clean_content.strip()


def save_cleaned_file(filename: str, content: str, base_dir: str, encoding: str) -> Tuple[bool, Optional[str]]:
    """
    Saves cleaned content to a .txt file.
    
    Args:
        filename: Original HTML filename (e.g., "001.html")
        content: Cleaned content to save
        base_dir: Directory where the file should be saved
        encoding: Encoding to use for writing
        
    Returns:
        Tuple of (success: bool, error: Optional[str])
    """
    try:
        # Change extension from .html to .txt
        txt_filename = filename.replace('.html', '.txt')
        file_path = Path(base_dir) / txt_filename
        
        with open(file_path, 'w', encoding=encoding) as f:
            f.write(content)
        
        return True, None
    except PermissionError:
        return False, f"Permission denied writing {txt_filename}"
    except Exception as e:
        return False, f"Error writing {txt_filename}: {str(e)}"


def process_html_cleaning(files_dir: str, log_filename: str) -> dict:
    """
    Process all HTML files, remove tags, save as .txt, and generate timing log.
    
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
        log_file.write("HTML FILE CLEANING LOG - ACTIVIDAD 2\n")
        log_file.write("=" * 80 + "\n")
        log_file.write(f"Processing directory: {files_dir}\n")
        log_file.write(f"Total files found: {len(html_files)}\n")
        log_file.write(f"Log file: {log_filename}\n")
        log_file.write("=" * 80 + "\n\n")
        
        # Write column headers
        log_file.write(f"{'File Name':<20} {'Clean Time (ms)':<18} {'Cumulative (ms)':<20} {'Files Processed':<15} {'Status':<10}\n")
        log_file.write("-" * 80 + "\n")
        
        # Process each file
        for html_file in html_files:
            # Step 1: Open the file
            success, content, encoding, error = open_file(html_file.name, files_dir)
            
            if not success:
                # Log the error even if we couldn't open the file
                error_count += 1
                error_files.append((html_file.name, error))
                log_file.write(f"{html_file.name:<20} {'N/A':<18} {cumulative_time:<20.3f} {file_count + 1:<15} {'ERROR':<10}\n")
                file_count += 1
                continue
            
            # Step 2: Clean the HTML tags (measure this time specifically)
            clean_start_time = time.perf_counter()
            
            try:
                clean_content = remove_html_tags(content)
                
                clean_end_time = time.perf_counter()
                clean_time_ms = (clean_end_time - clean_start_time) * 1000  # Convert to milliseconds
                
                # Step 3: Save the cleaned content
                save_success, save_error = save_cleaned_file(html_file.name, clean_content, files_dir, encoding)
                
                if not save_success:
                    error_count += 1
                    error_files.append((html_file.name, save_error))
                    status = "ERROR"
                else:
                    status = "SUCCESS"
                
            except Exception as e:
                error_count += 1
                error_files.append((html_file.name, f"Cleaning error: {str(e)}"))
                clean_time_ms = 0
                status = "ERROR"
            
            cumulative_time += clean_time_ms
            file_count += 1
            
            # Record individual time for statistics
            individual_times.append(clean_time_ms)
            
            # Write to log file
            log_file.write(f"{html_file.name:<20} {clean_time_ms:<18.3f} {cumulative_time:<20.3f} {file_count:<15} {status:<10}\n")
            
            # Print progress every 50 files
            if file_count % 50 == 0:
                print(f"Processed {file_count}/{len(html_files)} files...")
        
        # Calculate final statistics
        total_end_time = time.perf_counter()
        total_time_seconds = total_end_time - total_start_time
        total_time_ms = total_time_seconds * 1000
        
        # Write summary section
        log_file.write("\n" + "=" * 80 + "\n")
        log_file.write("CLEANING SUMMARY\n")
        log_file.write("=" * 80 + "\n")
        log_file.write(f"Total files processed: {file_count}\n")
        log_file.write(f"Successful: {file_count - error_count}\n")
        log_file.write(f"Errors: {error_count}\n")
        log_file.write(f"Total cleaning time: {cumulative_time:.3f} ms\n")
        log_file.write(f"Total program time: {total_time_ms:.3f} ms ({total_time_seconds:.3f} seconds)\n")
        
        if individual_times:
            avg_time = sum(individual_times) / len(individual_times)
            min_time = min(individual_times)
            max_time = max(individual_times)
            min_file = html_files[individual_times.index(min_time)].name
            max_file = html_files[individual_times.index(max_time)].name
            
            log_file.write(f"Average cleaning time per file: {avg_time:.3f} ms\n")
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
        "total_cleaning_time_ms": cumulative_time,
        "total_program_time_ms": total_time_ms,
        "total_program_time_seconds": total_time_seconds,
        "avg_time_ms": sum(individual_times) / len(individual_times) if individual_times else 0,
        "min_time_ms": min(individual_times) if individual_times else 0,
        "max_time_ms": max(individual_times) if individual_times else 0
    }


def main():
    """Main program entry point."""
    # Configuration
    files_directory = "CS13309_Archivos_HTML/Files"
    log_file = "log_a2_matricula.txt"
    
    print("HTML File Cleaner - Actividad 2")
    print("=" * 50)
    
    # Check if directory exists
    if not os.path.exists(files_directory):
        print(f"Error: Directory '{files_directory}' not found.")
        print("Please ensure the HTML files are in the correct location.")
        return
    
    # Process files
    print(f"Processing files from: {files_directory}")
    print(f"Generating log file: {log_file}")
    print(f"Output files will be saved as .txt in the same directory")
    print()
    
    stats = process_html_cleaning(files_directory, log_file)
    
    # Print summary to console
    print("\n" + "=" * 50)
    print("CLEANING COMPLETE")
    print("=" * 50)
    print(f"Total files processed: {stats['total_files']}")
    print(f"Successful: {stats['successful']}")
    print(f"Errors: {stats['errors']}")
    print(f"Total cleaning time: {stats['total_cleaning_time_ms']:.3f} ms")
    print(f"Total program time: {stats['total_program_time_ms']:.3f} ms ({stats['total_program_time_seconds']:.3f} seconds)")
    print(f"Average cleaning time per file: {stats['avg_time_ms']:.3f} ms")
    print(f"Log file saved: {log_file}")
    print("=" * 50)


if __name__ == "__main__":
    main()
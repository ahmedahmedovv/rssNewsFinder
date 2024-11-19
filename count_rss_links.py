import os
from collections import Counter
from datetime import datetime

def count_rss_links():
    results_dir = "search_results"
    
    # Get all RSS files
    rss_files = [f for f in os.listdir(results_dir) if f.startswith('rss_')]
    
    if not rss_files:
        print("No RSS files found!")
        return
    
    # Counter for all links
    link_counter = Counter()
    
    # Process each file
    for filename in rss_files:
        filepath = os.path.join(results_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Skip header lines
                next(f)  # Skip "RSS Links for: ..."
                next(f)  # Skip "Search Time: ..."
                next(f)  # Skip empty line
                
                # Count each link
                for line in f:
                    if line.strip():
                        link_counter[line.strip()] += 1
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    # Create output file with counts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"rss_links_with_counts_{timestamp}.txt"
    output_filepath = os.path.join(results_dir, output_filename)
    
    # Write results
    with open(output_filepath, 'w', encoding='utf-8') as f:
        f.write(f"RSS Links with Occurrence Counts\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Unique Links: {len(link_counter)}\n")
        f.write(f"Total Files Processed: {len(rss_files)}\n\n")
        
        # Write sorted links (by count, then alphabetically)
        for link, count in sorted(link_counter.items(), key=lambda x: (-x[1], x[0])):
            f.write(f"[{count}] {link}\n")
    
    print(f"Analysis complete! Output saved to: {output_filepath}")
    print(f"Processed {len(rss_files)} files and found {len(link_counter)} unique links")

if __name__ == "__main__":
    count_rss_links() 
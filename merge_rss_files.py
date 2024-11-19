import os
from datetime import datetime

def merge_rss_files():
    # Directory containing the RSS files
    results_dir = "search_results"
    
    # Get all RSS files
    rss_files = [f for f in os.listdir(results_dir) if f.startswith('rss_')]
    
    if not rss_files:
        print("No RSS files found to merge!")
        return
    
    # Create a set to store unique RSS links
    all_rss_links = set()
    
    # Process each file
    for filename in rss_files:
        filepath = os.path.join(results_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                # Skip the first two lines (header)
                next(f)  # Skip "RSS Links for: ..."
                next(f)  # Skip "Search Time: ..."
                next(f)  # Skip empty line
                
                # Add each link to the set
                for line in f:
                    if line.strip():  # Skip empty lines
                        all_rss_links.add(line.strip())
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
    
    # Create merged file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_filename = f"merged_rss_links_{timestamp}.txt"
    merged_filepath = os.path.join(results_dir, merged_filename)
    
    # Write merged results
    with open(merged_filepath, 'w', encoding='utf-8') as f:
        f.write(f"Merged RSS Links\n")
        f.write(f"Merge Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Unique Links: {len(all_rss_links)}\n\n")
        
        # Write sorted links
        for link in sorted(all_rss_links):
            f.write(f"{link}\n")
    
    print(f"Successfully merged {len(rss_files)} files!")
    print(f"Found {len(all_rss_links)} unique RSS links!")
    print(f"Merged file saved as: {merged_filepath}")
    
    # Optionally, you can delete the original files
    # if input("Delete original RSS files? (y/n): ").lower() == 'y':
    #     for filename in rss_files:
    #         os.remove(os.path.join(results_dir, filename))
    #     print("Original files deleted.")

if __name__ == "__main__":
    merge_rss_files() 
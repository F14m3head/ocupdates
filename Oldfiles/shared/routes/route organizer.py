# Import required libraries 
import sys
import os 

def openfile(sfile): # Opens file passed as argument
    while True:
        try:
            with open(sfile, 'r') as file: # Opens file and closes it automatically
                print(f"{os.path.basename(sfile)} opened successfully")
                contents = file.read() # Saves contents of file
                return contents
            break
        except:
            print("Please select a valid file")
            continue


def clean(contents): # Remove unecessary data
    routes = []
    columns = [2, 3, 7, 8]  # Positions to keep
    lines = contents.splitlines()

    for line in lines:
        parts = line.split(',')  # Split all commas
        kept_parts = []
        for index in columns:
            if index < len(parts):  # Make sure the column exists
                kept_parts.append(parts[index])
            else:
                kept_parts.append('')  # Add empty string if column doesn't exist
        # Join the kept parts back with commas
        routes.append(kept_parts)
    return routes

# Script
#contents = openfile(sys.argv) # Default option for file passsed on open
#routes = clean(contents) # Clean data
#routes.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0) # Sort routes by numerical order


contents = openfile('/Users/buscomble/Downloads/GTFSExport/routes.txt') # Hardcoded for testing
routes = clean(contents)
routes.sort(key=lambda x: int(x[0]) if x[0].isdigit() else 0) # Sort routes by numerical order'''


# Route printing
for i in range(len(routes)):
    print(routes[i])
#print(f"{routes['''Insert index here''']}") # Print a specific route by index

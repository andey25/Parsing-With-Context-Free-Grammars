import os

# Path to your 'hw 2' folder
path_to_hw_folder = '/Users/ad4215/Downloads/hw 2'
os.chdir(path_to_hw_folder)

# Now you can access files in the 'hw 2' folder directly
with open('atis3.pcfg', 'r') as file:
    data = file.read()
    print(data)

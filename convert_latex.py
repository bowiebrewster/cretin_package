import paths
import re
# this file is for reordering formulas in latex so that the formula number that latex displays is the same as the order in which the formulas are numbered in the latex file

def reoder_formulas(input:str, output:str):
    
    path = f'{paths.to_folder_cretin()}/{input}.txt'

    # creating pairs of formulas like eq4 -> eq7
    lis = []
    with open(path) as f:
        for line in f:
            if "\\begin{equation}\\label{eq" in line:
                print(line)
                val = line[26:28].strip('}').strip(':')
                print(val)
                lis.append(int(val))

    your_pairs_list = []
    for index, entry in enumerate(lis):
        your_pairs_list.append([entry,index+1])
    print(your_pairs_list)

    with open(path, 'r') as file:
        file_contents = file.read()

    # Step 1: Replace original labels with temporary unique labels
    for old, _ in your_pairs_list:
        temp_label = f'__TEMP__{old}__'
        pattern_to_find = r'\\label\{eq:' + str(old) + r'\}'  # Separated raw and formatted parts
        replacement_pattern = r'\\label{eq:' + temp_label + r'}'
        file_contents = re.sub(pattern_to_find, replacement_pattern, file_contents)

    # Step 2: Replace temporary labels with final labels
    for _, new in your_pairs_list:
        temp_label = f'__TEMP__{_}__'
        pattern_to_find = r'\\label\{eq:' + temp_label + r'\}'  # Separated raw and formatted parts
        replacement_pattern = r'\\label{eq:' + str(new) + r'}'
        file_contents = re.sub(pattern_to_find, replacement_pattern, file_contents)

    # Write the updated contents to a new file
    pathout = f'{paths.to_folder_cretin()}/{output}.txt'
    with open(pathout, 'w') as file:
        file.write(file_contents)

reoder_formulas('latex', 'updated_latex')
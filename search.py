import os, glob 
from collections import Counter
import pandas as pd
import paths


# We use this class to search through the test folder's .gen files. 
# Finding the most used keywords helps in prioritizing what functionality should be written first.
class Generators():
    def __init__(self):

        self.path = paths.to_previous_experiments()
        os.chdir(self.path)

    def word(self, input : str, word_slicing : tuple, print_path : bool = False):

        lis_hist = []

        def read_gen(word, complete_path):
            f = open(complete_path, "r")
            
            for line in f.readlines():
                lis = line.split()
                if len(lis) > 0:
                    if word in lis[0]:
                        if print_path:print(complete_path)
                        try:            
                            sliced = ' '.join( lis[slice(*word_slicing)])
                            lis_hist.append(sliced)
                        except:
                            lis_hist.append(line)

                        
        for folder in os.listdir():
            os.chdir(self.path+"/"+folder)
            # for every file that ends in .gen
            for file in glob.glob("*.gen"):
                read_gen(input, self.path+"/"+folder+"/"+file)


        # turn it into a frequncy table and print highest to lowest 
        letter_counts = Counter(lis_hist)
        df = pd.DataFrame.from_dict(letter_counts, orient='index')
        df = df.sort_values(by=[0], ascending = False)
        with pd.option_context('display.max_rows', None,
                            'display.max_columns', None,
                            'display.precision', 3,
                            ):
            return(df)
        
    def chapter(self, input : str):

        str_id = "c ----------------------------------"
        saves = []
        def read_gen(chapter, complete_path):
            f = open(complete_path, "r")
            lines = f.readlines()
            reading = False
            for i in range(len(lines)-2):
                line_i, line_j, line_k = lines[i], lines[i+1], lines[i+2]
                if (str_id in line_i) and (str_id in line_k) and (chapter in line_j):
                    reading = True
                if (str_id in line_i) and (str_id in line_k) and (chapter not in line_j):
                    reading = False
                if reading:
                    spt = line_i.split()
                    if len(spt) > 0:
                        saves.append(spt[0])

        os.chdir(self.path)
        for folder in os.listdir():
            os.chdir(self.path+"/"+folder)
            for file in glob.glob("*.gen"):
                read_gen(input, self.path +folder+"/"+file)


        letter_counts = Counter(saves)
        df = pd.DataFrame.from_dict(letter_counts, orient='index')
        df = df.sort_values(by=[0], ascending = False)
        with pd.option_context('display.max_rows', None,
                            'display.max_columns', None,
                            'display.precision', 3,
                            ):
            df = df.drop('c')
            try:
                df.drop(input.lower())
            except:
                pass

            return(df)




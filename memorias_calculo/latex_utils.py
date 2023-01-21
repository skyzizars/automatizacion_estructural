import os
import subprocess

def save_var_ltx(key,value,url):
    import csv
    dict_var = {}
    file_path = os.path.join(os.getcwd(), url)

    try:
        with open(file_path, newline='') as file:
            reader = csv.reader(file)
            for row in reader:
                dict_var[row[0]] = row[1]

    except FileNotFoundError:
        pass

    dict_var[key] = value

    with open(file_path, 'w') as f:
        for key, value in dict_var.items():
            f.write(f'{key},{value}\n')

def compile(name='main_mem'):
    if name[-3:] == 'tex':
        name = name[:-4]
    subprocess.run(['pdflatex', name+'.tex'])
    aux = ['.log','.aux','.fdb_latexmk','.fls']
    for i in aux:
        try:
            os.remove(name+i)
        except:
            pass
"""
From bash command line, python texify.py <name of results file>
If the results file is in a subdirectory of the working directory called 'results',
 then you do not need to specify the path of the results file
"""

import json
import sys
import os

def writeline(f,s):
    string_ = s + "\n"
    f.write(string_)

def newpage(f):
    writeline(f,"\\newpage\\noindent")

def create_tex_file(i,o):
    image_path = os.path.dirname(os.getcwd()) + "/images/"
    image_files = []
    score = ""
    line = "initialized"

    writeline(o,"\\documentclass{minimal}")
    writeline(o,"\\usepackage{graphicx}")
    writeline(o,"\\usepackage{color}")
    writeline(o,"\\begin{document}")
    writeline(o,"\\setlength{\\tabcolsep}{1.33mm}")
    writeline(o,"\\noindent")

    while line:
        line = i.readline()

        if "|||" in line:
            info = line.split("6666")[1]
            image_files = info.split("|||")

        if "6666PIC" in line:
            drawn = line.split("6666")[1].split("PIC")[1].split("@")[0]
            rejected = [image for image in image_files if image != drawn][0]
            writeline(o,"Chosen:\\\\")
            writeline(o,"\\includegraphics[scale=0.5]{%s}\\\\" % (image_path + drawn))
            writeline(o,"Not chosen:\\\\")
            writeline(o,"\\includegraphics[scale=0.5]{%s}\\\\" % (image_path + rejected))

        if "6666COORD" in line:
            coordvec = json.loads("[" + line.split("[")[1].split("]")[0] + "]")
            writeline(o,"Drawing:\\\\")
            writeline(o,"\\begin{tabular}{l l l l l l l l}")
            table_content = ""
            for n in range(0,49):
                if not n % 7:
                    table_content = table_content + "\\\\\n"
                if coordvec[n] == 0:
                    table_content = table_content + "\\color{yellow}{X}"
                else:
                    table_content = table_content + "X"
                if n != 48:
                    table_content = table_content + " & "
            writeline(o,table_content)
            writeline(o,"\\end{tabular}\\\\")

        if "6666GUESS" in line:
            guessed = line.split("6666")[1].split("GUESS")[1].split("@")[0]
            status = "wrong"
            if guessed == drawn:
                status = "right"
            writeline(o,"Receiver guessed %s" % status)
            writeline(o,"\\newpage\\noindent")

        if "6666SCORE" in line:
            score = line.split("@")[1]

    writeline(o,"Score:  " + score)
    writeline(o,"\\end{document}")


def main(argv):
    try:
        os.chdir("results")
    except:
        pass

    if len(argv) != 2:
        sys.exit(2)

    input_file = argv[1]

    output_dir = argv[1].split(".")[0]

    if os.path.exists(output_dir):
        sys.exit("No duplicates.")

    os.makedirs(output_dir)

    output_file = output_dir + "/" + output_dir + ".tex"

    i = open(input_file,'r')
    o = open(output_file,'w')

    create_tex_file(i,o)

    i.close()
    o.close()

if __name__ == "__main__":
    main(sys.argv)

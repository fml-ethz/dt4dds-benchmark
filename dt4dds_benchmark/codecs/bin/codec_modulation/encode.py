import sys

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

code = __import__("Modulation-based DNA storage_demo")

code.encodeFile_excluIndex_N(INPUT_FILE, OUTPUT_FILE)
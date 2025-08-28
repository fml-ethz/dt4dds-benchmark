import sys

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]

code = __import__("Modulation-based DNA storage_demo")

code.decodefile_excluIndex(INPUT_FILE, OUTPUT_FILE)
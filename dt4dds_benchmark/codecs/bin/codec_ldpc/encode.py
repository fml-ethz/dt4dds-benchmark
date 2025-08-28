import dna_storage
import pathlib
import sys

INPUT_FILE = sys.argv[1]
OUTPUT_FILE = sys.argv[2]
OLIGO_LENGTH = int(sys.argv[3])
BCH_CODE = int(sys.argv[4])
ALPHA = float(sys.argv[5])

dna_storage.encode_data(
    INPUT_FILE, 
    OLIGO_LENGTH, 
    OUTPUT_FILE, 
    BCH_CODE, 
    ALPHA, 
    f'{pathlib.Path(__file__).parent.resolve()}/supp',
    14, 
)
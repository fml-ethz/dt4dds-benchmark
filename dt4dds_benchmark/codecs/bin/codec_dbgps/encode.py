import argparse
from DNAfountain import DNAFountain
from test_utils import *

# parse arguments
arg = argparse.ArgumentParser()
arg.add_argument('-i', '--input', help='Input file')
arg.add_argument('-o', '--output', help='Output file')
arg.add_argument('-l', '--chunk_size', help='Size of chunks')
arg.add_argument('-n', '--droplet_num', help='Number of droplets')
args = arg.parse_args()

# codec parameters
kmer_length = 21
data_block_length = int(args.chunk_size)
fountain_seed = 2
fountain_init_index = 1
total_size = int(args.droplet_num)
index_bytes = 4
ec_bytes = 2
anchor_bytes = 4

# open and read input file
file1 = open(args.input, 'rb')
filebytes1 = file1.read()
file1.close()

# create DNA fountain object
fdna1 = DNAFountain(filebytes1, data_block_length, fountain_init_index, fountain_seed, index_bytes*4, anchor_bytes*4, ec_bytes*4)
fdna1.degree_table_folds = 1000
fdna1.ROBUST_FAILURE_PROBABILITY = 0.01
fdna1.c_value = 0.01
fdna1.gen_degrees()

# generate droplets
droplet_all = get_droplets_check_repeat_kmer(total_size, fdna1, kmer_length)

# write droplets to output file
p1 = 'CCTGCAGAGTAGCATGTC'  # 5'-->3'
p2 = 'CTGACACTGATGCATCCG'  # complement seq of P2
file2 = open(args.output, 'tw')
i = 0
for dps in droplet_all:
    file2.write(dps.to_DNA_CRC_sIndex())
    file2.write('\n')
    i = i + 1
file2.close()

# print all settings to log
print("\nEncode finished!")
print("\nSettings:")
print("Input file: ", args.input)
print("Output file: ", args.output)
print("Chunk size: ", data_block_length)
print("Number of droplets: ", total_size)
print("Number of chunks: ", fdna1.num_of_chunks)
print("Kmer length: ", kmer_length)
print("Data block length: ", data_block_length)
print("Fountain seed: ", fountain_seed)
print("Fountain initial index: ", fountain_init_index)
print("Total size: ", total_size)
print("Index bytes: ", index_bytes)
print("EC bytes: ", ec_bytes)
print("Anchor bytes: ", anchor_bytes)
print("P1: ", p1)
print("P2: ", p2)
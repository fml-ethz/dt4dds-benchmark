import argparse
from utils import *
from test_utils import *
from deBruijnGraph import DeBruijnGraph
from glass import Glass
from DNAdroplet import DNADroplet
import time

# parse arguments
arg = argparse.ArgumentParser()
arg.add_argument('-i', '--input', help='Input file')
arg.add_argument('-o', '--output', help='Output file')
arg.add_argument('-l', '--chunk_size', help='Size of chunks')
arg.add_argument('-n', '--chunk_num', help='Number of chunks')
arg.add_argument('--type', help='File type, default fasta', default='fasta')
args = arg.parse_args()


# codec parameters
kmer_size = 31
kmer_cut_off = 0
chunk_size = int(args.chunk_size)
f_seed = 2
fountain_init_index = 1
chunk_num = int(args.chunk_num)
index_bytes = 4
crc_bytes = 2
anchor_bytes = 4
file_type = str(args.type).lower()
double_index = False
both_way = False
max_path_num = 1050
index_l = 1
index_u = (chunk_num * 10) + index_l
input_file = str(args.input)
output_file = str(args.output)


# recover strands with De Bruijn graph
start = time.perf_counter()
deG = DeBruijnGraph()
deG.kmer_len = kmer_size
deG.veri_kmers = False
deG.max_path_num = max_path_num

# read input file
if file_type == 'FastQ' or file_type == 'fastq':
    deG.open_fastq(input_file)
else:
    if file_type == 'fasta' or file_type == 'Fasta':
        deG.open_fasta(input_file)
    else:
        deG.open_dump(input_file)

# remove low coverage k-mers
strands_recovered = {}
strand_search_details = {}
strand_search_details['crc_fail'] = 0
print('\nRemoving low coverage k-mers ......')
deG.remove_low_cov_kmers(kmer_cut_off)

# reconstruct DNA strands
print('\nReconstructing DNA strands ......')
a = time.perf_counter()
for index in range(index_l, index_u+1):
    deG.find_droplet_DNA(index, chunk_size)
    if len(deG.crc_paths) > 1:
        strand_search_details['crc_fail']  = strand_search_details['crc_fail']  + 1
    else:
        if len(deG.crc_paths) > 0:
            strands_recovered[index] = deG.crc_paths[0]

# print statistics
a = time.perf_counter() - a
# print('CRC fails:')
# print(strand_search_details['crc_fail'])
print('Recovered: ', end='')
print(len(strands_recovered), end= '')
print(' strands used ', end='')
print(a, end=' seconds\n')

# rebuild DNA droplets
print('Rebuilding DNA droplets........')
degree_table = get_degrees(chunk_num, chunk_num * 1000, f_seed)
cup = Glass(chunk_num)
for id in strands_recovered:
    adp = DNADroplet(bytes(chunk_size))
    adp.num_of_chunks = chunk_num
    adp.set_head_index(id)
    adp.set_droplet_from_DNA_CRC(strands_recovered[id])
    adp.degree = degree_table[id-1]
    adp.update()
    cup.addDroplet(adp)

# decode by fountain codes
print('Decoding by fountain codes .........')
cup.decode()
cup.writeToFile(output_file)
end = time.perf_counter() - start
print('Decoding time: ', end ='')
print(end)

# print all settings to log
print("\nDecode finished!")
print("\nSettings:")
print("Input file: ", args.input)
print("Output file: ", args.output)
print("Chunk size: ", chunk_size)
print("Number of droplets: ", chunk_num)
print("Number of chunks: ", cup.num_chunks)
print("Kmer length: ", kmer_size)
print("CRC bytes: ", crc_bytes)
print("Index bytes: ", index_bytes)
print("Anchor bytes: ", anchor_bytes)
print("Fountain seed: ", f_seed)
print("Fountain initial index: ", fountain_init_index)
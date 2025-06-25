import pathlib


def design_file_stats(design_file: pathlib.Path):
    """  """
    # check that the file exists
    if not design_file.exists():
        raise FileNotFoundError(f'Design file {design_file} does not exist.')

    # read the file to count the number of sequences and bases
    stats = {}
    with design_file.open() as f:
        for line in f:
            seq = line.strip()
            if seq:
                stats['n_sequences'] = stats.get('n_sequences', 0) + 1
                stats['n_bases'] = stats.get('n_bases', 0) + len(seq)

    # calculate the average sequence length
    stats['sequence_length'] = stats['n_bases'] / stats['n_sequences']
    
    return stats


def encoding_stats(input_file: pathlib.Path, design_file: pathlib.Path):
    """  """
    # check that the input file exists
    if not input_file.exists():
        raise FileNotFoundError(f'Input file {input_file} does not exist.')
    
    # get filesize
    stats = {'filesize_byte': input_file.stat().st_size}
    stats['filesize_bit'] = stats['filesize_byte'] * 8

    # get design file stats
    stats.update(design_file_stats(design_file))

    # calculate the code rate
    stats['code_rate'] = stats['filesize_bit'] / stats['n_bases']

    return stats

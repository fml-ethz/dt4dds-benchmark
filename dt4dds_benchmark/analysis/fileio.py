import Bio.SeqIO

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def read_fasta(path):
    """Read sequences from FASTA file.

    Args:
        path (str): Path to FASTA file.

    Returns:
        dict: Dictionary of {seq_id: sequence}.
    """
    seqs = Bio.SeqIO.parse(path, "fasta")
    seqs = {seq.id: str(seq.seq) for seq in seqs}
    logger.info(f"Read {len(seqs)} sequences from {path}.")
    return seqs


def read_txt(path):
    """Read sequences from text file.

    Args:
        path (str): Path to text file.

    Returns:
        dict: Dictionary of {seq_id: sequence}.
    """
    seqs = {}
    with open(path) as f:
        for i, line in enumerate(f.readlines()):
            seq = line.strip()
            seqs[i] = seq
    logger.info(f"Read {len(seqs)} sequences from {path}.")
    return seqs
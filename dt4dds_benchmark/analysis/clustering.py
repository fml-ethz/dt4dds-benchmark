import pandas as pd
import rapidfuzz
import tqdm.auto

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



def compare_to_references(sequences, reference_sequences):
    """Compare sequences to reference sequences.

    Args:
        sequences (dict): Dictionary of {seq_id: sequence}.
        reference_sequences (dict): Dictionary of {seq_id: sequence}.

    Returns:
        pd.DataFrame: Dataframe with the following columns:
            seqid (str): Sequence ID.
            ref_seqid (str): Reference sequence ID.
            edit_distance (int): Edit distance to reference sequence.
            similarity (float): Normalized similarity to reference sequence.
            length (int): Sequence length.
    """
    
    # get the reference sequence for each sequence, and calculate metrics
    seq_ids = []
    ref_seqids = []
    edit_distances = []
    similarities = []
    lengths = []
    for seq_id, seq in tqdm.auto.tqdm(sequences.items()):
        _, _, ref_seqid = rapidfuzz.process.extractOne(seq, reference_sequences, scorer=rapidfuzz.distance.Levenshtein.normalized_similarity)
        seq_ids.append(seq_id)
        ref_seqids.append(ref_seqid)
        lengths.append(len(seq))
        edit_distances.append(rapidfuzz.distance.Levenshtein.distance(seq, reference_sequences[ref_seqid]))
        similarities.append(rapidfuzz.distance.Levenshtein.normalized_similarity(seq, reference_sequences[ref_seqid]))

    # create a dataframe with the results
    df = pd.DataFrame({
        "seqid": seq_ids, 
        "ref_seqid": ref_seqids, 
        "edit_distance": edit_distances, 
        "similarity": similarities, 
        "length": lengths
    })
    return df



def assess_clustering_performance(df, reference_sequences):
    """ Assesses clustering performance based on metrics derived from sequence/reference relationships.

    Args:
        df (pd.DataFrame): Dataframe with data on sequence <> reference relations, i.e. output of compare_to_references().
        reference_sequences (dict): Dictionary of {seq_id: sequence}.

    Returns:
        dict: Dictionary with the following data:
            mean_n_clusters (float): Mean number of clusters per reference sequence.
            mean_editdistance (float): Mean edit distance to the reference sequence.
            mean_similarity (float): Mean similarity to the reference sequence.
            min_editdistance (float): Mean of the minimum edit distances to each reference sequence.
            max_similarity (float): Mean of the maximum similarities to each reference sequence.
            mean_length (float): Mean length of the reads.
            total_clusters (int): Total number of clusters.
            total_foundreferences (int): Total number of reference sequences found.
            accuracy (float): Mean base accuracy of the clusters.
            specificity (float): Ratio of unique reference sequences to total clusters.
            sensitivity (float): Ratio of unique reference sequences to total reference sequences.      
    """
    d = dict(
        mean_n_clusters = df.ref_seqid.value_counts().mean(),
        mean_editdistance = df.groupby('ref_seqid')['edit_distance'].mean().mean(),
        mean_similarity = df.groupby('ref_seqid')['similarity'].mean().mean(),
        min_editdistance = df.groupby('ref_seqid')['edit_distance'].min().mean(),
        max_similarity = df.groupby('ref_seqid')['similarity'].max().mean(),
        mean_length = df['length'].mean(),
        total_clusters = len(df),
        total_foundreferences = len(df.ref_seqid.unique()),
    )
    d['accuracy'] = 1 - d['min_editdistance'] / d['mean_length']
    d['specificity'] = d['total_foundreferences'] / d['total_clusters']
    d['sensitivity'] = d['total_foundreferences'] / len(reference_sequences)
    return d
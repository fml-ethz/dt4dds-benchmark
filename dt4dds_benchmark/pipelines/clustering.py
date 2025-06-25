import pathlib
import dataclasses
import shutil
from typing import List

from .basepipeline import BasePipeline
from ..clustering.baseclustering import BaseClustering
from .. import analysis

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



@dataclasses.dataclass
class Clustering(BasePipeline):
    """  """

    # required settings
    input_file: pathlib.Path           # path to the input file
    clustering: BaseClustering         # clustering algorithm to use

    # optional settings
    design_file: pathlib.Path = ''     # optional path to the design file to compare against for clustering metrics


    @classmethod
    def factory(cls, 
        input_files: List[pathlib.Path],            # list of paths to input files
        clusterings: List[BaseClustering],      # list of clustering algorithms to use
        **kwargs
    ):
        return super().factory(
            list_args={'input_file': input_files, 'clustering': clusterings},
            **kwargs
        )


    @property
    def _pipeline(self):
        return [
            (self.clustering, self.clustering.run, self.filepath_reads, self.filepath_clusters, 'clustering'),
        ]
    

    def _prepare_files(self):
        # copy the read file with the reads
        shutil.copy(str(self.input_file.resolve()), str(self.filepath_reads.resolve()))


    def _customize_result(self, result):
        # if an input file was given, check if the output file exists and is identical to the input file
        if self.design_file:
            ref_seqs = analysis.fileio.read_fasta(pathlib.Path(self.design_file).resolve())
            clusters = analysis.fileio.read_txt(self.filepath_clusters)
            seq_df = analysis.clustering.compare_to_references(clusters, ref_seqs)
            result.update(analysis.clustering.assess_clustering_performance(seq_df, ref_seqs))

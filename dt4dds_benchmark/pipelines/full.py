import pathlib
import dataclasses
from typing import List
import shutil

from .basepipeline import BasePipeline
from ..codecs.basecodec import BaseCodec
from ..workflows.baseworkflow import BaseWorkflow
from ..clustering.baseclustering import BaseClustering
from ..tools import encoding_stats, files_are_equal

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



@dataclasses.dataclass
class Full(BasePipeline):
    """  """

    # required settings
    input_file: pathlib.Path         # path to the input file
    codec: BaseCodec                 # codec to use
    workflow: BaseWorkflow           # workflow to use
    clustering: BaseClustering       # clustering algorithm to use


    @classmethod
    def factory(cls, 
        input_files: List[pathlib.Path],    # list of paths to input files
        codecs: List[BaseCodec],            # list of codecs to use
        workflows: List[BaseWorkflow],      # list of workflows to use
        clusterings: List[BaseClustering],  # list of clustering algorithms to use
        **kwargs
    ):
        return super().factory(
            list_args={'input_file': input_files, 'codec': codecs, 'workflow': workflows, 'clustering': clusterings},
            **kwargs
        )


    @property
    def _pipeline(self):
        return [
            (self.codec, self.codec.encode, self.filepath_input, self.filepath_sequences, 'encoding'),
            (self.workflow, self.workflow.run, self.filepath_sequences, self.filepath_reads, 'workflow'),
            (self.clustering, self.clustering.run, self.filepath_reads, self.filepath_clusters, 'clustering'),
            (self.codec, self.codec.decode, self.filepath_clusters, self.filepath_output, 'decoding'),
        ]
    

    def _prepare_files(self):
        # copy the input file to be encoded
        shutil.copy(str(self.input_file), str(self.filepath_input))


    def _customize_result(self, result):
        # assess the output
        output_exists = self.filepath_output.exists()
        output_identical = files_are_equal(str(self.input_file), str(self.filepath_output))
        logger.warning(f"Decoding success: {output_exists and output_identical}, output file exists: {output_exists}, files are equal: {output_identical}")
        result['decoding_success'] = output_exists and output_identical

        # add the encoding stats
        try:
            result.update(encoding_stats(self.input_file, self.filepath_sequences))
        except FileNotFoundError as e:
            logger.warning(f"Could not calculate encoding stats: {e}")

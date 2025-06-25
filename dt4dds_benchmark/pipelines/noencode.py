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
class NoEncode(BasePipeline):
    """  """

    # required settings
    design_file: pathlib.Path        # path to the file containing the design sequences
    codec: BaseCodec                 # codec to use
    workflow: BaseWorkflow           # workflow to use
    clustering: BaseClustering       # clustering algorithm to use

    # optional settings
    codec_folder: pathlib.Path = None       # path to the folder with the codec output, required files will be copied from there
    input_file: pathlib.Path = None         # path to the input file used for encoding, if given, decoding success will be checked


    @classmethod
    def factory(cls, 
        workflows: List[BaseWorkflow],      # list of workflows to use
        clusterings: List[BaseClustering],  # list of clustering algorithms to use
        **kwargs
    ):
        return super().factory(
            list_args={'workflow': workflows, 'clustering': clusterings},
            **kwargs
        )


    @property
    def _pipeline(self):
        return [
            (self.workflow, self.workflow.run, self.filepath_sequences, self.filepath_reads, 'workflow'),
            (self.clustering, self.clustering.run, self.filepath_reads, self.filepath_clusters, 'clustering'),
            (self.codec, self.codec.decode, self.filepath_clusters, self.filepath_output, 'decoding'),
        ]
    

    def _prepare_files(self):
        # copy the design file to be run with the workflow
        shutil.copy(str(self.design_file), str(self.filepath_sequences))

        # copy any required additional files from the encoding step
        for filename in self.codec.required_files:
            filename = pathlib.Path(filename)
            if not self.codec_folder:
                raise ValueError(f"Codec folder is required to copy the files {self.codec.required_files}")
            shutil.copy(str(self.codec_folder.resolve() / filename), str(self.output_folder.resolve() / filename.name))


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

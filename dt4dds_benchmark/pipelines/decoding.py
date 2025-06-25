import pathlib
import dataclasses
from typing import List
import shutil

from .basepipeline import BasePipeline
from ..codecs.basecodec import BaseCodec
from ..clustering.baseclustering import BaseClustering
from ..tools import files_are_equal

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)



@dataclasses.dataclass(kw_only=True)
class Decoding(BasePipeline):
    """  """

    # required settings
    read_file: pathlib.Path                 # path to the sequencing file with the workflow output
    clustering: BaseClustering              # clustering algorithm to use
    codec: BaseCodec                        # codec to use

    # optional settings
    codec_folder: pathlib.Path = None       # path to the folder with the codec output, required files will be copied from there
    input_file: pathlib.Path = None         # path to the input file used for encoding, if given, decoding success will be checked


    @classmethod
    def factory(cls, 
        read_files: List[pathlib.Path],                 # paths to the sequencing file with the workflow output
        codecs: List[BaseCodec],                        # codec to use
        clusterings: List[BaseClustering],              # list of clustering algorithms to use
        codec_folders: List[pathlib.Path],              # path to the folder with the codec output
        **kwargs
    ):
        return super().factory(
            list_args={'read_file': read_files, 'clustering': clusterings, 'codec': codecs, 'codec_folder': codec_folders},
            **kwargs
        )


    @property
    def _pipeline(self):
        return [
            (self.clustering, self.clustering.run, self.filepath_reads, self.filepath_clusters, 'clustering'),
            (self.codec, self.codec.decode, self.filepath_clusters, self.filepath_output, 'decoding'),
        ]


    def _prepare_files(self):
        # copy the read file with the reads
        shutil.copy(str(self.read_file.resolve()), str(self.filepath_reads.resolve()))
        
        # copy any required additional files from the encoding step
        for filename in self.codec.required_files:
            filename = pathlib.Path(filename)
            if not self.codec_folder:
                raise ValueError(f"Codec folder is required to copy the files {self.codec.required_files}")
            shutil.copy(str(self.codec_folder.resolve() / filename), str(self.output_folder.resolve() / filename.name))


    def _customize_result(self, result):
        # if an input file was given, check if the output file exists and is identical to the input file
        if self.input_file:
            output_exists = self.filepath_output.exists()
            output_identical = files_are_equal(str(self.input_file), str(self.filepath_output))
            logger.warning(f"Decoding success: {output_exists and output_identical}, output file exists: {output_exists}, files are equal: {output_identical}")
            result['input_file'] = self.input_file.name
            result['decoding_success'] = output_exists and output_identical
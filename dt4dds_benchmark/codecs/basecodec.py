import time
import pathlib
import dataclasses
from typing import List

from ..tools import Step, stats

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class BaseCodec(Step):
    """ Abstract class for codecs. To be overridden by actual codec implementations as a subclass. """

    required_files = []

    def __post_init__(self):
        super().__post_init__()
        self._class = 'Codec'

    # 
    # public methods
    # 

    def encode(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):
        """ Encode the data in the input file and write the output sequences to the sequence file. Returns the metadata of the process. """
        
        logger.info(f"Encoding {input_file} to {sequence_file} with {self}.")
        start = time.time()

        try:
            process = self._run_encoding(pathlib.Path(input_file), pathlib.Path(sequence_file), **kwargs)
            return process.metadata
        except Exception as e:
            logger.error(f"Encoding failed with {e}")
            raise e
        finally:
            try:
                statistics = stats.encoding_stats(pathlib.Path(input_file), pathlib.Path(sequence_file))
                logger.info(f"Encoded {statistics['filesize_byte']} bytes in {statistics['n_sequences']} sequences with {statistics['sequence_length']:.0f} nt, for a code rate of {statistics['code_rate']:.2f}")
            except FileNotFoundError:
                logger.warning(f"Sequence file {sequence_file} was not created.")
            logger.info(f"Encoding {self} took {time.time()-start:.1f} seconds")


    def decode(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):
        """ Decode the sequence file and write the data to the output file """
        
        logger.info(f"Decoding {sequence_file} with {self}")
        start = time.time()

        try:
            process = self._run_decoding(pathlib.Path(sequence_file), pathlib.Path(output_file), **kwargs)
            return process.metadata
        except Exception as e:
            logger.exception(f"Decoding failed with {e}")
            raise e
        finally:
            logger.info(f"Decoding took {time.time()-start:.1f} seconds")


    # 
    # override these methods in the subclass
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):
        """ To be override by the subclass """
        raise NotImplementedError("_run_encoding() not implemented")
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):
        """ To be override by the subclass """
        raise NotImplementedError("_run_decoding() not implemented")

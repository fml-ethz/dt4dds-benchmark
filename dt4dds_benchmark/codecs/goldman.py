import dataclasses
import pathlib

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class Goldman(BaseCodec):
    """
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().

    This codec has no supported parameters which directly influence the effective code rate.
    """

    required_files = ['segment_count.txt']

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_goldman' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_goldman' / 'decode.sh')

    # file names
    segment_count_file = 'segment_count.txt'

    
    # 
    # defaults
    # 
    
    @classmethod
    def default(cls, *args, **kwargs):
        return cls("default", **kwargs)


    # 
    # encoding and decoding
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_encode]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(sequence_file.resolve().parent / self.segment_count_file))

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        cmd.append(str(sequence_file.resolve().parent / self.segment_count_file))
        
        return SubProcess(cmd, **kwargs)
    

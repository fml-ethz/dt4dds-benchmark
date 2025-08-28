import dataclasses
import pathlib

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class Modulation(BaseCodec):
    """
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().

    This codec has no supported parameters which directly influence the effective code rate.
    """

    required_files = []

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_modulation' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_modulation' / 'decode.sh')

    
    # 
    # defaults
    # 
    
    @classmethod
    def default(cls, *args, **kwargs):
        return cls("default", **kwargs)
    
    @classmethod
    def medium_coderate(cls, *args, **kwargs):
        return cls("medium", **kwargs)


    # 
    # encoding and decoding
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_encode]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        
        return SubProcess(cmd, **kwargs)
    

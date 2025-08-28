import dataclasses
import pathlib

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class LDPC(BaseCodec):
    """
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().

    This codec has no supported parameters which directly influence the effective code rate.
    """

    required_files = []

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_ldpc' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_ldpc' / 'decode.sh')
    
    # codec settings
    oligo_length: int = 150     # oligo length
    bch: int = 2                # BCH symbols
    alpha: float = 0.1          # redundancy
    file_size: int = 0          # size of file to encode in bytes

    
    # 
    # defaults
    # 
    
    @classmethod
    def medium_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            oligo_length = 150,
            bch = 2,
            alpha = 0.1,
            file_size = file_size,
        )
        return cls("medium", **kwargs)
    
    
    @classmethod
    def default(cls, file_size, *args, **kwargs):
        kwargs.update(
            oligo_length = 150,
            bch = 2,
            alpha = 0.1,
            file_size = file_size,
        )
        return cls("default", **kwargs)


    # 
    # encoding and decoding
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_encode]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(self.oligo_length))
        cmd.append(str(self.bch))
        cmd.append(str(self.alpha))

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        cmd.append(str(self.oligo_length))
        cmd.append(str(self.bch))
        cmd.append(str(self.alpha))
        cmd.append(str(self.file_size))
        
        return SubProcess(cmd, **kwargs)
    

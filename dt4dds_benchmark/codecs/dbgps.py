import dataclasses
import pathlib
import math

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class DBGPS(BaseCodec):
    """
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().
    """

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_dbgps' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_dbgps' / 'decode.sh')

    # codec settings
    droplet_num: int = 2000             # number of droplets
    chunk_size: int = 35                # size of the encoded chunks in bytes
    ec_bytes: int = 2                   # number of ec bytes
    file_size: int = 0                  # size of file to encode in bytes

    # derived codec parameters
    chunk_num = property(lambda self: math.ceil(self.file_size/self.chunk_size))   # number of data chunks (chunk size=35), needed for decoding


    # 
    # defaults
    #     
    

    @classmethod
    def low_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            file_size = file_size,
            droplet_num = 2100,
            chunk_size = 31,
            ec_bytes = 2,
        )
        return cls("low", **kwargs)
    
    
    @classmethod
    def medium_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            file_size = file_size,
            droplet_num = 1050,
            chunk_size = 31,
            ec_bytes = 2,
        )
        return cls("medium", **kwargs)
    

    @classmethod
    def high_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            file_size = file_size,
            droplet_num = 730,
            chunk_size = 31,
            ec_bytes = 2,
        )
        return cls("high", **kwargs)
    

    @classmethod
    def default(cls, file_size, *args, **kwargs):
        kwargs.update(
            file_size = file_size,
            droplet_num = 2100,
            chunk_size = 31,
            ec_bytes = 2,
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
        cmd.extend(['--droplet_num', str(self.droplet_num)])
        cmd.extend(['--chunk_size', str(self.chunk_size)])
        cmd.extend(['--ec_bytes', str(self.ec_bytes)])

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        cmd.extend(['--chunk_num', str(self.chunk_num)])
        cmd.extend(['--chunk_size', str(self.chunk_size)])
        cmd.extend(['--ec_bytes', str(self.ec_bytes)])
        
        return SubProcess(cmd, **kwargs)
    

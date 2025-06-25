import dataclasses
import pathlib
import math

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class DNAFountain(BaseCodec):
    """ 
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().
    """

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_fountain' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_fountain' / 'decode.sh')

    # codec settings
    size: int = 32              # size of the encoded chunks in bytes
    max_homopolymer: int = 4    # maximum length of homopolymers
    gc: float = 0.5             # allowed deviation of GC content
    rs: int = 2                 # Reed-Solomon bytes
    delta: float = 0.1          # degree distribution tuning parameter
    c_dist: float = 0.025       # degree distribution tuning parameter
    alpha: float = 0.07         # ratio of additional redundancy sequences to add
    header_size: int = 4        # size of the header in bytes
    stop: int = None            # stop after this many sequences have been created
    file_size: int = 0          # size of file to encode in bytes

    # derived codec parameters
    chunk_size = property(lambda self: math.ceil((int(self.file_size)/int(self.size))))
    sequence_length = property(lambda self: 4*(self.size + self.rs + self.header_size))

    # 
    # defaults
    # 

    @classmethod
    def low_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            size = 32,
            rs = 2,
            alpha = 2.35,
            file_size = file_size,
        )
        return cls("low", **kwargs)
    
    
    @classmethod
    def medium_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            size = 32,
            rs = 2,
            alpha = 0.68,
            file_size = file_size,
        )
        return cls("medium", **kwargs)
    
    
    @classmethod
    def high_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            size = 34,
            rs = 0,
            alpha = 0.19,
            file_size = file_size,
        )
        return cls("high", **kwargs)
    
    
    @classmethod
    def medium_coderate_pool(cls, file_size, *args, **kwargs):
        kwargs.update(
            size = 24,
            rs = 2,
            alpha = 0.6,
            file_size = file_size,
        )
        return cls("medium_pool", **kwargs)
    
    
    @classmethod
    def high_coderate_pool(cls, file_size, *args, **kwargs):
        kwargs.update(
            size = 26,
            rs = 1,
            alpha = 0.14,
            file_size = file_size,
        )
        return cls("high_pool", **kwargs)
    
    
    @classmethod
    def max_coderate_pool(cls, file_size, *args, **kwargs):
        kwargs.update(
            size = 27,
            rs = 0,
            alpha = 0,
            file_size = file_size,
        )
        return cls("max_pool", **kwargs)
    
    
    @classmethod
    def default(cls, file_size, *args, **kwargs):
        kwargs.update(
            size = 32,
            max_homopolymer = 3,
            gc = 0.05,
            rs = 2,
            delta = 0.001,
            c_dist = 0.025,
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
        cmd.extend(['--size', str(self.size)])
        cmd.extend(['--max_homopolymer', str(self.max_homopolymer)])
        cmd.extend(['--gc', str(self.gc)])
        cmd.extend(['--rs', str(self.rs)])
        cmd.extend(['--delta', str(self.delta)])
        cmd.extend(['--c_dist', str(self.c_dist)])
        cmd.extend(['--alpha', str(self.alpha)])
        cmd.append('--no_fasta')

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        cmd.append(str(self.sequence_length))
        cmd.extend(['--header_size', str(self.header_size)])
        cmd.extend(['--chunk_num', str(self.chunk_size)])
        cmd.extend(['--rs', str(self.rs)])
        cmd.extend(['--delta', str(self.delta)])
        cmd.extend(['--c_dist', str(self.c_dist)])
        cmd.extend(['--max_homopolymer', str(self.max_homopolymer)])
        cmd.extend(['--gc', str(self.gc)])
        cmd.extend(['--size', str(self.size)])

        # add optional arguments
        if self.stop: cmd.extend(['--stop', str(self.stop)])
        
        return SubProcess(cmd, **kwargs)
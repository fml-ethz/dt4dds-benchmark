import dataclasses
import pathlib
from typing import List

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class YinYang(BaseCodec):
    """
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().

    This codec supports no parameters which directly influence the effective code rate.
    """

    required_files = ['supplementary_file', 'supplementary_file.len']

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_yinyang' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_yinyang' / 'decode.sh')

    # codec settings
    homopolymer: int = 4          # maximum length of allowed homopolymers
    gc_content: float = 0.75      # allowed range of GC content
    segment_length: int = 120     # length of the encoded sequences
    
    # 
    # defaults
    # 

    @classmethod
    def default(cls, *args, **kwargs):
        kwargs.update(
            segment_length = 140,
        )
        return cls("default", **kwargs)
    

    @classmethod
    def default_pool(cls, *args, **kwargs):
        kwargs.update(
            segment_length = 110,
        )
        return cls("default-pool", **kwargs)


    # 
    # encoding and decoding
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_encode]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))
        cmd.extend(['--supplementary_path', str((sequence_file.parent / 'supplementary_file').resolve())])
        cmd.extend(['--max_homopolymer', str(self.homopolymer)])
        cmd.extend(['--max_gc', str(self.gc_content)])
        cmd.extend(['--segment_length', str(self.segment_length)])

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        cmd.extend(['--supplementary_path', str((output_file.parent / 'supplementary_file').resolve())])
        cmd.extend(['--max_homopolymer', str(self.homopolymer)])
        cmd.extend(['--max_gc', str(self.gc_content)])
        cmd.extend(['--segment_length', str(self.segment_length)])
        
        return SubProcess(cmd, **kwargs)
    

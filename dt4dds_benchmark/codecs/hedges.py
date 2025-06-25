import dataclasses
import pathlib
import math

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class HEDGES(BaseCodec):
    """
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().

    The codec is configured with a code rate and a sequence length. The code rate is an index into the coderate array in the codec.
    """

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_hedges' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_hedges' / 'decode.sh')

    # codec settings
    code_rate: int = 1          # base code rate, defined as an index into the coderate array in the codec
    seq_length: int = 152       # length of the encoded sequences
    n_packets: int = 5          # number of packets to encode


    # 
    # defaults
    # 

    def _optimize_packets(file_size, slope, intercept, max_length = 152):
        """ 
        Because the codec uses a fixed packet size, the last packet is often not full. For fairness, we try to balance 
        the number of packets and the sequence length, so that only few unused bytes are present in the last packet. 
        The relationship between file size, number of packets, and sequence length follows an empirical linear relationship, characterized by the slope and intercept. 
        """
        n_packets = math.ceil(file_size / (slope * (max_length-2) + intercept))
        return math.ceil((file_size / n_packets - intercept) / slope) + 2, n_packets


    @classmethod
    def low_coderate(cls, file_size, max_length = 152, *args, **kwargs):
        seq_length, n_packets = cls._optimize_packets(file_size, 28.0, -1015, max_length=max_length)
        kwargs.update(
            code_rate = 3,
            seq_length = seq_length,
            n_packets = n_packets,
        )
        return cls("low", **kwargs)
    
    
    @classmethod
    def medium_coderate(cls, file_size, max_length = 152, *args, **kwargs):
        seq_length, n_packets = cls._optimize_packets(file_size, 44.6, -1338, max_length=max_length)
        kwargs.update(
            code_rate = 1,
            seq_length = seq_length,
            n_packets = n_packets,
        )
        return cls("medium", **kwargs)
    
    
    @classmethod
    def medium_coderate_pool(cls, *args, **kwargs):
        kwargs.update(
            code_rate = 1,
            seq_length = 110,
            n_packets = 9,
        )
        return cls("pool", **kwargs)
    
    
    @classmethod
    def default(cls, file_size, max_length = 152, *args, **kwargs):
        seq_length, n_packets = cls._optimize_packets(file_size, 44.6, -1338, max_length=max_length)
        kwargs.update(
            code_rate = 1,
            seq_length = seq_length,
            n_packets = n_packets,
        )
        return cls("default", **kwargs)


    # 
    # encoding and decoding
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_encode]

        # add required arguments
        cmd.append(str(self.code_rate))
        cmd.append(str(self.seq_length))
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(self.code_rate))
        cmd.append(str(self.seq_length))
        cmd.append(str(self.n_packets))
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        
        return SubProcess(cmd, **kwargs)
    

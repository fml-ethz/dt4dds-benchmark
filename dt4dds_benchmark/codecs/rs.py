import dataclasses
import pathlib
import math

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class DNARS(BaseCodec):
    """
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().
    """

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_rs' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_rs' / 'decode.sh')

    # codec settings
    mi: int = 6             # inner code symbol size in bits, hardcoded
    mo: int = 14            # outer code symbol size in bits, hardcoded
    index: int = 24         # length of index in bits, hardcoded
    seq_length: int = 126   # length of sequence in nts
    red_factor: int = 2     # redundancy factor, N-K
    num_seq: int = 100      # number of sequences to encode
    file_size: int = 0       # size of file to encode in bytes

    # derived codec parameters
    index_l = property(lambda self: int(self.index/self.mi))                # number of index symbols
    max_inner = property(lambda self: int(pow(2,self.mi)-1))                # maximum inner code length
    max_outer = property(lambda self: int(pow(2,self.mo)-1))                # maximum outer code length
    max_seq_length = property(lambda self: int(self.mi*self.max_inner*0.5)) # maximum sequence length for outer code
    
    par_N = property(lambda self: int(self.seq_length*2/self.mi))
    par_K = property(lambda self: int(self.par_N - self.red_factor))
    par_nuss = property(lambda self: int(((self.seq_length*2/self.mi - self.red_factor)*self.mi-self.mi*self.index_l)/self.mo))
    par_numblock = property(lambda self: int(((self.num_seq-1)/self.max_outer)+1))
    par_n = property(lambda self: int(self.num_seq/self.par_numblock))
    par_k = property(lambda self: int(((8*self.file_size)/(self.par_nuss*self.mo)/self.par_numblock)+1))


    # 
    # defaults
    # 

    @classmethod
    def low_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            seq_length = 150,
            red_factor = 4,
            num_seq = int((875/8192)*file_size),
            file_size = file_size,
        )
        return cls("low", **kwargs)
    
    
    @classmethod
    def medium_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            seq_length = 144,
            red_factor = 2,
            num_seq = int((855/15360)*file_size),
            file_size = file_size,
        )
        return cls("medium", **kwargs)
    
    
    @classmethod
    def high_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            seq_length = 144,
            red_factor = 2,
            num_seq = int((570/15360)*file_size),
            file_size = file_size,
        )
        return cls("high", **kwargs)
    
    
    @classmethod
    def max_coderate(cls, file_size, *args, **kwargs):
        kwargs.update(
            seq_length = 144,
            red_factor = 2,
            num_seq = math.ceil((98/3072)*file_size)+2,
            file_size = file_size,
        )
        return cls("max", **kwargs)
    
    
    @classmethod
    def medium_coderate_pool(cls, file_size, *args, **kwargs):
        kwargs.update(
            seq_length = 126,
            red_factor = 3,
            num_seq = 1110,
            file_size = file_size,
        )
        return cls("medium_pool", **kwargs)
    
    
    @classmethod
    def high_coderate_pool(cls, file_size, *args, **kwargs):
        kwargs.update(
            seq_length = 126,
            red_factor = 3,
            num_seq = 823,
            file_size = file_size,
        )
        return cls("high_pool", **kwargs)
    
    
    @classmethod
    def max_coderate_pool(cls, file_size, *args, **kwargs):
        kwargs.update(
            seq_length = 102,
            red_factor = 2,
            num_seq = 928,
            file_size = file_size,
        )
        return cls("max_pool", **kwargs)
    
    
    @classmethod
    def default(cls, file_size, *args, **kwargs):
        kwargs.update(
            file_size = file_size,
        )
        return cls("max", **kwargs)


    # 
    # encoding and decoding
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_encode]

        # add required arguments
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))
        cmd.extend(['--n', str(self.par_n)])
        cmd.extend(['--k', str(self.par_k)])
        cmd.extend(['--nuss', str(self.par_nuss)])
        cmd.extend(['--K', str(self.par_K)])
        cmd.extend(['--N', str(self.par_N)])
        cmd.extend(['--numblocks', str(self.par_numblock)])

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        cmd.append(str(self.seq_length))
        cmd.extend(['--n', str(self.par_n)])
        cmd.extend(['--k', str(self.par_k)])
        cmd.extend(['--nuss', str(self.par_nuss)])
        cmd.extend(['--K', str(self.par_K)])
        cmd.extend(['--N', str(self.par_N)])
        cmd.extend(['--numblocks', str(self.par_numblock)])
        
        return SubProcess(cmd, **kwargs)
    

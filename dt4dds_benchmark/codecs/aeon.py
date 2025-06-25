import dataclasses
import pathlib
import json
import uuid
from typing import List

from .basecodec import BaseCodec
from ..tools import SubProcess

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class DNAAeon(BaseCodec):
    """ 
    After initialization, the codec can be used to encode and decode files by calling encode() and decode().
    """

    required_files = ['config.json.ini', 'config.json.len']

    # executable paths
    command_path_encode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_aeon' / 'encode.sh')
    command_path_decode = str(pathlib.Path(__file__).parent.absolute() / 'bin' / 'codec_aeon' / 'decode.sh')

    # codec settings
    sync: int = 4
    chunk_size: int = 14
    package_redundancy: float = 0.45
    error_detection: str = "crc"
    n_threads: int = 1

    # codebook settings
    codebook_words: pathlib.Path = './codewords/codebooks.fasta'
    codebook_motifs: pathlib.Path = './codewords/codebooks.json'

    
    def _save_config(self, filepath: pathlib.Path, uuid: uuid.UUID):
        """ Save codec settings to a JSON file. """
        d = dict(
            general = dict(
                sync = self.sync,
                as_fasta = True,
                codebook = dict(words = self.codebook_words, motifs = self.codebook_motifs),
                threads = self.n_threads,
                zip = dict(most_common_only = True, decodable_only = True),
            ),
            NOREC4DNA = dict(
                chunk_size = self.chunk_size,
                package_redundancy = self.package_redundancy,
                insert_header = False,
                header_crc_length = 0,
                error_detection = self.error_detection,
            ),
            encode = dict(
                input = f"data/{str(uuid)}.input",
                output = f"data/{str(uuid)}.output.fasta",
                min_length = 0,
                same_length = True,
                update_config = True,
                keep_intermediary = False,        
            ),
            decode = dict(
                input = f"data/{str(uuid)}.input.fasta",
                output = f"data/{str(uuid)}.output",
                NOREC4DNA_config = f"data/{str(uuid)}.ini",
                length = 0,
                threshold = dict(loop = 1, finish = 0, checkpoint = 3),
                metric = dict(
                    fano = dict(rate = dict(low = 4, high = 5), error_probability = 0.05),
                    penalties = dict(crc = 0.1, no_hit = 8),
                ),
                queue = dict(size = 200000, runs = 5, reduce = 0.25)
            ),
        )

        # now save it
        with open(filepath, 'w') as f:
            json.dump(d, f, indent=4, sort_keys=False)


    # 
    # defaults
    # 

    @classmethod
    def low_coderate(cls, *args, **kwargs):
        kwargs.update(
            sync = 4,
            chunk_size = 25,
            package_redundancy = 1.68,
            error_detection = 'crc',
        )
        return cls("low", **kwargs)
    
    
    @classmethod
    def medium_coderate(cls, *args, **kwargs):
        kwargs.update(
            sync = 4,
            chunk_size = 25,
            package_redundancy = 0.34,
            error_detection = 'crc',
        )
        return cls("medium", **kwargs)
    
    
    @classmethod
    def high_coderate(cls, *args, **kwargs):
        kwargs.update(
            sync = 8,
            chunk_size = 28,
            package_redundancy = 0.031,
            error_detection = 'crc',
        )
        return cls("high", **kwargs)
    
    
    @classmethod
    def medium_coderate_pool(cls, *args, **kwargs):
        kwargs.update(
            sync = 4,
            chunk_size = 20,
            package_redundancy = 0.32,
            error_detection = 'crc',
        )
        return cls("medium_pool", **kwargs)
    
    
    @classmethod
    def high_coderate_pool(cls, *args, **kwargs):
        kwargs.update(
            sync = 12,
            chunk_size = 24,
            package_redundancy = 0.028,
            error_detection = 'crc',
        )
        return cls("high_pool", **kwargs)
    
    
    @classmethod
    def max_coderate_pool(cls, *args, **kwargs):
        kwargs.update(
            sync = 0,
            chunk_size = 28,
            package_redundancy = 0.0,
            error_detection = 'nocode',
        )
        return cls("max_pool", **kwargs)
    
    
    @classmethod
    def default(cls, *args, **kwargs):
        return cls("default", **kwargs)


    # 
    # encoding and decoding
    # 

    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        config_file = sequence_file.parent / 'config.json'
        uid = uuid.uuid1()
        self._save_config(config_file, uid)

        cmd = [self.command_path_encode]

        # add required arguments
        cmd.append(str(uid))
        cmd.append(str(config_file.resolve()))
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        config_file = sequence_file.parent / 'config.json'
        uid = uuid.uuid1()
        self._save_config(config_file, uid)

        cmd = [self.command_path_decode]

        # add required arguments
        cmd.append(str(uid))
        cmd.append(str(config_file.resolve()))
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))
        
        return SubProcess(cmd, **kwargs)
    

import pytest
import dt4dds_benchmark

from .conftest import assert_encoding, perform_encoding, assert_decoding, perform_decoding


testdata = [
    # 
    # DNA-Aeon codec
    # 
    pytest.param(
        dt4dds_benchmark.codecs.DNAAeon.low_coderate(), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 0.5, "n_sequences": 2088, "sequence_length": 149},
        marks=pytest.mark.codecs_aeon,
        id="aeon_low",
    ),
    pytest.param(
        dt4dds_benchmark.codecs.DNAAeon.medium_coderate(), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.0, "n_sequences": 1044, "sequence_length": 149},
        marks=pytest.mark.codecs_aeon,
        id="aeon_medium"
    ),
    pytest.param(
        dt4dds_benchmark.codecs.DNAAeon.high_coderate(), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.5, "n_sequences": 717, "sequence_length": 145, 'delta_n_sequences': 1, 'delta_sequence_length': 1},
        marks=pytest.mark.codecs_aeon,
        id="aeon_high"
    ),
    # 
    # DNA-Fountain codec
    # 
    pytest.param(
        dt4dds_benchmark.codecs.DNAFountain.low_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 0.5, "n_sequences": 2037, "sequence_length": 152},
        marks=pytest.mark.codecs_fountain,
        id="fountain_low"
    ),
    pytest.param(
        dt4dds_benchmark.codecs.DNAFountain.medium_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.0, "n_sequences": 1022, "sequence_length": 152},
        marks=pytest.mark.codecs_fountain,
        id="fountain_medium"
    ),
    pytest.param(
        dt4dds_benchmark.codecs.DNAFountain.high_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.5, "n_sequences": 682, "sequence_length": 152},
        marks=pytest.mark.codecs_fountain,
        id="fountain_high"
    ),
    # 
    # Goldman codec
    # 
    pytest.param(
        dt4dds_benchmark.codecs.Goldman.default(), 
        dt4dds_benchmark.inputs.pool_5kB, 
        {"code_rate": 0.34, "n_sequences": 1032, "sequence_length": 117},
        marks=pytest.mark.codecs_goldman,
        id="goldman_default"
    ),
    # 
    # RS codec
    # 
    pytest.param(
        dt4dds_benchmark.codecs.DNARS.low_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 0.5, "n_sequences": 2078, "sequence_length": 150},
        marks=pytest.mark.codecs_rs,
        id="rs_low"
    ),
    pytest.param(
        dt4dds_benchmark.codecs.DNARS.medium_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.0, "n_sequences": 1083, "sequence_length": 144},
        marks=pytest.mark.codecs_rs,
        id="rs_medium"
    ),
    pytest.param(
        dt4dds_benchmark.codecs.DNARS.high_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.5, "n_sequences": 722, "sequence_length": 144},
        marks=pytest.mark.codecs_rs,
        id="rs_high"
    ),
    pytest.param(
        dt4dds_benchmark.codecs.DNARS.max_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.73, "n_sequences": 623, "sequence_length": 144},
        marks=pytest.mark.codecs_rs,
        id="rs_max"
    ),
    # 
    # HEDGES codec
    # 
    pytest.param(
        dt4dds_benchmark.codecs.HEDGES.low_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 0.63, "n_sequences": 1785, "sequence_length": 138},
        marks=pytest.mark.codecs_hedges,
        id="hedges_low"
    ),
    pytest.param(
        dt4dds_benchmark.codecs.HEDGES.medium_coderate(dt4dds_benchmark.inputs.random_19kB.stat().st_size), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.07, "n_sequences": 1020, "sequence_length": 142},
        marks=pytest.mark.codecs_hedges,
        id="hedges_medium"
    ),
    # 
    # YinYang codec
    # 
    pytest.param(
        dt4dds_benchmark.codecs.YinYang.default(), 
        dt4dds_benchmark.inputs.random_19kB, 
        {"code_rate": 1.85, "n_sequences": 557, "sequence_length": 151, "delta_n_sequences": 1},
        marks=pytest.mark.codecs_yinyang,
        id="yinyang_default"
    ),
]








@pytest.mark.codecs
@pytest.mark.codecs_encoding
@pytest.mark.parametrize("codec,input_file,expected", testdata)
def test_encoding(tmp_path, codec, input_file, expected):
    assert_encoding(
        perform_encoding(codec, tmp_path, input_file),
        **expected
    )


@pytest.mark.codecs
@pytest.mark.codecs_decoding
@pytest.mark.parametrize("codec,input_file,expected", testdata)
def test_decoding(tmp_path, codec, input_file, expected):
    perform_encoding(codec, tmp_path, input_file)
    assert_decoding(
        perform_decoding(codec, tmp_path),
        input_file
    )
import pytest
import pathlib
import shutil
import dt4dds_benchmark



def perform_encoding(codec, folder, input, input_name="input", output_name="encoded.txt"):
    copied_input = (pathlib.Path(folder) / input_name).resolve()
    output = (pathlib.Path(folder) / output_name).resolve()
    shutil.copy(input.resolve(), copied_input)
    codec.encode(copied_input, output)
    return dt4dds_benchmark.tools.encoding_stats(copied_input, output)


def assert_encoding(results, code_rate, n_sequences, sequence_length, delta_coderate=0.01, delta_n_sequences=0, delta_sequence_length=0):
    print(results)
    assert results["code_rate"] == pytest.approx(code_rate, abs=delta_coderate), f"Expected {code_rate}, got {results['code_rate']}"
    assert results["n_sequences"] == pytest.approx(n_sequences, abs=delta_n_sequences), f"Expected {n_sequences}, got {results['n_sequences']}"
    assert results["sequence_length"] == pytest.approx(sequence_length, abs=delta_sequence_length), f"Expected {sequence_length}, got {results['sequence_length']}"


def perform_decoding(codec, folder, input_name="encoded.txt", output_name="output"):
    input = (pathlib.Path(folder) / input_name).resolve()
    output = (pathlib.Path(folder) / output_name).resolve()
    codec.decode(input, output)
    return output


def assert_decoding(output_file, input_file):
    assert dt4dds_benchmark.tools.files_are_equal(input_file, output_file), f"Decoded file is not equal to input file"

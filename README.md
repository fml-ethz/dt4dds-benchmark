# 🧬🏋 dt4dds-benchmark - Benchmarking suite for DNA data storage


- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Demo](#demo)
- [Usage and Tests](#usage-and-tests)
- [Default Codecs and Clusterers](#default-codecs-and-clusterers)
- [Extending to other Codecs and Clusterers](#extending-to-other-codecs-and-clusterers)
- [License](#license)


# Overview
`dt4dds-benchmark` is a Python package providing a comprehensive benchmarking suite for codecs and clustering algorithms in the field of DNA data storage. It provides customizable, Python-based wrappers for all steps of the digital DNA data storage pipeline: encoding with any codec, simulating arbitrary experimental workflows under standardized conditions, employing various clustering algorithms, and finally assessing decoding succcess. Additionally, it provides tools to facilitate automatic parameter sweeps while collecting performance data and enforcing runtime constraints.

This Python package is used in the following publication:

> Gimpel, A.L., Remschak, A., Stark, W.J., Heckel, R., Grass R.N. manuscript in preparation

The Jupyter notebooks and associated code used for generating the figures in the manuscript are found in the [dt4dds-benchmark_notebooks repository](https://github.com/fml-ethz/dt4dds-benchmark_notebooks).


# System requirements
## Hardware requirements
This package only requires a standard computer. The performance is mostly dependent on the choice of codec, clustering algorithm, and workflow. Particularly demanding combinations might fail unless sufficient system memory (i.e., > 8GB RAM) is available. The use of a computing cluster and workload manager is recommended for comprehensive, large-scale benchmarking across multiple parameters. 

## Software requirements
The package has been developed and tested on Ubuntu 20.04 using Python 3.10. The Python packages listed in [requirements.txt](/requirements.txt) are required. Note that the codecs and clustering algorithms for which default wrappers are included in this package - if needed by the user - must be installed individually, and may have additional requirements not covered by [requirements.txt](/requirements.txt). This is also the case for NGmerge and kalign, which can optionally be used to perform read merging and multi-sequence alignment.


# Installation guide
The recommended method for installation varies by the intended application. If you'd like to use the pipeline features and wrappers of this package with your own codec, please install from source. If instead you'd like to use the default codecs and clustering algorithms from the study, proceed with the Docker image.

## Docker image (recommended for testing with default codecs)
A Docker image based on the [Dockerfile](/Dockerfile) is available from `agimpel/dt4dds-benchmark` on Docker Hub. To run it, pull and start the image:
```bash
docker run -it agimpel/dt4dds-benchmark bash
```

To exchange scripts or data files with the container, it is recommended to mount a local folder (e.g., this repository's `demo` folder) to the container's `/data` directory:
```bash
docker run --mount type=bind,src=./demo,dst=/data -it agimpel/dt4dds-benchmark bash
```
From within the container, scripts using `dt4dds-benchmark` can use all of the default codecs and clustering algorithms described in the manuscript and outlined in the section [Default Codecs and Clusterers](#default-codecs-and-clusterers).


## From source (recommended for extension with new codecs)
To install this package from Github, use
```bash
git clone https://github.com/fml-ethz/dt4dds-benchmark
cd dt4dds-benchmark
python3 setup.py install .
```

These steps only install the Python-based wrappers, but not the underlying software of codecs and clustering algorithms. If the default codecs and clustering algorithms are to be used, these must be installed directly from the respective repositories (see Section [Default Codecs and Clusterers](#default-codecs-and-clusterers)). To simplify this, installation scripts (named install.sh) are provided in each subdirectory (e.g., [dt4dds_benchmark/codecs/bin/codec_rs/install.sh](dt4dds_benchmark/codecs/bin/codec_rs/install.sh)). Each codec and clustering algorithm has its own individual software requirements and dependencies, which are not covered by those outlined above (see Section [Default Codecs and Clusterers](#default-codecs-and-clusterers) for additional information).


# Demo
Two demonstration scripts outlining the functionality of this package are provided in the [demo](/demo/) subdirectory. They represent the basic pipeline and varying pipeline documented in more detail in the section of [Usage and Tests](#usage-and-tests). To execute them, make sure you have either installed this package from source with all default codecs, or are executing from within the Docker container:
```bash
python3 ./demo/basic_pipeline.py
```
The expected execution time on a standard computer is a few seconds for the basic pipeline, and about a minute for the varying pipeline (as it is running a complete parameter sweep).


# Usage and Tests 

First, ensure a codec and clustering algorithm is available, either by installing one of the defaults (see Section [Default Codecs and Clusterers](#default-codecs-and-clusterers)) or generating a wrapper for your own (see Section [Extending to other Codecs and Clusterers](#extending-to-other-codecs-and-clusterers))


## Simple pipelines
To run a simple pipeline covering all steps from encoding to decoding, load the package, define an input file, and instantiate a codec, clustering algorithm, and workflow with their respective parameters:
```python
import dt4dds_benchmark
import pathlib

input_path = pathlib.Path("./my_file")
filesize = input_path.stat().st_size

codec = dt4dds_benchmark.codecs.DNARS.high_coderate(filesize)
clustering = dt4dds_benchmark.clustering.BasicSet.default()
workflow = dt4dds_benchmark.workflows.ErrorGenerator(
    rate_substitutions=0.01, 
    rate_deletions=0, 
    rate_insertions=0, 
    dropout=0, 
    coverage=30
)
```
Then, define the pipeline and run it:
```python
pipeline = dt4dds_benchmark.pipelines.Full(
    input_file=input_path,
    codec=codec,
    workflow=workflow,
    clustering=clustering,
)

result, performance = pipeline.run()
```
As an output, you will receive a dictionary with the decoding success (`result['completed']`) and the step at which the pipeline failed, if any (`result['failed_at']`). In addition, a list with performance metrics of all individual steps is provided.

To support additional use cases, other types of pipelines are available:
- `dt4dds_benchmark.pipelines.NoEncode` skips file encoding, and runs the pipeline with a supplied file of sequences. This is especially useful if a codec's output is not deterministic.
- `dt4dds_benchmark.pipelines.Decoding` only attempts to cluster and decode a supplied sequencing dataset. This is useful to compare different clustering and decoding combinations with experimental sequencing data.
- `dt4dds_benchmark.pipelines.Clustering` only performs clustering of a supplied sequencing dataset. This can be used to compare clustering performance across different clustering algorithms.


## Varying parameters
To automatically generate and run pipelines systematically, i.e. to vary an experimental parameter in the workflow, a data manager and a pipeline variator is needed. The data manager will handle saving the generated results, while the pipeline variator will handle generating the adjusted pipelines.

By default, a data manager based on HDF5 files is used:
```python
manager = dt4dds_benchmark.pipelines.HDF5Manager("mydata.hdf5")
```

Then, any step of the pipeline must be parameterized. For example, the error rate in the workflow:
```python
import functools
workflow = functools.partial(dt4dds_benchmark.workflows.ErrorGenerator,
    rate_deletions=0,
    rate_insertions=0,
    dropout=0,
    coverage=30
)
func_kwarg = 'rate_substitutions'
vary_range = [0.001, 0.4]
```


And a focus variator is implemented which scans this parameter across the defined range in three iterations to pinpoint the parameter value at which decoding starts to fail:
```python
variator = dt4dds_benchmark.pipelines.FocusVariator(
    manager=manager, 
    pipeline=dt4dds_benchmark.pipelines.Full, 
    fixed_kwargs={'input_file': input_path, 'clustering': clustering, 'codec': codec},
    vary_kwarg='workflow',
    func=workflow,
    func_kwarg=func_kwarg,
    vary_range=vary_range,
    metric_reversed=True, # higher error = less success
)

variator.run()
```
By default, a total of 30 iterations are performed. The file defined in the data manager will now contain the same success conditions and performance metrics as a single pipeline, see above.

## Running tests
A suite of tests for the default codecs is provided, such that successful installation of the codecs can be confirmed. These tests are based on `pytest`, and test both for encoding and decoding capability. Marks are available to restrict tests to specific codecs or tasks only. For example, to test the encoding of the DNA-RS codec, run:
```bash
pytest -v -m "codecs_rs and codecs_encoding"
```
Note that some codecs can take very long to complete their decoding tests.


# Default Codecs and Clusterers
Default wrappers for the codecs and clustering algorithms used in the publication are provided with this package. However, in order to use these, they must be installed manually from the respective sources. To simplify this, installation scripts (named install.sh) are provided in each subdirectory (e.g., [dt4dds_benchmark/codecs/bin/codec_rs/install.sh](dt4dds_benchmark/codecs/bin/codec_rs/install.sh)). 

Please note that each codec and clustering algorithm has its own individual software requirements and dependencies, which are outlined below.


## Default codecs
A total of six default codecs were used, each with selected parameters to facilitate standardization. For all codecs, bash scripts are included that facilitate the harmonization of the input and outputs of each codec. For example, some codecs generate FASTA files instead of text files or generate supplement files required for decoding. These bash scripts handle this transparently.

For some codecs, minor changes to the implementation were performed to enable their automatic and parallelized execution. This includes, for example, removal of hard-coded file paths or the exposure of codec parameters using command-line arguments. 

### DNA-Aeon by Welzel et al.
- Publication: 10.1038/s41467-023-36297-3
- Repository: https://github.com/MW55/DNA-Aeon
- Requirements: Python 3 with requirements.txt available, cmake 


### DNA Fountain by Erlich and Zielinski
- Publication: 10.1126/science.aaj2038
- Repository: https://github.com/jdbrody/dna-fountain
- Requirements: Python 3 with numpy, Cython, tqdm, scipy, reedsolo, Biopython

Please note that the repository is not the official implementation of the codec. The official implementation uses Python 2, and setting up a working environment for Python 2 with the corresponding versions of the reedsolo and scipy packages was unsuccessful. The repository listed above is a direct port to Python 3 by Yihang Du, Wenrong Wu and Justin Brody.


### DNA-RS by Heckel et al.
- Publication: 10.1038/s41596-019-0244-5, 10.1038/s41467-020-19148-3
- Repository: https://github.com/reinhardh/dna_rs_coding
- Requirements: C++ with Boost, make


### "Goldman" by Goldman et al.
- Publication: 10.1038/nature11875
- Repository: https://github.com/allanino/DNA
- Requirements: Python 2

Please note that the repository is not the official implementation of the codec. It is however the most complete, open-source implementation and was further modified to accurately reflect the expected performance.


### HEDGES by Press et al.
- Publication: 10.1073/pnas.2004821117
- Repository: https://github.com/whpress/hedges
- Requirements: Python 2

Please note that the official repository linked above has been updated with a new, pure C++ version in late 2024. The version used for the study was the previous, original version using Python-C++ bindings. Unfortunately, this previous version has been purged from the official repository. However, forks of the previous version are still available, i.e. at https://github.com/shulp2211/hedges.



### Yin-Yang by Ping et al.
- Publication: 10.1038/s43588-022-00231-2
- Repository: https://github.com/BGI-SynBio/YinYangCode
- Requirements: Python 3 with numpy


## Default clustering algorithms
A total of six default clustering algorithms were used, each with selected parameters to facilitate standardization. For most algorithms, bash scripts are included that facilitate the harmonization of their input and outputs. In addition, as most clustering algorithms only yield the sequences belonging to each clusters, a post-processing step using a multiple-sequence alignment tool (see below) is employed to generate consensus sequences for each cluster identified by the algorithms.


### "Naive" by Erlich and Zielinski
- Publication: 10.1126/science.aaj2038
- Repository: None
- Requirements: None

This is not a clustering algorithm in a strict sense, but rather a method to reduce and weigh sequencing data by compiling the set of sequencing reads, ordered by abundance. It is used in the study by Erlich and Zielinski to accelerate decoding. It is considered the base case without (real) clustering prior to decoding.



### CD-HIT by Li et al.
- Publication: 10.1093/bioinformatics/bts565
- Repository: https://github.com/weizhongli/cdhit
- Requirements: C++, make


### Clover by Qu et al.
- Publication: 10.1093/bib/bbac336
- Repository: https://github.com/Guanjinqu/Clover
- Requirements: Python 3 with requirements.txt available


### LSH by Heckel and Darestani
- Publication: 10.1038/s41467-020-19148-3
- Repository: https://github.com/MLI-lab/noisy_dna_data_storage
- Requirements: Python 3 with sklearn-bio and numpy


### MMseqs2 by Steinegger et al.
- Publication: 10.1038/nbt.3988
- Repository: https://github.com/soedinglab/MMseqs2
- Requirements: C++, cmake, make


### Starcode by Zorita et al.
- Publication: 10.1093/bioinformatics/btv053
- Repository: https://github.com/gui11aume/starcode
- Requirements: C++, make





## Default tools
Two tools are used throughout some of the default pipelines: a read merger and a multiple-sequence aligner. These are optional when implementing other codecs, workflows, and clustering algorithms. Nonetheless, these tools, or similar programs, are recommended to improve decoding performance.

### NGmerge by Gaspar
- Publication: 10.1186/s12859-018-2579-2
- Repository: https://github.com/jsh58/NGmerge
- Requirements: C++, make

This read merger is used to merge the forward and reverse reads generated by the workflows in the study. This removes adapters and reduces overall error rates in the merged reads, at least slightly.


### kalign by Lassmann et al.
- Publication: 10.1186/1471-2105-6-298
- Repository: https://github.com/TimoLassmann/kalign
- Requirements: C++, make, Python 3 with Biopython

This tool is used to perform multiple-sequence alignment of reads from the same cluster. A python-based pipeline handles invocation of kalign, and performs the generation of a consensus sequence. 



# Extending to other Codecs and Clusterers

This package is easily extended to other codecs, clustering algorithms, or workflow simulations. In all cases, invocation, as well as in- and output are handled via bash scripts. Python-level access is then faciliated through the wrappers provided by this package. Thus, tools do not need to have any Python bindings to be used with this package.

Note that all in- and output is expected to be harmonized to fully text-based formats (i.e., not FASTA, FASTQ, or similar) in order to enable plug-and-play behaviour between different pipeline elements. If your workflow, clustering algorithm, or codec does not yield a text-based format directly, simply perform this harmonization as part of the invocation scripts.

## Adding a codec
Ensure you have a directory containing the codec's executable, as well as two bash scripts: one for encoding and one for decoding. These should accept file paths to fully text-based inputs and yield fully text-based outputs (no FASTA, FASTQ, or similar) at specified file paths. The bash scripts can be parameterized with additional command-line arguments to change the codec's settings as needed. Then, create a wrapper:

```python
import dataclasses
from dt4dds_benchmark.codecs import BaseCodec
from dt4dds_benchmark.tools import SubProcess


@dataclasses.dataclass
class MyCodec(BaseCodec):

    required_files = []

    # executable paths
    command_path_encode = './to/my/codec/encode.sh'
    command_path_decode = './to/my/codec/decode.sh'

    # codec settings
    param_a: int = 1
    param_b: float = 0.1
    param_c: str = "crc"


    def _run_encoding(self, input_file: pathlib.Path, sequence_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_encode]

        # add file paths
        cmd.append(str(input_file.resolve()))
        cmd.append(str(sequence_file.resolve()))

        # add parameters
        cmd.append(str(self.param_a))
        cmd.append(str(self.param_b))
        cmd.append(str(self.param_c))

        return SubProcess(cmd, **kwargs)
        
    

    def _run_decoding(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path_decode]

        # add file paths
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add parameters
        cmd.append(str(self.param_a))
        cmd.append(str(self.param_b))
        cmd.append(str(self.param_c))
        
        return SubProcess(cmd, **kwargs)
```
Instances of this object can then be used in any pipeline, as with the default codecs.



## Adding a clustering algorithm
Ensure you have a directory containing the clusterer's executable, as well as a bash scripts to invoke the clustering. The bash file should accept a file path to fully text-based file with sequencing reads and yield a fully text-based output (no FASTA, FASTQ, or similar). The bash script can be parameterized with additional command-line arguments to change the clusterer's settings as needed. Then, create a wrapper:

```python
import dataclasses
from dt4dds_benchmark.clustering import BaseClustering
from dt4dds_benchmark.tools import SubProcess


@dataclasses.dataclass
class MyClustering(BaseClustering):

    # executable path
    command_path = './to/my/clusterer/cluster.sh'

    # clustering settings
    param_a: int = 1
    param_b: float = 0.1
    param_c: str = "crc"


    def _run_clustering(self, input_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add file paths
        cmd.append(str(input_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add parameters
        cmd.append(str(self.param_a))
        cmd.append(str(self.param_b))
        cmd.append(str(self.param_c))

        return SubProcess(cmd, **kwargs)
```
Instances of this object can then be used in any pipeline, as with the default clustering algorithms.




## Adding a workflow
Ensure you have a directory containing the workflow's executable, as well as a bash scripts for invocation. This script should accept a file path to a fully text-based file with the design sequences, and yield a fully text-based output (no FASTA, FASTQ, or similar) at the specified file path. The bash script can be parameterized with additional command-line arguments to change the workflow's settings as needed. Then, create a wrapper:

```python
import dataclasses
from dt4dds_benchmark.workflows import BaseWorkflow
from dt4dds_benchmark.tools import SubProcess


@dataclasses.dataclass
class MyCodec(BaseWorkflow):

    # executable path
    command_path = './to/my/workflow/run.sh'

    # workflow settings
    param_a: int = 1
    param_b: float = 0.1
    param_c: str = "crc"


    def _run_workflow(self, sequence_file: pathlib.Path, output_file: pathlib.Path, **kwargs):

        cmd = [self.command_path]

        # add file paths
        cmd.append(str(sequence_file.resolve()))
        cmd.append(str(output_file.resolve()))

        # add parameters
        cmd.append(str(self.param_a))
        cmd.append(str(self.param_b))
        cmd.append(str(self.param_c))

        return SubProcess(cmd, **kwargs)
```
Instances of this object can then be used in any pipeline, as with the default workflows.



# License
This project is licensed under the GPLv3 license, see [here](LICENSE).
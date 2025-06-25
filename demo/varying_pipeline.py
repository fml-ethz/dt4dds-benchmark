import dt4dds_benchmark

# enable logging to console
dt4dds_benchmark.tools.logs.setup_console()

# define the input file
input_path = dt4dds_benchmark.inputs.random_5kB
filesize = input_path.stat().st_size

# set up the codec and clustering
codec = dt4dds_benchmark.codecs.DNAFountain.high_coderate(filesize)
clustering = dt4dds_benchmark.clustering.BasicSet.default()

# define the workflow with a varying parameter
import functools
workflow = functools.partial(dt4dds_benchmark.workflows.ErrorGenerator,
    rate_deletions=0,
    rate_insertions=0,
    dropout=0,
    coverage=30
)
func_kwarg = 'rate_substitutions'
vary_range = [0.001, 0.4]

# define the data manager
manager = dt4dds_benchmark.pipelines.HDF5Manager("mydata.hdf5")

# create and run the variator to vary the workflow parameter
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
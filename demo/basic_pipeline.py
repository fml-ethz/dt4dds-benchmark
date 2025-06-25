import dt4dds_benchmark

# enable logging to console
dt4dds_benchmark.tools.logs.setup_console()

# define the input file
input_path = dt4dds_benchmark.inputs.random_5kB
filesize = input_path.stat().st_size

# set up the codec, clustering, and workflow
codec = dt4dds_benchmark.codecs.DNARS.high_coderate(filesize)
clustering = dt4dds_benchmark.clustering.BasicSet.default()
workflow = dt4dds_benchmark.workflows.ErrorGenerator(
    rate_substitutions=0.01, 
    rate_deletions=0, 
    rate_insertions=0, 
    dropout=0, 
    coverage=30
)

# create and run the pipeline
pipeline = dt4dds_benchmark.pipelines.Full(
    input_file=input_path,
    codec=codec,
    workflow=workflow,
    clustering=clustering,
)
result, performance = pipeline.run()

# print the results
print("Result:", result)
print("Performance:", performance)
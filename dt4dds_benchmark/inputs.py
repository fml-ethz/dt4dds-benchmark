import pathlib

random_5kB = (pathlib.Path(__file__).parent.parent / "input_files" / "random" / "5kB").resolve()
random_17kB = (pathlib.Path(__file__).parent.parent / "input_files" / "random" / "17kB").resolve()
random_19kB = (pathlib.Path(__file__).parent.parent / "input_files" / "random" / "19kB").resolve()

pool_5kB = (pathlib.Path(__file__).parent.parent / "input_files" / "pool" / "5kB.tar.gz").resolve()
pool_17kB = (pathlib.Path(__file__).parent.parent / "input_files" / "pool" / "17kB.tar.gz").resolve()
pool_19kB = (pathlib.Path(__file__).parent.parent / "input_files" / "pool" / "19kB.tar.gz").resolve()
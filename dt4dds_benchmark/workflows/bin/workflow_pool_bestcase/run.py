import dt4dds
import argparse
import gc
import pathlib
import sys

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run(design_file, target_folder, coverage):

    logger.info(f"Running scenario on design file {design_file.resolve()} with output folder {target_folder.resolve()}")
    
    primers_0 = ["ACACGACGCTCTTCCGATCT", "AGACGTGTGCTCTTCCGATCT"]
    primers_2 = ["AATGATACGGCGACCACCGAGATCTACACTCTTTCCCTACACGACGCTCTTCCGATCT", "CAAGCAGAAGACGGCATACGAGATCGTGATGTGACTGGAGTTCAGACGTGTGCTCTTCCGATCT"]

    # assign efficiency properties
    dt4dds.properties.set_property_settings(
        dt4dds.settings.defaults.SequenceProperties(
            efficiency_distribution='normal',
            efficiency_params={'loc': 1.0, 'scale': 0.0051},
        )
    )



    # 
    # synthesis
    # 
    seq_list = dt4dds.tools.txt_to_seqlist(design_file)
    n_seqs = len(seq_list)
    logger.info(f"Total number of sequences: {n_seqs}")

    synthesis_settings = dt4dds.settings.defaults.ArraySynthesis_Twist(
        oligo_distribution_params={'mean': 0, 'sigma': (0.27+0.30)/2},
        deletion_length_bias=None,
        deletion_read_bias=None,
    )
    array_synthesis = dt4dds.processes.ArraySynthesis(synthesis_settings)
    array_synthesis.process(seq_list)
    pool = array_synthesis.sample_by_counts(1000*n_seqs)
    pool = dt4dds.generators.attach_primers_to_pool(pool, *primers_0)
    pool.volume = 1

    # free up space
    del seq_list, array_synthesis
    gc.collect()
    logger.info("Finished synthesis")



    # 
    # PCR
    # 
    pcr_settings = dt4dds.settings.defaults.PCR_Q5()
    pcr = dt4dds.processes.PCR(pcr_settings(
        primers=primers_0,
        template_volume=1,
        volume=20,
        efficiency_mean=0.95,
        n_cycles=15,
    ))
    pool = pcr.process(pool)

    # free up space
    del pcr
    gc.collect()
    logger.info("Finished PCR 1")



    # 
    # coverage sampling
    # 
    pool = pool.sample_by_counts(coverage*n_seqs)
    pool.volume = 5


    # 
    # PCR
    # 
    pcr_settings = dt4dds.settings.defaults.PCR_Q5()
    pcr = dt4dds.processes.PCR(pcr_settings(
        primers=primers_2,
        template_volume=5,
        volume=20,
        efficiency_mean=0.95,
        n_cycles=30,
    ))
    pool = pcr.process(pool)

    # free up space
    del pcr
    gc.collect()
    logger.info("Finished PCR 2")


    # 
    # sequencing
    # 
    sbs_sequencing = dt4dds.processes.SBSSequencing(
        dt4dds.settings.defaults.iSeq100(
            output_directory=target_folder,
            n_reads=30*n_seqs,
            read_length=150,
            read_mode='paired-end',
        )
    )
    sbs_sequencing.process(pool)
    logger.info("Finished sequencing")






def parse(args):
    parser = argparse.ArgumentParser(description='Scenario: Pool')

    parser.add_argument('design_file', type=str, help='Design file to simulate')
    parser.add_argument('target_folder', type=str, help='Target folder for output')
    parser.add_argument('--coverage', '-c', type=float, help='Coverage', default=50)

    args = parser.parse_args(args)

    design_file = pathlib.Path(args.design_file)
    if not design_file.exists():
        raise FileNotFoundError(f"Design file at {args.design_file} does not exist.")
    
    target_folder = pathlib.Path(args.target_folder)
    if not target_folder.exists():
        target_folder.mkdir(parents=True)
        logger.warning(f"Target folder at {args.target_folder} did not exist and was created.")

    return run(design_file, target_folder, args.coverage)


if __name__ == "__main__":
    dt4dds.helpers.logging.default_logging()
    parse(sys.argv[1:])
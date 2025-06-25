import dt4dds
import argparse
import gc
import pathlib
import sys

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def run(design_file, target_folder, n_pcrs):

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
        deletion_length_bias=None,
        deletion_read_bias=None,
    )
    array_synthesis = dt4dds.processes.ArraySynthesis(synthesis_settings)
    array_synthesis.process(seq_list)
    pool = array_synthesis.sample_by_counts(1.4e7*n_seqs) # 100 ng ssDNA @ 200 nt divided by 72000 sequences
    pool = dt4dds.generators.attach_primers_to_pool(pool, *primers_0)
    pool.volume = 1

    # free up space
    del seq_list, array_synthesis
    gc.collect()
    logger.info("Finished synthesis")


    # 
    # master pool PCR
    # 
    pcr_settings = dt4dds.settings.defaults.PCR_Q5()
    pcr = dt4dds.processes.PCR(pcr_settings(
        primers=primers_2,
        template_volume=1,
        volume=50,
        efficiency_mean=0.95,
        n_cycles=10,
    ))
    pool = pcr.process(pool)
    pool.volume = 20

    # free up space
    del pcr
    gc.collect()
    logger.info("Finished master pool PCR")

    
    # 
    # Serial PCR
    # 
    for i in range(n_pcrs):
        pool = pool.sample_by_counts(1e6*n_seqs) # 10 ng dsDNA @ 265 nt divided by 72000 sequences
        pool.volume = 1
        pcr_settings = dt4dds.settings.defaults.PCR_Q5()
        pcr = dt4dds.processes.PCR(pcr_settings(
            primers=primers_2,
            template_volume=1,
            volume=25,
            efficiency_mean=0.95,
            n_cycles=10,
        ))
        pool = pcr.process(pool)

        # free up space
        del pcr
        gc.collect()
        logger.info(f"Finished serial PCR {i+1}")



    # 
    # sequencing
    # 
    pool = pool.sample_by_moles(0.05*20e-6)
    sbs_sequencing = dt4dds.processes.SBSSequencing(
        dt4dds.settings.defaults.iSeq100(
            output_directory=target_folder,
            n_reads=70*n_seqs, # 5 million reads divided by 72000 sequences, as in Erlich et al.
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
    parser.add_argument('--n_pcrs', '-n', type=int, help='Number of PCRs', default=5)

    args = parser.parse_args(args)

    design_file = pathlib.Path(args.design_file)
    if not design_file.exists():
        raise FileNotFoundError(f"Design file at {args.design_file} does not exist.")
    
    target_folder = pathlib.Path(args.target_folder)
    if not target_folder.exists():
        target_folder.mkdir(parents=True)
        logger.warning(f"Target folder at {args.target_folder} did not exist and was created.")

    return run(design_file, target_folder, args.n_pcrs)


if __name__ == "__main__":
    dt4dds.helpers.logging.default_logging()
    parse(sys.argv[1:])
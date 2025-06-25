import pathlib
import tarfile
import tempfile

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def files_are_equal(original_file: pathlib.Path, compare_file: pathlib.Path) -> bool:
    """ Check if two files are equal, but check contents of tar files instead of the tar file itself."""
    original_file = pathlib.Path(original_file)
    compare_file = pathlib.Path(compare_file)
    if not original_file.exists():
        logger.info(f"Original file {original_file} does not exist.")
        return False
    if not compare_file.exists():
        logger.info(f"Comparison file {compare_file} does not exist.")
        return False
    
    if compare_files(original_file, compare_file):
        logger.info(f"Files {original_file} and {compare_file} are bytewise equal.")
        return True
    elif compare_archives(original_file, compare_file):
        logger.info(f"Archives {original_file} and {compare_file} are equivalent in contents.")
        return True
    else:
        logger.info(f"Files {original_file} and {compare_file} are neither equal nor equivalent in content.")
        return False

        
                

def compare_files(original_file: pathlib.Path, compare_file: pathlib.Path) -> bool:
    """ Check if two files are equal by bytewise comparison. Ignores if the file to compare is longer than the original file."""
    with open(original_file, "rb") as f, open(compare_file, "rb") as g:
        i = 0
        while (byte := f.read(1)):
            i += 1
            try:
                other_byte = g.read(1)
                if byte != other_byte:
                    logger.info(f"Files are different at byte {i}: {byte} vs. {other_byte}")
                    return False
            except:
                return False
    return True


def compare_archives(original_file: pathlib.Path, compare_file: pathlib.Path) -> bool:
    """ Check if two archives are equal by comparing their contents."""
    # create temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # create subdirectories
        tmpdir = pathlib.Path(tmpdir)
        (tmpdir / "in").mkdir()
        (tmpdir / "out").mkdir()

        # extract both the input and the output files
        try:
            tar = tarfile.open(original_file, "r:gz")
            tar.extractall(tmpdir / "in")
            tar.close()
        except Exception as e:
            logger.info(f"Original file could not be extracted: {e}.")
            return False
        try:
            tar = tarfile.open(compare_file, "r:gz")
            tar.extractall(tmpdir / "out")
            tar.close()
        except Exception as e:
            logger.info(f"Comparison file could not be extracted: {e}.")
            return False

        # compare all the files
        for file in (tmpdir / "in").rglob("*"):
            other_file = (tmpdir / "out" / file.relative_to(tmpdir / "in"))
            if not other_file.exists():
                logger.info(f"File {file} does not exist as {other_file}.")
                return False
            if file.is_file():
                file_is_equal = compare_files(file, other_file)
                logger.info(f"File {file} is equal to {other_file}: {file_is_equal}")
                if not file_is_equal:
                    return False
        return True
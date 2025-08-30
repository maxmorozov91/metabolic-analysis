import os
import subprocess as sp
from pathlib import Path
from typing import Literal

from src.services.common import logger, timing_decorator
from src.services.constants import MODE_DICT, APPLYABLE_FILETYPES


@timing_decorator
def analyze_sample(
        sample: str,
        /,
        *,
        sample_input_dir: Path,
        sample_result_dir: Path,
        db_dir: Path,
        gff_type: Literal["prodigal", "NCBI_prok"],
        threads: str
) -> bool:
    """
    Анализирует все файлы одного образца.

    :param sample: имя образца
    :param sample_input_dir: путь к папке с исходными файлами образца для анализа
    :param sample_result_dir: путь к папке с результатами анализа образца
    :param db_dir: путь к папке с БД
    :param gff_type: тип gff
    :param threads: количество потоков для параллельных вычислений
    :return: флаг успешности анализа образца
    """
    # список файлов, которые подлежат анализу
    files = [file for file in os.listdir(sample_input_dir) if file.split(".")[-1] in APPLYABLE_FILETYPES]
    files.sort()

    result_flags = dict() # словарь для хранения флагов успешности анализа файлов

    for filename in files:
        logger.info(f"Start a substrat prediction for {filename}")

        substract_predicted = predict_substrate(
            filename,
            db_dir=db_dir,
            sample_input_dir=sample_input_dir,
            sample_result_dir=sample_result_dir,
            gff_type=gff_type,
            threads=threads
        )

        result_flags[filename] = substract_predicted

    if all(result_flags.values()):
        logger.info(f"The sample analyzed successfully: {sample}")
        return True

    logger.warning(
        "Analysis failed for the next files:\n"
        ",\n".join([item[0] for item in result_flags.items() if not item[1]])
    )

    return False


@timing_decorator
def predict_substrate(
        filename: str,
        /,
        *,
        db_dir: Path,
        sample_input_dir: Path,
        sample_result_dir: Path,
        gff_type: Literal["prodigal", "NCBI_prok"],
        threads: str
) -> bool:
    """
    Прогнозирует субстрат для образца из одного файла.

    :param file_name: название файла с исходными данными
    :param input_filepath: полный путь к файлу с исходными данными
    :param filetype: тип файла с исходными данными
    :param db_dir: путь к папке с БД
    :param gff_type: тип gff
    :param sample_result_dir: путь к папке для сохранения результатов
    :param threads: количество потоков для параллельных вычислений
    :return: флаг успешности анализа
    """
    filetype = filename.split(".")[-1]  # тип файла по его расширению (fna, faa, fasta и т.п.)

    input_filepath = sample_input_dir / filename  # полный путь к файлу для анализа
    file_result_dir = sample_result_dir / filename  # полный путь к папке для сохранения результатов анализа файла

    mode = MODE_DICT[filetype]
    gff_filepath = sample_input_dir / (".".join(filename.split(".")[:-1]) + ".gff")  # полный путь к файлу gff

    command = [
        "run_dbcan",
        "easy_substrate",
        "--db_dir", db_dir,
        "--mode", mode,
        "--input_raw_data", input_filepath,
        "--output_dir", file_result_dir,
        "--threads", threads,
        "--gff_type", gff_type,
        "--input_gff", gff_filepath,
    ]

    logger.debug(
        "A command for the execution:\n"
        f"{command}"
    )

    try:
        sp.run(command, check=True)
        logger.info(f"Substrate predicted successfully for {filename}.")
        return True
    
    except sp.CalledProcessError as e:
        logger.error(f"Error during the substrate prediction for {filename}", exc_info=True)
        return False

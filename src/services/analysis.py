import os
import subprocess as sp
from pathlib import Path
from typing import Literal

from src.services.common import logger
from src.services.constants import MODE_DICT, APPLYABLE_FILETYPES


def analyze_sample(
        *,
        sample_name: str,
        sample_input_dir: str,
        sample_result_dir: str,
        db_dir: str,
        gff_type: Literal["prodigal", "NCBI_prok"],
        threads: str
) -> bool:
    """
    Анализирует все файлы одного образца.

    :param sample_name: имя образца
    :param sample_input_dir: путь к папке с исходными файлами образца для анализа
    :param sample_result_dir: путь к папке с результатами анализа образца
    :param db_dir: путь к папке с БД
    :param gff_type: тип gff
    :param threads: количество потоков для параллельных вычислений
    :return: флаг успешности анализа образца
    """
    result_flags = dict() # словарь для хранения флагов успешности анализа файлов

    for filename in os.listdir(sample_input_dir):
        # определим тип файла по его расширению (fna, faa, fasta и т.п.)
        filetype = filename.split(".")[-1]

        if not filetype in APPLYABLE_FILETYPES:
            logger.warning(f"Skip analysis for {filename}")
            continue

        input_filepath = sample_input_dir + "/" + filename

        substract_predicted = predict_substrate(
            filename=filename,
            input_filepath=input_filepath,
            filetype=filetype,
            db_dir=db_dir,
            gff_type=gff_type,
            sample_result_dir=sample_result_dir,
            threads=threads
        )

        result_flags[filename] = substract_predicted

    if all(result_flags.values()):
        logger.info(f"Sample analyzed successfully: {sample_name}")
        return True

    logger.warning(
        "Analysis failed for the next files:\n"
        ",\n".join([item[0] for item in result_flags.items() if not item[1]])
    )

    return False


def predict_substrate(
        *,
        filename: str,
        input_filepath: str,
        filetype: str,
        db_dir: str,
        gff_type: Literal["prodigal", "NCBI_prok"],
        sample_result_dir: str,
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
    mode = MODE_DICT[filetype]
    gff_filepath = ".".join(input_filepath.split(".")[:-1]) + ".gff"

    command = [
        "run_dbcan",
        "easy_substrate",
        "--db_dir", db_dir,
        "--mode", mode,
        "--input_raw_data", input_filepath,
        "--output_dir", sample_result_dir,
        "--threads", threads,
        "--gff_type", gff_type,
        "--input_gff", gff_filepath,
    ]

    try:
        sp.run(command, check=True)
        logger.debug(f"Substrate predicted successfully for {filename}.")
        return True
    
    except sp.CalledProcessError as e:
        logger.error(f"Error during substrate prediction for {filename}", exc_info=True)
        return False

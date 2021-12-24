from modules.fare_filing import FareFiling
import logging

def setup_logger():
    # create logger
    logger = logging.getLogger(__name__)
    logger.setLevel('DEBUG')

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter  = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    return logger

if __name__ == '__main__':
    logger = setup_logger()

    logger.info('Initializing App..')
    # gg = FareFiling(logger)
    gg = FareFiling()

    logger.info('Importing app config..')
    gg.import_config()

    logger.info('Backing up previous Excel input..')
    gg.backup_input(gg.df_input)

    logger.info('Generating fares..')
    fares = gg.gen_fares()

    logger.info('Creating output..')
    gg.create_output(fares)

    logger.info('Run complete!')
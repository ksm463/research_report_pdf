import logging

def setup_logger(log_path, logger_name=__name__) -> logging.Logger:

    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        filename=log_path
    )

    logger = logging.getLogger(logger_name)

    logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
    
    return logger

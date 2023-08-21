import logging
import os
import sys


def main():
    logger.info('investments')

    messages = src.cases.interface.Interface().exc()
    logger.info(messages)

    messages = src.adjust.revalue.Revalue().exc()
    logger.info(messages)

    src.metrics.overall.Overall(storage='').exc()

    # interface = src.algorithms.interface.Interface()
    # interface.graphs()


if __name__ == '__main__':
    root = os.getcwd()
    sys.path.append(root)
    sys.path.append(os.path.join(root, 'src'))

    # Threads
    os.environ['NUMEXPR_MAX_THREADS'] = '8'

    # logging
    logging.basicConfig(level=logging.INFO,
                        format='\n\n%(message)s\n%(asctime)s.%(msecs)03d',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger(__name__)

    # classes
    import src.cases.interface
    import src.adjust.revalue
    import src.algorithms.interface
    import src.metrics.overall

    main()

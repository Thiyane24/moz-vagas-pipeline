from pipeline.scraper import Scraper
from pipeline.transform import transformar
from pipeline.storage import storageS3
import logging

logger = logging.getLogger(__name__)



if __name__ == '__main__':
    logger.info(f"iniciando o pipeline: ")
    print("Scraping")
    print('\n')
    Scraper().run()
    
    print('\n')
    print("Transforming")
    transformar()
    
    print("\n")
    print("Loading")
    storageS3()
    
    print("\n")
    print("Pipeline finished successfully")
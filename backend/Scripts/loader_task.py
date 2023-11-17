from datetime import datetime
import sys
from time import sleep
from cbr_client.currency_loader import CurrencyLoader
from database.accessor import PostgresClient
import logging
from logging import Logger, getLogger


class LoaderTask:
    loader: CurrencyLoader | None = None
    db_client: PostgresClient | None = None
    logger: Logger | None = None
    check_interval_secs = 300

    def __init__(self):
        self.loader = CurrencyLoader()
        self.db_client = PostgresClient()
        self.db_client.connect()

        logging.basicConfig(stream=sys.stdout, level=logging.INFO)
        self.logger = getLogger('updater')

    def run_task(self):
        while True:
            last_date = self.db_client.get_last_value_date()
            now_date = datetime.utcnow().date()
            self.logger.info(f'last date: {last_date} | now date {now_date}')
            if not last_date or now_date > last_date:
                self.loader.load_data()
                self.logger.info(f'updated data for {now_date}')
            else:
                self.logger.info(f'last date is actual | sleep for'
                                 f' {self.check_interval_secs}')
                sleep(self.check_interval_secs)


if __name__ == '__main__':
    try:
        task = LoaderTask()
        task.run_task()
    except (KeyboardInterrupt, Exception):
        task.db_client.disconnect()

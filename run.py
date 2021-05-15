from application.use_cases.upwork.tasks import scan_upwork
import logging


def main(_async=False):
    """Main function.
    
    NOTE: _async functions have more control over exceptions and retries policies,
    prefer to use then. 
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s:%(name)s:%(levelname)s:%(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.FileHandler('./log/upwork_scraper.log'),
            logging.StreamHandler()
        ]
    )

    if not _async:
        scan_upwork({'username': 'bobsuperworker', 'password': 'Argyleawesome123!'})
    else:
        scan_upwork.delay({'username': 'bobsuperworker', 'password': 'Argyleawesome123!'})
    

if __name__ == "__main__":
    main(_async=False)
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ErrorInResponseException, WebDriverException
from application.exceptions import CaptchaException, ElementTookTooLongToLoad, LoginNotCompleted
from application.repository import JSONPersistence
from application.scanners.upwork import UpWorkScanner
from application.celery import app
from celery.utils.log import get_task_logger


logger = get_task_logger(__name__)


@app.task(
    bind=True,
    name='application.use_cases.scan_upwork',
    default_retry_delay=30 * 60,  # retries every 30min
    retry_kwargs={'max_retries': 10}
)
def scan_upwork(self, user_credentials):
    try:

        logger.info("starting task to scan upwork main page")
        
        scanner = UpWorkScanner(settings={"user_auth": user_credentials})
        scanner.login()
        user_data = scanner.scan_main_page()
        scanner.scan_profile_page() 
        scanner.scan_contact_info(close_driver=True) # Closes the drive in the last scan
        output = scanner.build_full_scan_data().dict()

        logger.info("saving scan from upwork main page")
        
        try:
            JSONPersistence.save({**output}, user_data["uuid"])
        except Exception as exc:
            logger.error(
                "error while saving the output file, scan will retry, error", repr(exc))
            raise self.retry(exc=exc)

    except CaptchaException as exc:
        logger.exception(
            "captcha error while scanning main portal, task will retry")
        raise self.retry(exc=exc)

    except ElementTookTooLongToLoad as exc:
        logger.exception("poor connection with the portal, task will retry")
        raise self.retry(exc=exc)

    except LoginNotCompleted as exc:
        logger.exception(
            "could not complete the login of user, task will retry")
        raise self.retry(exc=exc)
    
    except NoSuchElementException as exc:
        logger.warning(
            "some element was not loaded properly, due to either slow loading or removal, beware! task will retry")
        raise self.retry(exc=exc)
    
    except TimeoutException as exc:
        logger.warning(
            "timeout while trying to connect with the host, will retry")
        raise self.retry(exc=exc)
    
    except ErrorInResponseException as exc:
        logger.warning(
            "server side error while connecting with the host, will retry")
        raise self.retry(exc=exc)
    
    except WebDriverException as exc:
        logger.exception(
            "unexpected webdriver error while connecting with the host, will not retry. error %s", repr(exc))
        raise 

    except Exception as exc:
        logger.critical(
            "Unexpected error while parsing task, task will not retry. error %s", repr(exc))
        raise

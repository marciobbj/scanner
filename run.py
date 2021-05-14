from application.use_cases.upwork.tasks import scan_upwork_main_page


def main(async=False):
    if not async:
        scan_upwork_main_page({'username': 'bobsuperworker', 'password': 'Argyleawesome123!'})
    else:
        scan_upwork_main_page.delay({'username': 'bobsuperworker', 'password': 'Argyleawesome123!'})
    

if __name__ == "__main__":
    main(async=False)
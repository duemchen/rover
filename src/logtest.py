from logconfig import log

if __name__ == '__main__':

    to_log = 'Hello world!'
    print(f"About to log {to_log}")
    log.info(to_log)

    warning_to_log = 'This is a warning'
    print(f"About to log {warning_to_log}")
    log.warning(warning_to_log)
    log.debug('debug meldung')
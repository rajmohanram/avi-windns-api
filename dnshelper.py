from logging.config import dictConfig
import logging
from config import LogConfig

# Logging config
dictConfig(LogConfig().dict())
logger = logging.getLogger("windnsapi")


# check existence of record
def check_records(client, zone, host):
    pshell_cmd = "Get-DnsServerResourceRecord -ZoneName " + zone + " -RRType A -Name " + host
    output, streams, had_errors = client.execute_ps(pshell_cmd)
    if output:
        logger.info(f'Record already exists...')
        return True
    else:
        logger.info(f'Record does not exist...')
        return False


# Delete DNS A Record
def delete_dns_record(client, zone, host):
    logger.info('Checking if record already exist...')
    record_exist = check_records(client, zone, host)
    if record_exist:
        logger.info(f'Deleting existing record...')
        pshell_cmd = "Remove-DnsServerResourceRecord -ZoneName  " + zone + " -Name " + host + " -RRType A -Force"
        output, streams, had_errors = client.execute_ps(pshell_cmd)
        if not had_errors:
            logger.info(f'Deleted the record...')
            return True
        else:
            logger.info(f'Record deletion failed...')
            return False
    else:
        logger.info(f'Record deletion not required...')
        return True


# Add DNS A Record
def add_dns_record(client, zone, host, ip):
    logger.info('Checking if record already exist...')
    record_exist = check_records(client, zone, host)
    if record_exist:
        logger.info(f'Deleting existing record...')
        pshell_cmd = "Remove-DnsServerResourceRecord -ZoneName " + zone + " -Name " + host + " -RRType A -Force"
        output, streams, had_errors = client.execute_ps(pshell_cmd)

    # Add DNS record
    pshell_cmd = "Add-DnsServerResourceRecordA -ZoneName " + zone + " -Name " + host + " -IPv4Address " + ip
    output, streams, had_errors = client.execute_ps(pshell_cmd)
    if not had_errors:
        logger.info(f'Added new record...')
        return True
    else:
        logger.info(f'Record addition failed...')
        return False


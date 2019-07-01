import time
import os
import boto3
import logging


class Formatter(object):

    def __init__(self, logger=logging.getLogger(__name__)):
        self.logger = logger
        self.default_format = "email"

    def formatForEmail(self, message):
        hostname, output, url = message
        body_summary = []
        warning_text = ""

        subject = 'Scan results for {}'.format(hostname)
        body_url_text = 'Download link for scan results (valid up to 24 hours): {}'.format(url)
        for scan, success in output.items():
            if "tcp" in scan:
                scan_type_summary = 'Port scan is '
                body_summary.append(
                    scan_type_summary + 'SUCCESSFUL' if success else scan_type_summary + 'UNSUCCESSFUL'
                )
            if "tenable" in scan:
                scan_type_summary = 'Tenable.io scan is '
                body_summary.append(
                    scan_type_summary + 'SUCCESSFUL' if success else scan_type_summary + 'UNSUCCESSFUL'
                )
            if "dir" in scan:
                scan_type_summary = 'Directory enumeration scan is '
                body_summary.append(
                    scan_type_summary + 'SUCCESSFUL' if success else scan_type_summary + 'UNSUCCESSFUL'
                )
            if "ssh" in scan:
                scan_type_summary = 'SSH Observatory scan is '
                body_summary.append(
                    scan_type_summary + 'SUCCESSFUL' if success else scan_type_summary + 'UNSUCCESSFUL'
                )
            if "tls" in scan:
                scan_type_summary = 'TLS Observatory scan is '
                body_summary.append(
                    scan_type_summary + 'SUCCESSFUL' if success else scan_type_summary + 'UNSUCCESSFUL'
                )
            if "http" in scan:
                scan_type_summary = 'HTTP Observatory scan is '
                body_summary.append(
                    scan_type_summary + 'SUCCESSFUL' if success else scan_type_summary + 'UNSUCCESSFUL'
                )
            if "web" in scan:
                scan_type_summary = 'Web search is '
                body_summary.append(
                    scan_type_summary + 'SUCCESSFUL' if success else scan_type_summary + 'UNSUCCESSFUL'
                )

        if "UNSUCCESSFUL" in str(body_summary):
            warning_text = 'Not all scans successfully ran. You should run them manually.'

        body_text = (body_url_text, body_summary, warning_text)

        return subject, body_text

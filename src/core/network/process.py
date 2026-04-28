# -*- coding: utf-8 -*-

"""
    Process runner for network transports.
"""

import subprocess

from .exceptions import NetworkTransportError


class ProcessRunner(object):

    """Process runner wrapper."""

    def start_persistent(self, command):
        """
        Start a long-running process.

        :param list[str] command:
        :raise NetworkTransportError:
        :return: subprocess.Popen
        """

        try:
            return subprocess.Popen(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
        except OSError as error:
            raise NetworkTransportError(error)

    def run(self, command, timeout=30):
        """
        Run a short-lived command.

        :param list[str] command:
        :param int timeout:
        :raise NetworkTransportError:
        :return: subprocess.CompletedProcess
        """

        try:
            return subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
                check=True
            )
        except (OSError, subprocess.SubprocessError) as error:
            raise NetworkTransportError(error)

    def stop(self, process, timeout=5):
        """
        Stop a persistent process.

        :param subprocess.Popen|object process:
        :param int timeout:
        :raise NetworkTransportError:
        :return: None
        """

        if process is None:
            return

        try:
            if process.poll() is not None:
                return

            process.terminate()
            try:
                process.wait(timeout=timeout)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=timeout)
        except (OSError, subprocess.SubprocessError) as error:
            raise NetworkTransportError(error)
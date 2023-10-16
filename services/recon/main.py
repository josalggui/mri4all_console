import sys

sys.path.append("/opt/mri4all/console/external/")

import signal
import asyncio
import time

import common.logger as logger
import common.runtime as rt
import common.helper as helper

rt.set_service_name("recon")
log = logger.get_logger()

from common.version import mri4all_version
import common.queue as queue
from common.constants import *

main_loop = None  # type: helper.AsyncTimer # type: ignore


def process_reconstruction(scan_name: str) -> bool:
    log.info("Performing reconstruction...")
    # TODO: Process actual case!
    time.sleep(2)
    log.info("Reconstruction completed")

    if not queue.move_task(
        mri4all_paths.DATA_RECON + "/" + scan_name, mri4all_paths.DATA_COMPLETE
    ):
        log.error(
            f"Failed to move scan {scan_name} to completed folder. Critical Error."
        )
    return True


def run_reconstruction_loop():
    """
    Main processing function that is called continuously by the main loop
    """

    selected_scan = queue.get_scan_ready_for_recon()
    if selected_scan:
        log.info(f"Reconstructing scan: {selected_scan}")
        rt.set_current_task_id(selected_scan)

        if not queue.move_task(
            mri4all_paths.DATA_QUEUE_RECON + "/" + selected_scan,
            mri4all_paths.DATA_RECON,
        ):
            log.error(
                f"Failed to move scan {selected_scan} to recon folder. Unable to run reconstruction."
            )
        else:
            process_reconstruction(selected_scan)

        rt.clear_current_task_id()

    if helper.is_terminated():
        return


async def terminate_process(signalNumber, frame) -> None:
    """
    Triggers the shutdown of the service
    """
    log.info("Shutdown requested")
    # Note: main_loop can be read here because it has been declared as global variable
    if "main_loop" in globals() and main_loop.is_running:
        main_loop.stop()
    helper.trigger_terminate()


def prepare_recon_service() -> bool:
    """
    Prepare the reconstruction service
    """
    log.info("Preparing for reconstruction...")

    if not queue.check_and_create_folders():
        log.error("Failed to create data folders. Unable to start acquisition service.")
        return False

    # Clear the data acquisition folder, in case a previous instance has crashed. If a task
    # is found there, move it to the failure folder (probably the previous instance crashed)
    if not queue.clear_folder(mri4all_paths.DATA_ACQ, mri4all_paths.DATA_FAILURE):
        return False

    return True


def run():
    log.info(f"-- MRI4ALL {mri4all_version.get_version_string()} --")
    log.info("Reconstruction service started")

    if not prepare_recon_service():
        log.error("Error while preparing acquisition service. Terminating.")
        sys.exit(1)

    # Register system signals to be caught
    signals = (signal.SIGTERM, signal.SIGINT)
    for s in signals:
        helper.loop.add_signal_handler(
            s, lambda s=s: asyncio.create_task(terminate_process(s, helper.loop))
        )

    # Start the timer that will periodically trigger the scan of the task folder
    global main_loop
    main_loop = helper.AsyncTimer(0.1, run_reconstruction_loop)
    try:
        main_loop.run_until_complete(helper.loop)
    except Exception as e:
        log.exception(e)
    finally:
        # Finish all asyncio tasks that might be still pending
        remaining_tasks = helper.asyncio.all_tasks(helper.loop)  # type: ignore[attr-defined]
        if remaining_tasks:
            helper.loop.run_until_complete(helper.asyncio.gather(*remaining_tasks))

    log.info("Reconstruction service terminated")
    log.info("-------------")
    sys.exit()


if __name__ == "__main__":
    run()

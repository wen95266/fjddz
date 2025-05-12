# telegram_doudizhu_bot/utils/scheduler_utils.py
from typing import Callable, Any, Optional
from datetime import timedelta

from telegram.ext import ContextTypes, JobQueue

from utils.helpers import get_job_name # For consistent job naming

def set_job(
    context: ContextTypes.DEFAULT_TYPE,
    job_name: str,
    interval_seconds: int,
    callback_function: Callable,
    job_context_data: Optional[Any] = None, # Data to pass to the job callback
    run_once: bool = True
) -> None:
    """Adds or replaces a job in the JobQueue."""
    job_queue: JobQueue = context.job_queue
    if not job_queue:
        print(f"Error: JobQueue not available in context for job '{job_name}'.")
        return

    # Remove existing job with the same name before scheduling a new one
    # to prevent duplicates or issues if job properties change.
    clear_job(context, job_name)

    if run_once:
        job_queue.run_once(
            callback_function,
            when=timedelta(seconds=interval_seconds),
            data=job_context_data,
            name=job_name
        )
    else: # For recurring jobs
        job_queue.run_repeating(
            callback_function,
            interval=timedelta(seconds=interval_seconds),
            first=timedelta(seconds=interval_seconds), # Start after one interval
            data=job_context_data,
            name=job_name
        )
    # print(f"Job '{job_name}' scheduled to run {'once ' if run_once else 'every '}{interval_seconds}s.")


def clear_job(context: ContextTypes.DEFAULT_TYPE, job_name: str) -> None:
    """Removes a job from the JobQueue by its name."""
    job_queue: JobQueue = context.job_queue
    if not job_queue:
        print(f"Error: JobQueue not available in context for clearing job '{job_name}'.")
        return

    current_jobs = job_queue.get_jobs_by_name(job_name)
    if not current_jobs:
        # print(f"No job found with name '{job_name}' to clear.")
        return
    for job in current_jobs:
        job.schedule_removal()
        # print(f"Job '{job_name}' scheduled for removal.")

# Example usage in a handler:
# from utils.scheduler_utils import set_job, clear_job
# from jobs.game_jobs import bid_timeout_callback # The actual function for the job
# from utils.helpers import get_job_name
# from constants import JOB_TYPE_BID

# # To set a bid timeout for a player:
# chat_id = game.chat_id
# player_id = player.user_id
# job_name = get_job_name(JOB_TYPE_BID, chat_id, player_id)
# job_data = {"chat_id": chat_id, "user_id": player_id, "game_id": game.game_id_if_any} # Pass necessary data
# set_job(context, job_name, BID_TIMEOUT_SECONDS, bid_timeout_callback, job_data)

# # To clear it (e.g., when player bids):
# clear_job(context, job_name)

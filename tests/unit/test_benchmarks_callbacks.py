import threading
import time

from benchmarks.callbacks import load_app


def test_work_is_cpu_time_while_other_threads_hold_the_gil():
    stop = threading.Event()

    def spin():
        while not stop.is_set():
            pass

    other = threading.Thread(target=spin)
    other.start()
    try:
        before = time.thread_time()
        load_app._burn(0.1)  # pylint: disable=protected-access
        used = time.thread_time() - before
    finally:
        stop.set()
        other.join()
    assert used >= 0.1

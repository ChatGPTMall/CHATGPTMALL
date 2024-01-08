from django.db import connection
from threading import Thread


class DbThread(Thread):

    def run(self):
        super().run()
        connection.close()


def run_in_thread(target, args: tuple):
    """
    Run target function as thread
    """
    DbThread(target=target, args=args).start()
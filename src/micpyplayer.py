#!/usr/bin/env python3

import curses
import os
import sys
import logging
import threading
import time

from pathlib import Path
import track_player
from input_class import InputClass
from screen_painter import ScreenPainter


main_box = None

def main(stdscr):
    logger = logging.getLogger("micpyplayer")
    logger.setLevel(logging.DEBUG)

    known_extensions = '.mp3', '.wav', '.aac', '.aif', '.ogg', '.wma', '.flac', '.m4a', '.Mp3', '.MP3'

    arg_path = ""
    if len(sys.argv) < 2:
        arg_path = os.getcwd()
    else:
        arg_path = sys.argv[1]

    current_app_state = []
    current_app_state.append(AppState(Path(arg_path), 0, 1))
    current_app_state.append(threading.Lock())

    ch = logging.FileHandler("output_log.txt")
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s -%(relativeCreated)6d- %(threadName)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    curses.noecho()
    curses.curs_set(0)
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, 77)
    screen.refresh()
    main_box = MainBox(stdscr, current_app_state)
    # max_y, max_x = stdscr.getmaxyx()
    our_player = track_player.TrackPlayer(logger)
    thread_started = False
    refresher = ScreenPainter(stdscr, main_box, our_player, known_extensions, current_app_state, logger)

    while not current_app_state[0].exit_requested:
        logger.debug("cyclic refresh")
        refresher.refresh()

        if not thread_started:
            t1 = InputClass(our_player, stdscr, refresher, current_app_state, logger)
            t1.start()
            logger.debug("thread started")
            thread_started = True

        time.sleep(0.48)


class AppState(object):
    def __init__(self, curdir_path, offset_filelist, selected_line):
        self.curdir_path = curdir_path
        self.offset_filelist = offset_filelist
        self.selected_line = selected_line
        self.coord_max_y = None
        self.file_list_in_current_dir = None
        self.exit_requested = False
        self.show_menu = False



class MainBox(object):
    def __init__(self, stdscr, current_application_state):
        self.current_application_state = current_application_state
        self.update(stdscr)
        self.menu_x_size = 20
        self.min_x = None
        self.max_y = None
        self.max_x = None

    def update(self, stdscr):
        if self.current_application_state[0].show_menu:
            self.min_x = self.menu_x_size
        else:
            self.min_x = 1

        self.max_y, self.max_x = stdscr.getmaxyx()


curses.wrapper(main)

#!/usr/bin/env python3

import curses
import os
import sys
import logging
import threading
import time

from pathlib import Path
import player

curdir_path = None
offset_filelist = 0
selected_line = 1
coord_max_y = None
current_list_dir = None

logger = logging.getLogger("micpyplayer")
logger.setLevel(logging.DEBUG)


def main(stdscr):

    global curdir_path
    global offset_filelist
    global selected_line
    global coord_max_y
    global current_list_dir
    known_extensions = '.mp3', '.wav', '.aac', '.aif', '.ogg', '.wma'

    arg_path = ""
    if len(sys.argv) < 2:
        arg_path = os.getcwd()
    else:
        arg_path = sys.argv[1]

    curdir_path = Path(arg_path)

    ch = logging.FileHandler("output_log.txt")
    ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    curses.noecho()
    curses.curs_set(0)
    screen = stdscr.subwin(23, 79, 0, 0)
    screen.box()
    screen.hline(2, 1, curses.ACS_HLINE, 77)
    screen.refresh()
    max_y, max_x = stdscr.getmaxyx()
    our_player = player.Player(logger)
    thread_started = False
    refresher = ScreenRefresher(
        stdscr, max_y, max_x, our_player, known_extensions)

    while 1:
        refresher.refresh()

        if not thread_started:
            t1 = threading.Thread(target=get_input, args=(
                our_player, stdscr, refresher))
            t1.start()
            logger.debug("thread started")
            thread_started = True

        time.sleep(0.5)


class ScreenRefresher(object):
    def __init__(self, stdscr, max_y, max_x, our_player, known_extensions):
        self.stdscr = stdscr
        self.max_y = max_y
        self.max_x = max_x
        self.our_player = our_player
        self.known_extensions = known_extensions

    def refresh(self):
        global curdir_path
        global offset_filelist
        global selected_line
        global coord_max_y
        global current_list_dir

        logger.debug("refresh")
        # # Clear screen
        self.stdscr.clear()
        self.stdscr.border(0, 0, 0, 0, 0, 0, 0, 0)

        coord_max_y = self.max_y - 5

        self.stdscr.hline(self.max_y - 4, 1, curses.ACS_HLINE, self.max_x - 2)

        # print status for our_player
        line_1, line_2, progress_bar_bars = self.our_player.get_interface_lines(
            self.max_x)
        self.stdscr.addstr(self.max_y - 3, 1, line_1[:self.max_x - 3])
        line_2_and_bars = line_2[:progress_bar_bars] + \
            ((progress_bar_bars-len(line_2))*" ")
        self.stdscr.addstr(self.max_y - 2, 1, line_2[:self.max_x - 3])
        if progress_bar_bars > 0:
            self.stdscr.addstr(
                self.max_y - 2, 1, line_2_and_bars[:self.max_x - 3], curses.A_REVERSE)

        # print current path
        arg_path_print = str(curdir_path)[max(
            0, (len(str(curdir_path)) + 4) - self.max_x):]

        self.stdscr.addstr(0, int(self.max_x / 2) - int(((len(arg_path_print) + 2) / 2)),
                           "|" + arg_path_print + "|")

        current_list_dir = [s for s in os.listdir(str(curdir_path))
                            if (s.endswith(self.known_extensions) or
                                os.path.isdir(str(curdir_path) + "/" + s))
                            and not s.startswith(".")]

        current_list_dir.insert(0, "..")

        for line, f in enumerate(current_list_dir[offset_filelist:coord_max_y
                                                  + offset_filelist]):

            if curdir_path.joinpath(Path(f)).is_dir() and line > 0:
                f = f + "/"
            # coloring selection
            if selected_line == 1 + line:
                self.stdscr.addstr(
                    1 + line, 1, f[:self.max_x - 2], curses.A_REVERSE)
            else:
                self.stdscr.addstr(1 + line, 1, f, 0)

        self.stdscr.refresh()


def get_input(our_player, stdscr, refresher):

    logger.debug("inside thread ")
    global curdir_path
    global offset_filelist
    global selected_line
    global coord_max_y
    global current_list_dir
    logger.debug("curdir path " + str(curdir_path))

    while True:
        got_key = stdscr.getch()
        if got_key == curses.KEY_UP:
            logger.debug("key up")
            if offset_filelist > 0 and selected_line == 1:
                offset_filelist = offset_filelist - 1
            else:
                selected_line = max(1, selected_line - 1)

        elif got_key == curses.KEY_DOWN:
            logger.debug("key down")
            # if we are at the last entry and there still are entries
            if (coord_max_y + offset_filelist) < len(current_list_dir) \
                    and selected_line == coord_max_y:
                offset_filelist = offset_filelist + 1
            else:
                selected_line = min(min(coord_max_y, len(
                    current_list_dir)), selected_line + 1)
            # selected_line = min(coord_max_y, selected_line + 1)
        elif got_key == curses.KEY_RIGHT:
            logger.debug("key right")
            joined_path = curdir_path.joinpath(
                Path(current_list_dir[selected_line + offset_filelist - 1]))
            if selected_line == 1:
                offset_filelist = 0
                curdir_path = curdir_path.parent
            elif joined_path.is_dir():
                offset_filelist = 0
                curdir_path = joined_path
                selected_line = 1
            else:
                our_player.play(joined_path)
        refresher.refresh()
    # return curdir_path, offset_filelist, selected_line


curses.wrapper(main)

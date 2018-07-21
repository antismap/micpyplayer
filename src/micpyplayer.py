#!/usr/bin/env python3

import curses
import os
import sys
import logging
import threading
import time

from pathlib import Path
import track_player
import play_queue

curdir_path = None
offset_filelist = 0
selected_line = 1
coord_max_y = None
file_list_in_current_dir = None
exit_requested = False
logger = logging.getLogger("micpyplayer")
logger.setLevel(logging.DEBUG)
show_menu = False
main_box = None


def main(stdscr):

    global curdir_path
    global offset_filelist
    global selected_line
    global coord_max_y
    global file_list_in_current_dir
    global exit_requested
    global main_box
    known_extensions = '.mp3', '.wav', '.aac', '.aif', '.ogg', '.wma', '.flac', '.m4a', '.Mp3', '.MP3'

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
    main_box = MainBox(stdscr)
   # max_y, max_x = stdscr.getmaxyx()
    our_player = track_player.TrackPlayer(logger)
    thread_started = False
    refresher = ScreenPainter(
        stdscr, main_box, our_player, known_extensions)

    while not exit_requested:
        refresher.refresh()

        if not thread_started:
            t1 = threading.Thread(target=get_input, args=(
                our_player, stdscr, refresher))
            t1.start()
            logger.debug("thread started")
            thread_started = True

        time.sleep(0.48)


class MainBox(object):
    def __init__(self, stdscr):
        self.update(stdscr)
        self.menu_x_size = 20

    def update(self, stdscr):
        global show_menu
        if show_menu:
            self.min_x = self.menu_x_size
        else:
            self.min_x = 1

        self.max_y, self.max_x = stdscr.getmaxyx()


class ScreenPainter(object):

    def __init__(self, stdscr, main_box, our_player, known_extensions):
        self.stdscr = stdscr
        self.main_box = main_box
        self.our_player = our_player
        self.known_extensions = known_extensions

    def refresh(self):
        global curdir_path
        global offset_filelist
        global selected_line
        global coord_max_y
        global file_list_in_current_dir

        logger.debug("refresh")
        self.main_box.update(self.stdscr)
        # # Clear screen
        self.stdscr.clear()
        self.stdscr.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.stdscr.vline(self.main_box.max_y - 4, 1,
                          curses.ACS_HLINE, self.main_box.max_x - 2)

        coord_max_y = self.main_box.max_y - 5

        self.stdscr.hline(self.main_box.max_y - 4, 1,
                          curses.ACS_HLINE, self.main_box.max_x - 2)

        # print status for our_player
        self.draw_status()

        self.draw_menu()

        # print current path
        arg_path_print = str(curdir_path)[max(
            0, (len(str(curdir_path)) + 4) - self.main_box.max_x):]

        self.stdscr.addstr(0, int(self.main_box.max_x / 2) - int(((len(arg_path_print) + 2) / 2)),
                           "|" + arg_path_print + "|")

        self.draw_file_list(coord_max_y)

        self.stdscr.refresh()

    def draw_menu(self):
        global show_menu
        if show_menu:
            self.stdscr.vline(1, self.main_box.menu_x_size-1,
                              curses.ACS_VLINE, self.main_box.max_y - 5)
            self.stdscr.addstr(1, 2, "Menu", curses.A_UNDERLINE)
            self.stdscr.addstr(2, 2, "Browser")
            self.stdscr.addstr(3, 2, "Settings")
            self.stdscr.addstr(4, 2, "Themes")

    def draw_file_list(self, coord_max_y):
        global curdir_path
        global offset_filelist
        global selected_line
        global file_list_in_current_dir

        file_list_in_current_dir = [s for s in os.listdir(str(curdir_path))
                                    if (s.endswith(self.known_extensions) or
                                        os.path.isdir(str(curdir_path) + "/" + s))
                                    and not s.startswith(".")]

        file_list_in_current_dir.insert(0, "..")

        for line, f in enumerate(file_list_in_current_dir[offset_filelist:coord_max_y
                                                          + offset_filelist]):

            if curdir_path.joinpath(Path(f)).is_dir() and line > 0:
                f = f + "/"
            # coloring selection
            if selected_line == 1 + line:
                self.stdscr.addstr(
                    1 + line, self.main_box.min_x, f[:self.main_box.max_x - 2], curses.A_REVERSE)
            else:
                self.stdscr.addstr(1 + line, self.main_box.min_x, f, 0)

    def draw_status(self):
        # print status for our_player
        line_1, line_2, progress_bar_bars = self.our_player.get_interface_lines(
            self.main_box.max_x)
        self.stdscr.addstr(self.main_box.max_y - 3, 1,
                           line_1[:self.main_box.max_x - 3])
        line_2_and_bars = line_2[:progress_bar_bars] + \
            ((progress_bar_bars-len(line_2))*" ")
        self.stdscr.addstr(self.main_box.max_y - 2, 1,
                           line_2[:self.main_box.max_x - 3])
        if progress_bar_bars > 0:
            self.stdscr.addstr(
                self.main_box.max_y - 2, 1, line_2_and_bars[:self.main_box.max_x - 3], curses.A_REVERSE)


def get_input(our_player, stdscr, refresher):

    logger.debug("inside thread ")
    global curdir_path
    global offset_filelist
    global selected_line
    global coord_max_y
    global file_list_in_current_dir
    global exit_requested
    global show_menu

    while not exit_requested:
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
            if (coord_max_y + offset_filelist) < len(file_list_in_current_dir) \
                    and selected_line == coord_max_y:
                offset_filelist = offset_filelist + 1
            else:
                selected_line = min(min(coord_max_y, len(
                    file_list_in_current_dir)), selected_line + 1)
            # selected_line = min(coord_max_y, selected_line + 1)
        elif got_key == curses.KEY_RIGHT:
            logger.debug("key right")
            current_offset_in_file_list = selected_line + offset_filelist - 1
            joined_path = curdir_path.joinpath(
                Path(file_list_in_current_dir[current_offset_in_file_list]))
            if selected_line == 1:
                offset_filelist = 0
                curdir_path = curdir_path.parent
            elif joined_path.is_dir():
                offset_filelist = 0
                curdir_path = joined_path
                selected_line = 1
            else:
                current_queue = play_queue.PlayQueue(
                    curdir_path, file_list_in_current_dir, current_offset_in_file_list)
                our_player.play_new_queue(current_queue)
        elif got_key == ord('q'):
            exit_requested = True
            break
        elif got_key == ord('m'):
            show_menu = not show_menu
        refresher.refresh()
    # return curdir_path, offset_filelist, selected_line


curses.wrapper(main)

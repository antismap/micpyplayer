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

logger = logging.getLogger("micpyplayer")
logger.setLevel(logging.DEBUG)
main_box = None

def main(stdscr):
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
    refresher = ScreenPainter(stdscr, main_box, our_player, known_extensions, current_app_state )

    while not current_app_state[0].exit_requested:
        refresher.refresh()

        if not thread_started:
            t1 = InputClass(our_player, stdscr, refresher, current_app_state)
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


class ScreenPainter(object):

    def __init__(self, stdscr, main_box, our_player, known_extensions, current_app_state):
        self.stdscr = stdscr
        self.main_box = main_box
        self.our_player = our_player
        self.known_extensions = known_extensions
        self.current_app_state = current_app_state

    def refresh(self):

        # logger.debug("refresh")
        self.main_box.update(self.stdscr)
        # # Clear screen
        self.stdscr.clear()
        self.stdscr.border(0, 0, 0, 0, 0, 0, 0, 0)
        self.stdscr.vline(self.main_box.max_y - 4, 1,
                          curses.ACS_HLINE, self.main_box.max_x - 2)

        self.current_app_state[0].coord_max_y = self.main_box.max_y - 5

        self.stdscr.hline(self.main_box.max_y - 4, 1,
                          curses.ACS_HLINE, self.main_box.max_x - 2)

        # print status for our_player
        self.draw_status()

        self.draw_menu()

        self.draw_path_on_top()

        self.draw_file_list(self.current_app_state[0].coord_max_y)

        self.stdscr.refresh()

    def draw_path_on_top(self):
        arg_path_print = str(self.current_app_state[0].curdir_path)[max(
            0, (len(str(self.current_app_state[0].curdir_path)) + 4) - self.main_box.max_x):]

        self.stdscr.addstr(0, int(self.main_box.max_x / 2) - int(((len(arg_path_print) + 2) / 2)),
                           "|" + arg_path_print + "|")

    def draw_menu(self):
        if self.current_app_state[0].show_menu:
            self.stdscr.vline(1, self.main_box.menu_x_size-1,
                              curses.ACS_VLINE, self.main_box.max_y - 5)
            self.stdscr.addstr(1, 2, "Menu", curses.A_UNDERLINE)
            self.stdscr.addstr(2, 2, "Browser")
            self.stdscr.addstr(3, 2, "Settings")
            self.stdscr.addstr(4, 2, "Themes")

    def draw_file_list(self, coord_max_y):

        self.current_app_state[0].file_list_in_current_dir = [s for s in os.listdir(str(self.current_app_state[0].curdir_path))
                                    if (s.endswith(self.known_extensions) or
                                        os.path.isdir(str(self.current_app_state[0].curdir_path) + "/" + s))
                                    and not s.startswith(".")]

        self.current_app_state[0].file_list_in_current_dir.insert(0, "..")

        for line, f in enumerate(self.current_app_state[0].file_list_in_current_dir[self.current_app_state[0].offset_filelist:coord_max_y
                                                          + self.current_app_state[0].offset_filelist]):

            if self.current_app_state[0].curdir_path.joinpath(Path(f)).is_dir() and line > 0:
                f = f + "/"
            # coloring selection
            if self.current_app_state[0].selected_line == 1 + line:
                self.stdscr.addstr(
                    1 + line, self.main_box.min_x, " " + f[:self.main_box.max_x - 2], curses.A_REVERSE)
            else:
                self.stdscr.addstr(1 + line, self.main_box.min_x, " " +f, 0)

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


class InputClass(threading.Thread):
    def __init__(self, our_player, stdscr, refresher, current_app_state):

        self.our_player = our_player
        self.stdscr = stdscr
        self.refresher = refresher
        self.current_app_state = current_app_state
        self.get_input()
        threading.Thread.__init__(self)

    def get_input(self):
        logger.debug("inside thread ")

        while not self.current_app_state[0].exit_requested:
            got_key = self.stdscr.getch()
            if got_key == curses.KEY_UP:
                self.process_up()
            elif got_key == curses.KEY_DOWN:
                self.process_down(self.current_app_state[0].coord_max_y, self.current_app_state[0].file_list_in_current_dir)
            elif got_key == curses.KEY_RIGHT:
                self.process_right(self.current_app_state[0].file_list_in_current_dir, self.our_player)
            elif got_key == ord('q'):
                self.current_app_state[0].exit_requested = True
                break
            elif got_key == ord('m'):
                self.current_app_state[0].show_menu = not self.current_app_state[0].show_menu
            elif got_key == ord('+'):
                logger.debug("volume +")
            elif got_key == ord('-'):
                logger.debug("volume -")
            self.refresher.refresh()
        # return curdir_path, offset_filelist, selected_line

    def process_up(self):
        logger.debug("key up")
        if self.current_app_state[0].offset_filelist > 0 and self.current_app_state[0].selected_line == 1:
            self.current_app_state[0].offset_filelist = self.current_app_state[0].offset_filelist - 1
        else:
            self.current_app_state[0].selected_line = max(1, self.current_app_state[0].selected_line - 1)

    def process_right(self, file_list_in_current_dir, our_player):
        logger.debug("key right")
        current_offset_in_file_list = self.current_app_state[0].selected_line + self.current_app_state[0].offset_filelist - 1
        joined_path = self.current_app_state[0].curdir_path.joinpath(
            Path(file_list_in_current_dir[current_offset_in_file_list]))
        if self.current_app_state[0].selected_line == 1:
            self.current_app_state[0].offset_filelist = 0
            self.current_app_state[0].curdir_path = self.current_app_state[0].curdir_path.parent
        elif joined_path.is_dir():
            if os.access(joined_path, os.R_OK):
                self.current_app_state[0].offset_filelist = 0
                self.current_app_state[0].curdir_path = joined_path
                self.current_app_state[0].selected_line = 1
            else:
                logger.debug("no read permissions on joined_path, TODO notify user")
        else:
            current_queue = play_queue.PlayQueue(
                self.current_app_state[0].curdir_path, file_list_in_current_dir, current_offset_in_file_list)
            our_player.play_new_queue(current_queue)

    def process_down(self, coord_max_y, file_list_in_current_dir):
        logger.debug("key down")
        # if we are at the last entry and there still are entries
        if (coord_max_y + self.current_app_state[0].offset_filelist) < len(file_list_in_current_dir) \
                and self.current_app_state[0].selected_line == coord_max_y:
            self.current_app_state[0].offset_filelist = self.current_app_state[0].offset_filelist + 1
        else:
            self.current_app_state[0].selected_line = min(min(coord_max_y, len(
                file_list_in_current_dir)), self.current_app_state[0].selected_line + 1)
        # selected_line = min(coord_max_y, selected_line + 1)


curses.wrapper(main)

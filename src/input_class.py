import curses
import os
import threading
from pathlib import Path

import play_queue


class InputClass(threading.Thread):
    def __init__(self, our_player, stdscr_protected, refresher, current_app_state, logger):
        self.logger = logger
        self.our_player = our_player
        self.stdscr_protected = stdscr_protected
        self.refresher = refresher
        self.current_app_state = current_app_state
        threading.Thread.__init__(self)

    def run(self):
        self.logger.debug("inside thread ")

        while not self.current_app_state[0].exit_requested:
            got_key = self.stdscr_protected[0].getch()
            if got_key == curses.KEY_UP:
                self.process_up()
            elif got_key == curses.KEY_DOWN:
                self.process_down(self.current_app_state[0].coord_max_y,
                                  self.current_app_state[0].file_list_in_current_dir)
            elif got_key == curses.KEY_RIGHT:
                self.process_right(self.current_app_state[0].file_list_in_current_dir, self.our_player)
            elif got_key == ord('q'):
                self.current_app_state[0].exit_requested = True
                break
            elif got_key == ord('m'):
                self.current_app_state[0].show_menu = not self.current_app_state[0].show_menu
            elif got_key == ord('+'):
                self.current_app_state[0].volume_counter = 2
                self.logger.debug("volume +")
                self.current_app_state[0].volume = self.our_player.volume_up()
            elif got_key == ord('-'):
                self.current_app_state[0].volume_counter = 2
                self.current_app_state[0].volume = self.our_player.volume_down()
                self.logger.debug("volume -")
            elif got_key == ord(' '):
                self.our_player.play_pause()

            self.refresher.refresh()

    def process_up(self):
        self.logger.debug("key up")
        if self.current_app_state[0].offset_filelist > 0 and self.current_app_state[0].selected_line == 1:
            self.current_app_state[0].offset_filelist = self.current_app_state[0].offset_filelist - 1
        else:
            self.current_app_state[0].selected_line = max(1, self.current_app_state[0].selected_line - 1)

    def process_right(self, file_list_in_current_dir, our_player):
        self.logger.debug("key right")
        current_offset_in_file_list = self.current_app_state[0].selected_line + self.current_app_state[
            0].offset_filelist - 1
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
                self.logger.debug("no read permissions on joined_path, TODO notify user")
        else:
            current_queue = play_queue.PlayQueue(
                self.current_app_state[0].curdir_path, file_list_in_current_dir, current_offset_in_file_list)
            our_player.play_new_queue(current_queue)

    def process_down(self, coord_max_y, file_list_in_current_dir):
        self.logger.debug("key down")
        # if we are at the last entry and there still are entries
        if (coord_max_y + self.current_app_state[0].offset_filelist) < len(file_list_in_current_dir) \
                and self.current_app_state[0].selected_line == coord_max_y:
            self.current_app_state[0].offset_filelist = self.current_app_state[0].offset_filelist + 1
        else:
            self.current_app_state[0].selected_line = min(min(coord_max_y, len(
                file_list_in_current_dir)), self.current_app_state[0].selected_line + 1)

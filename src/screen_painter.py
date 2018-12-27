import curses
import os
from pathlib import Path


class ScreenPainter(object):

    def __init__(self, stdscr_protected, main_box, our_player, known_extensions, current_app_state, logger):
        self.logger = logger
        self.stdscr_protected = stdscr_protected
        self.main_box = main_box
        self.our_player = our_player
        self.known_extensions = known_extensions
        self.current_app_state = current_app_state

    def refresh(self):
        self.main_box.update()
        # # Clear screen
        self.stdscr_protected[1].acquire()
        self.stdscr_protected[0].clear()
        self.stdscr_protected[0].border(0, 0, 0, 0, 0, 0, 0, 0)
        self.stdscr_protected[0].vline(self.main_box.max_y - 4, 1,
                          curses.ACS_HLINE, self.main_box.max_x - 2)

        self.current_app_state[0].coord_max_y = self.main_box.max_y - 5

        self.stdscr_protected[0].hline(self.main_box.max_y - 4, 1,
                                       curses.ACS_HLINE, self.main_box.max_x - 2)

        # print status for our_player
        self.draw_status()
        self.draw_menu()
        self.draw_path_on_top()
        self.draw_file_list(self.current_app_state[0].coord_max_y)
        self.draw_volume()

        self.stdscr_protected[0].refresh()
        self.stdscr_protected[1].release()

    def draw_volume(self):
        self.logger.debug("volume counter " + str(self.current_app_state[0].volume_counter))
        if self.current_app_state[0].volume_counter > 0:
            volume = self.current_app_state[0].volume
            new_win_width = self.main_box.max_x - 8
            new_window = self.stdscr_protected[0].subwin(3, new_win_width, int(self.main_box.max_y / 2), 4)
            volume_text = "volume: " + str(volume) + "%"
            new_window.border(0, 0, 0, 0, 0, 0, 0, 0)
            new_window.addstr(0, int((self.main_box.max_x - 2 - 4) / 2) - int(((len(volume_text) + 2) / 2)),
                              "|" + volume_text + "|")
            self.stdscr_protected[0].addstr(int(self.main_box.max_y / 2) + 1, 5,
                                            int(volume * (new_win_width - 2) / (100)) * " ", curses.A_REVERSE)
            self.current_app_state[0].volume_counter = max(0, self.current_app_state[0].volume_counter - 1)

    def draw_path_on_top(self):
        arg_path_print = str(self.current_app_state[0].curdir_path)[max(
            0, (len(str(self.current_app_state[0].curdir_path)) + 4) - self.main_box.max_x):]

        self.stdscr_protected[0].addstr(0, int(self.main_box.max_x / 2) - int(((len(arg_path_print) + 2) / 2)),
                           "|" + arg_path_print + "|")

    def draw_menu(self):
        if self.current_app_state[0].show_menu:
            self.stdscr_protected[0].vline(1, self.main_box.menu_x_size - 1,
                                           curses.ACS_VLINE, self.main_box.max_y - 5)
            self.stdscr_protected[0].addstr(1, 2, "Menu", curses.A_UNDERLINE)
            self.stdscr_protected[0].addstr(2, 2, "Browser")
            self.stdscr_protected[0].addstr(3, 2, "Settings")
            self.stdscr_protected[0].addstr(4, 2, "Themes")

    def draw_file_list(self, coord_max_y):

        self.current_app_state[0].file_list_in_current_dir = [s for s in
                                                              os.listdir(str(self.current_app_state[0].curdir_path))
                                                              if (s.endswith(self.known_extensions) or
                                                                  os.path.isdir(str(
                                                                      self.current_app_state[0].curdir_path) + "/" + s))
                                                              and not s.startswith(".")]

        self.current_app_state[0].file_list_in_current_dir.insert(0, "..")

        for line, f in enumerate(
                self.current_app_state[0].file_list_in_current_dir[self.current_app_state[0].offset_filelist:coord_max_y
                                                                                                             +
                                                                                                             self.current_app_state[
                                                                                                                 0].offset_filelist]):

            if self.current_app_state[0].curdir_path.joinpath(Path(f)).is_dir() and line > 0:
                f = f + "/"
            # coloring selection
            if self.current_app_state[0].selected_line == 1 + line:
                self.stdscr_protected[0].addstr(
                    1 + line, self.main_box.min_x, " " + f[:self.main_box.max_x - 2], curses.A_REVERSE)
            else:
                self.stdscr_protected[0].addstr(1 + line, self.main_box.min_x, " " + f, 0)

    def draw_status(self):
        # print status for our_player
        line_1, line_2, progress_bar_bars = self.our_player.get_interface_lines(
            self.main_box.max_x)
        self.stdscr_protected[0].addstr(self.main_box.max_y - 3, 1,
                           line_1[:self.main_box.max_x - 3])
        line_2_and_bars = line_2[:progress_bar_bars] + \
                          ((progress_bar_bars - len(line_2)) * " ")
        self.stdscr_protected[0].addstr(self.main_box.max_y - 2, 1,
                           line_2[:self.main_box.max_x - 3])
        self.logger.debug("progress bars " + str(progress_bar_bars))
        if progress_bar_bars > 0:
            self.stdscr_protected[0].addstr(
                self.main_box.max_y - 2, 1, line_2_and_bars[:self.main_box.max_x - 3], curses.A_REVERSE)

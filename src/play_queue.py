from pathlib import Path


class PlayQueue(object):

    def __init__(self, current_file_folder, current_file_list, current_offset):
        self.song_list = [current_file_folder.joinpath(
            Path(x)) for x in current_file_list]
        self.song_list = self.song_list[current_offset:len(self.song_list)]

    def pop_song(self):
        if len(self.song_list) > 0:
            result = self.song_list.pop(0)
        else:
            result = Path("")
        return result

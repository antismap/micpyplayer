import play_queue
import os
from pathlib import Path


def test_play_queue():
    file_list = sorted([s for s in os.listdir(
        "test/fakemp3/") if not s.startswith(".")])

    print(str(file_list))

    our_queue = play_queue.PlayQueue(Path("test/fakemp3/"), file_list, 0)
    assert our_queue.pop_song() == Path('test/fakemp3/fakesong1.mp3')
    assert our_queue.pop_song() == Path("test/fakemp3/fakesong2.mp3")
    assert our_queue.pop_song() == Path("test/fakemp3/fakesong3.mp3")
    assert our_queue.pop_song() == None

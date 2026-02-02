import pytest
from music_player import MusicPlayer

@pytest.fixture
def player():
    return MusicPlayer()

@pytest.fixture
def start_player(player):
    player.start_playing("1")
    return player
    

def test_start_playing(player):
    player.start_playing("2")
    assert player.songplaying == 101
    assert len(player.queue) == 9
    assert player.playing == True

def test_play_or_pause(start_player):
    start_player.play_or_pause()
    assert start_player.playing is False

def test_skip(start_player):
    current = start_player.songplaying
    for _ in range(3):
        start_player.skip(False)
    assert start_player.songplaying != current 
    assert start_player.songplaying == 4

def test_add_to_queue(start_player):
    start_player.add_to_queue(7)
    start_player.add_to_queue(12)
    start_player.skip(False)
    assert start_player.songplaying == 7
    assert 12 in start_player.queue

def test_remove_from_queue(start_player):
    start_player.remove_from_queue(2)
    start_player.remove_from_queue(4)
    start_player.skip(False)
    assert start_player.songplaying == 3
    assert 4 not in start_player.queue
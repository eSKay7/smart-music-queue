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

def test_shuffle_behavior(start_player):
    cursong = start_player.songplaying
    originalqueue = list(start_player.queue)
    start_player.smart_shuffle()
    assert start_player.queue != originalqueue
    assert start_player.songplaying == cursong
    assert len(start_player.queue) == 9

def test_smart_shuffle_behavior_mock_data(start_player):
    start_player.ranking = {
                        1: [0, 0, 1, 0],
                        2: [0, 0, 0, 1],
                        3: [0, 5, 5, 0],
                        4: [5, 0, 0, 3],
                        5: [0, 0, 1, 0],
                        6: [0, 0, 1, 0],  
                        7: [0, 0, 1, 0],
                        8: [0, 0, 1, 0],
                        9: [0, 0, 1, 0],
                        10: [0, 0, 1, 0],
                        }
    start_player.train()
    assert start_player.model is not None
    start_player.smart_shuffle()
    assert start_player.queue.index(3) < start_player.queue.index(4)

def test_ml_model_creation_failed(player):
    player.train()
    assert player.model is None

def test_ml_model_creation_successful(start_player):
    start_player.skip(False)
    for _ in range(2):
        start_player.skip(True)
    start_player.add_to_queue(10)
    start_player.train()
    assert start_player.model is not None

def test_predict_song_score(start_player):
    assert 0 <= start_player.predict_song_score(start_player.songplaying) <= 1

def test_liked_song_ranking(start_player):
    liked_song = start_player.queue[-1]
    for _ in range(5):
        start_player.add_to_queue(liked_song)
        start_player.skip(False)
    start_player.skip(False)
    start_player.train()
    assert start_player.model is not None
    start_player.smart_shuffle()
    assert start_player.queue.index(liked_song) < len(start_player.queue) // 2
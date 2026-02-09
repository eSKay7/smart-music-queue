# Core Logic : Backend 
import random
import os 
import time
from typing import List, Optional
from ml_sample import traindata
from database import get_connection


playlist1 = [1,2,3,4,5,6,7,8,9,10]
playlist2 = [101,102,103,104,105,106,107,108,109,110]


class MusicPlayer:
    def __init__(self):
        self.playlists = {
            "1": list(playlist1),
            "2": list(playlist2)
        }
        self.queue: List[int] = []
        self.curindex: int = 0
        self.songplaying: Optional[int] = None  
        self.playing: bool = False                              # To determine if something is playing
        self.playd: List[int] = []                              # List of songs played
        self.temp: int = 0                                      # Index for adding to queue
        self.song_start_time: Optional[float] = None            # Time when current song started
        self.cur_playlist_id: Optional[str] = None
        self.model = None
    
    def get_playlist(self):
        return [{"id": pid, "name": f"Playlist {pid}", "count": len(pl)} for pid, pl in self.playlists.items()]
    
    def add_song_data(self):
        conn = get_connection()
        cur = conn.cursor()

        for song in (self.queue + ([self.songplaying] if self.songplaying else [])):
            cur.execute(
            """
            INSERT INTO song_interactions 
            (playlist_id, song_id, early_skipped, added, played, removed)
            VALUES
            (?, ?, 0, 0, 0, 0)
            ON CONFLICT (playlist_id, song_id) DO NOTHING
            """, (self.cur_playlist_id, song))
        conn.commit()
        conn.close()

    def start_playing(self, playlist_id: str):
        if playlist_id not in self.playlists:
            raise ValueError("Playlist doesn't exist")
        self.cur_playlist_id = str(playlist_id)
        self.queue = list(self.playlists[playlist_id])
        self.curindex = 0
        if self.queue:
            self.songplaying = self.queue.pop(self.curindex)
            self.playing = True
            self.song_start_time = time.time()
        else:
            self.songplaying = None
            self.playing = False
            self.song_start_time = None
        self.add_song_data()
        return self.get_state()      
    
    def play_or_pause(self):
        # Pause song
        if self.playing:
            print("Song Paused ", self.songplaying)
            self.playing = False
            if self.song_start_time:
                self.song_paused_time = time.time() - self.song_start_time
            self.song_start_time = None
        # Play paused song
        else:
            print("Playing Song ", self.songplaying)
            self.playing = True
            if hasattr(self, "song_paused_time"):
                self.song_start_time = time.time() - self.song_paused_time
                del self.song_paused_time
            else:
                self.song_start_time = time.time()
        return self.get_state()
    
    def smart_shuffle(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT song_id, early_skipped, added, played, removed
        FROM song_interactions
        WHERE playlist_id = ? 
        """, (self.cur_playlist_id,))
        rows = cur.fetchall()
        conn.close()
        ranking = {
            song_id: [early_skipped, added, played, removed]
            for song_id, early_skipped, added, played, removed in rows
            }
        if not self.model and ranking:
            self.train()
        if not self.model:
            print("Completely random shuffling playlist")
            newqueue = []
            for song, rank in ranking.items():
                newqueue.append(song)
            if self.songplaying in newqueue:
                newqueue.remove(self.songplaying)
            random.shuffle(newqueue)
            self.queue = newqueue
            self.curindex = 0
            self.playd = []
            self.temp = 0
            return self.get_state()
        
        scores = []
        for song in ranking:
            score = self.predict_song_score(song)
            scores.append((song, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        upper, middle, lower = [], [], []
        for song, score in scores:
            if score >= 0.66:
                upper.append(song)
            elif score >= 0.33:
                middle.append(song)
            else:
                lower.append(song)
        random.shuffle(upper)
        random.shuffle(middle)
        random.shuffle(lower)
        self.queue = upper + middle + lower
        if self.songplaying in self.queue:
            self.queue.remove(self.songplaying)
        self.curindex = 0
        self.playd = []
        self.temp = 0
        print("Shuffling based on ML rankings")
        return self.get_state()
    
    def train(self):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT song_id, early_skipped, added, played, removed
        FROM song_interactions
        WHERE playlist_id = ?
        """, (self.cur_playlist_id,))
        rows = cur.fetchall()
        conn.close()
        if not rows:
            print("Data insufficient")
        ranking = {
            song_id: [early_skipped, added, played, removed]
            for song_id, early_skipped, added, played, removed in rows
        }
        model = traindata(ranking)
        if not model:
            print("Data insufficient")
            return
        self.model = model
        print("Updated the ML model")

    def predict_song_score(self, song):
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
        """
        SELECT song_id, early_skipped, added, played, removed
        FROM song_interactions
        WHERE playlist_id = ? 
        """, (self.cur_playlist_id,))
        rows = cur.fetchall()
        conn.close()
        ranking = {
            song_id: [early_skipped, added, played, removed]
            for song_id, early_skipped, added, played, removed in rows
            }
        if not self.model or song not in ranking:
            return 0.5
        features = [ranking[song]]
        return self.model.predict_proba(features)[0][1]

    def skip(self, early: bool = False):
        conn = get_connection()
        cur = conn.cursor()
        if self.songplaying:
            if early:
                cur.execute(
                """
                UPDATE song_interactions
                SET early_skipped = early_skipped + 1
                WHERE playlist_id = ? and song_id = ?
                """,
                (self.cur_playlist_id, self.songplaying))
            else:
                cur.execute(
                """
                UPDATE song_interactions
                SET played = played + 1
                WHERE playlist_id = ? and song_id = ?
                """,
                (self.cur_playlist_id, self.songplaying))
            self.playd.append(self.songplaying)
        conn.commit()
        conn.close()
        self.train()
        if self.queue:   
            self.songplaying = self.queue.pop(self.curindex)
            self.song_start_time = time.time()
            self.playing = True
            if self.temp != 0:
                self.temp -= 1
        else:
            self.songplaying = None
            self.playing = False
            self.song_start_time = None
        return self.get_state()
    
    def add_to_queue(self, queue_song: int):
        conn = get_connection()
        cur = conn.cursor()
        self.queue.insert(self.temp, queue_song)
        self.temp += 1
        cur.execute(
        """
        UPDATE song_interactions
        SET added = added + 1
        WHERE playlist_id = ? and song_id = ?
        """,
        (self.cur_playlist_id, self.songplaying))
        conn.commit()
        conn.close()
        self.train()
        return self.get_state()
    
    def remove_from_queue(self, dequeue_song: int):
        if dequeue_song in self.queue:
            conn = get_connection()
            cur = conn.cursor()
            self.queue.remove(dequeue_song)
            cur.execute(
            """
            UPDATE song_interactions
            SET removed = removed + 1
            WHERE playlist_id = ? and song_id = ?
            """,
            (self.cur_playlist_id, self.songplaying))
            conn.commit()
            conn.close()
            self.train()
        else: 
            print("Song is not in queue")
        return self.get_state()
                           
    # Created state for front end  
    def get_state(self):
        elapsed = 0.0
        if self.song_start_time:
            elapsed = time.time() - self.song_start_time
        elif hasattr(self, "song_paused_time"):
            elapsed = self.song_paused_time
        return {
            "current_song": self.songplaying,
            "queue": list(self.queue),
            "playing": bool(self.playing),
            "temp": self.temp,
            "ranking": dict(self.ranking),
            "playd": list(self.playd),
            "elapsed": float(elapsed)
        }

# Running the code and showing data on Command Line using the class defined above
def run_on_cli():
    player = MusicPlayer()
    playlist = input("What playlist are you looking to play? ")
    try:
        player.start_playing(str(playlist))
    except Exception as e:
        print("Could not start playlist: ", e)
        return
    print("Now Playing: ", player.songplaying)
    print("Queue: ", player.queue)
    while True:
        action = int(input("Press 1 to play/pause, 2 to shuffle playlist, 3 to skip song, 4 to add a song to queue, 5 to remove a song from queue: "))
        match action:
            case 1:
                player.play_or_pause()
                print("State", player.get_state())
            case 2:
                player.smart_shuffle()
                print("Queue", player.queue)
            case 3:
                player.skip(early = False)
                print("Skipping")
                print("Now playing: ", player.songplaying)
                print("Here's the queue: ", player.queue)
            case 4:
                song = int(input("What song would you like to add to queue? "))
                player.add_to_queue(song)
                print("Added song, Here's the updated queue: ", player.queue)
            case 5:
                song = int(input("What song would you like to remove from queue? "))
                player.remove_from_queue(song)
                print("Here's the updated queue: ", player.queue) 
            case 6:
                break

if __name__ == "__main__":
    run_on_cli()

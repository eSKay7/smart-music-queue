import random
import json
import os 

RANKED_FILE = "rankedfile.json"

playlist1 = [1,2,3,4,5,6,7,8,9,10]
playlist2 = [101,102,103,104,105,106,107,108,109,110]
queue = []

playlist = input("What playlist are you looking to play? ")
match playlist:
    case "1":
        for i in playlist1:
            queue.append(i) 
    case "2":
        for j in playlist2:
            queue.append(j)
print(queue)        

curindex = 0
songplaying = queue.pop(curindex)
play = True
print("Now playing: ", songplaying)
print("Queue: ",queue)

def playorpause(play, songplaying):
    if play:
        print("Song Paused ", songplaying)
        play = False
        return play
    else:
        print("Playing Song ", songplaying)
        play = True
        return play
    
ranking = {}
for i in queue:
    ranking[i] = 0

def loadrank(queue):
    if os.path.exists(RANKED_FILE):
        with open(RANKED_FILE, "r") as file:
            ranking = json.load(file)
            newranking = {}
            for string, integer in ranking.items():
                newranking[int(string)] = integer
            ranking = newranking
            return ranking
    else:
        return {song: 0 for song in queue}

ranking = loadrank(queue)

def saverank(ranking):
    with open(RANKED_FILE, "w") as file:
        json.dump(ranking, file, indent=4)

def smartshuffle(queue, curindex, songplaying, ranking, playd):
    print("Smart Shuffling playlist")
    upper = []
    middle = []
    lower = []
    for rank in ranking:
        songrange = ranking[rank]
        if songrange >= 5:
            upper.append(rank)
        elif songrange < 5 and songrange > -2:
            middle.append(rank)
        else:
            lower.append(rank)
    queue.clear()
    random.shuffle(upper)
    random.shuffle(middle)
    random.shuffle(lower)
    queue.extend(upper)
    queue.extend(middle)
    queue.extend(lower)
    queue.remove(songplaying)
    curindex = 0
    print(queue)
    count = 0
    playd = []
    return queue, curindex, ranking, count, playd

playd = []
def skip(songplaying, curindex, queue, playd, temp):
    playd.append(songplaying)
    songplaying = queue.pop(curindex)
    print("Skipping")
    print("Now playing: ", songplaying)
    print("queue: ", queue)
    print("playd: ", playd)
    if temp != 0:
        temp -= 1
    return songplaying, queue, playd, temp

temp = 0
def addtoqueue(queue, ranking, temp, songplaying):
    queuesong = int(input("What song do you want to add to queue? "))
    print("temp = ", temp)
    print("Song playing: ", songplaying)
    queue.insert(temp, queuesong)
    temp += 1
    print("queue ", queue)
    if queuesong in ranking:
        ranking[queuesong] += 5
    saverank(ranking)
    print("Added song, Here's the queue: ", queue)
    return queue, ranking, temp

def removefromqueue(queue, curindex, ranking):
    dequeuesong = int(input("What song do you want to remove from queue? "))
    queue.remove(dequeuesong)
    if dequeuesong in ranking:
        ranking[dequeuesong] -= 3
    saverank(ranking)
    print("Removed song, Here's the queue: ", queue)
    return queue, ranking

while True:
    action = int(input("Press 1 to play/pause, 2 to shuffle playlist, 3 to skip song, 4 to add a song to queue, 5 to remove a song from queue: "))
    match action:
        case 1:
            play = playorpause(play, songplaying)
        case 2:
            queue, curindex, ranking, count, playd = smartshuffle(queue, curindex, songplaying, ranking, playd)
        case 3:
            songplaying, queue, playd, temp = skip(songplaying, curindex, queue, playd, temp)
        case 4:
            queue, ranking, temp = addtoqueue(queue, ranking, temp, songplaying)
        case 5:
            queue, ranking = removefromqueue(queue, curindex, ranking) 
        case 6:
            break

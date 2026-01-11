import random

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
songplaying = queue[curindex]
play = True
print("Now playing: ", songplaying)

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

def smartshuffle(queue, curindex, songplaying, ranking, playd):
    print("Smart Shuffling playlist")
    queue.remove(songplaying)
    queue.extend(playd)
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
    queue.extend(upper)
    queue.extend(middle)
    queue.extend(lower)
    queue.insert(0, songplaying)
    curindex = 0
    print(queue[curindex + 1:])
    count = 0
    playd = []
    return queue, curindex, ranking, count, playd

playd = []
def skip(songplaying, curindex, queue, playd):
    skipping = queue.pop(0)
    print("queue: ", queue)
    playd.append(skipping)
    print("playd: ", playd)
    songplaying = queue[curindex]
    print("Now playing: ", songplaying)
    return songplaying, queue, playd

count = 0
temp = 0
def addtoqueue(queue, curindex, ranking, temp, count):
    count += 1
    if count == 1:
        temp = curindex
    temp += 1
    queuesong = int(input("What song do you want to add to queue? "))
    print("curindex ", curindex)
    queue.insert(temp, queuesong)
    print("queue ", queue)
    if queuesong in ranking:
        ranking[queuesong] += 5
    print("Added song, Here's the queue: ", queue[curindex + 1:])
    return queue, ranking, temp, count

def removefromqueue(queue, curindex, ranking):
    dequeuesong = int(input("What song do you want to remove from queue? "))
    queue.remove(dequeuesong)
    if dequeuesong in ranking:
        ranking[dequeuesong] -= 3
    print("Removed song, Here's the queue: ", queue[curindex + 1:])
    return queue, ranking

while True:
    action = int(input("Press 1 to play/pause, 2 to shuffle playlist, 3 to skip song, 4 to add a song to queue, 5 to remove a song from queue: "))
    match action:
        case 1:
            play = playorpause(play, songplaying)
        case 2:
            queue, curindex, ranking, count, playd = smartshuffle(queue, curindex, songplaying, ranking, playd)
        case 3:
            songplaying, queue, playd = skip(songplaying, curindex, queue, playd)
        case 4:
            queue, ranking, temp, count = addtoqueue(queue, curindex, ranking, temp, count)
        case 5:
            queue, ranking = removefromqueue(queue, curindex, ranking) 
        case 6:
            break

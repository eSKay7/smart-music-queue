from sklearn.linear_model import LogisticRegression

def traindata(ranking):
    x = []
    y = []
    for song, rank in ranking.items():
        early, added, played, removed = map(int, rank)
        x.append([early, added, played, removed])
        negative = early*2 + removed*2
        positive = added*2 + played
        y.append(1 if positive > negative else 0)

    if len(set(y)) < 2:
        return None

    model = LogisticRegression()
    model.fit(x,y)
    return model
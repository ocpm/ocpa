
def test():
    return set([])


if __name__ == '__main__':
    events = {"a": {"1": 2, "2": 2}, "b": {"1": 1, "2": 1}}
    print(dict(sorted(events.items(), key=lambda kv: kv[1]["1"])))

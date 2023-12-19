def get_first_name(x):
    for item in x:
        if item["use"] == "official":
            return item["given"]
    return None


def get_last_name(x):
    for item in x:
        if item["use"] == "official":
            return item["family"]
    return None

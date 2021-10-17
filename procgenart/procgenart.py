import os
import tempfile
import random

import tweepy
import dotenv

import datetime

import scrolling.scrolling

generators = [
    { "generate": scrolling.scrolling.generate, "weight": 1, "suffix": "webp" },
]

# We don't use this in our code, but this is what we used to get the access token that we're pulling from .env
def manual_auth(auth):
    redirect_url = auth.get_authorization_url()
    print(redirect_url)
    
    verifier = input("Verifier: ")

    auth.request_token = {
        "oauth_token": auth.request_token["oauth_token"],
        "oauth_token_secret": verifier,
    }

    print(auth.get_access_token(verifier))


def weighted_select(generators, key="weight"):
    cumulative = []
    sum = 0
    for generator in generators:
        sum += generator[key]
        cumulative.append((generator, sum))
    
    selection = random.random() * sum
    for generator, cumulative_weight in cumulative:
        if selection <= cumulative_weight:
            return generator
    
    raise Exception(f"weighted select error (selection: {selection}, items: {cumulative})")


def main():
    # Init dotenv and random
    dotenv.load_dotenv()
    random.seed()


    # Auth to Twitter
    auth = tweepy.OAuthHandler(os.environ.get("API_KEY"), os.environ.get("API_SECRET"))

    # manual_auth(auth)
    # return

    auth.set_access_token(os.environ.get("ACCESS_TOKEN"), os.environ.get("ACCESS_TOKEN_SECRET"))
    api = tweepy.API(auth)


    # Pick a generator and generate into a (hopefully virtual) file
    file = tempfile.SpooledTemporaryFile(max_size=50 * 1024 * 1024, mode="wb+")
    seed = random.randint(0, 0xFFFFFFFFE)

    generator = weighted_select(generators)
    generator["generate"](file, seed)
    filename = f"{seed}.{generator['suffix']}"
    
    file.seek(0)


    # Write file to disk if we're in dry mode
    if os.environ.get("DRY") == "True":
        with open("dry/" + datetime.datetime.now().isoformat() + filename, "wb+") as out_file:
            out_file.write(file.read())
        return

    # Upload to Twitter
    media = api.media_upload(filename, file=file)
    print(media)
    status_response = api.update_status(filename, media_ids=[media.media_id])
    print(status_response)

if __name__ == "__main__":
    main()
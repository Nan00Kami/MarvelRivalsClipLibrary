from twitch_auth import get_app_access_token


def main():
    token = get_app_access_token()

    print("Twitch authentication successful.")
    print(f"Token received: {token[:6]}...")


if __name__ == "__main__":
    main()
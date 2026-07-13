from twitch_auth import get_app_access_token, get_client_id
from twitch_games import get_game


def main():
    access_token = get_app_access_token()
    client_id = get_client_id()

    game_data = get_game(
        game_name="Marvel Rivals",
        client_id=client_id,
        access_token=access_token,
    )

    if not game_data["data"]:
        print("Marvel Rivals was not found.")
        return

    game = game_data["data"][0]

    print("Game found.")
    print(f"Name: {game['name']}")
    print(f"Game ID: {game['id']}")


if __name__ == "__main__":
    main()
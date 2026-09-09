from database import init_db, save_clips
from twitch_auth import get_app_access_token, get_client_id
from twitch_clips import get_game_clips
from twitch_games import get_game


def main():
    init_db()

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
    print(f"Game: {game['name']} (ID: {game['id']})")

    # Fetch top 25 recent clips
    clips_response = get_game_clips(
        game_id=game["id"],
        client_id=client_id,
        access_token=access_token,
        first=25,
    )

    clips = clips_response.get("data", [])
    print(f"Fetched {len(clips)} clips from Twitch.")

    new_count = save_clips(clips)
    print(f"Saved {new_count} new clips to local database.")


if __name__ == "__main__":
    main()

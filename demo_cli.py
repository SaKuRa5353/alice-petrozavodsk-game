"""Simple CLI runner to test game logic locally."""

from game_engine import GameState, handle_user_input


def main() -> None:
    state = GameState()
    print("Напиши любой текст, чтобы начать игру. Команда выхода: exit")

    # The same state instance is reused to simulate one user session.
    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "exit":
            print("Пока!")
            break

        response, state = handle_user_input(user_input, state)
        print(response)


if __name__ == "__main__":
    main()

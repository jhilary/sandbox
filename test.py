from datetime import datetime

from bots import *
import gym
from gym import wrappers


def main():

    env_id = 'GuessCard-v1'
    opponent = SmarterBaselineBot()
    player = MishaBotV1New(debug=False)
    record_folder = f'./GuessCard_{player.name}_{datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}'

    gym.envs.register(
        id=env_id,
        entry_point='env:CardsGuessing',
        kwargs={
            "starting_money": 100,
            "opponent": opponent
        },
        max_episode_steps=1000,
        nondeterministic=True
    )

    env = gym.envs.make(env_id)
    env = wrappers.Monitor(env, record_folder, lambda _: True, uid=player.name)
    player.set_env(env)
    player.run(10)
    env.close()

    for video, _ in env.videos:
        print(f'asciinema play {video}')

    # gym.upload(record_folder, api_key='sk_OKAdH4EQUaO9mSyYJNPw')


if __name__ == "__main__":
    main()

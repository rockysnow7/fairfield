from baseball_metrics import Handedness, Player
from fastapi import FastAPI, Query
from glob import glob
from loguru import logger
from typing import Literal

import datetime


logger.add("server.log", rotation="100 MB")


def get_all_players() -> dict[str, Player]:
    paths = glob("retrosheet/*/*allplayers.csv")
    all_players = {}
    for path in paths:
        with open(path) as f:
            lines = f.readlines()
        lines = lines[1:]
        lines = [line.split(",")[:3] for line in lines]
        maps = {f"{first} {last}": Player(id_) for id_, last, first in lines}
        all_players.update(maps)
    return all_players

PLAYERS = get_all_players()
Name = Literal[*PLAYERS.keys()]

METRICS = [key for key in Player.__dict__.keys() if not key.startswith("_")]
Metric = Literal[*METRICS]


def call_metric_on_player(
    player: Player,
    metric: Metric,
    start_date: datetime.date,
    end_date: datetime.date,
):
    args = [start_date, end_date]
    if metric in {"throw_hand", "bat_hand"}:
        args = [start_date.year]

    f = getattr(player, metric)

    try:
        value = f(*args)
    except Exception as e:
        logger.exception(f"Request for metric {metric} on player {player.id} from {start_date} to {end_date} failed")
        return None

    if isinstance(value, Handedness):
        handednesses = {
            Handedness.LEFT: "Left",
            Handedness.RIGHT: "Right",
            Handedness.BOTH: "Both",
        }
        value = handednesses[value]
    return value


app = FastAPI()

@app.get("/api/v1/metrics")
def get_metrics(
    metrics: list[Metric] = Query(...),
    names: list[Name] = Query(...),
    start_date: datetime.date = Query(...),
    end_date: datetime.date = Query(...),
) -> dict[str, dict[str, float | str | None]]:
    players = {name: PLAYERS[name] for name in names}

    results = {}
    for name, player in players.items():
        metric_values = {}
        for metric in metrics:
            value = call_metric_on_player(player, metric, start_date, end_date)
            metric_values[metric] = value
        results[name] = metric_values
    return results

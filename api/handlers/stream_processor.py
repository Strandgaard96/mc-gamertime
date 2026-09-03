from __future__ import annotations

import os

import boto3

dynamodb = boto3.resource("dynamodb")
games_table = dynamodb.Table(os.environ.get("GAMES_TABLE", "boardsite-games"))


def process_stream_handler(event, context):
    for record in event.get("Records", []):
        if record["eventName"] != "INSERT":
            continue

        new_image = record["dynamodb"]["NewImage"]
        game_id = new_image.get("gameId", {}).get("S")
        date_logged = new_image.get("date", {}).get("S")

        if game_id and date_logged:
            games_table.update_item(
                Key={"pk": game_id},
                UpdateExpression="SET lastResultAt = :d",
                ExpressionAttributeValues={":d": date_logged},
            )

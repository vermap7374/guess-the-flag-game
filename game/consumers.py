import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

# Move Django imports inside a function to prevent import issues during ASGI initialization
def get_score_model():
    from .models import Score  # Import only when needed to avoid circular import errors
    return Score

class LeaderboardConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for handling real-time leaderboard updates.
    """

    async def connect(self):
        """
        Called when the WebSocket is handshaking as part of the connection process.
        - Adds the WebSocket connection to the 'leaderboard' group.
        - Accepts the connection.
        - Sends the latest leaderboard scores.
        """
        await self.channel_layer.group_add("leaderboard", self.channel_name)  # Add to leaderboard group
        await self.accept()  # Accept the WebSocket connection
        await self.send_leaderboard_update()  # Send the latest scores

    async def disconnect(self, close_code):
        """
        Called when the WebSocket disconnects.
        - Removes the WebSocket connection from the 'leaderboard' group.
        """
        await self.channel_layer.group_discard("leaderboard", self.channel_name)

    async def receive(self, text_data):
        """
        Called when the WebSocket receives a message from the client.
        - Triggers an update to send the latest leaderboard scores.
        """
        await self.send_leaderboard_update()

    async def send_leaderboard_update(self):
        """
        Fetches the top scores and sends them to all connected clients in the leaderboard group.
        """
        Score = get_score_model()  # Ensure Django models are initialized before querying
        scores = await self.get_top_scores(Score)  # Fetch top scores asynchronously
        await self.channel_layer.group_send(
            "leaderboard",
            {
                "type": "send_leaderboard",  # Call the `send_leaderboard` method
                "scores": scores,
            },
        )

    async def send_leaderboard(self, event):
        """
        Sends the updated leaderboard data to all connected WebSocket clients.
        """
        await self.send(text_data=json.dumps({"scores": event["scores"]}))  # Convert scores to JSON and send

    @sync_to_async
    def get_top_scores(self, Score):
        """
        Retrieves the top 10 scores from the database.
        - Orders them in descending order.
        - Formats the scores into a JSON-compatible list.
        """
        scores = Score.objects.order_by("-score")[:10]  # Get top 10 highest scores
        return [{"username": s.user.username, "score": s.score} for s in scores]  # Convert to a list of dictionaries

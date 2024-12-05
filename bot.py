import re
from botbuilder.core import ActivityHandler, TurnContext
from botbuilder.schema import ChannelAccount


class MyBot(ActivityHandler):
    def __init__(self):
        super(MyBot, self).__init__()
        self.points_table = {}  # Tracks points and emojis for users
        self.mentions_table = []  # Tracks mentions

    async def on_message_activity(self, turn_context: TurnContext):
        user_id = turn_context.activity.from_property.id
        user_name = turn_context.activity.from_property.name
        text = turn_context.activity.text or ""
        attachments = turn_context.activity.attachments

        # Initialize user in points table if not already present
        if user_id not in self.points_table:
            self.points_table[user_id] = {"name": user_name, "points": 0, "emojis": []}

        # Award points for image attachments
        if attachments:
            self.points_table[user_id]["points"] += 1

        # Check for emojis in the message
        emoji_pattern = re.compile(
            "[\U0001F600-\U0001F64F"  # Emoticons
            "\U0001F300-\U0001F5FF"  # Symbols & Pictographs
            "\U0001F680-\U0001F6FF"  # Transport & Map
            "\U0001F700-\U0001F77F"  # Alchemical Symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Supplemental Symbols
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"  # Enclosed Characters
            "]+",
            flags=re.UNICODE,
        )

        emojis_used = emoji_pattern.findall(text)
        if emojis_used:
            self.points_table[user_id]["points"] += len(emojis_used)
            self.points_table[user_id]["emojis"].extend(emojis_used)

        # Check for mentions
        if turn_context.activity.entities:
            for entity in turn_context.activity.entities:
                if entity.type == "mention":
                    mentioned_user = entity.get("mentioned", {})
                    mentioned_name = mentioned_user.get("name", "Unknown")
                    mentioned_id = mentioned_user.get("id", "Unknown")
                    self.mentions_table.append({
                        "mentioned_by": user_name,
                        "mentioned": mentioned_name,
                    })

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Welcome to the team!")

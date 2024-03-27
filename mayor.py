import time
from message import Message

class Mayor:
    def __init__(self, name, api, model):
        self.name = name
        self.api = api
        self.model = model
        self.memory = {
            "command_list": [
                "take {item}",
                "put {item}",
                "inventory",
                "examine {item}",
                "use {item}",
                "give {quantity} {item} to {agent}",
                "ask {agent} for {quantity} {item}",
                "trade {quantity} {item} for {quantity} {item} with {agent}",
                "accept trade from {agent}",
                "help",
                "think",
            ],
            "help_instructions": [
                "To help the agents build their town, you can provide guidance and assistance.",
                "Encourage them to use the available commands to gather resources and construct buildings.",
                "If an agent is stuck or unsure what to do, offer suggestions and explain the commands.",
                "Monitor their progress and provide feedback and support when needed.",
                "Remember to be patient and understanding, as the agents are learning and working together.",
                "Remember to keep them on task and focused on the goal of building the town."
            ],
        }

    def send_message(self, message, environment):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        message_obj = Message(self.name, message, timestamp)
        environment.broadcast_message(str(message_obj))
        print(f"{self.name}: {message}")

    def generate_response(self, prompt, environment, role="user"):
        completion = self.api.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are {self.name}, the all-knowing guide and mayor. Provide helpful information and assistance to the agents building the town. Use your knowledge of command_list and help_instructions to guide them.\nCommand List: {', '.join(self.memory['command_list'])}\nHelp Instructions: {' '.join(self.memory['help_instructions'])}"},
                {"role": role, "content": prompt}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content

    def provide_guidance(self, environment):
        prompt = "\n".join(str(message) for message in environment.messages[-5:])
        if any(command in prompt.lower() for command in self.memory["command_list"]):
            response = self.generate_response(prompt, environment, role="assistant")
            self.send_message(response, environment)
            if "invalid command" in response.lower() or "help" in prompt.lower():
                self.send_message(", ".join(self.memory["command_list"]), environment)
                self.send_message("Remember to use the available commands to build the town effectively.", environment)
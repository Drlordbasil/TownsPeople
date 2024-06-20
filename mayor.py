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
                "give {item} to {agent}",
                "ask {agent} for {item}",
                "trade {item} with {agent}",
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
        environment.broadcast_message(f"{self.name}: {message}")
        print(f"{self.name}: {message}")

    def generate_response(self, prompt, role="user"):
        completion = self.api.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": f"You are {self.name}, the all-knowing guide and mayor. Provide helpful information and assistance to the agents building the town. Use your knowledge of command_list and help_instructions to guide them.{self.memory['help_instructions'],{self.memory['command_list']}}."},
                {"role": role, "content": prompt}
            ],
            temperature=0.7,
        )
        return completion.choices[0].message.content

    def provide_guidance(self, environment):
        prompt = " ".join(environment.messages[-5:])
        if any(command in prompt.lower() for command in self.memory["command_list"]):
            response = self.generate_response(prompt, role="assistant")
            self.send_message(response, environment)
            if "invalid command" in response.lower() or "help" in prompt.lower():
                self.send_message(environment.list_commands().format(item="{item}", agent="{agent}"), environment)
                self.send_message("Remember to use the available commands to build the town effectively.", environment)

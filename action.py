from message import Message
from inventory import Inventory, InventoryItem

def update_inventory(agent, item_name, quantity, environment, action):
    if action == "take":
        if environment.remove_item(item_name, quantity):
            agent.inventory.add_item(item_name, quantity)
            agent.send_message(f"I took {quantity} {item_name} from the environment.", environment)
            agent.memory[f"took_{item_name}_{quantity}"] = True
            print(f"Agent {agent.name} took {quantity} {item_name} from the environment.")
        else:
            agent.send_message(f"Not enough {item_name} available in the environment.", environment)
    elif action == "put":
        if agent.inventory.remove_item(item_name, quantity):
            environment.add_item(item_name, quantity)
            agent.send_message(f"I put {quantity} {item_name} back in the environment.", environment)
            agent.memory[f"put_{item_name}_{quantity}"] = True
            print(f"Agent {agent.name} put {quantity} {item_name} back in the environment.")
        else:
            agent.send_message(f"I don't have enough {item_name} in my inventory.", environment)

def list_inventory(agent, environment):
    inventory_list = agent.inventory.list_inventory()
    if not agent.inventory.is_empty():
        agent.send_message(f"My inventory: {inventory_list}", environment)
        agent.memory["inventory"] = agent.inventory.to_dict()
        print(f"Agent {agent.name} listed their inventory: {inventory_list}")
    else:
        agent.send_message("My inventory is empty.", environment)
        agent.memory["inventory"] = Inventory().to_dict()

def examine_item(agent, item_name, environment):
    item = environment.get_item(item_name)
    if item:
        agent.send_message(f"Examining {item_name}: It is a {item.name}. Quantity: {item.quantity}.", environment)
        agent.memory[f"examined_{item_name}"] = item.to_dict()
        print(f"Agent {agent.name} examined {item_name}: {item}")
    else:
        agent.send_message(f"There is no {item_name} in the environment.", environment)

def use_item(agent, item_name, environment):
    item_quantity = agent.inventory.get_item_quantity(item_name)
    if item_quantity > 0:
        agent.inventory.remove_item(item_name, 1)
        agent.send_message(f"I used 1 {item_name} to build the town.", environment)
        agent.memory[f"used_{item_name}"] = True
        print(f"Agent {agent.name} used 1 {item_name} to build the town.")
    else:
        agent.send_message(f"I don't have any {item_name} in my inventory.", environment)

def give_item(agent, item_name, quantity, target_agent, environment):
    if agent.inventory.remove_item(item_name, quantity):
        target_agent.inventory.add_item(item_name, quantity)
        agent.send_message(f"I gave {quantity} {item_name} to {target_agent.name}.", environment)
        target_agent.send_message(f"I received {quantity} {item_name} from {agent.name}.", environment)
        agent.memory[f"gave_{item_name}_{quantity}_to_{target_agent.name}"] = True
        target_agent.memory[f"received_{item_name}_{quantity}_from_{agent.name}"] = True
        print(f"Agent {agent.name} gave {quantity} {item_name} to {target_agent.name}.")
    else:
        agent.send_message(f"I don't have enough {item_name} to give.", environment)

def ask_for_item(agent, item_name, quantity, target_agent, environment):
    agent.send_message(f"{target_agent.name}, can I have {quantity} {item_name} please?", environment)
    agent.memory[f"asked_{target_agent.name}_for_{item_name}_{quantity}"] = True
    print(f"Agent {agent.name} asked {target_agent.name} for {quantity} {item_name}.")

def trade_item(agent, item_name, quantity, target_item, target_quantity, target_agent, environment):
    if agent.inventory.get_item_quantity(item_name) >= quantity and target_agent.inventory.get_item_quantity(target_item) >= target_quantity:
        agent.send_message(f"{target_agent.name}, would you like to trade {quantity} {item_name} for {target_quantity} {target_item}?", environment)
        agent.memory[f"proposed_trade_{quantity}_{item_name}_for_{target_quantity}_{target_item}_with_{target_agent.name}"] = True
        print(f"Agent {agent.name} proposed a trade with {target_agent.name}: {quantity} {item_name} for {target_quantity} {target_item}.")
    else:
        agent.send_message(f"I don't have enough {item_name} or {target_agent.name} doesn't have enough {target_item} for the trade.", environment)

def accept_trade(agent, item_name, quantity, target_item, target_quantity, target_agent, environment):
    if agent.inventory.remove_item(item_name, quantity) and target_agent.inventory.remove_item(target_item, target_quantity):
        agent.inventory.add_item(target_item, target_quantity)
        target_agent.inventory.add_item(item_name, quantity)
        agent.send_message(f"I accepted the trade with {target_agent.name}. I gave {quantity} {item_name} and received {target_quantity} {target_item}.", environment)
        target_agent.send_message(f"I accepted the trade with {agent.name}. I gave {target_quantity} {target_item} and received {quantity} {item_name}.", environment)
        agent.memory[f"accepted_trade_{quantity}_{item_name}_for_{target_quantity}_{target_item}_with_{target_agent.name}"] = True
        target_agent.memory[f"accepted_trade_{target_quantity}_{target_item}_for_{quantity}_{item_name}_with_{agent.name}"] = True
        print(f"Agent {agent.name} and {target_agent.name} accepted the trade: {quantity} {item_name} for {target_quantity} {target_item}.")
    else:
        agent.send_message(f"The trade with {target_agent.name} couldn't be completed due to insufficient items.", environment)

def move(agent, new_position, environment, shared_grid, shared_grid_lock):
    with shared_grid_lock:
        if environment.is_valid_position(new_position):
            old_position = agent.position
            print(f"Agent {agent.name} moved from {old_position} to {new_position}")

            if old_position is not None:
                shared_grid[old_position[0] * environment.grid_size[1] + old_position[1]] = 0

            environment.update_agent_position(agent, new_position)
            shared_grid[new_position[0] * environment.grid_size[1] + new_position[1]] = 1
            agent.position = new_position
            agent.send_message(f"I moved to {new_position}.", environment)
        else:
            agent.send_message(f"Cannot move to {new_position}. Position is not valid.", environment)
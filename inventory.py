# inventory.py

class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item_name, quantity):
        existing_item = next((item for item in self.items if item["name"] == item_name), None)
        if existing_item:
            existing_item["quantity"] += quantity
        else:
            self.items.append({"name": item_name, "quantity": quantity})

    def remove_item(self, item_name, quantity):
        item = next((item for item in self.items if item["name"] == item_name), None)
        if item:
            if item["quantity"] >= quantity:
                item["quantity"] -= quantity
                if item["quantity"] == 0:
                    self.items.remove(item)
                return True
            else:
                return False
        else:
            return False

    def get_item_quantity(self, item_name):
        item = next((item for item in self.items if item["name"] == item_name), None)
        return item["quantity"] if item else 0

    def list_inventory(self):
        return ", ".join(f"{item['name']} ({item['quantity']})" for item in self.items)

    def is_empty(self):
        return len(self.items) == 0
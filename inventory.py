class InventoryItem:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

    def __str__(self):
        return f"{self.name} ({self.quantity})"

    def to_dict(self):
        return {
            "name": self.name,
            "quantity": self.quantity
        }

    @classmethod
    def from_dict(cls, item_dict):
        return cls(
            name=item_dict["name"],
            quantity=item_dict["quantity"]
        )

class Inventory:
    def __init__(self):
        self.items = []

    def add_item(self, item_name, quantity):
        item = next((item for item in self.items if item.name == item_name), None)
        if item:
            item.quantity += quantity
        else:
            self.items.append(InventoryItem(item_name, quantity))

    def remove_item(self, item_name, quantity):
        item = next((item for item in self.items if item.name == item_name), None)
        if item:
            if item.quantity >= quantity:
                item.quantity -= quantity
                if item.quantity == 0:
                    self.items.remove(item)
                return True
        return False

    def get_item_quantity(self, item_name):
        item = next((item for item in self.items if item.name == item_name), None)
        return item.quantity if item else 0

    def list_inventory(self):
        return ", ".join(str(item) for item in self.items)

    def is_empty(self):
        return len(self.items) == 0

    def to_dict(self):
        return {
            "items": [item.to_dict() for item in self.items]
        }

    @classmethod
    def from_dict(cls, inventory_dict):
        inventory = cls()
        inventory.items = [InventoryItem.from_dict(item_dict) for item_dict in inventory_dict["items"]]
        return inventory

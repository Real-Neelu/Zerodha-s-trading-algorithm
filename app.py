from dataclasses import dataclass
import flask

TICKER = "GOOGLE"

users = {
    "1" : {"balances" : {TICKER: 10, "USD" : 50000}},
    "2" : {"balances" : {TICKER: 10, "USD" : 50000}}
}

@dataclass
class Order:
     user_id: str
     price: float
     quantity: int
     side: str

bids: list[Order] = []
asks: list[Order] = []

app = flask.Flask(__name__)

@app.route ("/balance/<user_id>") 
def get_balance(user_id : str):
     user = users.get(user_id)
     if not user:
          return flask.jsonify({"msg": "user not found"}), 404
     return flask.jsonify(user["balances"])

@app.route ("/depth")    
def get_depth():
     depth = {
          "bids": [{"price": order.price, "quantity": order.quantity} for order in bids],
          "asks": [{"price": order.price, "quantity": order.quantity} for order in asks],
    }
     return flask.jsonify(depth)

@app.route("/order", methods = ["POST"])
def place_order():
     data = flask.request.json
     user_id = data.get("user_id")
     side = data.get("side")
     price = data.get("price")
     quantity = data.get("quantity")

     if user_id not in users:
          return flask.jsonify({"msg": "user not found"}), 404
     
     rem_quantity = match_order(user_id, price, quantity, side)
     if rem_quantity == 0:
          return flask.jsonify({'filledQuantity': quantity})
     

     order = Order( user_id, float(price), int(rem_quantity), side)

     if side == "bid": 
          bids.append(order)
          bids.sort(key=lambda o: o.price, reverse=True)
     elif side == "ask":
          asks.append(order)
          bids.sort(key=lambda o: o.price)
     else:
          return flask.jsonify({"msg": "Invalid side"}), 404
     

     print(data)

@app.route("/orders/<user_id>")
def flip_balances(user_id1: str, user_id2: str, quantity: int, price: float):
    user1 = users.get(user_id1)
    user2 = users.get(user_id2)

    if not user1 or not user2:
        return
    user1["balances"][TICKER] -= quantity
    user2["balances"][TICKER] += quantity
    user1["balances"]["USD"] += (quantity * price)
    user2["balances"]["USD"] -= (quantity * price)
    return


@app.route("/match_order")
def match_order(user_id:str , price:float , quantity:int , side:str):
     remaining_quantity = quantity
     if side == "bid":
          for order in asks:
               if order.price < price:
                    continue
               if order.price > price:
                    order.quantity -= remaining_quantity
                    flip_balances(order.user_id, user_id, remaining_quantity, order.price)
                    return
               else:
                    remaining_quantity -= order.quantity
                    flip_balances(order.user_id, user_id, order.quantity, order.price)
                    asks.pop()

     else:
          for order in bids:
               if order.price < price:
                    continue
               if order.price > price:
                    order.quantity -= remaining_quantity
                    flip_balances(order.user_id, user_id, remaining_quantity, order.price)
                    return
               else:
                    remaining_quantity -= order.quantity
                    flip_balances(order.user_id, user_id, order.quantity, order.price)
                    bids.pop()

     return remaining_quantity
     

if __name__ == "__main__":
    app.run()


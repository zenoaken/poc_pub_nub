from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from os import environ

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

SUBSCRIBE_KEY = 'sub-c-bcf3d5e6-4091-11e7-87db-02ee2ddab7fe'
PUBLISH_KEY = 'pub-c-21c8cf90-1313-4447-9051-39216f1cbfd4'

pnconfig = PNConfiguration()
pnconfig.subscribe_key = SUBSCRIBE_KEY
pnconfig.publish_key = PUBLISH_KEY
pubnub = PubNub(pnconfig)


@app.route("/")
def index():
    return "Agent Presence Test Server With Pub Nub"

@app.route('/app')
def app_page():
    return render_template('app.html')


@app.route("/api/user/<username>")
def user(username):
    presence = {
        "resources": [],
        "channels": []
    }
    result = {
        "uuid": username,
        "presence": presence
    }

    for channel in pubnub.where_now().uuid(username).sync().result.channels:
        if channel.startswith("users-on-product-"):
            presence["channels"].append(channel.split("-")[-1])
        elif channel.startswith("users-on-resource-"):
            presence["resources"].append(channel.split("-")[-1])

    return jsonify(result)


@app.route("/api/resource/<type>/<id>/presence")
def users_in_resource(type, id):
    return jsonify(users_statuses_in_channel("users-on-resource-%s" % id))


@app.route("/api/product/<product>/presence")
def user_in_channel(product):
    return jsonify(users_statuses_in_channel("users-on-product-%s" % product))


def users_statuses_in_channel(channel):
    occupants = filter(
            lambda x: x.channel_name == channel,
            pubnub.here_now().channels(channel).include_state(True).sync().result.channels
        )[0].occupants

    return map(lambda x: {"uuid": x.uuid, "state": x.state}, occupants)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=environ.get("PORT", 5000))

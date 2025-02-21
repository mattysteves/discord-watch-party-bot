import os
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands
import random
import json


load_dotenv()
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
WATCHLISTFILENAME = "watchlist.json"
# 8 = Admin
# 1024 = View Channel (Pretty much everyone)
EDIT_PERMISSION = 1024
# Called once bot is ready for further action.
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(guild_ids=[GUILD_ID], name="ping", description="pongs the user")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.slash_command(guild_ids=[GUILD_ID], name="popcorn", description="scoop some popcorn!")
async def popcorn(interaction: nextcord.Interaction):
    popcorn = random.randint(1, 100)
    kernels = random.randint(0, popcorn)
    response = f"{interaction.user.display_name} scooped {popcorn} bits of popcorn, "
    if kernels == 0:
        response += "and no kernels! :popcorn:"
        if popcorn == 100:
            response += " NOW THAT'S A BUTTERY BUCKET :butter:"
    elif kernels == popcorn:
        response += "but ALL OF THEM ARE JUST KERNELS :skull:"
    else:
        response += f"but {kernels} of them are just kernels!"
    await interaction.response.send_message(response)

# Help Command

@bot.slash_command(guild_ids=[GUILD_ID], name="help", description="lists all commands and descriptions")
async def help(interaction: nextcord.Interaction):
    response = "Here are all of my commands:\n\n"
    response += "/watchlist_create \n- create a new watchlist\n\n"
    response += "/watchlist_delete \n- delete an existing watchlist\n\n"
    response += "/watchlist_delete_all \n- delete all existing watchlists\n\n"
    response += "/watchlist_see_all \n- see all watchlists\n\n"
    response += "/watchlist_add \n- add a movie or show to a watchlist\n\n"
    response += "/watchlist_delete_media \n- remove a movie or show from a watchlist\n\n"
    response += "/watchlist_clear \n- remove all media from a watchlist\n\n"
    response += "/watchlist_view \n- view the contents of a wishlist\n\n"
    response += "/watchlist_join \n- join an existing watchlist\n\n"
    response += "/watchlist_leave \n- leave from a joined watchlist\n\n"
    response += "/watchlist_participants \n- view a watchlist's participants\n\n"
    response += "/watchlist_notifyall \n- notify all participants of a watchlist\n\n"
    response += "/watchlist_choose \n- select a random item from a watchlist\n\n"
    await interaction.response.send_message(response)


# ---------------------------------------------------------------------------
# Watchlist Commands - Create, delete and see watchlists
# ---------------------------------------------------------------------------

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_see_all", description="see all watchlists")
async def watchlist_see_all(interaction: nextcord.Interaction):

    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    if len(watchlist_data["watchlists"]) == 0: #Respond if there are no watchlists
        response = "You have no watchlists right now, create a watchlist with /watchlist_create and you will see it here!"
    else:
        response = "Here are all of your watchlists!\n\n"
        for watchlist in watchlist_data["watchlists"]: #Print every watchlist
            name = watchlist["name"]
            response += f"{name}\n"
            if len(watchlist["media"]) == 0: #Respond if watchlist has no media
                response += "- There are no items in this watchlist right now\n"
            else:
                for media in watchlist["media"]: #Print every media item
                    response += f"- {media}\n"
            response += "\n\n"

    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_create", 
                   description="create a new watchlist",
                   default_member_permissions=EDIT_PERMISSION)
async def watchlist_create(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist lists
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Check if the watchlist exists already
    watchlist_exists = False
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            watchlist_exists = True

    # Only create the watchlist if it does not already exist
    if watchlist_exists:
        response = f"A watchlist named {watchlist_name} already exists!"
    else:
        # write in the new watchlist to the json
        watchlist_data["watchlists"].append({'name': watchlist_name, 'media': [], 'participants': []})
        watchlist_file = open(WATCHLISTFILENAME, 'w')
        watchlist_file.write(json.dumps(watchlist_data))
        watchlist_file.close()
        response = f"Created a new watchlist named {watchlist_name}. Add movies and shows to your new watchlist!"

    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], 
                   name="watchlist_delete_all", 
                   description="delete all existing watchlists", 
                   default_member_permissions=EDIT_PERMISSION)
async def watchlist_delete_all(interaction: nextcord.Interaction):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    if len(watchlist_data["watchlists"]) == 0:
        response = "There are no watchlists for me to delete ¯\_(ツ)_/¯"
    else:
        watchlist_file = open(WATCHLISTFILENAME, 'w')
        watchlist_file.write(json.dumps({"watchlists": []}))
        watchlist_file.close()
        response = "Removed all watchlists, use /watchlist_create to make a new one!"

    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_delete", 
                   description="delete an existing watchlist",
                   default_member_permissions=EDIT_PERMISSION)
async def watchlist_delete(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Find watchlist
    found = 0
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            found = 1
            watchlist_data["watchlists"].remove(watchlist)
            watchlist_file = open(WATCHLISTFILENAME, 'w')
            watchlist_file.write(json.dumps(watchlist_data))
            watchlist_file.close()
            response = f"Removed watchlist named {watchlist_name}."

    if not found:
        response = f"Watchlist named {watchlist_name} does not exist"
    await interaction.response.send_message(response)


# ---------------------------------------------------------------------------
# Media Commands - Add media to watchlist
# ---------------------------------------------------------------------------

@bot.slash_command(guild_ids=[GUILD_ID],
                   name="watchlist_add",
                   description="add a movie or show to a watchlist",
                   default_member_permissions=EDIT_PERMISSION)
async def watchlist_add(interaction: nextcord.Interaction, media_name, watchlist_name):
    """
    Adds a movie or show to a specified watchlist.

    Parameters:
    interaction (nextcord.Interaction): The interaction object representing the command invocation.
    media_name (str): The name of the movie or show to be added.
    watchlist_name (str): The name of the watchlist to which the movie or show will be added.

    Returns:
    None
    """
    # Read the JSON data
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Check if the watchlist exists
    watchlist_exists = False
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            watchlist_exists = True
            # Check if media already exists in watchlist
            if media_name not in watchlist["media"]:
                watchlist["media"].append(media_name)
                response = f"Added *{media_name}* to the **{watchlist_name}** watchlist!"
            else:
                response = f"*{media_name}* is already in the **{watchlist_name}** watchlist!"
            break

    if not watchlist_exists:
        response = f"The **{watchlist_name}** watchlist does not exist! \nYou can create it with `/watchlist_create {watchlist_name}`"

    # Write the updated JSON data
    watchlist_file = open(WATCHLISTFILENAME, 'w')
    watchlist_file.write(json.dumps(watchlist_data))
    watchlist_file.close()

    await interaction.response.send_message(response)


# ---------------------------------------------------------------------------
# Media Commands - Remove media from watchlist
# ---------------------------------------------------------------------------

@bot.slash_command(guild_ids=[GUILD_ID],
                   name="watchlist_delete_media",
                   description="remove a movie or show from a watchlist",
                   default_member_permissions=EDIT_PERMISSION)
async def watchlist_delete_media(interaction: nextcord.Interaction, media_name, watchlist_name):
    """
    Removes a movie or show from a specified watchlist.

    Parameters:
    interaction (nextcord.Interaction): The interaction object representing the command invocation.
    media_name (str): The name of the movie or show to be removed.
    watchlist_name (str): The name of the watchlist from which the movie or show will be removed.

    Returns:
    None
    """
    # Read the JSON data
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Check if the watchlist exists
    watchlist_exists = False
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            watchlist_exists = True
            # Check if media exists in watchlist
            if media_name in watchlist["media"]:
                watchlist["media"].remove(media_name)
                response = f"Removed *{media_name}* from the **{watchlist_name}** watchlist!"
            else:
                response = f"*{media_name}* is not in the **{watchlist_name}** watchlist!"
            break

    if not watchlist_exists:
        response = f"The **{watchlist_name}** watchlist does not exist!"

    # Write the updated JSON data
    watchlist_file = open(WATCHLISTFILENAME, 'w')
    watchlist_file.write(json.dumps(watchlist_data))
    watchlist_file.close()

    await interaction.response.send_message(response)
    
    
# ---------------------------------------------------------------------------
# Media Commands - Select a random media from watchlist
# ---------------------------------------------------------------------------

@bot.slash_command(guild_ids=[GUILD_ID],
                   name="watchlist_choose",
                   description="select a random item from a watchlist")
async def watchlist_choose(interaction: nextcord.Interaction, watchlist_name):

    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    watchlist_exists = False

    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            watchlist_exists = True
            watchlist_length = len(watchlist["media"])
            if watchlist_length == 0:
                response = f"The **{watchlist_name}** watchlist is empty. \nYou can add items to it using '/watchlist_add <media_name> {watchlist_name}'"
            else:
                selected_media = random.choice(watchlist["media"])
                response = f"Let's watch **{selected_media}** \nTime to get out the popcorn!"


    if not watchlist_exists:
        response = f"The **{watchlist_name}** watchlist does not exist! \nYou can create it with `/watchlist_create {watchlist_name}`"

    await interaction.response.send_message(response)


# ---------------------------------------------------------------------------
# Media Commands - Clear a specified watchlist by removing all its media
# ---------------------------------------------------------------------------

@bot.slash_command(guild_ids=[GUILD_ID],
                   name="watchlist_clear",
                   description="remove all media from a watchlist")
async def watchlist_clear(interaction: nextcord.Interaction, watchlist_name):

    # Read the JSON data
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Find the watchlist
    found = False
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            found = True
            if len(watchlist["media"]) == 0:
                response = f"The **{watchlist_name}** watchlist is already empty."
            else:
                watchlist["media"] = []  # Clear the media list
                response = f"Cleared all media from the **{watchlist_name}** watchlist."

            # Write the updated JSON data
            watchlist_file = open(WATCHLISTFILENAME, 'w')
            watchlist_file.write(json.dumps(watchlist_data))
            watchlist_file.close()
            break

    if not found:
        response = f"Watchlist named {watchlist_name} does not exist."

    await interaction.response.send_message(response)

# ---------------------------------------------------------------------------
# Participant Commands - Join, leave, view or notifty watchlist participants
# ---------------------------------------------------------------------------

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_join", description="join an existing watchlist")
async def watchlist_join(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    #add participant to watchlist
    user_id = interaction.user.id
    found = 0
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            found = 1
            #check duplication
            if (user_id in watchlist["participants"]):
                response = "You are already in this watchlist."
                break
            else:
                watchlist["participants"].append(user_id)
                #write the change to json
                watchlist_file = open(WATCHLISTFILENAME, 'w')
                watchlist_file.write(json.dumps(watchlist_data))
                watchlist_file.close()
                response = f"You have joined the {watchlist_name} watchlist."
                break

    if not found:
        response = f"Watchlist named {watchlist_name} does not exist"
    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_leave", description="leave from a joined watchlist")
async def watchlist_leave(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Check if the watchlist exists
    user_id = interaction.user.id
    found = 0
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            found = 1
            # Check if user id is in the participants list
            if (user_id in watchlist["participants"]):
                watchlist["participants"].remove(user_id)
                #write the change to json
                watchlist_file = open(WATCHLISTFILENAME, 'w')
                watchlist_file.write(json.dumps(watchlist_data))
                watchlist_file.close()
                response = f"You have been removed from the {watchlist_name} watchlist."
                break
            else:
                response = "You are not currently in this watchlist"
                break

    if not found:
        response = f"Watchlist named {watchlist_name} does not exist"
    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_participants", description="view a watchlist's participants")
async def watchlist_participants(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Find watchlist
    found = 0
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            found = 1
            # Print Members
            response = f"Participants of {watchlist_name} watchlist:\n"
            for user_id in watchlist["participants"]:
                user = await bot.fetch_user(user_id) # This is an api call, must use await then get the name component step by step
                user_name = user.name
                response += "- " + user_name + "\n"
            if len(watchlist["participants"]) == 0:
                response = f"There are no participants in {watchlist_name} yet  :("

    if not found:
        response = f"Watchlist named {watchlist_name} does not exist"
    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_notifyall", description="notify all participants of a watchlist")
async def watchlist_notifyall(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    #add participant to watchlist
    found = 0
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            found = 1
            mentions = ' '.join(f'<@{user_id}>' for user_id in watchlist["participants"]) #Generate string of mentions in space-separated manner
            response = f'A watch party for the {watchlist_name} watchlist is starting soon! {mentions}'

    if not found:
        response = f"Watchlist named {watchlist_name} does not exist"
    await interaction.response.send_message(response)

bot.run(BOT_TOKEN)

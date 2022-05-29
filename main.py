from discord import Client, utils, member, Embed
import cfg
import random
import datetime
import traceback

client = Client()
token = cfg.token
random.seed()

async def get_movies():
    movies = dict()
    movie_channel = client.get_channel(cfg.movie_channel)
    messages = await movie_channel.history(limit=10000).flatten()
    for message in messages:
        skip = False
        votes = 0
        karma = False
        for reaction in message.reactions:
            if str(reaction.emoji) == '✅':
                skip = True
            if str(reaction.emoji) == '👍':
                votes += reaction.count
            if str(reaction.emoji) == '❤️':
                votes += reaction.count
                karma = True
        if not skip:
            if votes not in movies.keys():
                movies[votes] = {}
            movies[votes][message.id] = {'movie': message.content, 'karma': karma}
    return movies

async def pick_movies(channel, movies, count):
    movie_channel = client.get_channel(cfg.movie_channel)
    vote_counts = list(movies.keys())
    pick = 0
    while pick < count:
        pick += 1
        most_votes = max(vote_counts)
        candidates = movies[most_votes]
        choice = random.choice(list(candidates.keys()))
        message_link = "https://discord.com/channels/" + \
                       str(channel.guild.id) + '/' + str(movie_channel.id) + '/' + str(choice)
        embed = Embed()
        if candidates[choice]['karma']:
            embed.description = "Movie pick {0} is [{1}]({3}) with {2} votes using **KARMA**!".format(
                pick, candidates[choice]['movie'], most_votes, message_link)
        else:
            embed.description = "Movie pick {0} is [{1}]({3}) with {2} votes".format(
                pick, candidates[choice]['movie'], most_votes, message_link)
        await channel.send(embed=embed)
        del(movies[most_votes][choice])
        if len(list(movies[most_votes].keys())) == 0:
            del(movies[most_votes])
            vote_counts.remove(most_votes)

@client.event
async def on_message(message):
    try:
        if message.channel.id not in cfg.query_channels:
            return

        if message.content.lower().startswith('!mc'):
            if message.content.lower().startswith('!mc pick'):
                parts = message.content.split(' ', 2)
                if len(parts) != 3:
                    await message.channel.send("The correct command is:\n"
                                               "!mc pick [number of movies]")
                    return
                movies = await get_movies()
                await pick_movies(message.channel, movies, int(parts[2]))

            else:
                await message.channel.send("MovieCritic Commands:\n"
                                           "!mc pick [number of movies] - Pick the top X movies")


    except:
        print(str(datetime.datetime.utcnow()) + '\n' + traceback.format_exc())

client.run(token)
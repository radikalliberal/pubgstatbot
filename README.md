# pubgstatbot
A discord-Bot that presents stats for Players.

Things you have to do befor you can use the bot:

go to https://discordapp.com/developers/applications/me
and register an Application then create a bot user, like ![so](registerbot.png?raw=true)
you will get a **token** and **client-id** that is necessary for the program to work
the you can invite the bot to your server with

    https://discordapp.com/oauth2/authorize?client_id=**client-id**&scope=bot&permissions=36703232

you have to put your **client-id** into the url to make it work

also you have to register at http://pubgtracker.com and get an **API-KEY**

start bot with:

  **python main.py %DISCORD-BOT-TOKEN% %PUBGTRACKER.COM-API-KEY%**
  have fun


# Commandlist

## ?stats region match "stat" 
*graph of change in the chosen stat over time, for one or more players.
Only available if players are subscribed. Also data has to be aquired first for some time.*

    possible parameters:
    region = ['eu', 'na', 'as', 'sa', 'agg']
    match = ['solo', 'duo', 'squad']
    stats <- if multiple word the quotes are needed = ['k/d ratio', 'win %', 'time survived', 
            'win top 10 ratio', 'top 10s', 'top 10 ratio', 'losses', 'rating', 'best rating', 
            'damage pg', 'headshot kills pg', 'heals pg', 'kills pg', 'move distance pg', 
            'revives pg', 'road kills pg', 'team kills pg', 'time survived pg', 'top 10s pg', 
            'kills', 'assists', 'suicides', 'team kills', 'headshot kills', 'headshot kill ratio', 
            'vehicle destroys', 'road kills', 'daily kills', 'weekly kills', 'round most kills', 
            'max kill streaks', 'days', 'longest time survived', 'most survival time', 
            'avg survival time', 'win points', 'walk distance', 'ride distance', 'move distance', 
            'avg walk distance', 'avg ride distance', 'longest kill', 'heals', 'revives', 
            'boosts', 'damage dealt', 'dbnos', 'rounds played', 'wins']

    example: ?stats agg squad "Longest Kill"
    
## ?progression players match "stat" [region [season]]
*ranking of all subscribed players*

    possible parameters:
    players = one or more subscribed players, separated by colon
    region = ['eu', 'na', 'as', 'sa', 'agg']
    match = ['solo', 'duo', 'squad']
    seasons = ['2017-pre2']
    "stat" <- if multiple words the quotes are needed = ['k/d ratio', 'win %', 
            'time survived', 'rounds played', 'wins', 'win top 10 ratio', 'top 10s', 
            'top 10 ratio', 'losses', 'rating', 'best rating', 'damage pg', 'headshot kills pg', 
            'heals pg', 'kills pg', 'move distance pg', 'revives pg', 'road kills pg', 
            'team kills pg', 'time survived pg', 'top 10s pg', 'kills', 'assists', 'suicides', 
            'team kills', 'headshot kills', 'headshot kill ratio', 'vehicle destroys', 
            'road kills', 'daily kills', 'weekly kills', 'round most kills', 'max kill streaks', 
            'days', 'longest time survived', 'most survival time', 'avg survival time', 
            'win points', 'walk distance', 'ride distance', 'move distance', 'avg walk distance', 
            'avg ride distance', 'longest kill', 'heals', 'revives', 'boosts', 'damage dealt', 'dbnos'] 

    example: ?progression crazy_,DrDisRespect squad  "Longest Kill"
            
## ?subscribe player
*tracking for playerstats starts when a player is subscribed*

    possible parameters:
    player = some playername in pubg
    
    example: ?subscribe DrDisRespect
    
## ?unsubscribe
*tracking for playerstats stops when a player is unsubscribed, old stats are kept bnut hidden*

    possible parameters:
    player = some playername in pubg
    
    example: ?subscribe DrDisRespect
    
## ?subscribers
*givs a list of subscribed players*

    possible parameters:
    None
    
    example: ?subscribers

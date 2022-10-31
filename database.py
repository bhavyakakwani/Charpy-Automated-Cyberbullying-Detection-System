import discord
import mysql.connector
import os
import json
import datetime

if os.path.exists(os.getcwd() + "/config.json"):
    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Password": ""}
    with open(os.getcwd() + "/config.json", "w+") as f:
        json.dump(configTemplate, f) 

PASSWORD = configData["Password"]

def create_database():
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD
    )
    cursor = db.cursor()
    cursor.execute("create database if not exists charpy")
    db.close()

    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("""create table if not exists message_classification(
        message varchar(300) not null,
        predicted varchar(20),
        actual varchar(20)
    )""")
    cursor.execute("""create table if not exists warnings(
        warn_id int unsigned not null auto_increment,
        author_id bigint not null,
        server_id bigint not null,
        message varchar(300) not null,
        type varchar(20) not null,
        primary key(warn_id)
    )""")
    cursor.execute("""create table if not exists logs(
        server_id bigint not null,
        channel_id bigint not null,
        logging bool not null
    )""")
    cursor.execute("""create table if not exists tempban(
        user_id bigint not null,
        server_id bigint not null,
        start_time timestamp not null,
        duration int unsigned not null
    )""")
    cursor.execute("""create table if not exists tempmute(
        user_id bigint not null,
        server_id bigint not null,
        start_time timestamp not null,
        duration int unsigned not null
    )""")
    db.commit()
    db.close()

def check(guild):
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    cursor.execute("""select * from logs where server_id = %s""", (guild.id,))
    result = cursor.fetchall()
    db.close()
    return result

async def tempcheck(bot):
    db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = PASSWORD,
        database = "charpy"
    )
    cursor = db.cursor()
    current_time = datetime.datetime.now()
    current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""select user_id, server_id from tempmute where timestampdiff(second, start_time, %s) >= duration""", (current_time,))
    result1 = cursor.fetchall()
    cursor.execute("""select user_id, server_id from tempban where timestampdiff(second, start_time, %s) >= duration""", (current_time,))
    result2 = cursor.fetchall()
    cursor.execute("""delete from tempmute where timestampdiff(second, start_time, %s) >= duration""", (current_time,))
    cursor.execute("""delete from tempban where timestampdiff(second, start_time, %s) >= duration""", (current_time,))
    db.commit()
    db.close()
    if result1:
        for i in result1:
            guild = bot.get_guild(i[1])
            member = guild.get_member(i[0])
            mutedRole = discord.utils.get(guild.roles, name = "Muted")
            await member.remove_roles(mutedRole)
            result = check(guild)
            if result and result[0][2] == 1:
                embed = discord.Embed(title = "Member Unmuted", color = discord.Color.green())
                if member.avatar == None:
                    url = member.default_avatar_url
                else:
                    url = member.avatar_url
                embed.set_thumbnail(url = url)
                embed.add_field(name = "Member", value = member.mention, inline = False)
                embed.add_field(name = "Moderator", value = "<@931933313847939072>", inline = False)
                channel = discord.utils.get(bot.get_all_channels(), id = result[0][1])
                await channel.send(embed = embed)
    if result2:
        for i in result2:
            guild = bot.get_guild(i[1])
            user = await bot.fetch_user(i[0])
            await guild.unban(user)
            result = check(guild)
            if result and result[0][2] == 1:
                embed = discord.Embed(title = "Member Unbanned", color = discord.Color.green())
                if user.avatar == None:
                    url = user.default_avatar_url
                else:
                    url = user.avatar_url
                embed.set_thumbnail(url = url)
                embed.add_field(name = "Member", value = user.mention, inline = False)
                embed.add_field(name = "Moderator", value = "<@931933313847939072>", inline = False)
                channel = discord.utils.get(bot.get_all_channels(), id = result[0][1])
                await channel.send(embed = embed)
import os
import random
from typing_extensions import Self
from winreg import DeleteValue

import discord
from dotenv import load_dotenv
from discord.ext import commands


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="pixie ")

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    
@bot.event
async def on_message(message):
    await bot.process_commands(message)
    
    if message.author.bot:
        return 
    '''await message.channel.send("detect")'''

@bot.command(name='blackjack')
async def black_jack(ctx):
    msg = await ctx.send("게임 시작")
    
    await ctx.send("덱을 섞는 중...")
    deck = []
    for i in range(13):
        for j in range(4):
            deck.append(i)
            
    for i in range(52):
        tpos = random.randint(0,52-i)
        tmp = deck[tpos]
        deck[tpos] = deck[51-i]
        deck[51-i] = tmp
            
    dealer_cards = [deck[0]]
    player_cards = [deck[1],deck[2]]
    
    nowCardNum = 3
    
    async def show_board(channel, dealer_cards, player_cards): 
        
        def cardCalc(cards):
            show = ['🇦','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟','🇯','🇶','🇰']
            a = 0
            sum = 0
            str = ""
                
            for card in cards:
                str += show[card] + " "
                if card == 0:
                    a +=1
                if card >= 10 :
                    card = 9
                sum += (card+1)
            
            while a>0:
                if sum <=11:
                    sum += 10
                    a -= 1
                else:
                    break
            
            str += "\n합계 : " + str(sum)
            
            return str, sum
    
        dstr, dsum = cardCalc(dealer_cards)
        pstr, psum = cardCalc(player_cards)
        
        embed = discord.Embed(title = "blackjack")
        embed.add_field(name="딜러의 패", value=dstr, inline=False)
        embed.add_field(name="플레이어의 패", value=pstr, inline=False)
        
        ret = await channel.send(embed = embed)
    
        return ret
    
    board = await show_board(msg.channel,dealer_cards,player_cards)
    
    reaction_list = ['✅','🛑']
    for r in reaction_list:
        await board.add_reaction(r)
    def author_check(reaction, user) : 
        return str(reaction) in reaction_list and user == ctx.author and reaction.message.id == msg.id
    

bot.run(TOKEN)

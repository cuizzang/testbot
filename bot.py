import os
import random
import asyncio
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
    show = ['🇦','2️⃣','3️⃣','4️⃣','5️⃣','6️⃣','7️⃣','8️⃣','9️⃣','🔟','🇯','🇶','🇰']
    
    async def shuffle_deck():
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
        
        return deck
    
    deck = await shuffle_deck()
    
    nowCardNum = 0
    dsum = da = psum = pa = 0
    dstr = pstr = ""
    
    async def hit_card(deck,nowCardNum,tsum,ta,tstr):
        if nowCardNum == 52:
            await shuffle_deck()
            nowCardNum = 0
        
        tmp = deck[nowCardNum]
        nowCardNum+=1
        tstr += show[tmp] + " "
        if tmp == 0 and ta == 0:
            ta = 1
        if tmp >=10:
            tmp = 9
        tsum += tmp+1
        
        if tsum<12 and ta == 1:
            ta=2
            tsum+=10
        elif tsum>21 and ta == 2:
            ta=1
            tsum-=10
        return nowCardNum,tsum,ta,tstr 
        
    nowCardNum,dsum,da,dstr = await hit_card(deck,nowCardNum,dsum,da,dstr)
    nowCardNum,psum,pa,pstr = await hit_card(deck,nowCardNum,psum,pa,pstr)
    nowCardNum,psum,pa,pstr = await hit_card(deck,nowCardNum,psum,pa,pstr)
    
    embed = discord.Embed(title = "blackjack")
    
    async def show_board(channel): 
        embed.clear_fields()
        embed.add_field(name="딜러의 패", value=(dstr+"합계 : "+str(dsum)), inline=False)
        embed.add_field(name="플레이어의 패", value=(pstr+"합계 : "+str(psum)), inline=False)
        
        ret = await channel.send(embed = embed)
    
        return ret
    
    board = await show_board(msg.channel)
    
    reaction_list = ['✅','🛑']
    for r in reaction_list:
        await board.add_reaction(r)
        
    def author_check(reaction, user) : 
        return str(reaction) in reaction_list and user == ctx.author and reaction.message.id == board.id
    
    while(True):
        try:
            reaction, _user = await bot.wait_for("reaction_add", check = author_check, timeout= 120.0)
        except asyncio.TimeoutError:
            await ctx.send("시간초과 되었습니다.")
            return
        else:
            pass
        
        if str(reaction)=='✅':
            nowCardNum,psum,pa,pstr = await hit_card(deck,nowCardNum,psum,pa,pstr)
            embed.set_field_at(1,name="플레이어의 패", value=(pstr+"합계 : "+str(psum)), inline=False)
            await board.edit(embed = embed)
            await board.remove_reaction(reaction, _user)
            if psum>21:
                break
        else:
            break
    
    if psum>21:
        await asyncio.sleep(1.0)
        embed.set_field_at(1,name="플레이어의 패", value=(pstr+"Bust"), inline=False)
        await board.edit(embed = embed)
        await ctx.send("당신의 패배입니다.")
        return
    else:
        while dsum<17:
            await asyncio.sleep(1.0)
            nowCardNum,dsum,da,dstr = await hit_card(deck,nowCardNum,dsum,da,dstr)
            embed.set_field_at(0,name="딜러의 패", value=(dstr+"합계 : "+str(dsum)), inline=False)
            await board.edit(embed = embed)
    
    await asyncio.sleep(1.0)
    if dsum>21:
        embed.set_field_at(0,name="딜러의 패", value=(dstr+"Bust"), inline=False)
        await board.edit(embed = embed)
        await ctx.send("당신의 승리입니다.")
        return
    else :
        await asyncio.sleep(1.0)
        
        if psum < dsum:
            await ctx.send("당신의 패배입니다.")
        elif psum == dsum:
            await ctx.send("무승부입니다.")
        else:
            await ctx.send("당신의 승리입니다.")
        
        return
        

bot.run(TOKEN)

import os
import discord
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
from datetime import timedelta
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"تم تسجيل الدخول بنجاح باسم: {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"تمت مزامنة {len(synced)} أمر بنجاح.")
    except Exception as e:
        print(e)

# ==================== نظام الترحيب والوداع ====================
@bot.event
async def on_member_join(member):
    try:
        await member.send(f"أهلاً بك يا {member.mention} في سيرفر **{member.guild.name}**! نورتنا أتمنى أن تقضي وقتاً ممتعاً معنا.")
    except:
        pass

    channel = discord.utils.get(member.guild.text_channels, name="general") or \
              discord.utils.get(member.guild.text_channels, name="گشgeneral") or \
              member.guild.system_channel
              
    if channel:
        embed = discord.Embed(
            title="✨ عضو جديد انضم إلينا!",
            description=f"مرحباً بك {member.mention} في سيرفرنا! نورتنا.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"عدد الأعضاء الآن: {member.guild.member_count}")
        await channel.send(embed=embed)

@bot.event
async def on_member_remove(member):
    channel = discord.utils.get(member.guild.text_channels, name="general") or \
              discord.utils.get(member.guild.text_channels, name="گشgeneral") or \
              member.guild.system_channel
              
    if channel:
        embed = discord.Embed(
            title="🚪 غادرنا عضو",
            description=f"العضو {member.mention} غادر السيرفر. نتمنى له التوفيق!",
            color=discord.Color.red()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)

# ==================== أوامر متاحة للجميع ====================

@bot.tree.command(name="معلومات_السيرفر", description="عرض معلومات وإحصائيات السيرفر")
async def server_info(interaction: discord.Interaction):
    guild = interaction.guild
    owner = guild.owner
    if not owner:
        try:
            owner = await guild.fetch_member(guild.owner_id)
        except:
            owner = None
            
    embed = discord.Embed(title=f"معلومات السيرفر: {guild.name}", color=discord.Color.blue())
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👑 الأونر", value=owner.mention if owner else "غير معروف", inline=True)
    embed.add_field(name="👥 عدد الأعضاء", value=str(guild.member_count), inline=True)
    embed.add_field(name="📅 تاريخ الإنشاء", value=guild.created_at.strftime("%Y-%m-%d"), inline=True)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="الرولات", description="عرض قائمة رولات السيرفر بشكل منسق وجميل")
async def roles_list(interaction: discord.Interaction):
    roles = [role.mention for role in reversed(interaction.guild.roles) if role.name != "@everyone"]
    if not roles:
        roles_str = "لا توجد رولات في السيرفر حالياً."
    else:
        roles_str = " \n".join([f"🔹 {r}" for r in roles])
        
    embed = discord.Embed(title="📜 قائمة رولات السيرفر", description=roles_str, color=discord.Color.gold())
    embed.set_footer(text=f"إجمالي عدد الرولات: {len(roles)}")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="الأونر", description="معرفة مالك السيرفر الأساسي")
async def server_owner(interaction: discord.Interaction):
    guild = interaction.guild
    owner = guild.owner
    if not owner:
        try:
            owner = await guild.fetch_member(guild.owner_id)
        except:
            owner = None
    await interaction.response.send_message(f"👑 مالك السيرفر هو: {owner.mention if owner else 'غير معروف'}")

# ==================== أوامر الإشراف ====================

@bot.tree.command(name="مسح", description="مسح عدد محدد من الرسائل")
@app_commands.checks.has_permissions(administrator=True)
async def clear(interaction: discord.Interaction, amount: int):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"تم مسح {len(deleted)} رسالة بنجاح.", ephemeral=True)

@bot.tree.command(name="قفل", description="قفل الشات الحالي ومنع الأعضاء من الكتابة")
@app_commands.checks.has_permissions(manage_channels=True)
async def lock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    embed = discord.Embed(title="🔒 قفل الشات", description="تم قفل هذه القناة بواسطة الإدارة.", color=discord.Color.red())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="فتح", description="فتح الشات الحالي والسماح للأعضاء بالكتابة")
@app_commands.checks.has_permissions(manage_channels=True)
async def unlock(interaction: discord.Interaction):
    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=True)
    embed = discord.Embed(title="🔓 فتح الشات", description="تم فتح هذه القناة بواسطة الإدارة.", color=discord.Color.green())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="باند", description="حظر عضو من السيرفر مع إرسال تفاصيل بالخاص")
@app_commands.checks.has_permissions(administrator=True)
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "بدون سبب"):
    try:
        embed_dm = discord.Embed(title="🔨 تم حظرك من السيرفر", color=discord.Color.red())
        embed_dm.add_field(name="السيرفر", value=interaction.guild.name, inline=False)
        embed_dm.add_field(name="السبب", value=reason, inline=False)
        embed_dm.add_field(name="بواسطة المشرف", value=interaction.user.mention, inline=False)
        await member.send(embed=embed_dm)
    except:
        pass

    await member.ban(reason=reason)
    await interaction.response.send_message(f"تم حظر العضو {member.mention} بنجاح. السبب: {reason}")

@bot.tree.command(name="فك_الباند", description="إلغاء الحظر عن عضو بواسطة الآيدي مع إرسال رسالة")
@app_commands.checks.has_permissions(administrator=True)
async def unban(interaction: discord.Interaction, user_id: str, reason: str = "تخفيف العقوبة"):
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user)
        try:
            embed_dm = discord.Embed(title="🔓 تم فك الحظر عنك", color=discord.Color.green())
            embed_dm.add_field(name="السيرفر", value=interaction.guild.name, inline=False)
            embed_dm.add_field(name="السبب", value=reason, inline=False)
            embed_dm.add_field(name="بواسطة المشرف", value=interaction.user.mention, inline=False)
            await user.send(embed=embed_dm)
        except:
            pass
        await interaction.response.send_message(f"✅ تم فك الباند عن العضو {user.name} بنجاح.")
    except Exception as e:
        await interaction.response.send_message("❌ لم يتم العثور على العضو أو الآيدي غير صحيح.", ephemeral=True)

@bot.tree.command(name="ميوت", description="إسكات عضو مع إرسال التفاصيل للخاص")
@app_commands.checks.has_permissions(administrator=True)
async def mute(interaction: discord.Interaction, member: discord.Member, time_str: str, reason: str = "بدون سبب"):
    time_str = time_str.strip().lower()
    if time_str == "0m" or time_str == "0":
        delta = timedelta(days=27*365)
    elif time_str.endswith("d"):
        delta = timedelta(days=int(time_str[:-1]))
    elif time_str.endswith("h"):
        delta = timedelta(hours=int(time_str[:-1]))
    elif time_str.endswith("m"):
        delta = timedelta(minutes=int(time_str[:-1]))
    else:
        return await interaction.response.send_message("❌ صيغة الوقت خاطئة! استخدم مثلاً: 1d أو 1h أو 30m", ephemeral=True)

    try:
        embed_dm = discord.Embed(title="🔇 لقد تلقيت عقوبة ميوت", color=discord.Color.orange())
        embed_dm.add_field(name="السيرفر", value=interaction.guild.name, inline=False)
        embed_dm.add_field(name="المدة", value=time_str, inline=False)
        embed_dm.add_field(name="السبب", value=reason, inline=False)
        embed_dm.add_field(name="بواسطة المشرف", value=interaction.user.mention, inline=False)
        await member.send(embed=embed_dm)
    except:
        pass

    await member.timeout(discord.utils.utcnow() + delta, reason=reason)
    await interaction.response.send_message(f"تم إعطاء ميوت للعضو {member.mention} لمدة `{time_str}`. السبب: {reason}")

@bot.tree.command(name="فك_الميوت", description="إزالة الميوت عن العضو وإبلاغه بالخاص")
@app_commands.checks.has_permissions(administrator=True)
async def unmute(interaction: discord.Interaction, member: discord.Member):
    try:
        embed_dm = discord.Embed(title="🔊 تم رفع الميوت عنك", color=discord.Color.green())
        embed_dm.add_field(name="السيرفر", value=interaction.guild.name, inline=False)
        embed_dm.add_field(name="بواسطة المشرف", value=interaction.user.mention, inline=False)
        await member.send(embed=embed_dm)
    except:
        pass

    await member.timeout(None)
    await interaction.response.send_message(f"✅ تم إزالة الميوت عن العضو {member.mention} بنجاح.")

@bot.tree.command(name="تحذير", description="تحذير عضو وإرسال السبب بالخاص")
@app_commands.checks.has_permissions(administrator=True)
async def warn(interaction: discord.Interaction, member: discord.Member, reason: str):
    try:
        embed_dm = discord.Embed(title="⚠️ لقد تلقيت تحذيراً", color=discord.Color.gold())
        embed_dm.add_field(name="السيرفر", value=interaction.guild.name, inline=False)
        embed_dm.add_field(name="السبب", value=reason, inline=False)
        embed_dm.add_field(name="بواسطة المشرف", value=interaction.user.mention, inline=False)
        await member.send(embed=embed_dm)
    except:
        pass
        
    await interaction.response.send_message(f"تم تحذير العضو {member.mention} بنجاح. السبب: {reason}")

@bot.tree.command(name="تحذير_للكل", description="إرسال تحذير جماعي لجميع أعضاء السيرفر في الخاص")
@app_commands.checks.has_permissions(administrator=True)
async def warn_all(interaction: discord.Interaction, reason: str):
    await interaction.response.defer(ephemeral=True)
    success = 0
    failed = 0
    
    for member in interaction.guild.members:
        if member.bot:
            continue
        try:
            embed_dm = discord.Embed(title="⚠️ تحذير عام لجميع الأعضاء", color=discord.Color.gold())
            embed_dm.add_field(name="السيرفر", value=interaction.guild.name, inline=False)
            embed_dm.add_field(name="السبب", value=reason, inline=False)
            embed_dm.add_field(name="بواسطة الإدارة", value=interaction.user.mention, inline=False)
            await member.send(embed=embed_dm)
            success += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1
            
    await interaction.followup.send(f"✅ تم إرسال التحذير الجماعي بنجاح!\n- تم الإرسال إلى: `{success}` عضو\n- فشل الإرسال إلى: `{failed}` عضو", ephemeral=True)

@bot.tree.command(name="قول_للكل", description="إرسال رسالة إدارية لجميع الأعضاء في الخاص (نداء أو خبر هام)")
@app_commands.choices(type_choice=[
    app_commands.Choice(name="نداء (إعلان عام)", value="نداء"),
    app_commands.Choice(name="خبر هام (تنبيه للفويس أو غيره)", value="خبر هام")
])
@app_commands.checks.has_permissions(administrator=True)
async def say_all(interaction: discord.Interaction, type_choice: str, message: str):
    await interaction.response.defer(ephemeral=True)
    success = 0
    failed = 0
    
    if type_choice == "نداء":
        embed_title = f"📢 رسالة من إدارة سيرفر {interaction.guild.name}"
        embed_color = discord.Color.blue()
    else:
        embed_title = f"🚨 خبر هام من إدارة سيرفر {interaction.guild.name}"
        embed_color = discord.Color.red()

    for member in interaction.guild.members:
        if member.bot:
            continue
        try:
            embed_dm = discord.Embed(
                title=embed_title, 
                description=message, 
                color=embed_color
            )
            embed_dm.set_footer(text=f"سيرفر: {interaction.guild.name}")
            await member.send(embed=embed_dm)
            success += 1
            await asyncio.sleep(0.5)
        except:
            failed += 1
            
    await interaction.followup.send(f"✅ تم إرسال الـ ({type_choice}) بنجاح!\n- تم الإرسال إلى: `{success}` عضو\n- فشل الإرسال إلى: `{failed}` عضو", ephemeral=True)

# ==================== نظام التذاكر ====================

class AddMemberModal(discord.ui.Modal, title="إضافة عضو إلى التكت"):
    member_id = discord.ui.TextInput(label="آيدي العضو (User ID)", placeholder="اكتب آيدي العضو هنا...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.member_id.value))
            await interaction.channel.set_permissions(member, view_channel=True, send_messages=True)
            await interaction.response.send_message(f"✅ تم إضافة العضو {member.mention} إلى التكت بنجاح.", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message("❌ لم يتم العثور على العضو أو الآيدي غير صحيح.", ephemeral=True)

class RemoveMemberModal(discord.ui.Modal, title="إزالة عضو من التكت"):
    member_id = discord.ui.TextInput(label="آيدي العضو المراد إزالته", placeholder="اكتب آيدي العضو هنا...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.member_id.value))
            await interaction.channel.set_permissions(member, overwrite=None)
            await interaction.response.send_message(f"✅ تم إزالة العضو {member.mention} من التكت بنجاح.", ephemeral=False)
        except Exception as e:
            await interaction.response.send_message("❌ حدث خطأ، تأكد من الآيدي المدخل.", ephemeral=True)

class RenameChannelModal(discord.ui.Modal, title="إعادة تسمية التكت"):
    new_name = discord.ui.TextInput(label="اسم التكت الجديد", placeholder="ticket-newname", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.channel.edit(name=self.new_name.value)
        await interaction.response.send_message(f"✅ تم تغيير اسم التكت إلى: `{self.new_name.value}`", ephemeral=False)

class CloseConfirmView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=60)

    @discord.ui.button(label="✅ موافق على الإغلاق", style=discord.ButtonStyle.danger, custom_id="confirm_close")
    async def confirm_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("🔒 جاري إغلاق وحذف التكت خلال 3 ثوانٍ...")
        await asyncio.sleep(3)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ إلغاء", style=discord.ButtonStyle.secondary, custom_id="cancel_close")
    async def cancel_close(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.message.delete()
        await interaction.response.send_message("✅ تم إلغاء طلب إغلاق التكت.", ephemeral=True)

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="📌 استلام التكت", style=discord.ButtonStyle.blurple, custom_id="claim_ticket")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ عذراً، زر استلام التكت مخصص **للمشرفين فقط**!", ephemeral=True)
        button.disabled = True
        button.label = f"تم الاستلام بواسطة {interaction.user.name}"
        await interaction.response.edit_message(view=self)
        await interaction.followup.send(f"📌 تم استلام هذه التكت بواسطة المشرف: {interaction.user.mention}")

    @discord.ui.button(label="➕ إضافة عضو", style=discord.ButtonStyle.green, custom_id="add_member")
    async def add_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ هذه الصلاحية للمشرفين فقط!", ephemeral=True)
        await interaction.response.send_modal(AddMemberModal())

    @discord.ui.button(label="➖ إزالة عضو", style=discord.ButtonStyle.secondary, custom_id="remove_member")
    async def remove_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ هذه الصلاحية للمشرفين فقط!", ephemeral=True)
        await interaction.response.send_modal(RemoveMemberModal())

    @discord.ui.button(label="✏️ إعادة تسمية", style=discord.ButtonStyle.grey, custom_id="rename_ticket")
    async def rename_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not interaction.user.guild_permissions.manage_channels:
            return await interaction.response.send_message("❌ هذه الصلاحية للمشرفين فقط!", ephemeral=True)
        await interaction.response.send_modal(RenameChannelModal())

    @discord.ui.button(label="🔒 إغلاق التكت", style=discord.ButtonStyle.danger, custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # متاح للمشرف أو صاحب التكت عادي
        embed = discord.Embed(
            title="⚠️ طلب إغلاق التكت",
            description=f"قام {interaction.user.mention} بطلب إغلاق هذه التكت.\nيمكن لأي مشرف أو صاحب التكت الضغط على زر الموافقة أدناه لإغلاقها نهائياً.",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed, view=CloseConfirmView())

class TicketCreateView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🎫 فتح تكت جديدة", style=discord.ButtonStyle.green, custom_id="create_ticket")
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        category = discord.utils.get(guild.categories, name="Tickets")
        if not category:
            try:
                category = await guild.create_category("Tickets")
            except:
                pass
                
        try:
            channel = await guild.create_text_channel(f"ticket-{interaction.user.name}", category=category, overwrites=overwrites)
        except Exception as e:
            return await interaction.response.send_message("❌ حدث خطأ: تأكد من صلاحيات البوت (Manage Channels).", ephemeral=True)
        
        embed = discord.Embed(
            title="🎫 تكت جديدة", 
            description=f"مرحباً {interaction.user.mention}! اشرح مشكلتك وسيتم الرد عليك قريباً.\n\nاستخدم الأزرار أدناه للتحكم بالتكت.", 
            color=discord.Color.blue()
        )
        await channel.send(embed=embed, view=TicketControlView())
        await interaction.response.send_message(f"✅ تم فتح التكت الخاصة بك بنجاح: {channel.mention}", ephemeral=True)

@bot.tree.command(name="تكت", description="إرسال لوحة فتح التذاكر للأعضاء")
@app_commands.checks.has_permissions(administrator=True)
async def setup_ticket(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🎫 نظام التذاكر والدعم الفني",
        description="إذا كانت لديك مشكلة أو استفسار، اضغط على الزر أدناه لفتح تكت خاصة بك.",
        color=discord.Color.green()
    )
    await interaction.channel.send(embed=embed, view=TicketCreateView())
    await interaction.response.send_message("✅ تم إرسال لوحة التكت بنجاح.", ephemeral=True)

# معالجة الأخطاء لأوامر المشرفين
@clear.error
@lock.error
@unlock.error
@ban.error
@unban.error
@mute.error
@unmute.error
@warn.error
@warn_all.error
@say_all.error
@setup_ticket.error
async def admin_command_error(interaction: discord.Interaction, error):
    if isinstance(error, discord.app_commands.errors.MissingPermissions):
        await interaction.response.send_message("❌ عذراً، هذه الأوامر مخصصة **للمشرفين فقط**!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ حدث خطأ أثناء تنفيذ الأمر.", ephemeral=True)

keep_alive()
TOKEN = "MTU1MTY4NzA3NDM5NzI5MDQ5Ng.GdnqDZ.2Op6vBbyYvr1adXzkJAOBmYxITTvRUL6yT1D-o"
bot.run(TOKEN)
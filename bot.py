import telebot
from telebot import types

TOKEN = "8746341951:AAFWxU6u4mqSGBzCEaWs70zRUPTL-scOQiE"
ADMIN_ID = 6482915822
EXCHANGE_RATE = 12500  # 1$ = 12,500 so'm

bot = telebot.TeleBot(TOKEN)

users = {}
categories_info = {
    "BOY AKA": 3.0,
    "VIP UZBEK": 2.0
}
accounts = {
    "BOY AKA": [],
    "VIP UZBEK": []
}

admin_state = {}

def main_keyboard(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add("🛍 Akkaunt Sotib Olish", "💳 Balans To'ldirish")
    markup.add("👤 Profil", "ℹ️ Yo'riqnoma (@fakemailbot)")
    if user_id == ADMIN_ID:
        markup.add("🛠 Admin Panel")
    return markup

@bot.message_handler(commands=["start"])
def start_cmd(message):
    user_id = message.from_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0.0}
    
    caption = (
        f"🔥 **APEX STORE ga xush kelibsiz, {message.from_user.first_name}!**\n\n"
        "PUBG Mobile akkauntlarini xarid qilishingiz mumkin."
    )
    bot.send_message(message.chat.id, caption, reply_markup=main_keyboard(user_id), parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "🛠 Admin Panel" and m.from_user.id == ADMIN_ID)
def admin_panel(message):
    markup = types.InlineKeyboardMarkup(row_width=1)
    
    for cat, price in categories_info.items():
        markup.add(types.InlineKeyboardButton(f"➕ {cat} ga qo'shish (${price})", callback_data=f"add_{cat}"))
        
    markup.add(
        types.InlineKeyboardButton("📁 Yangi kategoriya va narx ochish", callback_data="create_new_category"),
        types.InlineKeyboardButton("📊 Ombordagi akkauntlar soni", callback_data="stock"),
        types.InlineKeyboardButton("🍪 APEX COOKIE ON SALE 🍪", callback_data="broadcast_cookie_sale")
    )
    bot.send_message(message.chat.id, "🛠 **Admin boshqaruv paneli:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("add_"))
def ask_account_details(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    category = call.data.replace("add_", "")
    admin_state[ADMIN_ID] = {"action": "wait_acc", "cat": category}
    
    price = categories_info.get(category, 0.0)
    bot.send_message(
        call.message.chat.id,
        f"📝 **{category} (${price})** uchun akkaunt ma'lumotlarini yuboring:\n\n"
        "Format:\n`Nomi | Login va Parol`\n\n"
        "Masalan:\n`M416 Glacier | Login: test, Parol: 123`",
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data == "create_new_category")
def ask_new_category(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    admin_state[ADMIN_ID] = {"action": "wait_new_cat"}
    
    bot.send_message(
        call.message.chat.id,
        "📁 **Yangi kategoriya va narx qo'shish:**\n\n"
        "Quyidagi formatda yuboring:\n"
        "`Kategoriya Nomi | Narxi | Akkaunt Nomi | Login va Parol`\n\n"
        "Masalan:\n`FIREWALL | 0.40 | Max Account | Login: abc, Parol: 789`",
        parse_mode="Markdown"
    )

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID and ADMIN_ID in admin_state)
def handle_admin_input(message):
    state = admin_state[ADMIN_ID].get("action")
    try:
        if state == "wait_acc":
            parts = message.text.split("|")
            if len(parts) < 2:
                bot.reply_to(message, "❌ Xato format! `Nomi | Login va Parol` ko'rinishida yuboring.")
                return
            name = parts[0].strip()
            details = parts[1].strip()
            category = admin_state[ADMIN_ID]["cat"]
            price = categories_info.get(category, 0.0)
            
            accounts[category].append({"name": name, "price": price, "details": details})
            del admin_state[ADMIN_ID]
            bot.reply_to(message, f"✅ Muvaffaqiyatli qo'shildi!\n\n📁 {category} (${price})\n📌 {name}")
            
        elif state == "wait_new_cat":
            parts = message.text.split("|")
            if len(parts) < 4:
                bot.reply_to(message, "❌ Xato format! Barcha 4 ta qismni `|` bilan ajrating.")
                return
            category = parts[0].strip().upper()
            price = float(parts[1].strip())
            name = parts[2].strip()
            details = parts[3].strip()
            
            categories_info[category] = price
            if category not in accounts:
                accounts[category] = []
            accounts[category].append({"name": name, "price": price, "details": details})
            
            del admin_state[ADMIN_ID]
            bot.reply_to(message, f"✅ Yangi kategoriya ochildi!\n\n📁 Papka: {category}\n💰 Narxi: ${price}\n📌 Nomi: {name}")
    except Exception as e:
        bot.reply_to(message, "❌ Xatolik yuz berdi. Formatni to'g'ri kiritganingizni tekshiring.")

@bot.callback_query_handler(func=lambda call: call.data == "stock")
def check_stock(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    text = "📊 **Ombordagi akkauntlar:**\n\n"
    for cat, price in categories_info.items():
        count = len(accounts.get(cat, []))
        text += f"🔹 **{cat} (${price}):** {count} ta mavjud\n"
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data == "broadcast_cookie_sale")
def broadcast_cookie_sale(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    stock_text = ""
    for cat, price in categories_info.items():
        count = len(accounts.get(cat, []))
        stock_text += f"🔹 **{cat} (${price}):** {count} ta mavjud\n"
        
    text = (
        f"🍪 **APEX COOKIE ON SALE** 🍪\n\n"
        f"🔥 Do'konga yangi PUBG Mobile akkauntlar keldi! Ulgurib qoling:\n\n"
        f"{stock_text}\n"
        f"🛒 Xarid qilish uchun botga kiring: @Apex_cookiebot"
    )
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🛍 Xarid qilish", url="https://t.me/Apex_cookiebot"))
    
    success, fail = 0, 0
    for uid in users.keys():
        try:
            bot.send_message(uid, text, parse_mode="Markdown", reply_markup=markup)
            success += 1
        except:
            fail += 1
    bot.send_message(call.message.chat.id, f"✅ E'lon yuborildi!\n👥 Yetib bordi: {success}\n❌ Bloklaganlar: {fail}")

@bot.message_handler(func=lambda m: m.text == "🛍 Akkaunt Sotib Olish")
def buy_acc_menu(message):
    markup = types.InlineKeyboardMarkup()
    for cat, price in categories_info.items():
        count = len(accounts.get(cat, []))
        markup.add(types.InlineKeyboardButton(f"📁 {cat} (${price}) [{count} ta]", callback_data=f"show_cat_{cat}"))
    bot.send_message(message.chat.id, "🛒 Mavjud Akkauntlar kategoriyasini tanlang:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("show_cat_"))
def view_category_accounts(call):
    bot.answer_callback_query(call.id)
    category = call.data.replace("show_cat_", "")
    acc_list = accounts.get(category, [])
    
    if not acc_list:
        bot.send_message(call.message.chat.id, "⚠️ Bu kategoriyada hozircha akkauntlar yo'q!")
        return
        
    markup = types.InlineKeyboardMarkup()
    for index, acc in enumerate(acc_list):
        markup.add(types.InlineKeyboardButton(f"{acc['name']} — ${acc['price']}", callback_data=f"get_{category}_{index}"))
    bot.send_message(call.message.chat.id, f"📋 **{category} kategoriyasidagi akkauntlar:**", reply_markup=markup, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: call.data.startswith("get_"))
def process_buy_account(call):
    bot.answer_callback_query(call.id)
    parts = call.data.split("_")
    index = int(parts[-1])
    category = "_".join(parts[1:-1])
    
    user_id = call.from_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0.0}
        
    acc_list = accounts.get(category, [])
    if index >= len(acc_list):
        bot.send_message(call.message.chat.id, "❌ Bu akkaunt allaqachon sotib bo'lingan.")
        return
        
    acc = acc_list[index]
    price = acc["price"]
    balance = users[user_id]["balance"]
    
    if balance < price:
        bot.send_message(call.message.chat.id, f"❌ Balansingizda yetarli mablag' yo'q!\nKerakli: ${price}\nSizda:${balance}")
        return
    
    users[user_id]["balance"] -= price
    purchased_acc = acc_list.pop(index)
    
    success_text = (
        f"🎉 **Tabriklaymiz! Akkaunt xarid qilindi!**\n\n"
        f"📌 **Nomi:** {purchased_acc['name']}\n"
        f"💰 **Narxi:** ${purchased_acc['price']}\n\n"
        f"🔐 **Ma'lumotlar:**\n`{purchased_acc['details']}`\n\n"
        f"💳 Qolgan balans: `${users[user_id]['balance']:.2f}`"
    )
    bot.send_message(call.message.chat.id, success_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "💳 Balans To'ldirish")
def deposit_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=3)
    buttons = []
    for d in range(1, 11):
        som_amount = d * EXCHANGE_RATE
        buttons.append(types.InlineKeyboardButton(f"${d} ({som_amount:,} so'm)", callback_data=f"pay_{d}"))
    markup.add(*buttons)
    bot.send_message(message.chat.id, f"💳 **Balans to'ldirish uchun miqdorni tanlang:**\n1$ = {EXCHANGE_RATE:,} so'm", reply_markup=markup, parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text == "👤 Profil")
def profile(message):
    user_id = message.from_user.id
    bal = users.get(user_id, {}).get("balance", 0.0)
    bot.send_message(message.chat.id, f"👤 **Profilingiz:**\n🆔 ID: `{user_id}`\n💰 Balans: `${bal:.2f}`", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.text in ["ℹ️ Yo'riqnoma (@fakemailbot)"])
def other_menus(message):
    bot.send_message(message.chat.id, f"ℹ️ Siz '{message.text}' bo'limini tanladingiz.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("pay_"))
def select_deposit_amount(call):
    bot.answer_callback_query(call.id)
    dollars = int(call.data.split("_")[1])
    som = dollars * EXCHANGE_RATE
    text = (
        f"💳 **Tanlangan summa: ${dollars} ({som:,} so'm)**\n\n"
        f"🔹 Humo: `9860 1606 0260 2171`\n"
        f"🔹 Visa: `4916 9903 3806 4196`\n\n"
        f"Karta raqamiga **{som:,} so'm** o'tkazib, chek skrinshotini (yoki faylini) shu botga yuboring!"
    )
    bot.send_message(call.message.chat.id, text, parse_mode="Markdown")

# Chek faqat sizga (adinga) keladi va o'zingiz xohlagan summani tanlab tasdiqlaysiz
@bot.message_handler(content_types=["photo", "document"])
def handle_receipt(message):
    user_id = message.from_user.id
    username = f"@{message.from_user.username}" if message.from_user.username else "Yo'q"
    caption = f"📥 **Yangi to'lov cheki keldi!**\n\n👤 User: {username}\n🆔 ID: `{user_id}`"
    
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("+$0.40", callback_data=f"topup_0.4_{user_id}"),
        types.InlineKeyboardButton("+$1", callback_data=f"topup_1_{user_id}"),
        types.InlineKeyboardButton("+$2", callback_data=f"topup_2_{user_id}"),
        types.InlineKeyboardButton("+$3", callback_data=f"topup_3_{user_id}"),
        types.InlineKeyboardButton("+$5", callback_data=f"topup_5_{user_id}"),
        types.InlineKeyboardButton("+$10", callback_data=f"topup_10_{user_id}")
    )
    
    try:
        if message.photo:
            bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)
        elif message.document:
            bot.send_document(ADMIN_ID, message.document.file_id, caption=caption, parse_mode="Markdown", reply_markup=markup)
        
        bot.reply_to(message, "✅ Chekingiz adminga yuborildi! Tekshirilib, tez orada balansingizga qo'shiladi.")
    except Exception as e:
        bot.reply_to(message, "❌ Xatolik yuz berdi.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("topup_"))
def confirm_topup(call):
    if call.from_user.id != ADMIN_ID:
        return
    bot.answer_callback_query(call.id)
    parts = call.data.split("_")
    amount = float(parts[1])
    target_id = int(parts[2])
    
    if target_id not in users:
        users[target_id] = {"balance": 0.0}
    
    users[target_id]["balance"] += amount
    
    try:
        bot.send_message(target_id, f"🎉 Tabriklaymiz! Balansingizga **${amount}** qo'shildi!", parse_mode="Markdown")
    except:
        pass
        
    try:
        bot.edit_message_caption(
            chat_id=call.message.chat.id, 
            message_id=call.message.message_id, 
            caption=call.message.caption + f"\n\n✅ **TASDIQLANDI (+${amount})**",
            parse_mode="Markdown"
        )
    except:
        pass

print("APEX STORE boti ishga tushdi...")
bot.infinity_polling()

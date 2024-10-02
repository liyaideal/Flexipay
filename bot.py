from telegram import ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ConversationHandler, filters
import logging

# 配置日志记录
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 替换为您的机器人令牌
TOKEN = '8155280589:AAEWEbLki3uw1AeuDuojaL0B3CIqcx2Qjuo'

# 定义状态
EVENT_NAME, EVENT_AMOUNT, EVENT_PARTICIPANTS, VIEW_EVENT, JOIN_EVENT = range(5)

# 存储所有收款活动的列表
payment_events = []

async def start(update, context):
    # 定义主菜单键盘
    keyboard = [
        ['创建收款活动', '查看收款活动'],
        ['我的付款', '收款统计'],
        ['帮助与指南', '设置']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        '欢迎使用 FlexiPay Bot！请选择一个功能：',
        reply_markup=reply_markup
    )
    

async def handle_message(update, context):
    text = update.message.text
    if text == '创建收款活动':
        pass  # 已由 ConversationHandler 处理
    elif text == '查看收款活动':
        pass  # 已由 ConversationHandler 处理
    elif text == '我的付款':
        await my_payments(update, context)
    elif text == '收款统计':
        await payment_statistics(update, context)
    elif text == '帮助与指南':
        await help_and_guide(update, context)
    elif text == '设置':
        await settings(update, context)
    else:
        await update.message.reply_text('抱歉，我不明白您的请求。')

async def create_payment_event(update, context):
    await update.message.reply_text('请您输入收款活动的名称：')
    return EVENT_NAME

async def event_name(update, context):
    context.user_data['event_name'] = update.message.text
    logger.info(f"用户输入的活动名称：{context.user_data['event_name']}")
    await update.message.reply_text('请输入每位参与者的付款金额（仅数字）：')
    return EVENT_AMOUNT

async def event_amount(update, context):
    text = update.message.text
    try:
        amount = float(text)
        context.user_data['event_amount'] = amount
        await update.message.reply_text('请输入参与人数：')
        return EVENT_PARTICIPANTS
    except ValueError:
        await update.message.reply_text('请输入有效的数字金额。')
        return EVENT_AMOUNT


async def event_participants(update, context):
    context.user_data['event_participants'] = update.message.text
    logger.info(f"用户输入的参与人数：{context.user_data['event_participants']}")
    # 创建活动字典
    event = {
        'creator_id': update.effective_user.id,
        'event_name': context.user_data['event_name'],
        'event_amount': context.user_data['event_amount'],
        'event_participants': context.user_data['event_participants'],
        'participants': [],  # 用于存储参与者的信息
    }
    # 将活动添加到全局列表
    payment_events.append(event)
    await update.message.reply_text('收款活动创建成功！')
    return ConversationHandler.END

async def view_payment_events(update, context):
    if not payment_events:
        await update.message.reply_text('当前没有收款活动。')
        return ConversationHandler.END
    # 构建活动列表消息
    message = '当前的收款活动：\n'
    for idx, event in enumerate(payment_events):
        message += f"{idx + 1}. {event['event_name']}\n"
    message += '\n请输入活动编号查看详情或参与（如：1）：'
    await update.message.reply_text(message)
    return VIEW_EVENT

async def select_event(update, context):
    text = update.message.text
    try:
        event_index = int(text) - 1
        if event_index < 0 or event_index >= len(payment_events):
            await update.message.reply_text('请输入有效的活动编号。')
            return VIEW_EVENT
    except ValueError:
        await update.message.reply_text('请输入数字编号。')
        return VIEW_EVENT
    # 保存用户选择的活动
    context.user_data['selected_event'] = payment_events[event_index]
    event = context.user_data['selected_event']
    # 显示活动详情
    message = f"活动名称：{event['event_name']}\n"
    message += f"金额：{event['event_amount']}\n"
    message += f"参与人数：{event['event_participants']}\n"
    message += '\n您是否要参与此活动？（是/否）'
    await update.message.reply_text(message)
    return JOIN_EVENT

async def join_event(update, context):
    text = update.message.text.lower()
    if text == '是':
        event = context.user_data['selected_event']
        user_id = update.effective_user.id
        if user_id not in event['participants']:
            event['participants'].append(user_id)
            await update.message.reply_text('您已成功参与活动！')
        else:
            await update.message.reply_text('您已参与过此活动。')
        return ConversationHandler.END
    elif text == '否':
        await update.message.reply_text('已取消参与。')
        return ConversationHandler.END
    else:
        await update.message.reply_text('请输入“是”或“否”。')
        return JOIN_EVENT

async def cancel(update, context):
    await update.message.reply_text('操作已取消。')
    return ConversationHandler.END

async def my_payments(update, context):
    user_id = update.effective_user.id
    message = '您参与的收款活动：\n'
    found = False
    for event in payment_events:
        if user_id in event['participants']:
            message += f"- {event['event_name']}\n"
            found = True
    if not found:
        message = '您还未参与任何收款活动。'
    await update.message.reply_text(message)

async def payment_statistics(update, context):
    if not payment_events:
        await update.message.reply_text('当前没有收款活动。')
        return
    message = '收款统计信息：\n'
    for event in payment_events:
        total_participants = int(event['event_participants'])
        paid_participants = len(event['participants'])
        message += f"活动名称：{event['event_name']}\n"
        message += f"应付人数：{total_participants}，已付人数：{paid_participants}\n"
        message += f"收款金额：{event['event_amount']}，总收款：{paid_participants * event['event_amount']}\n\n"
        
    await update.message.reply_text(message)

async def help_and_guide(update, context):
    await update.message.reply_text('这是帮助和指南。[功能待实现]')

async def settings(update, context):
    await update.message.reply_text('您可以在此调整设置。[功能待实现]')

def main():
    # 创建应用程序实例
    app = ApplicationBuilder().token(TOKEN).build()

    # 定义 ConversationHandler
    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex('^创建收款活动$'), create_payment_event),
            MessageHandler(filters.Regex('^查看收款活动$'), view_payment_events),
        ],
        states={
            # 创建收款活动的流程
            EVENT_NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), event_name)],
            EVENT_AMOUNT: [MessageHandler(filters.TEXT & (~filters.COMMAND), event_amount)],
            EVENT_PARTICIPANTS: [MessageHandler(filters.TEXT & (~filters.COMMAND), event_participants)],
            # 查看并参与活动的流程
            VIEW_EVENT: [MessageHandler(filters.TEXT & (~filters.COMMAND), select_event)],
            JOIN_EVENT: [MessageHandler(filters.TEXT & (~filters.COMMAND), join_event)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    # 添加处理器
    app.add_handler(CommandHandler('start', start))
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

    # 运行机器人
    app.run_polling()

if __name__ == '__main__':
    main()
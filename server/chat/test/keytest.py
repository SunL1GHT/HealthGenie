import keyboard


def record_start_and_end(key):
    trigger_key = keyboard.KeyboardEvent('down', 28, 'enter')
    if key.event_type == 'down' and key.name == trigger_key.name:
        print("你按下了enter键")
    if key.event_type == 'up' and key.name == trigger_key.name:
        print("你按下了enter键")


keyboard.hook(record_start_and_end)
# keyboard.hook_key('enter', bcd)
# recorded = keyboard.record(until='esc')
keyboard.wait()

# 结果：
# 你按下了enter键
# 你按下了enter键

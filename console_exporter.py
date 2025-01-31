#!/usr/bin/env python
# console_exporter - command prompt tool for generating metrics.
# An interactive command prompt tool designed for generating metrics. It is utilized for debugging notifications, creating complex rules, and more.
# The program structure is intentionally left simple so that it can be easily expanded.
from aiohttp import web
from prometheus_client import Counter,Gauge, Histogram, Summary, generate_latest, CONTENT_TYPE_LATEST
from  aioconsole import aprint, ainput
import asyncio
import inspect # this programs uses some kind of reflection

metrics_port = 8000

# Prometheus objects declared here
COMMANDS_COUNT = Counter(
    'demo_commands_count',
    'Total cli commands',
)
HISTOGRAM = Histogram(
    'demo_requests',
    'Demo histogram',
    buckets=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,20,100]
)
SUMMARY = Summary(
    'demo_summary',
    'Sum of numbers',
)
COUNTER = Counter(
    'demo_counter',
    'Demo events counter',
)
GAUGE = Gauge(
    'demo_gauge',
    'Demo gauge',
)


async def handle_metrics(request):
    """Metrics handler for /metrics"""
    resp = web.Response(body=generate_latest())
    resp.content_type = CONTENT_TYPE_LATEST
    return resp

######## Console commands ###########
async def cmd_gauge():
    """Gaudge testing loop."""
    await aprint('Gauge loop. Every entered number change current value of gauge metric. Empty string to stop.')
    while True:
        number = await ainput()
        number = number.strip()
        if number == '':
            return
        try:
            float_number = float(number)
            GAUGE.set(float_number)
        except ValueError:
            await aprint(f'Invalid number, skipped.')

async def cmd_hist():
    """Histogram testing loop."""
    await aprint('Histogram loop. Every entered number produce observation for histogram metric. Empty string to stop.')
    while True:
        number = await ainput()
        number = number.strip()
        if number == '':
            return
        try:
            float_number = float(number)
            HISTOGRAM.observe(float_number)
        except ValueError:
            await aprint(f'Invalid number, skipped.')


async def cmd_sum():
    """Summary testing loop."""
    await aprint('Sum observe loop. Every entered number produce observation for summary metric. Empty string to stop.')
    while True:
        number = await ainput()
        number = number.strip()
        if number == '':
            return
        try:
            float_number = float(number)
            SUMMARY.observe(float_number)
        except ValueError:
            await aprint(f'Invalid number, skipped.')

async def cmd_count():
    """Counter testing loop."""
    await aprint('Counter testing loop. Any input until "stop" or "exit" increments counter. Empty strings also increments counter.')
    while True:
        counter_input = await ainput()
        counter_input = counter_input.strip()
        if counter_input == 'exit' or counter_input == 'stop':
            return
        COUNTER.inc()



#### End of console commands ######

# Function to dynamically create the commands dictionary
def create_commands_dict():
    commands = {}
    for name, obj in globals().items():
        if name.startswith('cmd_') and inspect.iscoroutinefunction(obj):
            command_name = name.removeprefix('cmd_')
            commands[command_name] = obj
    return commands


# help cmd always needed
async def cmd_help():
    """This help."""
    await aprint('Available commands:')
    for cmd, func in commands.items():
        await aprint(f' {cmd} - {func.__doc__}')
# exit cmd always needed
async def cmd_exit():
    """Exit command."""
    exit()


async def console_task(app):
    """Interactive console"""
    await aprint(f"Metrics with prefix demo_* exported on http://0.0.0.0:{metrics_port}/metrics URL.\nCommands:" , ' '.join(sorted(commands.keys())))
    try:
        while True:
            await aprint('~> ', end='')
            user_input = await ainput()
            user_input = user_input.strip()
            await aprint("Execution command:", user_input)
            COMMANDS_COUNT.inc()
            if user_input in commands:
                await commands[user_input]()
            else:
                await aprint('Unknown command')

    except asyncio.CancelledError:
        print("Console task stopped")  # Finalization uses synchronous output

async def start_background_tasks(app):
    """Start background tasks"""
    app['console_task'] = asyncio.create_task(console_task(app))

async def cleanup_background_tasks(app):
    """Stop background tasks"""
    app['console_task'].cancel()
    await app['console_task']

def init_app():
    """Initialize the application"""
    app = web.Application()
    app.router.add_get('/metrics', handle_metrics)
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    return app

# Create the commands dictionary
commands = create_commands_dict()

if __name__ == '__main__':
    web.run_app(init_app(), port=metrics_port, print=None)
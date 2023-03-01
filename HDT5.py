import simpy
import random

semillaAleatoria = 42 
NUM_PROCESSES = 100
INTERVAL = 1
MEMORY_CAPACITY = 200
CPU_CAPACITY = 1
INSTRUCTIONS_PER_TIME_UNIT = 3

class Process:
    def __init__(self, env, name, memory, instructions):
        self.env = env
        self.name = name
        self.memory = memory
        self.instructions = instructions
        self.status = 'new'
        self.wait_time = 0
        self.cpu_time = 0

    def __repr__(self):
        return f'Process({self.name})'

def process_generator(env, ram):
    name = 0
    while True:
        yield env.timeout(random.expovariate(1/INTERVAL))
        name += 1
        memory = random.randint(1, 10)
        print("El espacio aleatorio generado de memoria es", memory)
        instructions = random.randint(1, 10)
        print("El numero de instrucciones es", instructions)
        p = Process(env, name, memory, instructions)
        env.process(process_lifecycle(env, p, ram))

def process_lifecycle(env, process, ram):
    process.status = 'new'
    with ram.get(process.memory) as mem:
        yield mem
        process.status = 'ready'
        env.process(cpu_scheduler(env, process))
        while process.instructions > 0:
            yield env.timeout(1)
            process.instructions -= INSTRUCTIONS_PER_TIME_UNIT
            process.cpu_time += 1
            if process.instructions <= 0:
                break
            if process.cpu_time % 3 == 0:
                if random.randint(1, 2) == 1:
                    process.status = 'waiting'
                    env.process(io_scheduler(env, process))
                    yield env.timeout(1)
                    process.wait_time += 1
                else:
                    process.status = 'ready'
                    env.process(cpu_scheduler(env, process))
    ram.put(process.memory)
    process.status = 'terminated'

def cpu_scheduler(env, process):
    with cpu.request() as req:
        yield req
        process.status = 'running'
        while process.instructions > 0:
            yield env.timeout(1)
            process.instructions -= INSTRUCTIONS_PER_TIME_UNIT
            process.cpu_time += 1
            if process.instructions <= 0:
                break
            if process.cpu_time % 3 == 0:
                if random.randint(1, 2) == 1:
                    process.status = 'waiting'
                    env.process(io_scheduler(env, process))
                    yield env.timeout(1)
                    process.wait_time += 1
                else:
                    process.status = 'ready'
                    env.process(cpu_scheduler(env, process))
        process.status = 'terminated'

def io_scheduler(env, process):
    yield env.timeout(random.randint(1, 2))
    process.status = 'ready'
    env.process(cpu_scheduler(env, process))

env = simpy.Environment()
random.seed(semillaAleatoria)
cpu = simpy.Resource(env, capacity=CPU_CAPACITY)
ram = simpy.Container(env, init=MEMORY_CAPACITY, capacity=MEMORY_CAPACITY)
env.process(process_generator(env, ram))
env.run(until=NUM_PROCESSES)





import time
from multiprocessing import Queue
from typing import Optional, Any

from openai import OpenAIError

from app import App
from interpreter import Interpreter
from llm import LLM
from utils.settings import Settings

class Core:
    def __init__(self):
        self.status_queue = Queue()
        self.interrupt_execution = False
        self.settings_dict = Settings().get_dict()
        self.interpreter = Interpreter(self.status_queue)
        self.llm = None
        try:
            self.llm = LLM()
        except OpenAIError as e:
            self.status_queue.put(f'Set your OpenAPI API Key in Settings and Restart the App. Error: {e}')
        except Exception as e:
            self.status_queue.put(f'An error occurred during startup. Please fix and restart the app.\n'
                                  f'Error likely in file {Settings().settings_file_path}.\n'
                                  f'Error: {e}')

    def execute_user_request(self, user_request: str) -> None:
        self.stop_previous_request()
        time.sleep(0.1)
        self.execute(user_request)

    def stop_previous_request(self) -> None:
        self.interrupt_execution = True

    def execute(self, user_request: str, step_num: int = 0) -> Optional[str]:
        self.interrupt_execution = False
        if not self.llm:
            status = 'Set your OpenAPI API Key in Settings and Restart the App'
            self.status_queue.put(status)
            return status
        try:
            instructions: dict[str, Any] = self.llm.get_instructions_for_objective(user_request, step_num)
            if instructions == {}:
                instructions = self.llm.get_instructions_for_objective(user_request + ' Please reply in valid JSON',
                                                                       step_num)
            for step in instructions['steps']:
                if self.interrupt_execution:
                    self.status_queue.put('Interrupted')
                    self.interrupt_execution = False
                    return 'Interrupted'
                success = self.interpreter.process_command(step)
                if not success:
                    return 'Unable to execute the request'
        except Exception as e:
            status = f'Exception Unable to execute the request - {e}'
            self.status_queue.put(status)
            return status
        if instructions['done']:
            self.status_queue.put(instructions['done'])
            self.play_ding_on_completion()
            return instructions['done']
        else:
            self.status_queue.put('Fetching further instructions based on current state')
            return self.execute(user_request, step_num + 1)

    def play_ding_on_completion(self):
        if self.settings_dict.get('play_ding_on_completion'):
            print('\a')

    def cleanup(self):
        self.llm.cleanup()

"""The ask user tool. Copyright (C) 2024 SynaLinks. License: GPL-3.0"""

import copy
from typing import List, Optional, Callable
import json
import dspy
from .base import BaseTool
from ..types.state import AgentState

class AskUserSignature(dspy.Signature):
    """Infer the question to ask to the user"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    context = dspy.InputField(desc = "The previous actions (what you have done)")
    purpose = dspy.InputField(desc = "The purpose of the action (what you have to do now)")
    prompt = dspy.InputField(desc = "The action specific instructions (how to do it)")
    question = dspy.OutputField(desc = "The question to ask to the user")

class SimulateAnswerSignature(dspy.Signature):
    """Answer from the perspective of a real person, if you don't known imagine what an average user would answer"""
    objective = dspy.InputField(desc = "The long-term objective (what you are doing)")
    chat_history = dspy.InputField(desc = "The chat history")
    question = dspy.InputField(desc = "The question to assess")
    user_answer = dspy.OutputField(desc = "The answer from the perspective of a real person (only few words)")

class AskUserTool(BaseTool):

    def __init__(
            self,
            agent_state: AgentState,
            ask_user_func: Optional[Callable[[str], str]] = None,
            num_history: int = 50,
            simulated: bool = True,
        ):
        super().__init__(name = "AskUser")
        self.predict = dspy.Predict(AskUserSignature)
        self.simulated = simulated
        self.simulate = dspy.Predict(SimulateAnswerSignature)
        self.agent_state = agent_state
        self.num_history = num_history
        self.ask_user_func = ask_user_func

    def ask_user(self, question : str) -> str:
        if self.ask_user_func:
            return self.ask_user_func(question)
        else:
            raise ValueError(
                "You should specify a function to call to use `AskUser` outside simulation")

    def simulate_ask_user(self, question: str):
        chat_history = json.dumps(self.agent_state.chat_history[:-self.num_history], indent=2)
        simulation = self.simulate(
            objective = self.agent_state.objective,
            chat_history = chat_history,
            question = question,
        )
        answer = simulation.user_answer
        return answer

    def forward(
            self,
            context: str,
            objective: str,
            purpose: str,
            prompt: str,
            disable_inference: bool = False,
        ) -> dspy.Prediction:
        """Method to perform DSPy forward prediction"""
        if not disable_inference:
            prediction = self.predict(
                objective = objective,
                context = context,
                purpose = purpose,
                prompt = prompt,
            )
            question = prediction.question
            self.agent_state.chat_history.append(
                {"role": "AI", "message": question}
            )
            if self.simulated:
                answer = self.simulate_ask_user(question)
            else:
                answer = self.ask_user(question)
            self.agent_state.chat_history.append(
                {"role": "User", "message": answer}
            )
            return dspy.Prediction(
                question = question,
                answer = answer,
            )
        else:
            self.agent_state.chat_history.append(
                {"role": "AI", "message": prompt}
            )
            if self.simulated:
                answer = self.simulate_ask_user(question)
            else:
                answer = self.ask_user(message)
            self.agent_state.chat_history.append(
                {"role": "User", "message": answer}
            )
            return dspy.Prediction(
                question = prompt,
                answer = answer,
            )

    def __deepcopy__(self, memo):
        cpy = (type)(self)(
            agent_state = self.agent_state,
            num_history = self.num_history,
            ask_user_func = self.ask_user_func,
            simulated = self.simulated,
        )
        cpy.predict = copy.deepcopy(self.predict)
        return cpy
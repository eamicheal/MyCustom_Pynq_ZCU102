#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan 28 17:41:02 2023

This script contains code for running the ANN Module with TVM-optimized models for Kirett Project

@author: Micheal Ezekiel
"""

import os
import numpy as np
import torch
import tvm
from tvm import relay
from tvm.contrib import graph_executor
import json

# Import the HerzModel def
# from modeldefine.define_herzmodel import *
from define_herzmodel import *

# Get the directory containing script.py as base_dir
base_dir = os.path.dirname(os.path.abspath(__file__))

class TvmModelRunner:
    def __init__(self, tvm_model, input_shape, model_name):
        self.tvm_model = tvm_model.eval()
        self.input_shape = input_shape
        self.model_name = model_name
        self.target = tvm.target.Target("llvm", host="llvm")
        self.dev = tvm.cpu(0)

    def optimize_and_run(self, input_data):
        input_data_torch = torch.randn(self.input_shape)
        scripted_model = torch.jit.trace(self.tvm_model, input_data_torch).eval()
        input_name = "input0"
        input_shape_list = [(input_name, self.input_shape)]
        mod, params = relay.frontend.from_pytorch(scripted_model, input_shape_list)

        with tvm.transform.PassContext(opt_level=3):
            lib = relay.build(mod, target=self.target, params=params)

        dtype = "float32"
        tvm_module = graph_executor.GraphModule(lib["default"](self.dev))
        tvm_module.set_input(input_name, tvm.nd.array(input_data.astype(dtype)))

        num_runs = 10
        num_measurements = 3
        timer = tvm_module.module.time_evaluator("run", self.dev, number=num_runs, repeat=num_measurements)
        timings = timer()
        mean_inference_time = timings.mean * 1000000

        tvm_module.run()
        tvm_output = tvm_module.get_output(0)
        output_values = tvm_output.asnumpy().tolist()

        result_data = {"ann_id": self.model_name, "ann_values": output_values}
        print(json.dumps(result_data))

class MainScript:
    def __init__(self):
        self.person_data = None

    def load_model(self):
        model_file = "HerzModel.pth"
        model_path = os.path.join(base_dir, model_file)
        herz_model = torch.load(model_path)
        input_shape = (1, 13)
        model_name = "herz"
        self.runner = TvmModelRunner(herz_model, input_shape, model_name)

    def run(self, data):
        input_data = np.array(list(data.values()), dtype=np.float32).reshape([1, 13])
        self.runner.optimize_and_run(input_data)

if __name__ == "__main__":
    main_script = MainScript()
    main_script.load_model()

    data = {
        'nibp_sys': 72,
        'nibp_dia': 111,
        'SkinCond': 1,
        'mean_arterial_pressure': 98,
        'chief_complaint_pain_or_discomfort_chest': 0,
        'pre_existing_heart_disease': 0,
        'pre_existing_heart_failure': 0,
        'pain_scale': 0,
        'respiratory_rate': 42,
        'weak_pulse': 1,
        'strong_pulse': 0,
        'naca': 3,
        'Circ': 4
    }

    main_script.run(data)



"""
rewrite your previous code (myAI.py) such that:
1. it doesn't care about the patient number
2. it doesn't take data from an Excel file any longer
3. it rather takes the data directly from a dictionary called "data" in another myfile.py file (process_ANN_trigger function) below whose print(data) returns {'nibp_sys': 72.0, 'nibp_dia': 111.0, 'SkinCond': 1, 'mean_arterial_pressure': 98.0, 'chief_complaint_pain_or_discomfort_chest': 0, 'pre_existing_heart_disease': 0, 'pre_existing_heart_failure': 0, 'pain_scale': 0, 'respiratory_rate': 42.0, 'weak_pulse': 1, 'strong_pulse': 0, 'naca': 3, 'Circ': 4}
Where the process_ANN_trigger code below starts the myAI.py, send the data to the myAI.py and the results from myAI.py are returned to the 

class ANNMessenger(Messenger):
    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.message_payload = [
            (MessageType.PATIENT_VITALS, {"patient_id": 3})
        ]

    def process_ANN_trigger(self, message: Message):

        completed_process = subprocess.Popen(
            ['python3', 'myAI.py'],
            stdout=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )  # ,check=True)

        ann_ids = []
        ann_values = []

        for line in completed_process.stdout:
            try:
                # Parse each line as a JSON object
                output_data = json.loads(line.strip())

                # Extract ANN ID and the first ANN value from the nested list
                ann_id = output_data.get("ann_id", "").strip('\'')
                ann_val = output_data.get("ann_values", [])[0]

                # Append the extracted data to the respective lists
                ann_ids.append(ann_id)
                ann_values.append(ann_val)
            except json.JSONDecodeError:
                # Handle JSON decoding error by printing an error message
                print("Value_Error")

        # Remove the extra [] around ANN values
        ann_values = [val[0] for val in ann_values]

        # Format the ANN values to three decimal places
        ann_values = [round(val, 3) for val in ann_values]

        print("ann_ids:", ann_ids)
        print("ann_values:", ann_values)

        # Reply to the original message with extracted ANN IDs and values
        return message.reply_to({"ann_ids": ann_ids, "ann_values": ann_values})
"""

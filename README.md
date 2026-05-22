```text
 ___  _      _ _     ___                       _                 _
|   \(_)__ _(_) |_  | _ \___ __ ___  __ _ _ _ (_)___ ___ _ _    /_\  _ __ _ __
| |) | / _` | |  _| |   / -_) _/ _ \/ _` | ' \| (_-</ -_) '_|  / _ \| '_ \ '_ \
|___/|_\__, |_|\__| |_|_\___\__\___/\__, |_||_|_/__/\___|_|   /_/ \_\ .__/ .__/
       |___/                        |___/                           |_|  |_|
```
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Welcome to my Digit Recogniser App repository !

This repo contains the source code and deployment configurations for a web app that performs real-time handwritten digit recognition, deployed via AWS Amplify. It utilises a backend serverless architecture of AWS Lambda with a Flask-based API handled by a Lambda adapter, together with Joblib serialisation of a trained scikit-learn MLP model.<br>

The original neural network (NN) model itself was an adapted and customised scikit-learn implementation of my previous (July 2022) _**modified**_ Python TensorFlow version, and trained on the popular MNIST data. Deployment in the wild exposed a weakness that was not apparent during validation and testing: persistent misidentification of the digits 7 and 9 as 3. Probable reasons: an MLP model trained on raw pixels exhibiting spatial blindness i.e. the model treats every pixel as an independent feature based strictly on its grid coordinate (x, y), and has no concept of spatial relationships or shapes.<br>

**Resolution:** Refactor, reconfigure, and redeploy. Still using the MNIST dataset, a PyTorch implementation of a convolutional neural network (CNN) was carried out, and further improved with data augmentation and transformations. The result now is a satisfactorily performing app without performance issues.

Application functionalities:<br>
* Image Upload: Classify handwritten digits from uploaded JPEG/PNG files.
* Interactive Canvas: Draw digits directly using a mouse or touch interface.
* Inference Results: Obtain a digit classification along with its confidence percentage.<br>

## Architecture Description

Original scikit-learn MLP model:

```
Browser → Frontend → AWS Amplify (Hosting + API Management) → Lambda Backend (Flask + Lambda Adapter + NN Joblib)
```

Updated PyTorch CNN model:

```
Browser → Frontend → AWS Amplify (Hosting + API Management) → Lambda Backend (Flask + ONNX Runtime + PyTorch CNN)
```

<br>

## Project Architecture (updated)

![Project Architecture](hdc-architecture-updated.svg)

<br>

## Project Structure (Updated)

```text

digit-recogniser-amplify-deploy/
├── template.yaml                  # SAM/CloudFormation infrastructure definition
├── samconfig.toml                 # SAM deployment configuration (auto-generated)
├── README.md
│
├── backend/                       # Lambda function package
│   ├── app.py                     # Flask handler + ONNX inference logic
│   ├── mnist_cnn.onnx             # Trained CNN model (ONNX format)
│   ├── requirements.txt           # Python dependencies (onnxruntime, flask, etc.)
│   └── onnxruntime/               # ONNX Runtime bundled for Lambda (x86_64)
│
└── frontend/                      # Static site hosted on AWS Amplify
    ├── index.html                 # Canvas UI for drawing/uploading digits
    └── script.js                  # Fetch calls to API Gateway /predict endpoint

```
<br>

Enjoy further details by checking out:

  1. [Original NN Model for this App](https://github.com/kea333/digit-recogniser-amplify-deploy/blob/main/Digit_Classifier_ML_Model.ipynb)<br>
      Original Digit_Classifier_ML_Model.ipynb notebook (deliberately left in repo) with detailed descrition of project background and ML/NN engineering decisions.<br>

  2. [Updated NN Model for this App](https://github.com/kea333/digit-recogniser-amplify-deploy/blob/main/Digit_Classifier_ML_Model_Updated.ipynb)
      Updated Digit_Classifier_ML_Model_Updated.ipynb notebook - a straighforward problem fix without too much talk. Detailed explanations may be added in due course.

  3. [App on Demonstration](https://main.d28bhzqcmfxh8w.amplifyapp.com/)<br>
     In addition to uploading digit images for inference, you may also draw digits here.<br>
     
  4. [My other Projects Portfolio](https://webint.tech/)<br>
     Under construction - coming soon !
  
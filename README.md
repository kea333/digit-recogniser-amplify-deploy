```text
 ___  _      _ _     ___                       _                 _
|   \(_)__ _(_) |_  | _ \___ __ ___  __ _ _ _ (_)___ ___ _ _    /_\  _ __ _ __
| |) | / _` | |  _| |   / -_) _/ _ \/ _` | ' \| (_-</ -_) '_|  / _ \| '_ \ '_ \
|___/|_\__, |_|\__| |_|_\___\__\___/\__, |_||_|_/__/\___|_|   /_/ \_\ .__/ .__/
       |___/                        |___/                           |_|  |_|
```
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Welcome to my Digit Recogniser App repository !

This repo contains the source code and deployment configurations for a web app that performs real-time handwritten digit recognition, deployed via AWS Amplify. It utilises a backend serverless architecture of AWS Lambda with a Flask-based API handled by a Lambda adapter, together with Joblib serialisation of a trained scikit-learn MLP model.
<br>
The neural network (NN) model itself is an adapted and customised scikit-learn implementation of my previous (July 2022) _**modified**_ Python TensorFlow version, and trained on the popular MNIST data.
<br>
This deployment provides added functionalities:<br>
* Interactive Canvas: Draw digits directly using a mouse or touch interface.
* Image Upload: Classify handwritten digits from uploaded JPEG/PNG files.
* Inference Results: Obtain a digit classification along with its confidence percentage.
<br>

## Project Architecture

```
Browser → Frontend → AWS Amplify (Hosting + API Management) → Lambda Backend (Flask + Lambda Adapter + scikit-learn / Joblib)
```
<br>

<img width="1416" height="694" alt="HDC Architecture" src="https://github.com/user-attachments/assets/ed8ff2cd-bb08-4f90-8895-5a92673955a2" />

<br>

## Project Structure

```text

digit-recogniser-amplify-deploy/
├── .gitignore
├── LICENSE
├── README.md
├── Digit_Classifier_ML_Model.ipynb
├── sample_handwritten_digits/
├── amplify.yaml                          # Amplify build specification
├── frontend/                             # Static site (Amplify Hosting)
│     ├── index.html                      # Frontend markup
│     ├── style.css                       # Frontend styling
│     └── script.js                       # Frontend javascript
├── backend/                              # Lambda function (Python)
│     ├── app.py                          # Flask app wrapped for Lambda
│     ├── preprocess.py                   # Image preprocessing logic
│     ├── requirements.txt                # Python dependencies for Lambda
│     └── my_sklearn_model.joblib         # My trained model saved as joblib
└── template.yaml                         # AWS SAM template to deploy Lambda + API Gateway

```
<br>

Enjoy further details by checking out:

  1. [Neural Network Model for this App](https://github.com/kea333/digit-recogniser-amplify-deploy/blob/main/Digit_Classifier_ML_Model.ipynb)<br>
     A step-by-step guide through my adapted and customised implementation, and the same as the Python notebook _**Digit_Classifier_ML_Model**_  above in this repo.<br>
     You may also run the notebook in your local Jupyter environment, where you may upload handwritten digit images for inference.<br>
     
  2. [App on Demonstration](https://main.d28bhzqcmfxh8w.amplifyapp.com/)<br>
     In addition to uploading digit images for inference, you may also draw digits here.<br>
     
  3. [My other Project's Portfolio](https://webint.tech/)
     Under construction - coming soon !
  

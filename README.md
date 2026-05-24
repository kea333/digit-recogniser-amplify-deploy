```text
 ___  _      _ _     ___                       _                 _
|   \(_)__ _(_) |_  | _ \___ __ ___  __ _ _ _ (_)___ ___ _ _    /_\  _ __ _ __
| |) | / _` | |  _| |   / -_) _/ _ \/ _` | ' \| (_-</ -_) '_|  / _ \| '_ \ '_ \
|___/|_\__, |_|\__| |_|_\___\__\___/\__, |_||_|_/__/\___|_|   /_/ \_\ .__/ .__/
       |___/                        |___/                           |_|  |_|
```
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 

## Welcome to my Digit Recogniser App repository !

This repo contains the source code and deployment configurations for a web app that performs real-time handwritten digit recognition deployed via AWS Amplify. It utilises a backend serverless architecture of AWS Lambda with a Flask-based API handled by a Lambda adapter, together with ONNX Runtime execution of a trained PyTorch CNN model exported to ONNX format.<br>

The original neural network (NN) model itself was an adapted and customised scikit-learn implementation of my previous (July 2022) _**modified**_ Python TensorFlow version, and trained on the popular MNIST data. Deployment in the wild exposed a weakness that was not apparent during validation and testing: persistent misidentification of the digits 7 and 9 as 3. Probable reasons: an MLP model trained on raw pixels exhibiting spatial blindness i.e. the model treats every pixel as an independent feature based strictly on its grid coordinate (x, y), and has no concept of spatial relationships or shapes.<br>

**Resolution:** Refactor, reconfigure, and redeploy. Still using the MNIST dataset, a PyTorch implementation of a convolutional neural network (CNN) was carried out, and further improved with data augmentation and transformations. The result now is a satisfactorily performing app without performance issues.

Application functionalities:<br>
* Image Upload: Classify handwritten digits from uploaded JPEG/PNG files.
* Interactive Canvas: Draw digits directly using a mouse or touch interface.
* Inference Results: Obtain a digit classification along with its confidence percentage.<br>

## Architecture Description

1. Original scikit-learn MLP model:

```
Browser → Frontend → AWS Amplify (Hosting + API Management) → Lambda Backend (Flask + Lambda Adapter + NN Joblib)
```

2. Updated PyTorch CNN model:

```
Browser → Frontend → AWS Amplify (Hosting + API Management) → Lambda Backend (Flask + ONNX Runtime + CNN ONNX Model)
```

<br>

## Project Architecture (updated)

![Project Architecture](hdc-architecture-updated.png)

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

### **Security Considerations**

The following precautions have been taken to address common bad actor methods:<br>

1. CORS + API URL:<br>

Web application vulnerabilities stemming from exposed backend endpoints, reverse-engineering of client-side source code, and unrestricted cross-origin sharing represent critical vectors of attack for direct API abuse, data exfiltration, and unauthorised cross-domain exploitation.<br>
API requests are routed through a proxy, keeping the backend endpoint out of client-side code. Cross-origin requests are restricted to the production frontend domain only. Please see [AWS CORS Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/cors.html)<br>
<br>

2. Error handling and debug mode:<br>

Vulnerabilities resulting from verbose error leakage, stack trace exposure, and active debug interfaces could lead to system mapping and remote code execution.<br>
Unhandled exceptions are logged server-side via CloudWatch without exposing internal details to the client. The application runs with debug mode disabled in all environments. Please see [AWS Prescriptive Logging Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/logging-monitoring-for-application-owners/logging-best-practices.html)<br>
<br>

3. Input validation:<br>

Vulnerabilities deriving from malicious file uploads and insecure canvas inputs expose web apps to system takeovers, data theft, and client-side code execution.<br>
Uploaded files are validated against an allowlist of permitted image MIME types on both the frontend and backend. To prevent oversized input abuse and possible black hat probing via this method, payload size is capped at _MB (aha, did you expect me to reveal actual size? 😊 ). Please see [XSS (Cross Site Scripting)](https://owasp.org/www-community/attacks/xss/)<br>

<br>

Enjoy further details by checking out:

  1. [Original NN Model for this App](https://github.com/kea333/digit-recogniser-amplify-deploy/blob/main/Digit_Classifier_ML_Model.ipynb)<br>
      Original _Digit Classifier ML Model.ipynb_ notebook (deliberately left in repo) with detailed description of mini-project
      background and ML/NN engineering decisions.<br>

  2. [Updated NN Model for this App](https://github.com/kea333/digit-recogniser-amplify-deploy/blob/main/Digit_Classifier_ML_Model_Updated.ipynb)
      Updated notebook _Digit Classifier ML Model Updated.ipynb_ - a straighforward problem fix without too much talk. Detailed explanations may be added in due course.

  3. [App on Demonstration](https://main.d28bhzqcmfxh8w.amplifyapp.com/)<br>
     In addition to uploading digit images for inference, you may also draw digits here.<br>
     
  4. [My other Projects Portfolio](https://webint.tech/)<br>
     Under construction - coming soon !
  
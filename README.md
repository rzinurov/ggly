# GGLY

Facebook Messenger bot that puts googly eyes on human faces

Demo video:

[![GGLY bot demo](https://img.youtube.com/vi/DIlFDJY08Ls/0.jpg)](https://www.youtube.com/watch?v=DIlFDJY08Ls)

Try it out [here](http://m.me/ggly111)

# How it works

It's a Python [HTTP Google Cloud function](https://cloud.google.com/functions/docs/tutorials/http), that listens to
[Facebook Messenger Webhooks](https://developers.facebook.com/docs/messenger-platform/webhook/), detects human faces on
photos using [OpenCV](https://opencv.org/) library, draws [googly eyes](https://en.wikipedia.org/wiki/Googly_eyes)
on them and saves results to [Google Cloud Storage](https://cloud.google.com/storage/). It uses async request handling
in order to be able to process webhook calls within required time.

# Installation

Preconditions:

* [Python 3](https://www.python.org/downloads/), [Virtualenv](https://virtualenv.pypa.io/en/latest/) and [pip](https://pypi.org/project/pip/)
* [Google Cloud Platform](https://console.cloud.google.com) project
* [Google Cloud SDK](https://cloud.google.com/sdk/)

```
virtualenv -p python3 venv
. venv/bin/activate
pip install -r requirements.txt

gcloud init
gsutil mb gs://ggly
gsutil mb gs://ggly-tasks-fb
```

# Deployment

## URL handler
```
gcloud functions deploy ggly --entry-point handle_url --runtime python37 --trigger-http --region europe-west1
```
You can test it with the following call:
```
curl https://europe-west1-<PROJECT_NAME>.cloudfunctions.net/ggly?url=<IMAGE_URL>
```
## Facebook Messenger handler
```
gcloud functions deploy ggly_fb --entry-point handle_fb_webhook --runtime python37 --trigger-http --region europe-west1
Add FB_ACCESS_TOKEN and FB_VERIFY_TOKEN environment variables to the function

gcloud functions deploy ggly_fb_worker --entry-point handle_fb_gcs_event --runtime python37 --trigger-resource ggly-tasks-fb --trigger-event google.storage.object.finalize --region europe-west1
Add FB_ACCESS_TOKEN and FB_VERIFY_TOKEN environment variables to the function
```

# Local development:

1. Create a new gcloud service account and grant it the following roles:
    - roles/logging.logWriter
    - roles/storage.objectCreator

2. Open permission settings for your GCS bucket and add `Storage Legacy Bucket Reader` for the service account
3. Download service account credentials file and save it to `.credentials` folder

```
FLASK_APP=local_http.py GOOGLE_APPLICATION_CREDENTIALS=.credentials/ggly-local-dev.json flask run
```
```
curl -X GET "localhost:5000/ggly?url=<IMAGE_URL>"
```

# Camera mode
PYTHONPATH=.:./venv/bin/python python ggly/local/camera.py

Demo video:

[![Camera mode demo](https://img.youtube.com/vi/CPTCqqRuiv4/0.jpg)](https://www.youtube.com/watch?v=CPTCqqRuiv4)

# Bot review

![review](https://user-images.githubusercontent.com/8040747/65640583-f8bd2f00-dfea-11e9-8ecf-5e1854292bc3.png)

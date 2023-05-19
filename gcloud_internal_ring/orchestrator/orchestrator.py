from googleapiclient.discovery import build
import google.auth
import google.auth.transport.requests

GCLOUD_CREDS = "asc23-378811-ca4948da7594.json"
SERVICE_NAME = ""
IMAGE_URL    = ""

def load_creds():
    creds, proj  = google.auth.load_credentials_from_file(GCLOUD_CREDS)
    auth_request = google.auth.transport.requests.Request()
    creds.refresh(auth_request) 
    return (creds, proj)

if __name__ == "__main__":
    creds, proj = load_creds()

    service = build('run', 'v1', credentials=creds)
    service_request = {
        'apiVersion': 'serving.knative.dev/v1',
        'kind': 'Service',
        'metadata': {
            'name': SERVICE_NAME,
        },
        'spec': {
            'template': {
                'spec': {
                    'containers': [
                        {
                            'image': IMAGE_URL,
                        },
                    ],
                },
            },
        },
    }
    # response = service.namespaces().services().create(parent=f'namespaces/{proj}/services', body=service_request).execute()

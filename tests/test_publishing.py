from flask import Flask
from publishing.publish import create_app  # Ensure this is the correct import

def test_publishing_endpoint():
    app = create_app()
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200, "Homepage should return status 200"
    assert b"Sample News Title" in response.data, "Sample news title should appear in the output"

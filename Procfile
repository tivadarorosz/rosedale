# The --keep-alive option sets the maximum time (in seconds) to wait for requests on a keep-alive connection.
# This ensures that the health check requests are handled properly by Gunicorn.
web: cd /workspace && gunicorn --keep-alive 60 app:app
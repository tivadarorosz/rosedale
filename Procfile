# The --keep-alive option sets the maximum time (in seconds) to wait for requests on a keep-alive connection.
# The --timeout option sets the maximum time for a response from the healthcheck endpoint
web: gunicorn --preload --keep-alive 60 --timeout 30 app:app
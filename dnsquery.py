from flask import Flask, flash, redirect, render_template, request, session, abort
import os
import subprocess
import sys


app = Flask(__name__)

@app.route('/',methods = ['POST', 'GET'])
def dnsQuery():
    if request.method == 'GET':
        # Render the main page
        return render_template('dns-query.html')
    elif request.method == 'POST':
        # Arguments to send to method
        hostname = str(request.form.get('hostname'))
        name_server = str(request.form.get('name_server'))
        record_type = str(request.form.get('record_type'))

        # Build the results
        result = resolver(hostname,name_server,record_type)

        # Render the page with the results
        return render_template('dns-query.html',result=result)

def resolver(host, nameServer, recordType):
    # Check if host is empty
    if host == "":
        return "No host provided!"

    # Check if nameServer is empty
    if nameServer == "":
        # Set default resolver
        nameServer = str("8.8.8.8")

    # Check if recordType is empty
    if recordType == "":
        # Set default record type to ANY
        recordType = str("ANY")

    # Build command to run
    command = "dig @" + nameServer + " " + host + " " + recordType

    # Run command and store results
    result = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Return the command results
    return result.stdout.read().decode(sys.stdout.encoding)


if __name__ == '__main__':
    app.run(debug = True)